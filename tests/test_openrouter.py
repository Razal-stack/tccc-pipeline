import pytest

from tccc import openrouter


def fake_usage(monkeypatch, used):
    calls = []

    def fake_call(path, key, body=None, timeout=180):
        calls.append((path, key))
        return {"data": {"usage": used}}
    monkeypatch.setattr(openrouter, "call", fake_call)
    monkeypatch.setattr(openrouter, "BUDGET", 7.0)
    return calls


def test_under_the_cap_returns(monkeypatch, capsys):
    calls = fake_usage(monkeypatch, 3.9)
    openrouter.guard_budget("test-key")
    assert calls == [("/key", "test-key")]
    assert "$3.90" in capsys.readouterr().out


@pytest.mark.parametrize("used", [7.0, 9.5])
def test_at_or_over_the_cap_exits(monkeypatch, used):
    fake_usage(monkeypatch, used)
    with pytest.raises(SystemExit) as stop:
        openrouter.guard_budget("test-key")
    assert "budget cap reached" in str(stop.value)
