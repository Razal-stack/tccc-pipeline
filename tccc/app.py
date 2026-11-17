"""TCCC Casualty Cards: web app over the pipeline, built around how cards are used at a casualty collection point.

    python3 -m uvicorn tccc.app:app --port 8000      # then open http://localhost:8000

Casualties: everyone, most urgent first, with what each card still needs. Card: the card in MIST order beside the
PDF. Accuracy: what was measured and what it means. Guide: how a medic uses it. Read live from the results on disk.
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
STATUS = {"ok": ("Complete", "Everything important was said. Print, sign and attach."),
          "get": ("Missing information", "Something important was not said. Ask the person who handed over."),
          "conf": ("Needs checking", "A value was unclear or contradicted itself. Compare it with the recording.")}
app = FastAPI(title="TCCC Casualty Cards")
esc = html.escape

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--navy:#0b1a45;--navy2:#13265e;--royal:#2547d0;--royal2:#1b37a8;--tint:#eef2fd;--bg:#f6f8fc;--ink:#0f1b33;--soft:#5b6782;
--line:#e3e8f2;--hair:#eef1f7;--u:#c4320a;--ud:#e5484d;--ub:#fdeceb;--p:#a15c00;--pd:#f5a524;--pb:#fff5e1;--r:#18794e;--rd:#30a46c;--rb:#e6f6ee;
--n:#5b6782;--nd:#a3adc2;--nb:#f0f2f7;--mono:'JetBrains Mono',ui-monospace,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 Inter,system-ui,sans-serif;font-feature-settings:"tnum","cv11";-webkit-font-smoothing:antialiased}
a{color:var(--royal);text-decoration:none}a:hover{text-decoration:underline}
.app{display:grid;grid-template-columns:236px minmax(0,1fr);min-height:100vh}
aside{background:var(--navy);color:#c9d3ef;padding:20px 14px;position:sticky;top:0;height:100vh;display:flex;flex-direction:column}
.brand{display:flex;gap:10px;align-items:center;color:#fff;font-weight:700;font-size:15px;padding:0 8px 22px;text-decoration:none}
.brand i{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#4f74ff,var(--royal));display:grid;place-items:center;font:700 12px var(--mono);font-style:normal}
.brand small{display:block;font-weight:400;font-size:11px;color:#8d9bc7}
aside a.nav{display:block;color:#c9d3ef;padding:9px 12px;border-radius:8px;font-weight:500;margin-bottom:2px;text-decoration:none}
aside a.nav:hover{background:var(--navy2);color:#fff}aside a.nav.on{background:var(--royal);color:#fff}
aside .foot{margin-top:auto;font-size:12px;color:#8d9bc7;padding:12px 8px 0;border-top:1px solid #23346b;line-height:1.6}
main{padding:28px 36px 60px;max-width:1240px}.head{display:flex;align-items:flex-start;gap:16px;margin-bottom:20px;flex-wrap:wrap}
.head .grow{flex:1;min-width:280px}h1{font-size:24px;font-weight:700;letter-spacing:-.02em;margin:0 0 4px}h2{font-size:15px;font-weight:600;margin:0 0 10px}
.lede{color:var(--soft);max-width:760px;margin:0}.sub{color:var(--soft);font-size:13px}.mono{font-family:var(--mono);font-size:12.5px}
.btn{background:var(--royal);color:#fff;border:0;border-radius:8px;padding:9px 16px;font:600 14px Inter,sans-serif;cursor:pointer;box-shadow:0 1px 2px rgba(15,27,51,.15)}
.btn:hover{background:var(--royal2)}.btn:disabled{background:#8fa2e6;cursor:wait}.btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line)}
.panel{background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 1px 2px rgba(15,27,51,.04)}
.drop{display:none;gap:16px;align-items:center;flex-wrap:wrap;padding:18px 20px;margin-bottom:20px;border:1.5px dashed #a9b8ee;background:#fbfcff}
.drop.show{display:flex}.drop.over{background:var(--tint);border-color:var(--royal)}.drop label{flex:1;min-width:260px;cursor:pointer}
.drop label b{display:block;font-size:15px}.drop input{display:none}.file{font:12.5px var(--mono);color:var(--royal);margin-top:4px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-bottom:16px}
.tile{all:unset;box-sizing:border-box;cursor:pointer;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:block;transition:box-shadow .15s}
.tile:hover{box-shadow:0 2px 10px rgba(15,27,51,.08)}.tile.on{border-color:var(--royal);box-shadow:0 0 0 3px #d7e0fb}
.tile .t{display:flex;align-items:center;gap:8px;font-weight:600;font-size:13px}.tile b{display:block;font-size:28px;font-weight:700;letter-spacing:-.02em;margin:4px 0 2px}
.tile span{font-size:12.5px;color:var(--soft);line-height:1.45;display:block}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}.dot.all{background:var(--royal)}.dot.ok,.dot.r{background:var(--rd)}.dot.get,.dot.p{background:var(--pd)}.dot.conf,.dot.u{background:var(--ud)}.dot.n{background:var(--nd)}
.bar2{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px 14px;border-bottom:1px solid var(--line)}
.search{flex:1;min-width:220px;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font:14px Inter,sans-serif;outline:none}.search:focus{border-color:var(--royal);box-shadow:0 0 0 3px #d7e0fb}
.lbl{font-size:12.5px;font-weight:600;color:var(--soft);margin-left:6px}
.chip{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:500;padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink)}
.chip:hover{background:var(--hair)}.chip.on{background:var(--tint);border-color:var(--royal);color:var(--royal2)}.chip i{font-style:normal;color:var(--soft);font-size:12px}
table{width:100%;border-collapse:collapse}th{text-align:left;font-weight:500;font-size:12px;color:var(--soft);padding:10px 14px;border-bottom:1px solid var(--line);background:#fafbfe;position:sticky;top:0}
td{padding:13px 14px;border-bottom:1px solid var(--hair);vertical-align:top}tr:last-child td{border-bottom:0}
tr.row{cursor:pointer}tr.row:hover td{background:#f7f9ff}td.go{color:#b5bfd6;text-align:right;font-size:16px;vertical-align:middle}tr.row:hover td.go{color:var(--royal)}
.who{font-weight:600}.badge{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;padding:3px 10px;border-radius:999px;white-space:nowrap}
.badge.u,.badge.conf{background:var(--ub);color:var(--u)}.badge.p,.badge.get{background:var(--pb);color:var(--p)}.badge.r,.badge.ok{background:var(--rb);color:var(--r)}.badge.n{background:var(--nb);color:var(--n)}
.why{display:block;font-size:12.5px;color:var(--soft);margin-top:5px;max-width:360px}
.meter{display:flex;align-items:center;gap:8px}.meter s{display:block;width:64px;height:6px;border-radius:3px;background:var(--hair);overflow:hidden;text-decoration:none}
.meter s i{display:block;height:100%;background:var(--royal)}.meter span{font:12.5px var(--mono);color:var(--soft)}
.empty{padding:30px;text-align:center;color:var(--soft);display:none}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:start}.stick{position:sticky;top:20px}
.box{padding:16px 18px;margin-bottom:14px}.box.warn{border-left:4px solid var(--pd)}.box.bad{border-left:4px solid var(--ud)}.box.good{border-left:4px solid var(--rd)}
.box ul{margin:6px 0 0;padding-left:18px}.box li{margin:3px 0}.mist{display:grid;grid-template-columns:30px 1fr;gap:12px 12px;margin:14px 0 0}
.mist .l{font:600 14px var(--mono);color:#fff;background:var(--navy);border-radius:7px;text-align:center;height:28px;line-height:28px}
dl{display:grid;grid-template-columns:120px 1fr;gap:4px 12px;margin:0}dt{color:var(--soft);font-size:13px}dd{margin:0;font-weight:500}
.vit{width:auto;margin-top:2px}.vit td,.vit th{border:0;border-bottom:1px solid var(--hair);padding:4px 18px 4px 0;background:none;position:static;font-size:13px;font-weight:400}
.vit th{color:var(--soft)}.say{font:12.5px/1.8 var(--mono);color:#33405c;white-space:pre-wrap}
iframe{width:100%;height:86vh;border:1px solid var(--line);border-radius:12px;background:#fff}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:20px 0 24px}.facts div{padding:16px 18px;font-size:13px;color:var(--soft)}
.facts b{display:block;font-size:28px;font-weight:700;color:var(--ink);letter-spacing:-.02em}.facts .hero{background:var(--navy);border-color:var(--navy);color:#b8c4ea}.facts .hero b{color:#fff}
.hbar{display:flex;align-items:center;gap:10px}.hbar s{display:block;height:8px;border-radius:4px;background:var(--royal);text-decoration:none}.hbar s.dim{background:#c6cee0}.hbar span{font:12.5px var(--mono);color:var(--soft)}
.finding{padding:18px 20px;margin-bottom:16px}.finding p.take{font-size:16px;font-weight:600;margin:0 0 4px}.finding p.note{color:var(--soft);margin:0 0 12px;max-width:820px}
.finding table td,.finding table th{padding:9px 10px}.guide{max-width:820px}.guide .panel{padding:18px 22px;margin-bottom:14px}.guide ol,.guide ul{padding-left:20px;margin:0}.guide li{margin:7px 0}
.key{display:grid;grid-template-columns:190px 1fr;gap:12px 16px;align-items:start}
@media(max-width:960px){.app{grid-template-columns:1fr}aside{position:static;height:auto}.cols{grid-template-columns:1fr}.stick{position:static}main{padding:20px}}
"""


