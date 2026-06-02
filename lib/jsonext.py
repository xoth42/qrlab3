"""JSON helpers with native support for complex numbers."""

import json

def encode_complex(obj):
    """Encode Python complex numbers into a JSON-friendly mapping."""
    if isinstance(obj, complex):
        return {"__complex__": True, "re": obj.real, "im": obj.imag}
    raise TypeError

def decode_complex(obj):
    """Decode complex numbers that were stored by :func:`encode_complex`."""
    if "__complex__" in obj:
        return obj["re"] + 1j * obj["im"]
    return obj

def dump(*args, **kwargs):
    """
    Wrapper for :func:`json.dump` with sensible defaults.

    Complex numbers are serialized as ``{"__complex__": True, ...}`` so the
    project can round-trip settings files and instrument state without custom
    encoders at every call site.
    """
    kwargs["default"] = encode_complex
    kwargs["indent"] = kwargs.get("indent", 4)
    kwargs["sort_keys"] = kwargs.get("sort_keys", True)
    json.dump(*args, **kwargs)

def load(f, **kwargs):
    """Wrapper for :func:`json.load` that restores encoded complex values."""
    return json.load(f, object_hook=decode_complex, **kwargs)
