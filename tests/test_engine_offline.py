"""AC-5: importing the engine must not touch the network."""

import importlib
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_import_performs_no_network(monkeypatch):
    def _blocked(*args, **kwargs):
        raise AssertionError("network access attempted at import time")

    monkeypatch.setattr(socket, "socket", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    if hasattr(socket, "getaddrinfo"):
        monkeypatch.setattr(socket, "getaddrinfo", _blocked)

    import valuation_engine

    importlib.reload(valuation_engine)  # re-executes module top-level
