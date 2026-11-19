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


LISTEN = ("Transcribe this casualty handover recording verbatim, in English. Include every word, number, correction "
          "and repetition exactly as spoken. Output only the transcript.")


def _request(model, audio: bytes, keyterms, chat):
    """Speech models use the transcription endpoint; audio chat models get the recording plus 'transcribe verbatim'."""
    b64 = base64.b64encode(audio).decode()
    if chat:
        content = [{"type": "text", "text": LISTEN}, {"type": "input_audio", "input_audio": {"data": b64, "format": "wav"}}]
        return "/chat/completions", {"model": model, "temperature": 0, "max_tokens": 2000,
                                     "messages": [{"role": "user", "content": content}]}
    body = {"model": model, "input_audio": {"data": b64, "format": "wav"}, "language": "en", "temperature": 0}
    if keyterms:
        body["keyterms"] = KEYTERMS
    if "whisper" in model:
        body["provider"] = {"options": {"groq": {"prompt": VOCAB}}}
    return "/audio/transcriptions", body


def transcribe(key: str, model: str, wav: Path, keyterms: bool = False, chat: bool = False) -> tuple:
    """Whole recording -> (text, (cost, seconds)). Resent at 16 kHz if the model rejects the file as too large."""
    data = audio = wav.read_bytes()
    for attempt in range(4):
        path, body = _request(model, audio, keyterms, chat)
        try:
            r = call(path, key, body, timeout=300)
            u = r.get("usage") or {}
            text = (r["choices"][0]["message"].get("content") or "") if chat else r.get("text", "")
            return text.strip(), (u.get("cost") or 0.0, u.get("seconds") or 0.0)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (400, 413) and ("large" in msg.lower() or "sample rate" in msg.lower()) and audio is data:
                audio = to_16k(data)  # some models cap file size or only take 16 kHz
                continue
            if e.code in (402, 429, 502, 503) and attempt < 3:  # 402: credit held by in-flight requests, wait
                time.sleep(5 * (attempt + 1))
                continue
            return f"__ERROR__ {e.code} {msg}", (0.0, 0.0)
        except Exception as e:  # noqa: BLE001
            if attempt < 3:
                time.sleep(3)
                continue
            return f"__ERROR__ {e}", (0.0, 0.0)
