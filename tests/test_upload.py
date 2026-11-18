"""An upload spends money, so it must stop at the spend cap before any model is called."""
from fastapi.testclient import TestClient

from tccc import app as app_module


def test_upload_stops_at_spend_cap(monkeypatch, tmp_path):
    called = []
    monkeypatch.setitem(app_module.SETS, "live", tmp_path)
    monkeypatch.setattr(app_module, "load_key", lambda: "test-key")
    monkeypatch.setattr(app_module, "guard_budget", lambda key: (_ for _ in ()).throw(SystemExit("budget cap reached")))
    monkeypatch.setattr(app_module, "process", lambda *a, **k: called.append(a))
    r = TestClient(app_module.app).post("/upload", files={"audio": ("x.wav", b"RIFF", "audio/wav")})
    assert r.status_code == 200
    assert "budget cap reached" in r.text
    assert called == []
