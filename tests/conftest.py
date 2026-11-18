import socket

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "golden: reproduces the published scores from cached model replies (slower)")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Tests are offline: any attempt to open a real connection fails loudly."""
    def refuse(*args, **kwargs):
        raise RuntimeError("network access is not allowed in tests")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
