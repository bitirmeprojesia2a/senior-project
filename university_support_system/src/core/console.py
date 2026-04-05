"""Console/stdout helpers for local CLI scripts."""

from __future__ import annotations

import io
import sys
from typing import TextIO


def _reconfigure_stream(stream: TextIO, *, encoding: str, errors: str) -> TextIO:
    """Best-effort stdio reconfiguration for Windows-friendly UTF-8 output."""
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding=encoding, errors=errors)
        return stream

    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        return io.TextIOWrapper(buffer, encoding=encoding, errors=errors)

    return stream


def configure_utf8_stdio(*, errors: str = "replace") -> None:
    """Force UTF-8 stdout/stderr for CLI scripts without requiring PYTHONIOENCODING."""
    sys.stdout = _reconfigure_stream(sys.stdout, encoding="utf-8", errors=errors)
    sys.stderr = _reconfigure_stream(sys.stderr, encoding="utf-8", errors=errors)