def page(tab, body, title="TCCC Casualty Cards"):
    nav = "".join(f"<a class='nav{' on' if t == tab else ''}' href='{u}'>{n}</a>" for t, n, u in
                  (("board", "Casualties", "/"), ("bench", "Accuracy", "/benchmark"), ("guide", "How to use it", "/guide")))
    return HTMLResponse(f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style><div class=app><aside><a class=brand href=/><i>TC</i><div>TCCC Casualty Cards<small>DD Form 1380 from handovers</small></div></a>
{nav}<div class=foot>Listening: ElevenLabs Scribe v2 Medical<br>Reading: Gemini 3.8 Flash<br>About 10 s and 1 US cent per card</div></aside>
<main>{body}</main></div></html>""")


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
    return next(((label, cls) for key, label, cls in EVAC if card.get(key)), ("Not stated", "n"))


def who(card):
    name = card.get("name") or card.get("battle_roster") or (f"Last four {card['last4']}" if card.get("last4") else "")
    return name or "Name not given", bool(name)


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
    """(key, what exactly): missing information first, because the person who handed over may leave."""
    get, conf = rv.get("Ask the sender", []), rv.get("Check these", [])
    if get:
        return "get", "Ask for: " + ", ".join(get[:3]) + (f", and {len(get) - 3} more" if len(get) > 3 else "")
    if conf:
        return "conf", "Check: " + conf[0][:90] + (f" (and {len(conf) - 1} more)" if len(conf) > 1 else "")
    return "ok", "Print, sign and attach."


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
        st, why = status(rv)
        counts[st] += 1
        counts[ec] += 1
        f1, _ = answer_key(card)
        line = " · ".join(x for x in (", ".join(mechanism(card)), ", ".join(injuries(card)[:2])) if x)
        rid = stem.replace("handover-", "")
        find = " ".join((person, rid, line, " ".join(care(card)))).lower()
        rows += (f"<tr class=row data-st={st} data-ev={ec} data-q='{esc(find)}' onclick=\"location='/card/{name}/{stem}'\">"
                 f"<td><span class='badge {ec}'><span class='dot {ec}'></span>{ev}</span></td>"
                 f"<td><div class=who>{esc(person) if known else '<span class=sub>Name not given</span>'}</div>"
                 f"<div class='sub mono'>{rid}{' · just added' if name == 'live' else ''}</div></td>"
                 f"<td>{esc(line) or '<span class=sub>not stated</span>'}<div class=sub>{esc(', '.join(care(card)[:3]))}</div></td>"
                 f"<td><span class='badge {st}'>{STATUS[st][0]}</span><span class=why>{esc(why)}</span></td>"
                 f"<td>{'' if f1 is None else f'<div class=meter><s><i style=width:{f1:.0%}></i></s><span>{f1:.0%}</span></div>'}</td><td class=go>›</td></tr>")
    n = sum(counts[k] for k in STATUS)
    tiles = (f"<button class='tile on' data-st=''><div class=t><span class='dot all'></span>All casualties</div><b>{n}</b>"
             f"<span>Every handover recorded so far.</span></button>" + "".join(
                 f"<button class=tile data-st={k}><div class=t><span class='dot {k}'></span>{t}</div><b>{counts[k]}</b><span>{d}</span></button>"
                 for k, (t, d) in STATUS.items()))
    chips = "<button class='chip on' data-ev=''>All</button>" + "".join(
        f"<button class=chip data-ev={c}><span class='dot {c}'></span>{lbl}<i>{counts[c]}</i></button>"
        for c, lbl in (("u", "Urgent"), ("p", "Priority"), ("r", "Routine"), ("n", "Not stated")))
    return page("board", f"""<div class=head><div class=grow><h1>Casualties</h1>
<p class=lede>Each recorded handover becomes a filled TCCC card. Most urgent at the top. Open a casualty to see the card and what it still needs.</p></div>
<button class=btn onclick="document.querySelector('.drop').classList.toggle('show')">+ New handover</button></div>
<form class='panel drop' action=/upload method=post enctype=multipart/form-data>
<label><b>Drop a handover recording here, or click to choose one</b><span class=sub>Upload the whole recording (.wav, .mp3, .m4a).
The card is ready in about 10 seconds. Nothing is guessed: anything not said stays blank.</span><div class=file></div>
<input type=file name=audio accept="audio/*" required></label><button class=btn>Create card</button></form>
<div class=tiles>{tiles}</div>
<div class=panel><div class=bar2><input class=search placeholder="Search name, roster number, recording, injury or treatment">
<span class=lbl>Evacuation priority</span>{chips}</div>
<table><thead><tr><th>Evacuation</th><th>Casualty</th><th>What happened · what was done</th><th>Card status</th>
<th title="Testing only: how closely the card agrees with the official answer for that recording">Matches answer key</th><th></th></tr></thead>
<tbody>{rows}</tbody></table><div class=empty>No casualties match these filters.</div></div>
<script>
let f={{st:'',ev:'',q:''}},rows=[...document.querySelectorAll('tr.row')];
function apply(){{let shown=0;rows.forEach(r=>{{r.hidden=(f.st&&r.dataset.st!==f.st)||(f.ev&&r.dataset.ev!==f.ev)||(f.q&&!r.dataset.q.includes(f.q));shown+=!r.hidden}});
document.querySelector('.empty').style.display=shown?'none':'block'}}
function pick(sel,key){{document.querySelectorAll(sel).forEach(b=>b.onclick=()=>{{f[key]=b.dataset[key];document.querySelectorAll(sel).forEach(x=>x.classList.toggle('on',x===b));apply()}})}}
pick('.tile','st');pick('.chip','ev');document.querySelector('.search').oninput=e=>{{f.q=e.target.value.toLowerCase().trim();apply()}};
let d=document.querySelector('.drop'),inp=d.querySelector('input'),show=()=>d.querySelector('.file').textContent=inp.files[0]?'Selected: '+inp.files[0].name:'';
inp.onchange=show;d.ondragover=e=>{{e.preventDefault();d.classList.add('over')}};d.ondragleave=()=>d.classList.remove('over');
d.ondrop=e=>{{e.preventDefault();d.classList.remove('over');inp.files=e.dataTransfer.files;show()}};
d.onsubmit=()=>{{let b=d.querySelector('.btn');b.disabled=true;b.textContent='Listening, about 10 seconds'}};
</script>""")


@app.get("/card/{name}/{stem}")
def card_page(name: str, stem: str):
    card = json.loads((SETS[name] / "predictions" / f"{stem}.json").read_text())
    rv = review(name, stem)
    (ev, ec), (person, known) = evac(card), who(card)
    st, _ = status(rv)
    get, conf = rv.get("Ask the sender", []), rv.get("Check these", [])
    todo = ""
    if get:
        todo += f"<div class='panel box warn'><h2>Missing information: ask the person who handed over</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in get)}</ul></div>"
    if conf:
        todo += f"<div class='panel box bad'><h2>Needs checking: compare with the recording</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in conf)}</ul></div>"
    if not todo:
        todo = "<div class='panel box good'><h2>Complete</h2>Everything important was said. Print, sign and attach.</div>"
    ident = [({"last4": "Last four"}.get(k, k.replace("_", " ").capitalize()), card[k])
             for k in ("name", "last4", "battle_roster", "service", "unit", "date", "allergies") if card.get(k)]
    ident += [("Sex", "Male" if card.get("gender_m") else "Female")] if card.get("gender_m") or card.get("gender_f") else []
    vit = [i for i in range(1, 5) if any(card.get(f"signs_{i}_{k}") for k in ("pulse", "resp_rate", "spo2", "avpu", "bp_systolic"))]

    def cell(i, k):
        if k == "bp":
            return f"{card[f'signs_{i}_bp_systolic']}/{card[f'signs_{i}_bp_diastolic']}" if card[f"signs_{i}_bp_systolic"] else ""
        return card[f"signs_{i}_{k}"]
    vrows = "".join(f"<tr><th>{lbl}</th>" + "".join(f"<td>{esc(str(cell(i, k)))}</td>" for i in vit) + "</tr>" for lbl, k in
                    (("Time", "time"), ("Pulse", "pulse"), ("BP", "bp"), ("Resp rate", "resp_rate"), ("SpO2", "spo2"), ("AVPU", "avpu"), ("Pain", "pain"))
                    if any(cell(i, k) for i in vit))  # only rows the handover gave
    other = [TREAT[k] for k in TREAT if card.get(k) is True]
    ident_html = ("<dl>" + "".join(f"<dt>{esc(k)}</dt><dd>{esc(str(v))}</dd>" for k, v in ident) + "</dl>") if ident else "<span class=sub>No identity details given.</span>"
    f1, errs = answer_key(card)
    key = ""
    if f1 is not None:
        what = {"missed": "left blank", "invented": "not said", "wrong": "different"}
        table = ("<table><tr><th>Field</th><th>Result</th><th>Card</th><th>Answer key</th></tr>" + "".join(
            f"<tr><td class=mono>{f}</td><td>{what[o]}</td><td>{esc(str(p))}</td><td>{esc(str(t))}</td></tr>" for f, o, p, t in errs) + "</table>") if errs else "Every field agrees."
        key = f"<div class='panel box'><h2>Answer key: {f1:.0%} of filled fields agree</h2><span class=sub>Testing only.</span>{table}</div>"
    unknown = "" if known else " No name, roster number or last four was said: take them from the casualty's ID tags."
    wounded = f" at {card['time']}" if card.get("time") else ""
    return page("board", f"""<p class=sub><a href=/>Casualties</a> / {stem.replace('handover-', '')}</p>
<div class=head><div class=grow><h1>{esc(person) if known else 'Name not given'}</h1>
<p class=lede><span class='badge {ec}'><span class='dot {ec}'></span>{ev}</span> <span class='badge {st}'>{STATUS[st][0]}</span>{unknown}</p></div>
<a class='btn ghost' href='/pdf/{name}/{stem}' target=_blank>Open PDF to print</a></div>
<div class=cols><div>{todo}
<div class='panel box'><h2>The card, in MIST order</h2>{ident_html}
<div class=mist><span class=l>M</span><div>{esc(', '.join(mechanism(card)) or 'not stated')}{wounded}</div>
<span class=l>I</span><div>{esc('; '.join(injuries(card)) or 'not stated')}<div class=sub>{esc(card.get('notes') or '')}</div></div>
<span class=l>S</span><div>{f"<table class=vit>{vrows}</table>" if vit else 'no observations given'}</div>
<span class=l>T</span><div>{esc(', '.join(care(card) + other) or 'none given')}</div></div></div>
<div class='panel box'><h2>What was said</h2><div class=say>{esc(rv.get('Transcript', ''))}</div></div>{key}</div>
<div class=stick><iframe src='/pdf/{name}/{stem}#view=FitH' title='Filled DD Form 1380'></iframe></div></div>""", person)


def bar(v, dim=False):
    return f"<div class=hbar><s class='{'dim' if dim else ''}' style='width:{v * 240:.0f}px'></s><span>{v:.0%}</span></div>"


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
        names = {"identity": "Who (name, ID, unit)", "evac": "Evacuation priority", "mechanism": "Mechanism", "tourniquets": "Tourniquets",
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
    head = (f"<div class=facts><div class='panel hero'><b>{h['f1']:.1%}</b>of filled fields right, on 25 recordings never used for tuning</div>"
            f"<div class=panel><b>{h['critical_f1']:.1%}</b>on drugs, tourniquets, vital signs and evacuation</div>"
            f"<div class=panel><b>{h['invented']} in 25</b>cards had a value nobody said</div>"
            f"<div class=panel><b>{a['f1']:.1%}</b>across all 50 recordings</div></div>") if h and a else ""
    return page("bench", f"""<div class=head><div class=grow><h1>Accuracy</h1><p class=lede>Scored against the answer key that came with the recordings. Only the
fields a handover actually filled are counted, because an empty card already "matches" most of the form. Half the recordings were
locked away until the end, so the headline is a fair test.</p></div></div>{head}
<div class='panel finding'><p class=take>Drugs, tourniquets and evacuation are nearly always right. Names are the weak spot.</p>
<p class=note>Names are spelled the way they sound ("Kaur" heard as "Carr"). In the field the ID tag settles it, which is why the card asks for it.</p>
<table style='max-width:620px'>{groups}</table></div>
<div class='panel finding'><p class=take>Most mistakes start in the audio, not in the reading.</p>
<p class=note>Every mistake is traced to the step that caused it. Two radio recordings are mostly static; no model recovers them.</p>
<table style='max-width:860px'>{stages}</table></div>
<div class='panel finding'><p class=take>Listening: ElevenLabs Scribe v2 Medical, told which words to expect.</p>
<p class=note>Share of the true values that made it into the transcript, on the 21 hardest and trickiest recordings. Hard audio means radio,
heavy noise or two people talking. Telling it to expect words like TXA and IV lifted drug and kit words from 90% to 97%.</p>
<table><tr><th>Speech model</th><th>Numbers caught on hard audio</th><th>Drug and kit words caught</th><th>Cost per audio hour</th></tr>{stt_rows}</table></div>
<div class='panel finding'><p class=take>Reading: Gemini 3.8 Flash, the most accurate for the price.</p>
<p class=note>Tuning set, 25 recordings. Two strong models made the same mistakes on 99.6% of fields, so a second-opinion model would add almost nothing.</p>
<table><tr><th>Language model</th><th>Filled fields right</th><th>Values not said, per card</th></tr>{model_rows}</table></div>
<div class='panel finding'><p class=take>Every run is logged.</p><p class=note>Newest first. The prompt column is a fingerprint of the instructions used.</p>
<table><tr><th>Model</th><th>Recordings</th><th>Prompt</th><th>Filled fields right</th><th>Safety-critical</th><th>Values not said</th></tr>{hist}</table></div>""")


@app.get("/guide")
def guide():
    return page("guide", f"""<div class=guide><div class=head><div class=grow><h1>How to use it</h1>
<p class=lede>Built for the casualty collection point: many casualties, little time, one medic writing cards. The system writes the card
from the handover, so the medic only deals with the gaps.</p></div></div>
<div class=panel><h2>At the handover</h2><ol>
<li><b>Record the whole handover</b>, start to finish. Do not trim it: corrections ("six fifteen, correction six fifty") and read-backs matter.</li>
<li><b>Upload it</b> with <i>New handover</i> on the Casualties page. The card is ready in about 10 seconds.</li>
<li><b>Read the card status before the person handing over leaves.</b> If it says <i>Missing information</i>, ask for those items now ("say again tourniquet time").</li>
<li>If it says <i>Needs checking</i>, compare the value with what you heard. The transcript is on the card page.</li>
<li><b>Print, check, sign, attach.</b> Fasten the card to the casualty where it can be seen (wrist or belt loop). It travels with them.</li></ol></div>
<div class=panel><h2>What the labels mean</h2><div class=key>
<span class='badge ok'>Complete</span><span>Everything a surgeon needs was said and nothing is in doubt. Print, sign and attach.</span>
<span class='badge get'>Missing information</span><span>Something important was not said: who the casualty is, evacuation priority, a tourniquet time, a drug's dose or route. Ask the person who handed over.</span>
<span class='badge conf'>Needs checking</span><span>Something was garbled, corrected or contradicted itself. It was left blank, not guessed. Compare with the recording.</span>
<span class='badge u'><span class='dot u'></span>Urgent</span><span>Evacuation priority said in the handover (also Cat A or T1). Shown first.</span>
<span class='badge n'><span class='dot n'></span>Not stated</span><span>No evacuation priority was given in the handover. Ask for it.</span>
<span class=sub>Matches answer key</span><span>Testing only: how closely a card agrees with the official answer for that recording.</span></div></div>
<div class=panel><h2>Rules the system follows</h2><ul>
<li><b>Blank means not said.</b> It never fills a value it did not hear. A blank box is safer than a wrong dose.</li>
<li><b>No name, no guess.</b> If no name, battle roster number or last four was said, the card shows "Name not given". Take the details from the
casualty's ID tags and write them on the card. The battle roster number is initials plus last four (JS4417), and is only filled when spoken that way.</li>
<li><b>Corrections win.</b> The last thing said replaces what came before. Anything retracted ("ignore that, other casualty") is left off.</li>
<li><b>Most urgent first.</b> The list is sorted Urgent, then Priority, then Routine, then cards where no priority was stated.</li></ul></div>
<div class=panel><h2>What it does not do</h2><ul><li>It does not replace the medic's signature or judgment. Every card is checked by a person before it is attached.</li>
<li>It needs a network connection today. An offline speech model gets about three quarters of the values and is the next step for forward use.</li></ul>
<p class=sub style='margin-top:10px'>Models in use: {STT_MODEL} (listening) and {LLM_MODEL} (reading the transcript).</p></div></div>""")


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
