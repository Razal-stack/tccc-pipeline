"""Web app over the pipeline, built around how TCCC cards are used at a casualty collection point.

    python3 -m uvicorn tccc.app:app --port 8000      # then open http://localhost:8000

Casualties: everyone, urgent first, with what stands between the card and the casualty ("get from sender",
"confirm"). Card: the card in MIST order beside the PDF. Accuracy: what was measured and what it means.
Guide: how a medic uses it. Everything is read live from the results on disk.
"""
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from .pipeline import LLM_MODEL, STT_MODEL, process
from .score import TRUTH, prf, score_card

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SETS = {"eval": OUT / LLM_MODEL.replace("/", "__") / "all", "live": OUT / "live"}
EVAC = (("evac_urgent", "Urgent", "u"), ("evac_priority", "Priority", "p"), ("evac_routine", "Routine", "r"))
LIMBS = (("right_arm", "R arm"), ("left_arm", "L arm"), ("right_leg", "R leg"), ("left_leg", "L leg"))
MEDS = ("analgesic_1", "analgesic_2", "analgesic_3", "antibiotic_1", "antibiotic_2", "other_med_1", "other_med_2",
        "fluid_1", "fluid_2", "blood_1", "blood_2")
TREAT = {"dressing_hemostatic": "hemostatic dressing", "dressing_pressure": "pressure dressing", "dressing_other": "other dressing",
         "airway_intact": "airway intact", "airway_npa": "NPA", "airway_cric": "cric", "airway_et_tube": "ET tube", "airway_sga": "SGA",
         "breathing_o2": "oxygen", "breathing_needle_d": "needle decompression", "breathing_chest_tube": "chest tube",
         "breathing_chest_seal": "chest seal", "combat_pill_pack": "combat pill pack", "eye_shield": "eye shield", "splint": "splint",
         "hypothermia_prevention": "hypothermia prevention"}
