"""Typed interfaces for dynamic mclient/objectsharer proxies.

These protocols are consumed only by static type checkers and IDEs.
Runtime behavior is unchanged.

2026-07-02T16:45:02Z
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, overload


class UnknownInstrumentProxy(Protocol):
    """Fallback proxy when the instrument type is not modeled yet."""

    def __getattr__(self, name: str) -> Any:
        ...


class SC5511AInstrument(Protocol):
    """SignalCore SC5511A proxy (see instrument_plugins/SC5511A.py)."""

    def do_set_frequency(self, frequency_hz: float) -> Any:
        ...

    def do_get_frequency(self) -> float:
        ...

    def do_get_idn(self) -> str:
        ...


class KeysightAWGInstrument(Protocol):
    """Keysight AWG proxy (see instrument_plugins/Keysight_AWG.py)."""

    def do_get_part(self) -> str:
        ...

    def do_get_clock_freq(self) -> float:
        ...


class KeysightDIGInstrument(Protocol):
    """Keysight DIG proxy (see instrument_plugins/Keysight_DIG.py)."""

    def do_get_part(self) -> str:
        ...

    def do_get_clock_freq(self) -> float:
        ...

    def do_get_if_period(self) -> int:
        ...

    def do_get_clock_sync_freq(self) -> float:
        ...

    def do_get_prescaler(self, channel: int) -> int:
        ...


class AlazarDaemonInstrument(Protocol):
    """Alazar daemon proxy (see instrument_plugins/Alazar_Daemon.py)."""

    def set_ch1_range(self, value: str) -> Any:
        ...

    def set_ch2_range(self, value: str) -> Any:
        ...

    def set_nsamples(self, value: int) -> Any:
        ...

    def set_naverages(self, value: int) -> Any:
        ...

    def set_ch1_coupling(self, value: str) -> Any:
        ...

    def set_ch2_coupling(self, value: str) -> Any:
        ...

    def set_clock_source(self, value: str) -> Any:
        ...

    def set_sample_rate(self, value: str) -> Any:
        ...

    def set_engJ_trig_src(self, value: str) -> Any:
        ...

    def set_engJ_trig_lvl(self, value: int) -> Any:
        ...

    def set_real_signals(self, value: bool) -> Any:
        ...

    def setup_channels(self) -> Any:
        ...

    def setup_trigger(self) -> Any:
        ...


class ReadoutIQInfoInstrument(Protocol):
    """Readout_IQ_Info proxy (see instrument_plugins/Readout_IQ_Info.py)."""

    def do_get_sequence(self, pulse_len: int | None = None) -> Any:
        ...

    def set_pulse_width(self, pulse_width: int) -> Any:
        ...


class QubitInfoInstrument(Protocol):
    """Qubit_Info proxy (see instrument_plugins/Qubit_Info.py)."""

    def get_parameter_values(self) -> dict[str, Any]:
        ...


class DataFileProxy(Protocol):
    def get_fullname(self) -> str:
        ...


class DataServerProxy(Protocol):
    def get_file(self, path: str) -> DataFileProxy:
        ...


class InstrumentsProxy(Protocol):
    """Typed interface for the remote `instruments` object.

    Extend this with more overloads as you add instrument plugins.
    """

    @overload
    def create(
        self,
        name: str,
        instype: Literal["SC5511A"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> SC5511AInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: Literal["Keysight_AWG"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> KeysightAWGInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: Literal["Keysight_DIG"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> KeysightDIGInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: Literal["Alazar_Daemon"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> AlazarDaemonInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: Literal["Readout_IQ_Info"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> ReadoutIQInfoInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: Literal["Qubit_Info"],
        waittime: int = 5000,
        **kwargs: Any,
    ) -> QubitInfoInstrument:
        ...

    @overload
    def create(
        self,
        name: str,
        instype: str,
        waittime: int = 5000,
        **kwargs: Any,
    ) -> UnknownInstrumentProxy:
        ...

    def create(self, name: str, instype: str, waittime: int = 5000, **kwargs: Any) -> Any:
        ...

    def get(self, name: str) -> UnknownInstrumentProxy | None:
        ...

    def list_instruments(self) -> list[str]:
        ...

    def get_all_parameters(self) -> dict[str, dict[str, Any]]:
        ...
