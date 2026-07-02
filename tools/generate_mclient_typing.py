#!/usr/bin/env python3
"""Generate typed protocols and factory overloads for instrument proxies.

This script parses instrument plugin source files via AST (no imports),
extracts the primary Instrument-derived class and its public methods,
and writes a typed module that static analyzers can consume.

2026-07-02T17:05:00Z
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MethodSig:
    name: str
    params_src: str


@dataclass(frozen=True)
class PluginType:
    instype: str
    class_name: str
    protocol_name: str
    module_relpath: str
    class_doc: str
    methods: tuple[MethodSig, ...]


def _timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _snake_to_camel(name: str) -> str:
    parts = re.split(r"[^0-9A-Za-z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _sanitize_protocol_name(instype: str) -> str:
    camel = _snake_to_camel(instype)
    if not camel:
        camel = "Instrument"
    if camel[0].isdigit():
        camel = f"I{camel}"
    return f"{camel}Instrument"


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""


def _is_public_method(fn: ast.FunctionDef) -> bool:
    if fn.name.startswith("_"):
        return False
    if fn.name in {"remove"}:
        # Proxy lifecycle method exists everywhere and is often noisy.
        return False
    return True


def _format_method_params(fn: ast.FunctionDef) -> str:
    """Build a permissive parameter list preserving call shapes.

    We intentionally annotate everything as Any to avoid false precision while
    preserving names and optional/default markers for IDE hints.
    """

    parts: list[str] = ["self"]

    posonly = fn.args.posonlyargs
    regular = fn.args.args
    defaults = fn.args.defaults

    regular_no_self = regular[1:] if regular and regular[0].arg == "self" else regular
    combined = posonly + regular_no_self
    required_count = len(combined) - len(defaults)

    for idx, arg in enumerate(combined):
        name = arg.arg
        suffix = " = ..." if idx >= required_count else ""
        parts.append(f"{name}: Any{suffix}")

    if posonly:
        parts.append("/")

    if fn.args.vararg:
        parts.append(f"*{fn.args.vararg.arg}: Any")
    elif fn.args.kwonlyargs:
        parts.append("*")

    for kwarg, kwdefault in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
        suffix = " = ..." if kwdefault is not None else ""
        parts.append(f"{kwarg.arg}: Any{suffix}")

    if fn.args.kwarg:
        parts.append(f"**{fn.args.kwarg.arg}: Any")

    return ", ".join(parts)


def _first_line_doc(node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    doc = ast.get_docstring(node) or ""
    line = doc.strip().splitlines()[0] if doc.strip() else ""
    return line


def _escape_docstring(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

_FLAG_VALUES = {
    "FLAG_GET": 0x01,
    "FLAG_SET": 0x02,
    "FLAG_GET_AFTER_SET": 0x04,
    "FLAG_SOFTGET": 0x08,
}

def _resolve_flag_name(node: ast.AST) -> int | None:
    if isinstance(node, ast.Attribute) and node.attr in _FLAG_VALUES:
        return _FLAG_VALUES[node.attr]
    return None


def _eval_simple_expr(node: ast.AST | None) -> object | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Tuple):
        values = []
        for elt in node.elts:
            value = _eval_simple_expr(elt)
            if value is None:
                return None
            values.append(value)
        return tuple(values)
    if isinstance(node, ast.List):
        values = []
        for elt in node.elts:
            value = _eval_simple_expr(elt)
            if value is None:
                return None
            values.append(value)
        return values
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_simple_expr(node.operand)
        if isinstance(value, (int, float)):
            return value if isinstance(node.op, ast.UAdd) else -value
        return None
    if isinstance(node, ast.BinOp):
        left = _eval_simple_expr(node.left)
        right = _eval_simple_expr(node.right)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.BitOr) and isinstance(left, int) and isinstance(right, int):
            return left | right
        if isinstance(node.op, ast.BitAnd) and isinstance(left, int) and isinstance(right, int):
            return left & right
        if isinstance(node.op, ast.Add):
            return left + right  # type: ignore[operator]
        if isinstance(node.op, ast.Sub):
            return left - right  # type: ignore[operator]
        if isinstance(node.op, ast.Mult):
            return left * right  # type: ignore[operator]
        if isinstance(node.op, ast.Mod):
            return left % right  # type: ignore[operator]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range":
        args = [_eval_simple_expr(arg) for arg in node.args]
        if any(arg is None for arg in args):
            return None
        if len(args) == 1:
            return tuple(range(args[0]))  # type: ignore[arg-type]
        if len(args) == 2:
            return tuple(range(args[0], args[1]))  # type: ignore[arg-type]
        if len(args) == 3:
            return tuple(range(args[0], args[1], args[2]))  # type: ignore[arg-type]
    if isinstance(node, ast.Attribute):
        resolved = _resolve_flag_name(node)
        if resolved is not None:
            return resolved
    return None


def _expand_parameter_names(param_name: str, channels: object | None, channel_prefix: str | None) -> list[str]:
    if channels is None:
        return [param_name]
    if not isinstance(channels, (list, tuple)):
        channels = (channels,)

    names: list[str] = []
    for channel in channels:
        if channel_prefix:
            try:
                channel_name = channel_prefix % channel
            except Exception:
                channel_name = f"{channel_prefix}{channel}"
            names.append(f"{channel_name}{param_name}")
        else:
            names.append(f"{param_name}{channel}")
    return names


def _collect_dynamic_methods(cls: ast.ClassDef) -> list[MethodSig]:
    methods: dict[str, MethodSig] = {}

    def add_method(name: str, params_src: str) -> None:
        methods.setdefault(name, MethodSig(name=name, params_src=params_src))

    for node in ast.walk(cls):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "self":
            continue

        if node.func.attr == "add_parameter" and node.args:
            param_name = _eval_simple_expr(node.args[0])
            if not isinstance(param_name, str):
                continue

            kw_map = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            flags = _eval_simple_expr(kw_map.get("flags"))
            if not isinstance(flags, int):
                flags = _FLAG_VALUES["FLAG_GET"] | _FLAG_VALUES["FLAG_SET"]
            channels = _eval_simple_expr(kw_map.get("channels"))
            channel_prefix = _eval_simple_expr(kw_map.get("channel_prefix"))
            if channel_prefix is not None and not isinstance(channel_prefix, str):
                channel_prefix = None

            for expanded_name in _expand_parameter_names(param_name, channels, channel_prefix):
                if flags & (_FLAG_VALUES["FLAG_GET"] | _FLAG_VALUES["FLAG_SOFTGET"]):
                    add_method(f"get_{expanded_name}", "self, query: Any = ..., **lopts: Any")
                if flags & _FLAG_VALUES["FLAG_SET"]:
                    add_method(f"set_{expanded_name}", "self, value: Any, **lopts: Any")

        elif node.func.attr == "add_function" and node.args:
            func_name = _eval_simple_expr(node.args[0])
            if isinstance(func_name, str):
                add_method(func_name, "self, *args: Any, **kwargs: Any")

    return list(methods.values())


def _select_primary_class(tree: ast.Module) -> ast.ClassDef | None:
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if not classes:
        return None

    for cls in classes:
        base_names = {_base_name(b) for b in cls.bases}
        if "Instrument" in base_names:
            return cls

    for cls in classes:
        if not cls.name.startswith("_"):
            return cls

    return classes[0]


def _parse_plugin_file(path: Path, root: Path) -> PluginType | None:
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None

    cls = _select_primary_class(tree)
    if cls is None:
        return None

    methods: dict[str, MethodSig] = {}
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and _is_public_method(node):
            methods[node.name] = MethodSig(name=node.name, params_src=_format_method_params(node))

    for dyn_method in _collect_dynamic_methods(cls):
        methods.setdefault(dyn_method.name, dyn_method)

    sorted_methods = sorted(methods.values(), key=lambda m: m.name)

    rel = path.relative_to(root).as_posix()
    instype = path.stem
    protocol_name = _sanitize_protocol_name(instype)

    return PluginType(
        instype=instype,
        class_name=cls.name,
        protocol_name=protocol_name,
        module_relpath=rel,
        class_doc=_first_line_doc(cls),
        methods=tuple(sorted_methods),
    )


def _iter_plugins(plugin_dir: Path) -> Iterable[Path]:
    for path in sorted(plugin_dir.glob("*.py")):
        if path.name == "__init__.py" or path.name.startswith("_"):
            continue
        yield path


def _render(types: list[PluginType], ts: str) -> str:
    lines: list[str] = []
    lines.append('"""Auto-generated typing protocols for dynamic mclient instruments.')
    lines.append("")
    lines.append("Generated by tools/generate_mclient_typing.py.")
    lines.append("Do not edit manually; regenerate instead.")
    lines.append("")
    lines.append(ts)
    lines.append('"""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Any, Literal, Protocol, overload")
    lines.append("")
    lines.append("")
    lines.append("class UnknownInstrumentProxy(Protocol):")
    lines.append("    \"\"\"Fallback proxy when the instrument type is not modeled yet.\"\"\"")
    lines.append("")
    lines.append("    def __getattr__(self, name: str) -> Any:")
    lines.append("        ...")
    lines.append("")

    for t in types:
        lines.append("")
        lines.append(f"class {t.protocol_name}(Protocol):")
        hint = f" ({t.class_doc})" if t.class_doc else ""
        lines.append(
            f"    \"\"\"Proxy for {t.instype} -> {t.class_name} in {t.module_relpath}{_escape_docstring(hint)}\"\"\""
        )
        if not t.methods:
            lines.append("")
            lines.append("    def __getattr__(self, name: str) -> Any:")
            lines.append("        ...")
        else:
            for m in t.methods:
                lines.append("")
                lines.append(f"    def {m.name}({m.params_src}) -> Any:")
                lines.append("        ...")

    lines.append("")
    lines.append("")
    lines.append("class InstrumentsProxy(Protocol):")
    lines.append("    \"\"\"Typed interface for dynamic mclient.instruments proxy.\"\"\"")

    for t in types:
        lines.append("")
        lines.append("    @overload")
        lines.append("    def create(")
        lines.append("        self,")
        lines.append("        name: str,")
        lines.append(f"        instype: Literal[\"{t.instype}\"],")
        lines.append("        waittime: int = 5000,")
        lines.append("        **kwargs: Any,")
        lines.append(f"    ) -> {t.protocol_name}:")
        lines.append("        ...")

    lines.append("")
    lines.append("    @overload")
    lines.append("    def create(")
    lines.append("        self,")
    lines.append("        name: str,")
    lines.append("        instype: str,")
    lines.append("        waittime: int = 5000,")
    lines.append("        **kwargs: Any,")
    lines.append("    ) -> UnknownInstrumentProxy:")
    lines.append("        ...")
    lines.append("")
    lines.append("    def create(self, name: str, instype: str, waittime: int = 5000, **kwargs: Any) -> Any:")
    lines.append("        ...")
    lines.append("")
    lines.append("    def get(self, name: str) -> UnknownInstrumentProxy | None:")
    lines.append("        ...")
    lines.append("")
    lines.append("    def list_instruments(self) -> list[str]:")
    lines.append("        ...")
    lines.append("")
    lines.append("    def get_all_parameters(self) -> dict[str, dict[str, Any]]:")
    lines.append("        ...")
    lines.append("")

    return "\n".join(lines)


def _render_mclient_stub(ts: str) -> str:
    return "\n".join(
        [
            '"""Type stub for the dynamic mclient module."""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import Any",
            "",
            "from tools.generated.mclient_typing_autogen import InstrumentsProxy",
            "",
            f"# Generated at {ts}",
            "",
            "instruments: InstrumentsProxy",
            "datasrv: Any",
            "",
            "def parse_chans(chans: str) -> list[int | str] | None: ...",
            "",
            "class Container: ...",
            "",
            "def get_container_object(name: str) -> Container: ...",
            "",
            "def get_qubit_info(name: str, detune: float | None = ...) -> Container: ...",
            "",
            "def get_readout_info(name: str) -> Any: ...",
            "",
            "def save_instruments() -> Any: ...",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugins-dir",
        default="instrumentserver/instrument_plugins",
        help="Directory containing instrument plugin Python files.",
    )
    parser.add_argument(
        "--output",
        # 2026-07-02T17:11:10Z legacy default kept for traceability:
        # default="mclient_typing_autogen.py",
        default="tools/generated/mclient_typing_autogen.py",
        help="Output file path for generated typing module.",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    plugin_dir = (repo_root / args.plugins_dir).resolve()
    out_path = (repo_root / args.output).resolve()

    if not plugin_dir.exists():
        raise SystemExit(f"Plugin directory not found: {plugin_dir}")

    types: list[PluginType] = []
    for plugin_path in _iter_plugins(plugin_dir):
        parsed = _parse_plugin_file(plugin_path, repo_root)
        if parsed is not None:
            types.append(parsed)

    types.sort(key=lambda t: t.instype)
    ts = _timestamp()
    content = _render(types, ts)
    stub_content = _render_mclient_stub(ts)

    # 2026-07-02T17:11:10Z ensure generated directory exists by default.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    (repo_root / "mclient.pyi").write_text(stub_content, encoding="utf-8")
    typings_dir = repo_root / "typings"
    typings_dir.mkdir(parents=True, exist_ok=True)
    (typings_dir / "mclient.pyi").write_text(stub_content, encoding="utf-8")
    print(f"Generated {out_path} with {len(types)} instrument protocol entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
