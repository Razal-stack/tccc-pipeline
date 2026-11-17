"""Small web app over the pipeline: upload a recording, review the card, see how the system scores.

    python3 -m uvicorn tccc.app:app --port 8000      # then open http://localhost:8000

Pages: dashboard (accuracy, benchmark history, every card with its flags), card (review sheet beside the PDF,
field-by-field score when ground truth exists), upload (new recording -> card in about 10 s).
"""
import html
import json
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from .pipeline import LLM_MODEL, process
from .score import TRUTH, prf, score_card

ROOT = Path(__file__).resolve().parent.parent
SETS = {"eval": ROOT / "out" / LLM_MODEL.replace("/", "__") / "all", "live": ROOT / "out" / "live"}
app = FastAPI(title="TCCC cards")

STYLE = """<style>body{font:15px system-ui;margin:0 auto;max-width:1100px;padding:16px;color:#1b1b1b;background:#fafafa}
h1{font-size:22px}h2{font-size:17px;margin-top:28px}table{border-collapse:collapse;width:100%;background:#fff}
td,th{border-bottom:1px solid #e3e3e3;padding:6px 8px;text-align:left;font-size:14px}.k{display:inline-block;
background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:10px 14px;margin:0 8px 8px 0}.k b{display:block;
font-size:22px}.warn{color:#a14d00}.bad{color:#b00020}pre{white-space:pre-wrap;background:#fff;border:1px solid #e3e3e3;
padding:12px;border-radius:8px}.row{display:flex;gap:16px;flex-wrap:wrap}.row>*{flex:1 1 420px}a{color:#0b57d0}</style>"""


def page(title, body):
    return HTMLResponse(f"<!doctype html><meta charset=utf-8><title>{title}</title>{STYLE}<h1>{title}</h1>{body}")


def card_score(card):
    truth = TRUTH.get(card["file"])
    if not truth:
        return None, []
    per_field, _ = score_card(card, truth)
    c = {o: list(per_field.values()).count(o) for o in ("correct", "wrong", "invented", "missed")}
    return prf(c)[2], [(f, o, card.get(f), truth.get(f)) for f, o in per_field.items() if o not in ("correct", "blank_ok")]


def cards(name):
    d = SETS[name] / "predictions"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        card = json.loads(p.read_text())
        review = (SETS[name] / "review" / f"{p.stem}.md").read_text()
        n_ask = review.split("## Check these")[0].count("\n- ") - review.count("nothing missing")
        n_flag = review.split("## Check these")[1].split("## Card")[0].count("\n- ") - review.count("nothing flagged")
        yield p.stem, card, n_ask, n_flag


@app.get("/")
def dashboard():
    runs = [json.loads(l) for l in (ROOT / "out" / "runs.jsonl").read_text().splitlines()] if (ROOT / "out" / "runs.jsonl").exists() else []
    best = {r["split"]: r for r in runs if r["model"] == LLM_MODEL}
    kpis = "".join(f'<span class=k>{lbl}<b>{best[s]["f1"]:.1%}</b>critical {best[s]["critical_f1"]:.1%}, '
                   f'{best[s]["invented"]} made up</span>' for s, lbl in (("heldout", "Held-out F1"), ("all", "All 50 F1")) if s in best)
    hist = "".join(f"<tr><td>{r['model']}</td><td>{r['split']}</td><td>{r['prompt']}</td><td>{r['f1']:.1%}</td>"
                   f"<td>{r['critical_f1']:.1%}</td><td>{r['invented']}</td><td>{r['boxes_f1']:.1%}</td></tr>" for r in reversed(runs[-30:]))
    rows = ""
    for name in ("live", "eval"):
        for stem, card, n_ask, n_flag in cards(name):
            f1, _ = card_score(card)
            rows += (f"<tr><td><a href='/card/{name}/{stem}'>{stem}</a></td><td>{name}</td>"
                     f"<td class={'warn' if n_ask else ''}>{n_ask}</td><td class={'warn' if n_flag else ''}>{n_flag}</td>"
                     f"<td>{'' if f1 is None else f'{f1:.0%}'}</td><td><a href='/pdf/{name}/{stem}'>PDF</a></td></tr>")
    return page("TCCC cards from recorded handovers", f"""{kpis}
<h2>New recording</h2><form action=/upload method=post enctype=multipart/form-data>
<input type=file name=audio accept="audio/*" required> <button>Make card</button> <small>about 10 s, under 1 cent</small></form>
<h2>Cards</h2><table><tr><th>Recording</th><th>Set</th><th>Ask sender</th><th>Flags</th><th>Score vs truth</th><th></th></tr>{rows}</table>
<h2>Benchmark history (run ledger)</h2><table><tr><th>Model</th><th>Split</th><th>Prompt</th><th>F1</th><th>Critical F1</th>
<th>Made up</th><th>Body boxes F1</th></tr>{hist}</table>""")


@app.get("/card/{name}/{stem}")
def card_page(name: str, stem: str):
    card = json.loads((SETS[name] / "predictions" / f"{stem}.json").read_text())
    review = (SETS[name] / "review" / f"{stem}.md").read_text()
    f1, errs = card_score(card)
    score = "" if f1 is None else (f"<h2>Against ground truth: F1 {f1:.0%}</h2><table><tr><th>Field</th><th>Outcome</th>"
                                   "<th>Card</th><th>Truth</th></tr>" + "".join(
        f"<tr><td>{f}</td><td class={'bad' if o in ('invented', 'wrong') else 'warn'}>{o}</td><td>{html.escape(str(p))}</td>"
        f"<td>{html.escape(str(t))}</td></tr>" for f, o, p, t in errs) + "</table>")
    return page(stem, f"""<p><a href=/>back</a></p><div class=row><pre>{html.escape(review)}</pre>
<iframe src='/pdf/{name}/{stem}' style='min-height:900px;border:1px solid #e3e3e3'></iframe></div>{score}""")


@app.get("/pdf/{name}/{stem}")
def pdf(name: str, stem: str):
    return FileResponse(SETS[name] / "cards" / f"{stem}.pdf", media_type="application/pdf")


@app.post("/upload")
def upload(audio: UploadFile = File(...)):
    dst = SETS["live"] / "uploads" / Path(audio.filename or "recording.wav").name
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(audio.file.read())
    process(dst, SETS["live"])
    return RedirectResponse(f"/card/live/{dst.stem}", status_code=303)
