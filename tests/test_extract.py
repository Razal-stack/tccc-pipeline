"""The reader's reply is checked before use, and a bad reply is not retried (temperature 0 would repeat it)."""
import json

import pytest

from tccc import extract


def fake_api(monkeypatch, content, finish="stop"):
    calls = []

    def call(path, key, body=None, timeout=180):
        calls.append(path)
        return {"choices": [{"finish_reason": finish, "message": {"content": content}}], "usage": {"cost": 0.01}}
    monkeypatch.setattr(extract, "call", call)
    return calls


def test_good_reply_is_returned_with_cost(monkeypatch):
    fake_api(monkeypatch, 'Sure: {"fields": {"last4": ["4417", "last four 4417"], "evac_urgent": true}, "flags": []}')
    reply, cost = extract.ask("m", "text", "k")
    assert reply["fields"]["last4"] == ["4417", "last four 4417"] and cost == 0.01


@pytest.mark.parametrize("content, finish, why", [
    ('{"fields": {}}', "length", "cut off"),
    ("I could not read the transcript.", "stop", "not valid JSON"),
    ('{"fields": ["last4", "4417"]}', "stop", "'fields' is not an object"),
    ('{"fields": {"last4": null}}', "stop", "last4"),
    ('{"fields": {"last4": ["4417", "q", "extra"]}}', "stop", "last4"),
    ('{"fields": {}, "flags": "check pulse"}', "stop", "'flags' must be a list"),
])
def test_unusable_replies_raise_bad_reply(monkeypatch, content, finish, why):
    fake_api(monkeypatch, content, finish)
    with pytest.raises(extract.BadReply, match=why):
        extract.ask("m", "text", "k")


@pytest.fixture
def run_setup(monkeypatch, tmp_path):
    monkeypatch.setattr(extract, "OUT", tmp_path)
    monkeypatch.setattr(extract, "load_key", lambda: "k")
    monkeypatch.setattr(extract, "guard_budget", lambda key: None)
    monkeypatch.setattr(extract, "transcript", lambda stem: "text")
    monkeypatch.setattr(extract.time, "sleep", lambda s: None)
    return tmp_path


def test_bad_reply_is_not_retried(monkeypatch, run_setup):
    calls = fake_api(monkeypatch, "not json")
    out = extract.run("m/x", ["handover-abc.wav"])
    assert len(calls) == 1 and not (out / "handover-abc.json").exists()


def test_network_errors_are_retried_then_cached(monkeypatch, run_setup):
    tries = []

    def flaky(path, key, body=None, timeout=180):
        tries.append(1)
        if len(tries) < 3:
            raise OSError("connection reset")
        return {"choices": [{"message": {"content": '{"fields": {"time": ["0650", "correction six fifty"]}}'}}]}
    monkeypatch.setattr(extract, "call", flaky)
    out = extract.run("m/x", ["handover-abc.wav"])
    assert len(tries) == 3
    assert json.loads((out / "handover-abc.json").read_text())["fields"]["time"][0] == "0650"
