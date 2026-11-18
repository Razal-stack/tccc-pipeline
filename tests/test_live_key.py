"""Running live with your own key: lookup order, and a plain message (not a stack trace) when no key is set."""
import pytest
from fastapi.testclient import TestClient

from tccc import app as app_module, config, openrouter


@pytest.fixture
def env_files(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    repo, parent = tmp_path / "repo.env", tmp_path / "parent.env"
    monkeypatch.setattr(config, "ENV_FILES", (repo, parent))
    return repo, parent


def test_missing_key_gives_plain_message(env_files):
    with pytest.raises(SystemExit) as stop:
        openrouter.load_key()
    assert ".env.example" in str(stop.value) and "OPENROUTER_API_KEY" in str(stop.value)


def test_lookup_order_env_then_repo_then_parent(env_files, monkeypatch):
    repo, parent = env_files
    parent.write_text("OPENROUTER_API_KEY=from-parent\n")
    assert openrouter.load_key() == "from-parent"
    repo.write_text("OPENROUTER_API_KEY='from-repo'\n")
    assert openrouter.load_key() == "from-repo"
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-env")
    assert openrouter.load_key() == "from-env"


def test_empty_value_in_env_file_counts_as_unset(env_files):
    repo, parent = env_files
    repo.write_text("OPENROUTER_API_KEY=\nTCCC_SECOND=\n")
    parent.write_text("OPENROUTER_API_KEY=from-parent\n")
    assert openrouter.load_key() == "from-parent"
    assert config.setting("TCCC_SECOND", "default") == "default"  # copying .env.example cannot switch the second listen off


def test_upload_without_key_shows_message_not_500(env_files, monkeypatch, tmp_path):
    called = []
    monkeypatch.setitem(app_module.SETS, "live", tmp_path)
    monkeypatch.setattr(app_module, "process", lambda *a, **k: called.append(a))
    r = TestClient(app_module.app).post("/upload", files={"audio": ("x.wav", b"RIFF", "audio/wav")})
    assert r.status_code == 200
    assert "No OpenRouter key found" in r.text and ".env.example" in r.text
    assert called == []
