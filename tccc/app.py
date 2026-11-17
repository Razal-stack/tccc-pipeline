"""Web app over the pipeline: upload a recording, review its card, see how the system scores.

    python3 -m uvicorn tccc.app:app --port 8000      # then open http://localhost:8000

Tabs: Cards (every card, its flags and score; upload a new recording), Benchmark (speech-to-text and model
comparisons, prompt history, accuracy by group, where errors come from), How it works. Everything is read live
from the results on disk, so a new run shows up on refresh.
"""
import csv
import html
import json
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from .pipeline import LLM_MODEL, STT_MODEL, process
from .score import TRUTH, group_of, prf, score_card

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SETS = {"eval": OUT / LLM_MODEL.replace("/", "__") / "all", "live": OUT / "live"}
app = FastAPI(title="TCCC cards")
esc = html.escape
CHOSEN = ' <span class="pill info">chosen</span>'

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Spline+Sans+Mono:wght@400;500;600&display=swap');
:root{--navy:#041018;--ink:#0b0b0b;--blue:#0065b4;--sky:#079eda;--bg:#f4f6f8;--card:#fff;--line:#e2e6ea;--muted:#5b6670;
--green:#05893e;--amber:#b25e00;--red:#d40924;--mono:'Spline Sans Mono',ui-monospace,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 'Atkinson Hyperlegible',system-ui,sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--navy);color:#fff;padding:0 24px}.bar{max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:28px;height:60px;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.02em;display:flex;align-items:center;gap:10px;color:#fff}.brand i{width:10px;height:22px;background:linear-gradient(var(--sky),var(--blue));display:inline-block}
.brand small{font-family:var(--mono);font-size:11px;color:#8fb7d3;letter-spacing:.08em}
nav{display:flex;gap:4px;margin-left:auto}nav a{color:#b9c6d0;font-family:var(--mono);font-size:13px;padding:8px 12px;border-radius:6px}
nav a:hover{color:#fff;text-decoration:none;background:#0d2230}nav a.on{color:#fff;background:#0d2230;box-shadow:inset 0 -2px 0 var(--sky)}
main{max-width:1240px;margin:0 auto;padding:24px}h1{font-size:26px;margin:4px 0 4px}h2{font-size:18px;margin:0 0 12px}
.sub{color:var(--muted);margin:0 0 20px}.label{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:20px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.kpi b{display:block;font:600 28px/1.2 var(--mono);color:var(--navy);margin-top:4px}
.kpi.hero{background:var(--navy);border-color:var(--navy)}.kpi.hero b{color:#fff}.kpi.hero .label{color:#8fb7d3}.kpi span{font-size:13px;color:var(--muted)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-bottom:16px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}
table{width:100%;border-collapse:collapse}th{font:500 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:9px 10px;border-bottom:1px solid #eef1f4;font-size:14px;vertical-align:middle}tr:last-child td{border-bottom:0}tbody tr:hover{background:#f8fafc}
.mono{font-family:var(--mono);font-size:13px}.pill{display:inline-block;font:500 12px var(--mono);padding:2px 9px;border-radius:999px;white-space:nowrap}
.ok{background:#e4f4ea;color:var(--green)}.warn{background:#fdf0e1;color:var(--amber)}.bad{background:#fde6e9;color:var(--red)}.info{background:#e3effa;color:var(--blue)}.grey{background:#eef1f4;color:var(--muted)}
.meter{display:flex;align-items:center;gap:10px;min-width:160px}.meter .t{flex:1;height:8px;background:#eef1f4;border-radius:4px;overflow:hidden}
.meter .t i{display:block;height:100%;background:var(--blue);border-radius:4px}.meter .t i.alt{background:#b8c3cc}.meter .t i.pick{background:linear-gradient(90deg,var(--sky),var(--blue))}.meter .t i.good{background:var(--green)}.meter .t i.mid{background:var(--amber)}.meter .t i.low{background:var(--red)}
.meter b{font:500 13px var(--mono);width:46px;text-align:right}
.drop{border:2px dashed #b9c9d6;border-radius:10px;padding:18px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;background:#fafcfd}
button{background:var(--blue);color:#fff;border:0;border-radius:8px;padding:10px 18px;font:600 14px 'Atkinson Hyperlegible',sans-serif;cursor:pointer}button:disabled{background:#7a9cb8;cursor:wait}
.list{margin:0;padding:0;list-style:none}.list li{padding:8px 12px;border-radius:8px;margin-bottom:6px;font-size:14px}
.ask li{background:#fdf0e1;border-left:3px solid var(--amber)}.flag li{background:#fde6e9;border-left:3px solid var(--red)}.none li{background:#e4f4ea;border-left:3px solid var(--green)}.plain li{background:#f2f7fb;border-left:3px solid var(--sky)}
dl{display:grid;grid-template-columns:minmax(150px,auto) 1fr;gap:4px 14px;margin:0 0 14px}dt{font:12px var(--mono);color:var(--muted);padding-top:2px}dd{margin:0;font-weight:700}
.transcript{font:13px/1.7 var(--mono);color:#33404a;background:#f8fafc;border-radius:8px;padding:12px 14px;white-space:pre-wrap}
.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:16px;align-items:start}.sticky{position:sticky;top:16px}
iframe{width:100%;height:85vh;border:1px solid var(--line);border-radius:10px;background:#fff}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;counter-reset:s}
.step{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--sky);border-radius:10px;padding:16px}
.step:before{counter-increment:s;content:"0" counter(s);font:600 12px var(--mono);color:var(--sky)}.step h3{margin:6px 0;font-size:16px}.step p{margin:0;color:var(--muted);font-size:14px}
.chips span{display:inline-block;font:12px var(--mono);background:#e3effa;color:var(--blue);border-radius:6px;padding:2px 8px;margin:0 6px 6px 0}
@media(max-width:860px){.split{grid-template-columns:1fr}.sticky{position:static}nav{margin-left:0}}
"""


def page(tab, title, sub, body):
    tabs = "".join(f"<a class='{'on' if t == tab else ''}' href='{u}'>{n}</a>"
                   for t, n, u in (("cards", "Cards", "/"), ("bench", "Benchmark", "/benchmark"), ("how", "How it works", "/how")))
    return HTMLResponse(f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} · TCCC</title><style>{CSS}</style><header><div class=bar><a class=brand href=/><i></i>TCCC CARDS
<small>RECORDED HANDOVER → CASUALTY CARD</small></a><nav>{tabs}</nav></div></header>
<main><h1>{esc(title)}</h1><p class=sub>{sub}</p>{body}</main></html>""")


def meter(v, cls=""):
    cls = cls or ("good" if v >= .95 else "" if v >= .9 else "mid" if v >= .8 else "low")
    return f"<div class=meter><div class=t><i class='{cls}' style='width:{v:.1%}'></i></div><b>{v:.0%}</b></div>"


def runs():
    p = OUT / "runs.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def latest(split):
    return next((r for r in reversed(runs()) if r["model"] == LLM_MODEL and r["split"] == split), None)


def review(name, stem):
    """Review sheet sections as {title: [lines]} (Ask the sender, Check these, Card, Transcript)."""
    parts = (SETS[name] / "review" / f"{stem}.md").read_text().split("\n## ")[1:]
    out = {}
    for part in parts:
        title, _, body = part.partition("\n")
        out[title] = [l[2:] for l in body.splitlines() if l.startswith("- ") and l[2:] not in ("nothing missing", "nothing flagged")] \
            if title != "Transcript" else [body.strip()]
    return out


def card_score(card):
    truth = TRUTH.get(card["file"])
    if not truth:
        return None, []
    per_field, _ = score_card(card, truth)
    c = Counter(per_field.values())
    return prf(c)[2], [(f, o, card.get(f), truth.get(f)) for f, o in per_field.items() if o not in ("correct", "blank_ok")]


def all_cards():
    for name in ("live", "eval"):
        d = SETS[name] / "predictions"
        for p in sorted(d.glob("*.json")) if d.exists() else []:
            yield name, p.stem, json.loads(p.read_text()), review(name, p.stem)


@app.get("/")
def cards_tab():
    h, a = latest("heldout"), latest("all")
    kpis = ""
    if h:
        kpis += f"<div class='kpi hero'><div class=label>Held-out accuracy (F1)</div><b>{h['f1']:.1%}</b><span>25 recordings never tuned on</span></div>"
        kpis += f"<div class=kpi><div class=label>Safety-critical</div><b>{h['critical_f1']:.1%}</b><span>drugs, tourniquets, vitals, evac</span></div>"
        kpis += f"<div class=kpi><div class=label>Made-up values</div><b>{h['invented'] / 25:.2f}</b><span>per card, held-out</span></div>"
    if a:
        kpis += f"<div class=kpi><div class=label>All 50 cards</div><b>{a['f1']:.1%}</b><span>F1 on filled fields</span></div>"
    kpis += "<div class=kpi><div class=label>Per card</div><b>~10 s</b><span>about 1 US cent</span></div>"
    rows = ""
    for name, stem, card, rv in all_cards():
        f1, _ = card_score(card)
        ask, flags = len(rv.get("Ask the sender", [])), len(rv.get("Check these", []))
        status = "<span class='pill ok'>Ready</span>" if not ask and not flags else \
            (f"<span class='pill warn'>Ask {ask}</span> " if ask else "") + (f"<span class='pill bad'>Check {flags}</span>" if flags else "")
        who = card.get("name") or card.get("battle_roster") or "<span style='color:var(--muted)'>no identity given</span>"
        rows += (f"<tr><td><a class=mono href='/card/{name}/{stem}'>{stem.replace('handover-', '')}</a></td><td>{who}</td>"
                 f"<td><span class='pill {'info' if name == 'live' else 'grey'}'>{'new' if name == 'live' else 'eval'}</span></td>"
                 f"<td>{status}</td><td>{meter(f1) if f1 is not None else '<span class=mono>no truth</span>'}</td>"
                 f"<td><a class=mono href='/pdf/{name}/{stem}' target=_blank>PDF ↗</a></td></tr>")
    return page("cards", "Casualty cards", "Every recorded handover turned into a filled DD Form 1380, with what a medic should check.",
                f"""<div class=kpis>{kpis}</div>
<div class=panel><h2>New recording</h2><form class=drop action=/upload method=post enctype=multipart/form-data
onsubmit="this.querySelector('button').disabled=true;this.querySelector('button').textContent='Listening… about 10 s'">
<input type=file name=audio accept="audio/*" required><button>Make card</button>
<span class=label>speech → card → checks → PDF</span></form></div>
<div class=panel><table><thead><tr><th>Recording</th><th>Casualty</th><th>Set</th><th>Medic review</th><th>Score vs ground truth</th><th></th></tr></thead>
<tbody>{rows}</tbody></table></div>""")


@app.get("/card/{name}/{stem}")
def card_tab(name: str, stem: str):
    card = json.loads((SETS[name] / "predictions" / f"{stem}.json").read_text())
    rv = review(name, stem)
    f1, errs = card_score(card)

    def items(key, cls, empty):
        xs = rv.get(key, [])
        return f"<ul class='list {cls if xs else 'none'}'>" + "".join(f"<li>{esc(x)}</li>" for x in xs or [empty]) + "</ul>"

    groups = {}
    for k, v in card.items():
        if v and k not in ("file", "injury_boxes", "notes"):
            groups.setdefault(group_of(k), []).append((k, "✓" if v is True else v))
    fields = "".join(f"<div class=label style='margin:10px 0 6px'>{g.replace('_', ' ')}</div><dl>"
                     + "".join(f"<dt>{esc(k.replace('_', ' '))}</dt><dd>{esc(str(v))}</dd>" for k, v in kv) + "</dl>" for g, kv in groups.items())
    boxes = "".join(f"<span>{esc(b)}</span>" for b in card["injury_boxes"]) or "<span>none</span>"
    diff = ""
    if f1 is not None:
        diff = ("<div class=panel><h2>Against ground truth</h2>" + (meter(f1) if errs else "<p>Every field matches.</p>")
                + ("<table><thead><tr><th>Field</th><th>Outcome</th><th>Card</th><th>Truth</th></tr></thead><tbody>" + "".join(
                    f"<tr><td class=mono>{f}</td><td><span class='pill {'bad' if o in ('invented', 'wrong') else 'warn'}'>{o}</span></td>"
                    f"<td>{esc(str(p))}</td><td>{esc(str(t))}</td></tr>" for f, o, p, t in errs) + "</tbody></table>" if errs else "") + "</div>")
    score = f" · score <b>{f1:.0%}</b> vs ground truth" if f1 is not None else ""
    return page("cards", stem.replace("handover-", "Handover "), f"<a href=/>← all cards</a>{score}", f"""<div class=split><div>
<div class=panel><h2>Ask the sender</h2>{items('Ask the sender', 'ask', 'Nothing critical missing')}</div>
<div class=panel><h2>Check these</h2>{items('Check these', 'flag', 'Nothing flagged')}</div>
<div class=panel><h2>On the card</h2>{fields}<div class=label style='margin:10px 0 6px'>notes</div><p>{esc(card.get('notes') or '-')}</p>
<div class=label style='margin:10px 0 6px'>body diagram</div><div class=chips>{boxes}</div></div>
<div class=panel><h2>What was said</h2><div class=transcript>{esc(rv.get('Transcript', [''])[0])}</div></div>{diff}</div>
<div class=sticky><iframe src='/pdf/{name}/{stem}#view=FitH'></iframe></div></div>""")


@app.get("/benchmark")
def bench_tab():
    stt = []
    p = ROOT / "transcripts" / "_bakeoff.csv"
    if p.exists():
        stt = sorted(csv.DictReader(p.open()), key=lambda r: -float(r["hard_files_numbers"]))
    stt_rows = "".join(f"<tr><td class=mono>{esc(r['model'])}{CHOSEN if r['model'] == STT_MODEL + '+keyterms' else ''}</td>"
                       f"<td>{meter(float(r['hard_files_numbers']), 'pick' if r['model'] == STT_MODEL + '+keyterms' else 'alt')}</td>"
                       f"<td>{meter(float(r['all_numbers']), 'alt')}</td><td>{meter(float(r['drugs_kit']), 'alt')}</td>"
                       f"<td class=mono>{esc(r['cost_per_audio_hour'])}</td></tr>" for r in stt)
    models = []
    for d in OUT.iterdir():
        s = d / "dev" / "score.json"
        if s.exists():
            j = json.loads(s.read_text())
            models.append((j["overall"]["f1"], d.name.replace("__", "/"), j["critical"]["f1"], j["overall"].get("invented", 0)))
    model_rows = "".join(f"<tr><td class=mono>{esc(m)}{CHOSEN if m == LLM_MODEL else ''}</td>"
                         f"<td>{meter(f1, 'pick' if m == LLM_MODEL else 'alt')}</td><td>{meter(c, 'alt')}</td><td class=mono>{inv / 25:.2f}</td></tr>"
                         for f1, m, c, inv in sorted(models, reverse=True))
    rs = runs()
    hist = "".join(f"<tr><td class=mono>{esc(r['model'])}</td><td><span class='pill {'warn' if r['split'] == 'heldout' else 'grey'}'>{r['split']}</span></td>"
                   f"<td class=mono>{r['prompt']}</td><td>{meter(r['f1'])}</td><td>{meter(r['critical_f1'])}</td>"
                   f"<td class=mono>{r['invented']}</td><td>{meter(r['boxes_f1'])}</td></tr>" for r in reversed(rs))
    groups, stages, kinds = "", "", ""
    h = OUT / LLM_MODEL.replace("/", "__") / "heldout" / "score.json"
    if h.exists():
        g = json.loads(h.read_text())["groups"]
        groups = "".join(f"<tr><td>{k.replace('_', ' ')}</td><td>{meter(v['f1'])}</td></tr>" for k, v in sorted(g.items(), key=lambda kv: -kv[1]["f1"]))
    a = latest("all")
    if a:
        n = max(1, len(a["errors"]))
        explain = {"transcription": "never reached the transcript", "extraction": "in the transcript, model missed it",
                   "invented": "written but never said", "validation": "a check removed a right value"}
        stages = "".join(f"<tr><td>{k} <span class=label>{explain.get(k, '')}</span></td><td>{meter(v / n, 'alt')}</td><td class=mono>{v}</td></tr>"
                         for k, v in sorted(a["stages"].items(), key=lambda kv: -kv[1]))
        kinds = "".join(f"<tr><td>{k}</td><td>{meter(v / n, 'alt')}</td><td class=mono>{v}</td></tr>"
                        for k, v in Counter(e.get("kind", "?") for e in a["errors"]).most_common())
    return page("bench", "Benchmark", "Every choice in the pipeline was measured. Tuning used 25 recordings; the other 25 were held out and run once.",
                f"""<div class=grid2><div class=panel><h2>Accuracy by field group <span class=label>held-out</span></h2><table>{groups}</table></div>
<div class=panel><h2>Where errors come from <span class=label>all 50</span></h2><table>{stages}</table>
<h2 style='margin-top:18px'>Kinds of error</h2><table>{kinds}</table></div></div>
<div class=panel><h2>Speech-to-text <span class=label>share of true values found in the transcript</span></h2><table><thead><tr><th>Model</th>
<th>Hard audio numbers</th><th>All numbers</th><th>Drugs &amp; kit</th><th>Cost / audio hour</th></tr></thead><tbody>{stt_rows}</tbody></table></div>
<div class=panel><h2>Extraction models <span class=label>dev set, latest prompt each was run with</span></h2><table><thead><tr><th>Model</th>
<th>F1</th><th>Safety-critical</th><th>Made up / card</th></tr></thead><tbody>{model_rows}</tbody></table></div>
<div class=panel><h2>Run history <span class=label>every scored run, newest first</span></h2><table><thead><tr><th>Model</th><th>Split</th><th>Prompt</th>
<th>F1</th><th>Safety-critical</th><th>Made up</th><th>Body diagram</th></tr></thead><tbody>{hist}</tbody></table></div>""")


@app.get("/how")
def how_tab():
    steps = [("Transcribe", f"{STT_MODEL}, with a list of expected words (TXA, IV, unit names). Whole recording, no chopping."),
             ("Extract", f"{LLM_MODEL} reads the transcript and returns only fields that were said, each with the exact words."),
             ("Check", "Plain code: value must be in the transcript, right format, medically plausible. Fails → blank + flag."),
             ("Body diagram", "Spoken locations map to the card's 163 named tick boxes by lookup, so the X lands exactly."),
             ("PDF + review", "Filled into the real DD Form 1380, read back to verify. Review sheet: ask the sender, check these."),
             ("Score", "Against ground truth. Every error tagged by step and kind, logged for the next round.")]
    return page("how", "How it works", "One fixed chain, no agent loop. Accuracy first, then cost, then speed.",
                "<div class=steps>" + "".join(f"<div class=step><h3>{t}</h3><p>{esc(d)}</p></div>" for t, d in steps) + "</div>"
                + """<div class=grid2 style='margin-top:16px'><div class=panel><h2>Why it is built this way</h2><ul class='list plain'>
<li>Blank and flagged beats confident and wrong: a surgeon acts on this card.</li>
<li>Two strong models agree on 99.6% of fields, so a second-opinion model adds almost nothing.</li>
<li>Noise reduction made transcription worse; raw audio goes in.</li><li>The body diagram is named tick boxes, so no vision model is needed.</li></ul></div>
<div class=panel><h2>In the field</h2><ul class='list plain'><li>Record the handover; the card is ready in about 10 seconds.</li>
<li>The medic reads a short list, not 138 boxes: what to ask the sender, what to confirm.</li>
<li>Every value traces back to the words that were spoken.</li><li>Fifty casualties run in parallel in about a minute.</li></ul></div></div>""")


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