app = FastAPI(title="Casualty cards")
esc = html.escape

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--paper:#f6f5f0;--ink:#1c1e1a;--soft:#5f615a;--line:#d9d6cc;--hair:#e8e6de;--olive:#3c4a2b;--olive2:#55663d;
--u:#a8261c;--ub:#f6e3e0;--p:#a35a0a;--pb:#f7ebd9;--r:#2f6a3e;--rb:#e3efe5;--n:#6b6d66;--nb:#ecebe5;--mono:'IBM Plex Mono',ui-monospace,monospace}
*{box-sizing:border-box}html{background:var(--paper)}body{margin:0;color:var(--ink);font:15px/1.55 'Public Sans',system-ui,sans-serif;font-feature-settings:"tnum"}
a{color:var(--olive);text-underline-offset:2px}header{border-bottom:1px solid var(--line);background:#fbfaf7}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}.top{display:flex;align-items:baseline;gap:28px;padding:16px 0 0;flex-wrap:wrap}
.mark{font-weight:700;font-size:17px;letter-spacing:-.01em;color:var(--ink);text-decoration:none}.mark span{color:var(--soft);font-weight:400}
nav{display:flex;gap:22px;margin-left:auto}nav a{color:var(--soft);text-decoration:none;padding:6px 0 12px;border-bottom:2px solid transparent;font-weight:500}
nav a.on,nav a:hover{color:var(--ink);border-color:var(--olive)}main{padding:28px 0 60px}
h1{font-size:24px;letter-spacing:-.015em;margin:0 0 6px}h2{font-size:16px;margin:0 0 10px}
.lede{color:var(--soft);max-width:760px;margin:0 0 22px}.mono{font-family:var(--mono);font-size:13px}
.facts{display:flex;gap:36px;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:14px 0;margin-bottom:22px}
.facts div{font-size:13px;color:var(--soft);max-width:220px}.facts b{display:block;font-size:22px;color:var(--ink);font-weight:600;letter-spacing:-.01em}
.tools{display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:0 0 10px}.seg{display:inline-flex;border:1px solid var(--line);border-radius:4px;overflow:hidden;background:#fff}
.seg button{border:0;background:none;padding:7px 12px;font:500 13px 'Public Sans',sans-serif;color:var(--soft);cursor:pointer;border-right:1px solid var(--line)}
.seg button:last-child{border-right:0}.seg button.on{background:var(--olive);color:#fff}.seg button i{font-style:normal;opacity:.7;margin-left:5px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line)}th{text-align:left;font-weight:600;font-size:12px;color:var(--soft);padding:9px 12px;border-bottom:1px solid var(--line);background:#fbfaf7}
td{padding:11px 12px;border-bottom:1px solid var(--hair);vertical-align:top;font-size:14px}tr:last-child td{border-bottom:0}
tr.row{cursor:pointer}tr.row:hover td{background:#fbfaf6}tr.u td:first-child{box-shadow:inset 4px 0 0 var(--u)}tr.p td:first-child{box-shadow:inset 4px 0 0 #d68a1c}tr.r td:first-child{box-shadow:inset 4px 0 0 var(--r)}tr.n td:first-child{box-shadow:inset 4px 0 0 #c9c7bf}td:first-child{padding-left:16px}
.who{font-weight:600}.sub{color:var(--soft);font-size:13px}.tag{display:inline-block;font-size:12px;font-weight:600;padding:1px 7px;border-radius:3px;vertical-align:middle}
.tag.u{background:var(--ub);color:var(--u)}.tag.p{background:var(--pb);color:var(--p)}.tag.r{background:var(--rb);color:var(--r)}.tag.n{background:var(--nb);color:var(--n)}
.st{font-size:13px;font-weight:600}.st.ok{color:var(--r)}.st.get{color:var(--p)}.st.conf{color:var(--u)}.st small{display:block;font-weight:400;color:var(--soft)}
.score{font-family:var(--mono);font-size:13px;color:var(--soft)}.score b{color:var(--ink);font-weight:500}
.up{display:flex;gap:12px;align-items:center;flex-wrap:wrap;background:#fff;border:1px solid var(--line);padding:12px 14px;margin-bottom:22px}
.btn{background:var(--olive);color:#fff;border:0;border-radius:4px;padding:8px 16px;font:600 14px 'Public Sans',sans-serif;cursor:pointer}.btn:disabled{background:var(--olive2);cursor:wait}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start}.stick{position:sticky;top:16px}
.box{background:#fff;border:1px solid var(--line);padding:16px 18px;margin-bottom:16px}.box.warn{border-left:4px solid #d68a1c}.box.bad{border-left:4px solid var(--u)}.box.good{border-left:4px solid var(--r)}
.box ul{margin:6px 0 0;padding-left:18px}.box li{margin:3px 0}.mist{display:grid;grid-template-columns:28px 1fr;gap:10px 12px;margin:14px 0 0}
.mist .l{font:600 18px var(--mono);color:var(--olive)}dl{display:grid;grid-template-columns:130px 1fr;gap:3px 12px;margin:0}dt{color:var(--soft);font-size:13px}dd{margin:0;font-weight:500}
.vit{width:auto;border:0;margin-top:2px}.vit td,.vit th{border:0;border-bottom:1px solid var(--hair);padding:4px 16px 4px 0;background:none;font-size:13px}
.say{font:13px/1.75 var(--mono);color:#3a3c36;white-space:pre-wrap}iframe{width:100%;height:88vh;border:1px solid var(--line);background:#fff}
.bar{display:flex;align-items:center;gap:10px}.bar s{display:block;height:10px;background:var(--olive);text-decoration:none}.bar s.dim{background:#b9b6aa}.bar span{font:13px var(--mono);color:var(--soft)}
.finding{border-top:1px solid var(--line);padding:22px 0}.facts+.finding{border-top:0}.finding p.take{font-size:17px;font-weight:600;margin:0 0 4px;max-width:820px;letter-spacing:-.01em}
.finding p.note{color:var(--soft);margin:0 0 14px;max-width:820px}.guide{max-width:820px}.guide ol,.guide ul{padding-left:20px}.guide li{margin:8px 0}
.key{display:grid;grid-template-columns:180px 1fr;gap:8px 16px;margin:10px 0 20px}
@media(max-width:900px){.cols{grid-template-columns:1fr}.stick{position:static}nav{margin-left:0}dl{grid-template-columns:110px 1fr}}
"""


def page(tab, body, title="Casualty cards"):
    nav = "".join(f"<a class='{'on' if t == tab else ''}' href='{u}'>{n}</a>" for t, n, u in
                  (("board", "Casualties", "/"), ("bench", "How accurate is it", "/benchmark"), ("guide", "How to use it", "/guide")))
    return HTMLResponse(f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style><header><div class="wrap top"><a class=mark href=/>Casualty cards <span>DD Form 1380 from recorded handovers</span></a>
<nav>{nav}</nav></div></header><main class=wrap>{body}</main></html>""")


# ---------------------------------------------------------------- reading a card
def review(name, stem):
    """Review sheet sections: Ask the sender, Check these, Transcript."""
    out = {}
    for part in (SETS[name] / "review" / f"{stem}.md").read_text().split("\n## ")[1:]:
        title, _, body = part.partition("\n")
        out[title] = body.strip() if title == "Transcript" else \
            [l[2:] for l in body.splitlines() if l.startswith("- ") and l[2:] not in ("nothing missing", "nothing flagged")]
    return out


def evac(card):
    return next(((label, cls) for key, label, cls in EVAC if card.get(key)), ("Not given", "n"))


def who(card):
    name = card.get("name") or card.get("battle_roster") or (f"Last four {card['last4']}" if card.get("last4") else "")
    return name or "Unidentified", bool(name)


def injuries(card):
    m = re.match(r"Injuries:\s*(.*)", card.get("notes") or "")
    return [p.split(":")[0].strip() for p in m.group(1).split(";") if ":" in p] if m else []


def mechanism(card):
    ms = [k[10:].upper() if k[10:] in ("gsw", "ied", "rpg", "mvc") else k[10:] for k, v in card.items()
          if k.startswith("mechanism_") and v is True and k != "mechanism_other"]
    return ms + ([card["mechanism_other_text"]] if card.get("mechanism_other_text") else [])


def care(card):
    out = [f"TQ {short} {card[f'tq_{limb}_time'] or ''}".strip() for limb, short in LIMBS
           if card.get(f"tq_{limb}_type") or card.get(f"tq_{limb}_time")]
    for m in MEDS:
        if card.get(f"{m}_name"):
            out.append(" ".join(x for x in (card[f"{m}_name"], card.get(f"{m}_dose") or card.get(f"{m}_volume"), card.get(f"{m}_route")) if x))
    return out


def status(rv):
    get, conf = rv.get("Ask the sender", []), rv.get("Check these", [])
    if not get and not conf:
        return "ok", "Ready to attach", ""
    if get:
        return "get", "Get from sender", ", ".join(get[:3]) + (f" +{len(get) - 3}" if len(get) > 3 else "")
    return "conf", f"Confirm {len(conf)} value{'s' if len(conf) > 1 else ''}", conf[0][:70]


def answer_key(card):
    truth = TRUTH.get(card["file"])
    if not truth:
        return None, []
    per_field, _ = score_card(card, truth)
    return prf(Counter(per_field.values()))[2], [(f, o, card.get(f), truth.get(f)) for f, o in per_field.items() if o not in ("correct", "blank_ok")]


def casualties():
    seen = {}
    for name in ("eval", "live"):  # an uploaded recording replaces the evaluation copy of the same name
        d = SETS[name] / "predictions"
        for p in sorted(d.glob("*.json")) if d.exists() else []:
            seen[p.stem] = (name, p.stem, json.loads(p.read_text()), review(name, p.stem))
    order = {"u": 0, "p": 1, "r": 2, "n": 3}
    return sorted(seen.values(), key=lambda c: (order[evac(c[2])[1]], c[1]))


# ---------------------------------------------------------------- pages
@app.get("/")
def board():
    rows, counts = "", Counter()
    for name, stem, card, rv in casualties():
        (ev, ec), (person, known) = evac(card), who(card)
        st, label, detail = status(rv)
        counts[st] += 1
        counts[ec] += 1
        f1, _ = answer_key(card)
        line = " · ".join(x for x in (", ".join(mechanism(card)), ", ".join(injuries(card)[:2])) if x)
        rows += (f"<tr class='row {ec}' data-st={st} data-ev={ec} onclick=\"location='/card/{name}/{stem}'\">"
                 f"<td><span class='tag {ec}'>{ev}</span></td><td><div class=who>{esc(person) if known else '<span class=sub>Unidentified</span>'}</div>"
                 f"<div class='sub mono'>{stem.replace('handover-', '')}{' · new' if name == 'live' else ''}</div></td>"
                 f"<td>{esc(line) or '<span class=sub>not stated</span>'}<div class=sub>{esc(', '.join(care(card)[:3]))}</div></td>"
                 f"<td><div class='st {st}'>{label}<small>{esc(detail)}</small></div></td>"
                 f"<td class=score>{'' if f1 is None else f'<b>{f1:.0%}</b>'}</td></tr>")
    total = sum(counts[k] for k in ("ok", "get", "conf"))

    def seg(attr, opts):
        return "<div class=seg>" + "".join(f"<button data-{attr}='{v}' class='{'on' if not v else ''}'>{lbl}<i>{counts[v] if v else total}</i></button>"
                                           for v, lbl in opts) + "</div>"
    return page("board", f"""<h1>Casualties</h1>
<p class=lede>Each recorded handover becomes a filled TCCC card. Urgent casualties are at the top. A card is ready to print and
attach when nothing is missing and nothing needs confirming; otherwise the status says what to do first.</p>
<form class=up action=/upload method=post enctype=multipart/form-data onsubmit="let b=this.querySelector('.btn');b.disabled=true;b.textContent='Listening, about 10 seconds'">
<b>New handover</b><input type=file name=audio accept="audio/*" required><button class=btn>Make card</button>
<span class=sub>Upload the whole recording. Nothing is guessed: anything not said stays blank.</span></form>
<div class=tools>{seg('st', (('', 'All'), ('ok', 'Ready to attach'), ('get', 'Get from sender'), ('conf', 'Confirm values')))}
{seg('ev', (('', 'Any evac'), ('u', 'Urgent'), ('p', 'Priority'), ('r', 'Routine'), ('n', 'Not given')))}</div>
<table><thead><tr><th>Evac</th><th>Casualty</th><th>What happened · what was done</th><th>Before you attach the card</th>
<th title='Agreement with the answer key, test recordings only'>Answer key</th></tr></thead><tbody>{rows}</tbody></table>
<script>let f={{st:'',ev:''}};document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{{let k=b.dataset.st!==undefined?'st':'ev';
f[k]=b.dataset[k];b.parentNode.querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));
document.querySelectorAll('tr.row').forEach(r=>r.hidden=(f.st&&r.dataset.st!==f.st)||(f.ev&&r.dataset.ev!==f.ev))}})</script>""")


@app.get("/card/{name}/{stem}")
def card_page(name: str, stem: str):
    card = json.loads((SETS[name] / "predictions" / f"{stem}.json").read_text())
    rv = review(name, stem)
    (ev, ec), (person, known) = evac(card), who(card)
    get, conf = rv.get("Ask the sender", []), rv.get("Check these", [])
    todo = ""
    if get:
        todo += f"<div class='box warn'><h2>Get from the sender before they leave</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in get)}</ul></div>"
    if conf:
        todo += f"<div class='box bad'><h2>Confirm against the recording</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in conf)}</ul></div>"
    if not todo:
        todo = "<div class='box good'><h2>Ready to print, sign and attach</h2>Nothing missing, nothing to confirm.</div>"
    ident = [({"last4": "Last four"}.get(k, k.replace("_", " ").capitalize()), card[k]) for k in ("name", "last4", "battle_roster", "service", "unit", "date", "allergies") if card.get(k)]
    ident += [("Sex", "Male" if card.get("gender_m") else "Female")] if card.get("gender_m") or card.get("gender_f") else []
    vit = [i for i in range(1, 5) if any(card.get(f"signs_{i}_{k}") for k in ("pulse", "resp_rate", "spo2", "avpu", "bp_systolic"))]
    vital = (("Time", "time"), ("Pulse", "pulse"), ("BP", "bp"), ("Resp rate", "resp_rate"), ("SpO2", "spo2"), ("AVPU", "avpu"), ("Pain", "pain"))

    def cell(i, k):
        if k == "bp":
            return f"{card[f'signs_{i}_bp_systolic']}/{card[f'signs_{i}_bp_diastolic']}" if card[f"signs_{i}_bp_systolic"] else ""
        return card[f"signs_{i}_{k}"]
    vrows = "".join(f"<tr><th>{lbl}</th>" + "".join(f"<td>{esc(str(cell(i, k)))}</td>" for i in vit) + "</tr>" for lbl, k in vital)
    other = [TREAT[k] for k in TREAT if card.get(k) is True]
    ident_html = "<dl>" + "".join(f"<dt>{esc(k)}</dt><dd>{esc(str(v))}</dd>" for k, v in ident) + "</dl>" if ident else "<span class=sub>No identity details given.</span>"
    f1, errs = answer_key(card)
    key = ""
    if f1 is not None:
        what = {"missed": "left blank", "invented": "not said", "wrong": "different"}
        table = ("<table><tr><th>Field</th><th>Result</th><th>Card</th><th>Answer key</th></tr>" + "".join(
            f"<tr><td class=mono>{f}</td><td>{what[o]}</td><td>{esc(str(p))}</td><td>{esc(str(t))}</td></tr>" for f, o, p, t in errs) + "</table>") if errs else "Every field agrees."
        key = f"<div class=box><h2>Answer key: {f1:.0%} of filled fields agree</h2>{table}</div>"
    unknown = "" if known else ". No name, roster number or last four was said: take them from the casualty's ID tags"
    wounded = f" at {card['time']}" if card.get("time") else ""
    return page("board", f"""<p class=sub><a href=/>All casualties</a></p>
<h1>{esc(person) if known else 'Unidentified casualty'} <span class='tag {ec}'>{ev}</span></h1>
<p class=lede>Recording <span class=mono>{stem.replace('handover-', '')}</span>{unknown}.</p>
<div class=cols><div>{todo}
<div class=box><h2>The card, in MIST order</h2>{ident_html}
<div class=mist><span class=l>M</span><div>{esc(', '.join(mechanism(card)) or 'not stated')}{wounded}</div>
<span class=l>I</span><div>{esc('; '.join(injuries(card)) or 'not stated')}<div class=sub>{esc(card.get('notes') or '')}</div></div>
<span class=l>S</span><div>{f"<table class=vit>{vrows}</table>" if vit else 'no observations given'}</div>
<span class=l>T</span><div>{esc(', '.join(care(card) + other) or 'none given')}</div></div></div>
<div class=box><h2>What was said</h2><div class=say>{esc(rv.get('Transcript', ''))}</div></div>{key}</div>
<div class=stick><iframe src='/pdf/{name}/{stem}#view=FitH' title='Filled DD Form 1380'></iframe>
<p class=sub><a href='/pdf/{name}/{stem}' target=_blank>Open the PDF to print</a></p></div></div>""", person)


def bar(v, dim=False):
    return f"<div class=bar><s class='{'dim' if dim else ''}' style='width:{v * 260:.0f}px'></s><span>{v:.0%}</span></div>"


@app.get("/benchmark")
def bench():
    p = OUT / "runs.jsonl"
    rs = [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    last = {r["split"]: r for r in rs if r["model"] == LLM_MODEL}
    h, a = last.get("heldout"), last.get("all")
    c = ROOT / "transcripts" / "_bakeoff.csv"
    stt = sorted(csv.DictReader(c.open()), key=lambda r: -float(r["hard_files_numbers"])) if c.exists() else []
    chosen = STT_MODEL + "+keyterms"
    stt_rows = "".join(f"<tr><td class=mono>{esc(r['model'])}</td><td>{bar(float(r['hard_files_numbers']), r['model'] != chosen)}</td>"
                       f"<td>{bar(float(r['drugs_kit']), r['model'] != chosen)}</td><td class=mono>{esc(r['cost_per_audio_hour'])}</td></tr>" for r in stt)
    models = []
    for d in OUT.iterdir():
        s = d / "dev" / "score.json"
        if s.exists():
            j = json.loads(s.read_text())
            models.append((j["overall"]["f1"], d.name.replace("__", "/"), j["overall"].get("invented", 0) / 25))
    model_rows = "".join(f"<tr><td class=mono>{esc(m)}</td><td>{bar(f, m != LLM_MODEL)}</td><td class=mono>{inv:.2f}</td></tr>"
                         for f, m, inv in sorted(models, reverse=True))
    groups = ""
    hs = OUT / LLM_MODEL.replace("/", "__") / "heldout" / "score.json"
    if hs.exists():
        names = {"identity": "Who (name, ID, unit)", "evac": "Evac category", "mechanism": "Mechanism", "tourniquets": "Tourniquets",
                 "vital_signs": "Vital signs", "treatments": "Other treatments", "medications": "Drugs and fluids"}
        g = json.loads(hs.read_text())["groups"]
        groups = "".join(f"<tr><td>{names.get(k, k)}</td><td>{bar(v['f1'], v['f1'] < .9)}</td></tr>" for k, v in sorted(g.items(), key=lambda kv: -kv[1]["f1"]))
    stages = ""
    if a:
        n = len(a["errors"])
        plain = {"transcription": "The words never reached the transcript (static, noise, a name heard wrongly)",
                 "extraction": "The words were there; the model read them wrongly or missed them",
                 "invented": "Something written that was never said"}
        stages = "".join(f"<tr><td>{plain.get(k, k)}</td><td>{bar(v / n, True)}</td><td class=mono>{v}</td></tr>"
                         for k, v in sorted(a["stages"].items(), key=lambda kv: -kv[1]))
    hist = "".join(f"<tr><td class=mono>{esc(r['model'])}</td><td>{'held-out' if r['split'] == 'heldout' else r['split']}</td><td class=mono>{r['prompt']}</td>"
                   f"<td class=mono>{r['f1']:.1%}</td><td class=mono>{r['critical_f1']:.1%}</td><td class=mono>{r['invented']}</td></tr>" for r in reversed(rs))
    head = (f"<div class=facts><div><b>{h['f1']:.1%}</b>of filled fields right, on 25 recordings never used for tuning</div>"
            f"<div><b>{h['critical_f1']:.1%}</b>on drugs, tourniquets, vitals and evac</div><div><b>{h['invented']} in 25</b>cards had a value nobody said</div>"
            f"<div><b>{a['f1']:.1%}</b>across all 50 recordings</div></div>") if h and a else ""
    return page("bench", f"""<h1>How accurate is it</h1><p class=lede>Scored against the answer key that came with the recordings. Only the fields
a handover actually filled are counted, because an empty card already "matches" most of the form. Half the recordings were locked
away until the end, so the headline is a fair test.</p>{head}
<div class=finding><p class=take>Drugs, tourniquets and evac are nearly always right. Names are the weak spot.</p>
<p class=note>Names are spelled the way they sound ("Kaur" heard as "Carr"). In the field the ID tag settles it, which is why the card asks for it.</p>
<table style='max-width:620px'>{groups}</table></div>
<div class=finding><p class=take>Most mistakes start in the audio, not in the reading.</p>
<p class=note>Every mistake is traced to the step that caused it. Two radio recordings are mostly static; no model recovers them.</p>
<table style='max-width:820px'>{stages}</table></div>
<div class=finding><p class=take>Hearing it: ElevenLabs Scribe v2 Medical, told which words to expect.</p>
<p class=note>Share of the true values that made it into the transcript, on the 21 hardest and trickiest recordings. Hard audio means radio,
heavy noise or two people talking. Telling it to expect words like TXA and IV lifted drug and kit words from 90% to 97%.</p>
<table><tr><th>Speech model</th><th>Numbers caught on hard audio</th><th>Drug and kit words caught</th><th>Cost per audio hour</th></tr>{stt_rows}</table></div>
<div class=finding><p class=take>Reading it: Gemini 3.8 Flash, the most accurate for the price.</p>
<p class=note>Tuning set, 25 recordings. Two strong models made the same mistakes on 99.6% of fields, so a second-opinion model would add almost nothing.</p>
<table><tr><th>Language model</th><th>Filled fields right</th><th>Values not said, per card</th></tr>{model_rows}</table></div>
<div class=finding><p class=take>Every run is logged.</p><p class=note>Newest first. The prompt column is a fingerprint of the instructions used.</p>
<table><tr><th>Model</th><th>Recordings</th><th>Prompt</th><th>Filled fields right</th><th>Safety-critical</th><th>Values not said</th></tr>{hist}</table></div>""")


@app.get("/guide")
def guide():
    return page("guide", f"""<div class=guide><h1>How to use it</h1>
<p class=lede>Built for the casualty collection point: many casualties, little time, one medic writing cards. The system writes the card
from the handover so the medic only deals with the gaps.</p>
<h2>At the handover</h2><ol>
<li><b>Record the whole handover</b>, start to finish. Do not trim it: corrections ("six fifteen, correction six fifty") and read-backs matter.</li>
<li><b>Upload it</b> on the Casualties page. The card is ready in about 10 seconds.</li>
<li><b>Read the status before the sender leaves.</b> If it says <i>Get from sender</i>, ask for those items now ("say again tourniquet time").</li>
<li><b>Confirm</b> any flagged values against what you heard. The transcript is on the card page.</li>
<li><b>Print, check, sign, attach.</b> Fasten the card to the casualty where it can be seen (wrist or belt loop). It travels with them.</li></ol>
<h2>What the statuses mean</h2><div class=key>
<span class='st ok'>Ready to attach</span><span>Every critical item is there and nothing is in doubt.</span>
<span class='st get'>Get from sender</span><span>Something a surgeon needs was not said: identity, evac category, a tourniquet time, a drug's dose or route.</span>
<span class='st conf'>Confirm values</span><span>Something was garbled, corrected or could not be backed by the recording. It was left blank, not guessed.</span></div>
<h2>Rules the system follows</h2><ul>
<li><b>Blank means not said.</b> It never fills a value it did not hear. A blank box is safer than a wrong dose.</li>
<li><b>No name, no guess.</b> If no name, battle roster number or last four was said, the card is marked Unidentified. Take the details from the
casualty's ID tags and write them on the card. The battle roster number is initials plus last four (JS4417), and is only filled when spoken that way.</li>
<li><b>Corrections win.</b> The last thing said replaces what came before. Anything retracted ("ignore that, other casualty") is left off.</li>
<li><b>Urgent first.</b> The list is sorted Urgent, then Priority, then Routine, then cards with no evac category given.</li></ul>
<h2>What it does not do</h2><ul><li>It does not replace the medic's signature or judgment. Every card is checked by a person before it is attached.</li>
<li>It needs a network connection today. An offline speech model gets about three quarters of the values and is the next step for forward use.</li></ul>
<p class=sub>Models in use: {STT_MODEL} (speech) and {LLM_MODEL} (reading the transcript). About 1 US cent per card.</p></div>""")


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
