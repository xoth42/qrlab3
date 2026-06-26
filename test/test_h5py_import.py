"""Regression tests for the dataserver h5py DLL failure on Windows.

dataserver.py imports h5py at module load time (line 25). On Windows, a pip-
installed h5py (or a broken conda reinstall after ``pip uninstall h5py``)
often fails with::

    ImportError: DLL load failed while importing defs: The specified procedure could not be found.

The supported fix is conda-forge only::

    conda install -c conda-forge h5py hdf5 --force-reinstall

See environment.yml — h5py must not be installed via pip on Windows.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

H5PY_DLL_ERROR_FRAGMENT = "DLL load failed while importing defs"

WINDOWS_H5PY_FIX = (
    "On Windows, install h5py+hdf5 from conda-forge only (not pip):\n"
    "  conda install -c conda-forge h5py hdf5 --force-reinstall\n"
    "If you ran ``pip uninstall h5py`` on a conda env, remove any "
    "*.conda_trash files under site-packages/h5py/ then reinstall with conda."
)


def _h5py_dist_info() -> importlib.metadata.PackageMetadata | None:
    try:
        return importlib.metadata.metadata("h5py")
    except importlib.metadata.PackageNotFoundError:
        return None


def _h5py_installer() -> str | None:
    """Return 'pip', 'conda', or None from the h5py *.dist-info/INSTALLER file."""
    for path in sys.path:
        for dist_info in Path(path).glob("h5py-*.dist-info"):
            installer = dist_info / "INSTALLER"
            if installer.is_file():
                return installer.read_text(encoding="utf-8").strip().lower()
    return None


def _h5py_package_dir() -> Path | None:
    """Locate h5py on disk without importing native extensions."""
    for path in sys.path:
        candidate = Path(path) / "h5py"
        if (candidate / "__init__.py").is_file():
            return candidate
    return None


def _conda_trash_files(pkg_dir: Path | None) -> list[Path]:
    if pkg_dir is None or not pkg_dir.is_dir():
        return []
    return sorted(pkg_dir.glob("*.conda_trash"))


def test_h5py_no_conda_trash_leftovers():
    """Leftover *.conda_trash files break h5py after pip uninstall + conda reinstall."""
    trash = _conda_trash_files(_h5py_package_dir())
    if trash:
        names = ", ".join(p.name for p in trash[:5])
        extra = f" (+{len(trash) - 5} more)" if len(trash) > 5 else ""
        pytest.fail(
            f"Found {len(trash)} h5py *.conda_trash file(s) ({names}{extra}).\n"
            + WINDOWS_H5PY_FIX
        )


def test_h5py_import_matches_dataserver():
    """Same import path as dataserver/dataserver.py — must not raise ImportError."""
    try:
        h5py = importlib.import_module("h5py")
    except ImportError as exc:
        msg = str(exc)
        if H5PY_DLL_ERROR_FRAGMENT in msg and sys.platform == "win32":
            pytest.fail(f"h5py import failed ({msg}).\n{WINDOWS_H5PY_FIX}")
        raise

    dist = _h5py_dist_info()
    version = dist["Version"] if dist is not None else "unknown"
    assert h5py.__file__ is not None
    assert version != "unknown"


def test_h5py_basic_file_roundtrip():
    """Minimal HDF5 read/write — catches broken native bindings after import succeeds."""
    h5py = importlib.import_module("h5py")

    data = np.array([1.0, 2.0, 3.0])
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
        path = tmp.name

    try:
        with h5py.File(path, "w") as f:
            f.create_dataset("dataset", data=data)

        with h5py.File(path, "r") as f:
            readback = f["dataset"][:]

        np.testing.assert_array_equal(readback, data)
    finally:
        Path(path).unlink(missing_ok=True)
