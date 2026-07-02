"""Type stub for the dynamic mclient module."""

from __future__ import annotations

from typing import Any

from tools.generated.mclient_typing_autogen import InstrumentsProxy

# Generated at 2026-07-02T17:16:03Z

instruments: InstrumentsProxy
datasrv: Any

def parse_chans(chans: str) -> list[int | str] | None: ...

class Container: ...

def get_container_object(name: str) -> Container: ...

def get_qubit_info(name: str, detune: float | None = ...) -> Container: ...

def get_readout_info(name: str) -> Any: ...

def save_instruments() -> Any: ...