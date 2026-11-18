"""Speech-to-text through OpenRouter, with domain key terms to bias recognition toward drugs, kit and units."""
import audioop
import base64
import io
import time
import urllib.error
import wave
from pathlib import Path

from .openrouter import call

VOCAB = ("Expected vocabulary: NATO alphabet (Alpha, Bravo, Charlie ... Juliet, Sierra, Zulu), MIST, TCCC, battle roster, "
         "last four, CAT tourniquet, SOFTT-W, NPA, cric, needle decompression, chest seal, TXA, ketamine, fentanyl, "
         "lozenge, OTFC, morphine, ertapenem, moxifloxacin, Hartmann's, Plasma-Lyte, whole blood, IO, IV, IM, "
         "Cat A, T1, urgent, priority, routine, AVPU, sats, resps, obs, GSW, IED, RPG.")

KEYTERMS = ["TXA", "IV", "IO", "IM", "CAT", "SOFTT-W", "tourniquet", "fentanyl", "lozenge", "ketamine", "morphine",
            "ertapenem", "moxifloxacin", "Hartmann's", "Plasma-Lyte", "whole blood", "NPA", "cric", "chest seal",
            "needle decompression", "hypothermia prevention kit", "HPMK", "blizzard blanket", "battle roster",
            "last four", "MIST", "Cat A", "T1", "urgent", "priority", "routine", "AVPU", "Yorks", "Lancs", "Rifles",
            "Para", "Commando", "Royal Anglian", "Royal Welsh", "RMP", "RAF Regiment", "Irish Guards"]


def _wav(frames, width, rate):
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1), w.setsampwidth(width), w.setframerate(rate), w.writeframes(frames)
    return out.getvalue()


def to_16k(data: bytes) -> bytes:
    """48 kHz wav -> 16 kHz mono wav (a third of the size; speech models work at 16 kHz anyway)."""
    with wave.open(io.BytesIO(data)) as w:
        ch, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.readframes(w.getnframes())
    if ch > 1:
        frames = audioop.tomono(frames, width, .5, .5)
    frames, _ = audioop.ratecv(frames, width, 1, rate, 16000, None)
    return _wav(frames, width, 16000)


def transcribe(key, model, wav: Path, keyterms=False):
    """Whole recording -> text (no chopping: voice-activity splitting dropped radio speech)."""
    return _send(key, model, wav.read_bytes(), keyterms)


def _send(key, model, data: bytes, keyterms):
    body = {"model": model, "input_audio": {"data": base64.b64encode(data).decode(), "format": "wav"},
            "language": "en", "temperature": 0}
    if keyterms:
        body["keyterms"] = KEYTERMS
    if "whisper" in model:
        body["provider"] = {"options": {"groq": {"prompt": VOCAB}}}
    for attempt in range(3):
        try:
            r = call("/audio/transcriptions", key, body)
            u = r.get("usage") or {}
            return r.get("text", ""), (u.get("cost") or 0.0, u.get("seconds") or 0.0)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code == 400 and "large audio" in msg and body["input_audio"]["data"] == base64.b64encode(data).decode():
                body["input_audio"]["data"] = base64.b64encode(to_16k(data)).decode()  # some models cap file size
                continue
            if e.code in (429, 502, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return f"__ERROR__ {e.code} {msg}", (0.0, 0.0)
        except Exception as e:  # noqa: BLE001
            if attempt < 2:
                time.sleep(3)
                continue
            return f"__ERROR__ {e}", (0.0, 0.0)
