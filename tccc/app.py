"""TCCC Casualty Cards: web app over the pipeline, built around how cards are used at a casualty collection point.

    python3 -m uvicorn tccc.app:app --port 8000      # then open http://localhost:8000

Casualties: everyone, most urgent first, with what each card still needs. Card: the card in MIST order beside the
PDF. Benchmark: what was measured and what it means. Guide: how a medic uses it. Read live from the results on disk.
"""
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from .pipeline import LLM_MODEL, SECOND_MODEL, STT_MODEL, process
from .score import TRUTH, prf, score_card

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SETS = {"eval": OUT / LLM_MODEL.replace("/", "__") / "all", "live": OUT / "live"}
LOGO = (Path(__file__).parent / "static" / "logo.svg").read_text()
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
          "get": ("Missing information", "Something important was not said. Ask the person who handed over, before they leave."),
          "conf": ("Needs checking", "A value was unclear, corrected or heard differently by the two listens. Check it against the recording.")}
app = FastAPI(title="TCCC Casualty Cards")
esc = html.escape

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap');
:root{--bg:#faf9f7;--panel:#fff;--ink:#181818;--ink2:#414141;--soft:#706e6b;--mute:#a19f9b;--line:#e7e6e4;--hair:#f1f0ee;
--navy:#041018;--blue:#0065b4;--sky:#079eda;--tint:#eef5fb;
--u:#c4321e;--ub:#fbedea;--p:#a5640a;--pb:#fcf3e4;--r:#2f7d4f;--rb:#eaf5ee;--n:#868685;--nb:#f1f0ee;
--serif:Newsreader,Georgia,serif;--sans:Geist,system-ui,-apple-system,sans-serif;--mono:'Geist Mono',ui-monospace,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--sans);-webkit-font-smoothing:antialiased;font-feature-settings:"tnum"}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.app{display:grid;grid-template-columns:232px minmax(0,1fr);min-height:100vh}
aside{border-right:1px solid var(--line);padding:22px 14px;position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:2px}
.logo{display:block;padding:0 10px 4px}.logo svg{height:30px;width:auto;display:block}
.prod{font-size:12px;color:var(--soft);padding:0 10px 22px}
aside a.nav{color:var(--ink2);padding:7px 10px;border-radius:8px;text-decoration:none;font-weight:450}
aside a.nav:hover{background:var(--hair)}aside a.nav.on{background:#fff;color:var(--ink);font-weight:500;box-shadow:0 0 0 1px var(--line)}
aside .foot{margin-top:auto;font-size:12px;color:var(--soft);padding:14px 10px 0;border-top:1px solid var(--line);line-height:1.7}
aside .foot b{font-weight:500;color:var(--ink2)}
main{padding:36px 48px 72px;min-width:0;width:100%;max-width:1400px;margin:0 auto}
.head{display:flex;align-items:flex-end;gap:16px;margin-bottom:28px;flex-wrap:wrap}.head .grow{flex:1;min-width:300px}
h1{font:400 34px/1.15 var(--serif);letter-spacing:-.01em;margin:0 0 8px}h2{font:400 22px/1.25 var(--serif);margin:0 0 6px}
h3{font-size:14px;font-weight:600;margin:0 0 10px}.lede{color:var(--soft);font-size:15px;max-width:720px;margin:0}
.sub{color:var(--soft);font-size:12.5px}.mono{font-family:var(--mono);font-size:12.5px}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--navy);color:#fff;border:0;border-radius:999px;padding:9px 18px;font:500 14px var(--sans);cursor:pointer;text-decoration:none}
.btn:hover{background:#1b2a36;text-decoration:none}.btn:disabled{background:#6b7680;cursor:wait}
.btn.ghost{background:#fff;color:var(--ink);box-shadow:inset 0 0 0 1px var(--line)}.btn.ghost:hover{background:var(--hair)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px}
.stats{display:flex;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-bottom:28px}
.stats div{flex:1;min-width:170px;padding:16px 20px 16px 0;margin-right:20px;border-right:1px solid var(--line)}.stats div:last-child{border-right:0}
.stats span{font-size:12.5px;color:var(--soft);display:block}.stats b{display:block;font:500 26px/1.3 var(--sans);letter-spacing:-.02em;margin-top:2px}
.stats b small{font-size:13px;color:var(--soft);font-weight:400;letter-spacing:0;margin-left:4px}
.drop{display:none;gap:16px;align-items:center;flex-wrap:wrap;padding:18px 20px;margin-bottom:24px;border:1px dashed #cfcdc9;background:#fff;border-radius:12px}
.drop.show{display:flex}.drop.over{background:var(--tint);border-color:var(--blue)}.drop label{flex:1;min-width:260px;cursor:pointer}
.drop label b{display:block;font-weight:500}.drop input{display:none}.file{font:12.5px var(--mono);color:var(--blue);margin-top:4px}
.tabs{display:flex;gap:26px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.tab{all:unset;cursor:pointer;padding:10px 0;margin-bottom:-1px;border-bottom:2px solid transparent;color:var(--soft);font-weight:500;display:flex;gap:7px;align-items:center}
.tab i{font-style:normal;font:500 12px var(--mono);background:var(--hair);color:var(--ink2);border-radius:999px;padding:1px 8px}
.tab:hover{color:var(--ink)}.tab.on{color:var(--ink);border-color:var(--navy)}.tab.on i{background:var(--navy);color:#fff}
.hint{color:var(--soft);font-size:13px;margin:12px 0 14px;min-height:20px}
.bar2{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px 14px;border-bottom:1px solid var(--line)}
.search{flex:1;min-width:220px;border:1px solid var(--line);border-radius:8px;padding:8px 12px;font:14px var(--sans);outline:none;background:#fff}
.search:focus{border-color:var(--blue);box-shadow:0 0 0 3px var(--tint)}.lbl{font-size:12.5px;color:var(--soft);margin-left:4px}
.chip{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-size:13px;padding:5px 11px;border-radius:999px;box-shadow:inset 0 0 0 1px var(--line);background:#fff;color:var(--ink2)}
.chip:hover{background:var(--hair)}.chip.on{box-shadow:inset 0 0 0 1px var(--navy);color:var(--ink);font-weight:500}.chip i{font-style:normal;color:var(--mute);font-size:12px}
table{width:100%;border-collapse:collapse}th{text-align:left;font-weight:500;font-size:12px;color:var(--soft);padding:10px 14px;border-bottom:1px solid var(--line)}
td{padding:14px;border-bottom:1px solid var(--hair);vertical-align:top}tr:last-child td{border-bottom:0}
tr.row{cursor:pointer}tr.row:hover td{background:#fcfbfa}td.go{color:var(--mute);text-align:right;vertical-align:middle;width:24px}tr.row:hover td.go{color:var(--ink)}
.who{font-weight:500}.dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex:none;background:var(--n)}
.dot.u,.dot.conf{background:var(--u)}.dot.p,.dot.get{background:#d98a1a}.dot.r,.dot.ok{background:var(--r)}.dot.all{background:var(--navy)}
.tag{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:500;padding:2px 9px 2px 8px;border-radius:999px;white-space:nowrap}
.tag.u,.tag.conf{background:var(--ub);color:var(--u)}.tag.p,.tag.get{background:var(--pb);color:var(--p)}.tag.r,.tag.ok{background:var(--rb);color:var(--r)}.tag.n{background:var(--nb);color:var(--soft)}
.why{display:block;font-size:12.5px;color:var(--soft);margin-top:5px;max-width:380px}
.key{display:flex;align-items:center;gap:8px}.key s{display:block;width:56px;height:4px;border-radius:2px;background:var(--hair);overflow:hidden;text-decoration:none}
.key s i{display:block;height:100%;background:var(--navy)}.key span{font:12.5px var(--mono);color:var(--soft)}
.cmp td{padding:7px 10px 7px 0;font-size:13px;border-bottom:1px solid var(--hair)}.cmp td:first-child{color:var(--soft);width:34%}
.cmp tr.wrong td:nth-child(2),.cmp tr.invented td:nth-child(2){color:var(--u);font-weight:500}.cmp tr.missed td:nth-child(2){color:var(--p)}
.legend2{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--soft);margin:2px 0 10px}.legend2 span{display:inline-flex;gap:6px;align-items:center}
.dot.correct{background:var(--r)}.dot.wrong{background:var(--u)}.dot.missed{background:#d98a1a}.dot.invented{background:#7a4fc7}
.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0;margin:8px 0 24px;counter-reset:l}
.layer{position:relative;background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:0 14px 14px 0}
.layer:after{content:"→";position:absolute;right:-13px;top:22px;color:var(--mute);font-size:15px}.layer:last-child:after{content:none}
.layer b{display:block;font:500 15px var(--sans);margin:4px 0}.layer .n{font:500 11.5px var(--mono);color:var(--blue)}
.layer p{margin:6px 0 0;color:var(--soft);font-size:13px}.layer .tool{display:inline-block;margin-top:10px;font:12px var(--mono);background:var(--hair);border-radius:6px;padding:2px 7px;color:var(--ink2)}
.layer.code{background:#fbfaf8}.listens{display:grid;grid-template-columns:1fr 1fr;gap:16px}.listens h4{margin:0 0 6px;font-size:13px;font-weight:600}
@media(max-width:900px){.listens{grid-template-columns:1fr}}
.allergy{display:inline-block;margin-top:5px;font-size:12px;font-weight:500;color:var(--u);background:var(--ub);border-radius:6px;padding:1px 7px}
.stats b.evb{font-size:15px;font-weight:400;color:var(--soft);line-height:2.1}.stats b.evb em{font:500 24px var(--sans);font-style:normal;margin:0 2px 0 8px;color:var(--ink)}
.stats b.evb em:first-child{margin-left:0}.stats b.evb em.u{color:var(--u)}.stats b.evb em.p{color:#c27a10}.stats b.evb em.r{color:var(--r)}.stats b.evb em.n{color:var(--mute)}
.stats div:nth-child(2){flex:2}
.tried{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:12px 28px}
.try{display:grid;grid-template-columns:28px 1fr;gap:12px;padding:12px 0;border-top:1px solid var(--hair)}
.try .n{font:500 13px var(--mono);color:#fff;background:var(--navy);border-radius:50%;width:26px;height:26px;display:grid;place-items:center}
.try b{font-weight:600}.try p{margin:4px 0 0;color:var(--soft)}.try p.res{color:var(--ink)}.try p.res:before{content:"Result: ";font-weight:600}
.empty{padding:36px;text-align:center;color:var(--soft);display:none}
.cols{display:grid;grid-template-columns:minmax(380px,.85fr) minmax(0,1.25fr);gap:24px;align-items:start}.stick{position:sticky;top:16px}
.box{padding:18px 20px;margin-bottom:14px}.box.warn{background:#fffaf2;border-color:#f0dcbc}.box.bad{background:#fff8f6;border-color:#f2d3cc}.box.good{background:#f6fbf8;border-color:#cfe6d7}
.box ul{margin:4px 0 0;padding-left:18px}.box li{margin:4px 0}.box h3 .dot{margin-right:8px;vertical-align:middle}
.mist{display:grid;grid-template-columns:28px 1fr;gap:14px 14px;margin-top:16px}
.mist .l{font:500 13px var(--mono);color:#fff;background:var(--navy);border-radius:7px;text-align:center;height:26px;line-height:26px}
dl{display:grid;grid-template-columns:120px 1fr;gap:5px 14px;margin:0}dt{color:var(--soft);font-size:13px}dd{margin:0;font-weight:500}
.vit{width:auto}.vit td,.vit th{border:0;border-bottom:1px solid var(--hair);padding:5px 18px 5px 0;font-size:13px;font-weight:400}
.vit th{color:var(--soft)}.say{font:12.5px/1.8 var(--mono);color:var(--ink2);white-space:pre-wrap}
iframe{width:100%;height:calc(100vh - 32px);border:1px solid var(--line);border-radius:12px;background:#fff}
.finding{padding:22px 24px;margin-bottom:16px}.finding .note{color:var(--soft);margin:2px 0 16px;max-width:780px}
.finding td,.finding th{padding:9px 12px 9px 0}
.hbar{display:flex;align-items:center;gap:10px}.hbar s{display:block;height:6px;border-radius:3px;background:var(--navy);text-decoration:none}.hbar s.dim{background:#d9d7d3}
.hbar span{font:12.5px var(--mono);color:var(--soft)}.pick{font-size:11.5px;font-weight:500;color:var(--blue);background:var(--tint);border-radius:999px;padding:1px 8px;margin-left:8px}
.guide{columns:2 520px;column-gap:16px}.guide .panel{padding:22px 26px;margin-bottom:16px;break-inside:avoid;display:inline-block;width:100%}.guide ol,.guide ul{padding-left:20px;margin:6px 0 0}.guide li{margin:8px 0}
.legend{display:grid;grid-template-columns:200px 1fr;gap:14px 16px;align-items:start;margin-top:8px}
@media(max-width:960px){.app{grid-template-columns:1fr}aside{position:static;height:auto}.cols{grid-template-columns:1fr}.stick{position:static}main{padding:24px 18px}}
"""


def page(tab, body, title="TCCC Casualty Cards"):
    nav = "".join(f"<a class='nav{' on' if t == tab else ''}' href='{u}'>{n}</a>" for t, n, u in
                  (("board", "Casualties", "/"), ("how", "How it works", "/how"), ("bench", "Benchmark", "/benchmark"), ("guide", "Guide", "/guide")))
    return HTMLResponse(f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style><div class=app><aside><a class=logo href=/ aria-label=Home>{LOGO}</a>
<div class=prod>Casualty cards · DD Form 1380</div>{nav}
<div class=foot>50 recorded handovers turned into TCCC cards.<br><a href=/how>How it works</a> · <a href=/benchmark>How accurate</a></div></aside>
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


def vitals(card):
    """Latest set of observations in one line: pulse, BP, SpO2, AVPU, and when."""
    i = max((i for i in range(1, 5) if any(card.get(f"signs_{i}_{k}") for k in ("pulse", "bp_systolic", "spo2", "avpu"))), default=0)
    if not i:
        return "", ""
    g = lambda k: card.get(f"signs_{i}_{k}") or ""  # noqa: E731
    parts = [f"P {g('pulse')}" if g("pulse") else "", f"BP {g('bp_systolic')}/{g('bp_diastolic')}" if g("bp_systolic") else "",
             f"SpO2 {g('spo2')}" if g("spo2") else "", g("avpu")[:1] and f"AVPU {g('avpu')[:1]}"]
    return " · ".join(x for x in parts if x), (f"at {g('time')}" if g("time") else "time not given") + (f", set {i}" if i > 1 else "")


def has_tq(card):
    return any(card.get(f"tq_{l}_type") or card.get(f"tq_{l}_time") for l, _ in LIMBS)


def status(rv):
    """(key, what exactly): missing information first, because the person who handed over may leave."""
    get, conf = rv.get("Ask the sender", []), rv.get("Check these", [])
    if get:
        return "get", "Ask for " + ", ".join(get[:3]) + (f", and {len(get) - 3} more" if len(get) > 3 else "")
    if conf:
        return "conf", conf[0][:100] + (f" (and {len(conf) - 1} more)" if len(conf) > 1 else "")
    return "ok", "Print, sign and attach."


def answer_key(card):
    truth = TRUTH.get(card["file"])
    if not truth:
        return None, []
    per_field, _ = score_card(card, truth)
    return prf(Counter(per_field.values()))[2], [(f, o, card.get(f), truth.get(f)) for f, o in per_field.items() if o != "blank_ok"]


def casualties():
    seen = {}
    for name in ("eval", "live"):  # an uploaded recording replaces the evaluation copy of the same name
        d = SETS[name] / "predictions"
        for p in sorted(d.glob("*.json")) if d.exists() else []:
            seen[p.stem] = (name, p.stem, json.loads(p.read_text()), review(name, p.stem))
    order = {"u": 0, "p": 1, "r": 2, "n": 3}
    return sorted(seen.values(), key=lambda c: (order[evac(c[2])[1]], c[1]))


def runs():
    p = OUT / "runs.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


# ---------------------------------------------------------------- pages
@app.get("/")
def board():
    rows, counts = "", Counter()
    for name, stem, card, rv in casualties():
        (ev, ec), (person, known) = evac(card), who(card)
        st, why = status(rv)
        counts[st] += 1
        counts[ec] += 1
        f1, cmp = answer_key(card)
        counts["tq"] += has_tq(card)
        line = " · ".join(x for x in (", ".join(mechanism(card)), ", ".join(injuries(card)[:2])) if x)
        v, vt = vitals(card)
        allergy = card.get("allergies") if (card.get("allergies") or "").upper() not in ("", "NKA") else ""
        oc = Counter(o for _, o, _, _ in cmp)
        keycell = "" if f1 is None else (f"<div class=key><s><i style=width:{f1:.0%}></i></s><span>{f1:.0%}</span></div>"
                                         f"<div class=sub style=margin-top:4px>{oc['correct']} match · {oc['wrong'] + oc['invented']} off · {oc['missed']} missed</div>")
        rid = stem.replace("handover-", "")
        find = " ".join((person, rid, line, " ".join(care(card)))).lower()
        rows += (f"<tr class=row data-st={st} data-ev={ec} data-q='{esc(find)}' onclick=\"location='/card/{name}/{stem}'\">"
                 f"<td><span class='tag {ec}'><span class='dot {ec}'></span>{ev}</span></td>"
                 f"<td><div class=who>{esc(person) if known else '<span style=color:var(--soft)>Name not given</span>'}</div>"
                 f"<div class='sub mono'>{rid}{' · just added' if name == 'live' else ''}</div>"
                 f"<div class=sub>{'wounded ' + card['time'] if card.get('time') else 'wound time not given'}</div>"
                 f"{f'<div class=allergy>Allergy: {esc(allergy)}</div>' if allergy else ''}</td>"
                 f"<td>{esc(line) or '<span class=sub>not stated</span>'}<div class=sub>{esc(', '.join(care(card)[:3]))}</div></td>"
                 f"<td>{esc(v) or '<span class=sub>no observations</span>'}<div class=sub>{esc(vt)}</div></td>"
                 f"<td><span class='tag {st}'><span class='dot {st}'></span>{STATUS[st][0]}</span><span class=why>{esc(why)}</span></td>"
                 f"<td>{keycell}</td><td class=go>›</td></tr>")
    n = sum(counts[k] for k in STATUS)
    h = next((r for r in reversed(runs()) if r["model"] == LLM_MODEL and r["split"] == "heldout"), None)
    stats = (f"<div><span>Casualties</span><b>{n}</b></div>"
             f"<div><span>For the evacuation request</span><b class=evb><em class=u>{counts['u']}</em> urgent <em class=p>{counts['p']}</em> priority "
             f"<em class=r>{counts['r']}</em> routine <em class=n>{counts['n']}</em> not stated</b></div>"
             f"<div><span>Ready to attach</span><b>{counts['ok']}<small>of {n}</small></b></div>"
             f"<div><span>Tourniquets on</span><b>{counts['tq']}<small>casualties</small></b></div>"
             + (f"<div><span>Accuracy on unseen recordings</span><b>{h['f1']:.1%}<small>of filled fields right</small></b></div>" if h else ""))
    tabs = f"<button class='tab on' data-st='' data-hint='Every recorded handover, most urgent first.'>All<i>{n}</i></button>" + "".join(
        f"<button class=tab data-st={k} data-hint='{esc(d)}'><span class='dot {k}'></span>{t}<i>{counts[k]}</i></button>" for k, (t, d) in STATUS.items())
    chips = "<button class='chip on' data-ev=''>Any</button>" + "".join(
        f"<button class=chip data-ev={c}><span class='dot {c}'></span>{lbl}<i>{counts[c]}</i></button>"
        for c, lbl in (("u", "Urgent"), ("p", "Priority"), ("r", "Routine"), ("n", "Not stated")))
    return page("board", f"""<div class=head><div class=grow><h1>Casualties</h1>
<p class=lede>Each recorded handover becomes a filled TCCC card. Most urgent first; open a casualty to see the card and what it still needs.</p></div>
<button class=btn onclick="document.querySelector('.drop').classList.toggle('show')">New handover</button></div>
<form class=drop action=/upload method=post enctype=multipart/form-data>
<label><b>Drop a handover recording, or click to choose one</b><span class=sub>The whole recording, any common audio format. Ready in about
20 seconds. Nothing is guessed: anything not said stays blank.</span><div class=file></div>
<input type=file name=audio accept="audio/*" required></label><button class=btn>Create card</button></form>
<div class=stats>{stats}</div>
<div class=tabs>{tabs}</div><p class=hint>Every recorded handover, most urgent first.</p>
<div class=panel><div class=bar2><input class=search placeholder="Search by name, roster number, recording, injury or treatment">
<span class=lbl>Evacuation</span>{chips}</div>
<table><thead><tr><th>Evacuation</th><th>Casualty</th><th>What happened · what was done</th><th>Latest vitals</th><th>Card</th>
<th title="Testing only: agreement with the official answer for that recording">Answer key</th><th></th></tr></thead>
<tbody>{rows}</tbody></table><div class=empty>No casualties match these filters.</div></div>
<script>
let f={{st:'',ev:'',q:''}},rows=[...document.querySelectorAll('tr.row')];
function apply(){{let shown=0;rows.forEach(r=>{{r.hidden=(f.st&&r.dataset.st!==f.st)||(f.ev&&r.dataset.ev!==f.ev)||(f.q&&!r.dataset.q.includes(f.q));shown+=!r.hidden}});
document.querySelector('.empty').style.display=shown?'none':'block'}}
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{f.st=b.dataset.st;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x===b));
document.querySelector('.hint').textContent=b.dataset.hint;apply()}});
document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{{f.ev=b.dataset.ev;document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===b));apply()}});
document.querySelector('.search').oninput=e=>{{f.q=e.target.value.toLowerCase().trim();apply()}};
let d=document.querySelector('.drop'),inp=d.querySelector('input'),show=()=>d.querySelector('.file').textContent=inp.files[0]?'Selected: '+inp.files[0].name:'';
inp.onchange=show;d.ondragover=e=>{{e.preventDefault();d.classList.add('over')}};d.ondragleave=()=>d.classList.remove('over');
d.ondrop=e=>{{e.preventDefault();d.classList.remove('over');inp.files=e.dataTransfer.files;show()}};
d.onsubmit=()=>{{let b=d.querySelector('.btn');b.disabled=true;b.textContent='Listening, about 20 seconds'}};
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
        todo += f"<div class='panel box warn'><h3><span class='dot get'></span>Missing information: ask the person who handed over</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in get)}</ul></div>"
    if conf:
        todo += f"<div class='panel box bad'><h3><span class='dot conf'></span>Needs checking: compare with the recording</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in conf)}</ul></div>"
    if not todo:
        todo = "<div class='panel box good'><h3><span class='dot ok'></span>Complete</h3>Everything important was said. Print, sign and attach.</div>"
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
                    if any(cell(i, k) for i in vit))
    other = [TREAT[k] for k in TREAT if card.get(k) is True]
    ident_html = ("<dl>" + "".join(f"<dt>{esc(k)}</dt><dd>{esc(str(v))}</dd>" for k, v in ident) + "</dl>") if ident else "<span class=sub>No identity details given.</span>"
    f1, errs = answer_key(card)
    key = ""
    if f1 is not None:
        show = lambda v: "✓" if v is True else ("" if v in (False, None) else esc(str(v)))  # noqa: E731
        c = Counter(o for _, o, _, _ in errs)
        rows = "".join(f"<tr class={o}><td>{f.replace('_', ' ')}</td><td><span class='dot {o}'></span> {show(p) or '<span class=sub>blank</span>'}</td>"
                       f"<td>{show(t) or '<span class=sub>blank</span>'}</td></tr>" for f, o, p, t in sorted(errs, key=lambda e: e[1] == "correct"))
        key = (f"<div class='panel box'><h3>Card vs answer key: {f1:.0%} <span class=sub>· testing only</span></h3><div class=legend2>"
               f"<span><span class='dot correct'></span>{c['correct']} match</span><span><span class='dot wrong'></span>{c['wrong']} different</span>"
               f"<span><span class='dot missed'></span>{c['missed']} not captured</span><span><span class='dot invented'></span>{c['invented']} not in answer key</span></div>"
               f"<table class=cmp><tr><th>Field</th><th>Our card</th><th>Answer key</th></tr>{rows}</table></div>")
    unknown = "" if known else " · no name, roster number or last four was said: take them from the casualty's ID tags"
    wounded = f" at {card['time']}" if card.get("time") else ""
    return page("board", f"""<p class=sub><a href=/>Casualties</a> / {stem.replace('handover-', '')}</p>
<div class=head><div class=grow><h1>{esc(person) if known else 'Name not given'}</h1>
<p class=lede><span class='tag {ec}'><span class='dot {ec}'></span>{ev}</span> <span class='tag {st}'><span class='dot {st}'></span>{STATUS[st][0]}</span>
<span class=sub>{unknown}</span></p></div><a class='btn ghost' href='/pdf/{name}/{stem}' target=_blank>Open PDF to print</a></div>
<div class=cols><div>{todo}{key}
<div class='panel box'><h3>The card, in MIST order</h3>{ident_html}
<div class=mist><span class=l>M</span><div>{esc(', '.join(mechanism(card)) or 'not stated')}{wounded}</div>
<span class=l>I</span><div>{esc('; '.join(injuries(card)) or 'not stated')}<div class=sub>{esc(card.get('notes') or '')}</div></div>
<span class=l>S</span><div>{f"<table class=vit>{vrows}</table>" if vit else 'no observations given'}</div>
<span class=l>T</span><div>{esc(', '.join(care(card) + other) or 'none given')}</div></div></div>
<div class='panel box'><h3>What was heard</h3>{heard(rv.get('Transcript', ''))}</div></div>
<div class=stick><iframe src='/pdf/{name}/{stem}#view=FitH&navpanes=0&pagemode=none' title='Filled DD Form 1380'></iframe></div></div>""", person)


def heard(text):
    """The two listens side by side, named, with why there are two."""
    if "TRANSCRIPT B" not in text:
        return f"<div class=say>{esc(text)}</div>"
    a, b = text.split("TRANSCRIPT B (second listen):")
    a = a.replace("TRANSCRIPT A (medical speech model):", "").strip()
    return (f"<p class=sub style='margin:-4px 0 12px'>Two different models listened to the same recording. Where they heard a value "
            f"differently, the card leaves it blank and asks you to check.</p><div class=listens>"
            f"<div><h4>Listen 1 · ElevenLabs Scribe v2 Medical</h4><div class=say>{esc(a)}</div></div>"
            f"<div><h4>Listen 2 · Qwen 3.8 Omni Flash</h4><div class=say>{esc(b.strip())}</div></div></div>")


def bar(v, dim=False):
    return f"<div class=hbar><s class='{'dim' if dim else ''}' style='width:{v * 220:.0f}px'></s><span>{v:.0%}</span></div>"


# card-model cost for all 50 recordings, measured on the run (one transcript; two transcripts add about 40%)
COST50 = {"google/gemini-3.8-flash": .34, "google/gemini-4-argon": .36, "google/gemini-4-hydrogen": 1.16, "openai/gpt-6.1-terra": .18,
          "deepseek/deepseek-v4.1-flash": .36, "z-ai/glm-5.3": .52, "qwen/qwen4-max": .36, "z-ai/glm-5.3-flash": .46,
          "qwen/qwen3.8-max-0902": .72, "qwen/qwen3.8-27b": .56, "openai/gpt-6.2-sol": .24, "openai/gpt-5.6-luna": .06,
          "mistralai/mistral-large-4-0": 1.08, "qwen/qwen3.8-flash": .34}


@app.get("/benchmark")
def bench():
    rs = runs()
    last = {r["split"]: r for r in rs if r["model"] == LLM_MODEL}
    h, a = last.get("heldout"), last.get("all")
    c = ROOT / "transcripts" / "_bakeoff.csv"
    stt = sorted((r for r in csv.DictReader(c.open()) if "+deepfilternet" not in r["model"] and "+demucs" not in r["model"]),
                 key=lambda r: -float(r["all_numbers"])) if c.exists() else []
    chosen = {STT_MODEL + "+keyterms", SECOND_MODEL}
    stt_rows = "".join(f"<tr><td class=mono>{esc(r['model'])}{'<span class=pick>in use</span>' if r['model'] in chosen else ''}</td>"
                       f"<td>{bar(float(r['all_numbers']), r['model'] not in chosen)}</td><td>{bar(float(r['hard_files_numbers']), r['model'] not in chosen)}</td>"
                       f"<td class=mono>{esc(r['cost_per_audio_hour'])}</td></tr>" for r in stt[:14])
    models = {}
    for r in rs:
        if r["split"] == "dev" and r["model"] != LLM_MODEL or (r["model"] == LLM_MODEL and r["split"] == "dev" and "+" not in r.get("transcripts", "+")):
            models[r["model"]] = r
    held = {r["model"]: r for r in rs if r["split"] == "heldout" and "+" not in r.get("transcripts", "").split("keyterms")[-1]}
    unseen = {m: f"{r['f1']:.1%}" for m, r in held.items()}
    model_rows = "".join(
        f"<tr><td class=mono>{esc(m)}{'<span class=pick>in use</span>' if m == LLM_MODEL else ''}</td><td>{bar(r['f1'], m != LLM_MODEL)}</td>"
        f"<td class=mono>{unseen.get(m, '<span class=sub>not run</span>')}</td>"
        f"<td class=mono>{held[m]['invented'] if m in held else ''}</td><td class=mono>${COST50.get(m, 0):.2f}</td></tr>"
        for m, r in sorted(models.items(), key=lambda kv: -kv[1]["f1"])[:12])
    groups = ""
    hs = OUT / LLM_MODEL.replace("/", "__") / "heldout" / "score.json"
    if hs.exists():
        names = {"identity": "Who (name, ID, unit)", "evac": "Evacuation priority", "mechanism": "Mechanism", "tourniquets": "Tourniquets",
                 "vital_signs": "Vital signs", "treatments": "Other treatments", "medications": "Drugs and fluids"}
        g = json.loads(hs.read_text())["groups"]
        groups = "".join(f"<tr><td>{names.get(k, k)}</td><td>{bar(v['f1'], v['f1'] < .9)}</td></tr>" for k, v in sorted(g.items(), key=lambda kv: -kv[1]["f1"]))
    head = (f"<div class=stats><div><span>Accuracy on 25 unseen recordings</span><b>{h['f1']:.1%}</b></div>"
            f"<div><span>Of what it writes, right</span><b>{h['precision']:.1%}</b></div>"
            f"<div><span>Drugs, tourniquets, vitals, evac</span><b>{h['critical_f1']:.1%}</b></div>"
            f"<div><span>Across all 50</span><b>{a['f1']:.1%}</b></div></div>") if h and a else ""
    return page("bench", f"""<div class=head><div class=grow><h1>Benchmark</h1><p class=lede>Every choice was measured against the answer key that came
with the recordings. Only fields a handover actually filled are scored, since an empty card already "matches" most of the form. Half
the recordings were locked away and run once at the end.</p></div></div>{head}
<div class='panel finding'><h2>Drugs and tourniquets are always right. Names are the weak spot.</h2>
<p class=note>Accuracy by part of the card, on the 25 unseen recordings. Names are spelled the way they sound ("Kaur" heard as "Carr");
in the field the ID tag settles it, which is why the card asks for it.</p><table style='max-width:560px'>{groups}</table></div>
<div class='panel finding'><h2>Listening is the ceiling, so we listen twice.</h2>
<p class=note>19 speech models on all 50 recordings: share of the true values that reached the transcript. Hard audio means radio,
heavy noise or two voices. A second, different model holds 21 of the 80 values the first one misses; where the two disagree, the card
flags the value instead of guessing (unseen accuracy 92.5% to 93.8%). Four denoisers were also tested; all made hard audio worse.</p>
<table><tr><th>Speech model</th><th>All recordings</th><th>Hard audio</th><th>Per audio hour</th></tr>{stt_rows}</table></div>
<div class='panel finding'><h2>Why Gemini 3.8 Flash, when Gemini 4 Argon scored higher</h2>
<p class=note>On the 25 tuning recordings the top six are within 1 point, and their 95% intervals overlap: that gap is noise, not
skill. So the deciding test was the 25 locked-away recordings, scored once. There, Gemini 3.8 Flash was as accurate as Argon and made
up 2 values where Argon made up 9 and GPT-6.1 Terra 5. Terra is $0.16 cheaper for all 50 cards; on a casualty card, two and a half
times as many invented values is not worth 16 cents.</p>
<table><tr><th>Language model</th><th>Tuning set</th><th>Unseen recordings</th><th>Made up (unseen)</th><th>Cost for 50 cards</th></tr>{model_rows}</table></div>
<div class='panel finding'><h2>What a run costs</h2>
<p class=note>The final pipeline on all 50 recordings: Scribe v2 Medical $0.15, second listen $0.03, Gemini reading both transcripts
$0.47. About <b>$0.65 for all 50</b>, 1.3 cents a card, about 20 seconds each, all 50 in parallel in about a minute. Every model
call is cached, so re-scoring or changing the checks costs nothing.</p></div>""")


LAYERS = (
    ("The recording comes in", "The whole handover, exactly as recorded: radio crackle, gunfire, two people talking. We do not cut it or try to clean up the background noise.", "audio file"),
    ("Two listeners write it down", "Two different speech-to-text tools each turn the recording into written words, at the same time. Like two people taking down the same radio message.", "ElevenLabs Scribe (medical) + Qwen Omni"),
    ("A reader fills in the card", "An AI model reads both write-ups and fills in each box on the card, quoting the words it took each answer from. If the two listeners heard a number differently, it leaves that box empty and asks the medic.", "Gemini Flash"),
    ("Automatic checks", "Simple fixed rules, no AI: every answer must appear in what was said, be in the right format, and make medical sense (for example oxygen between 50 and 100). Anything that fails is left empty and flagged.", "fixed rules"),
    ("The card is printed", "The answers go into the official TCCC card (DD Form 1380), including the marks on the body diagram. The finished card is then read back to make sure every box landed correctly.", "official PDF"),
    ("The medic checks and signs", "The medic sees the card plus a short to-do list: what to ask the person who handed over, and what to double-check. Then signs it and attaches it to the casualty.", "this app"),
)

TRIED = (
    ("Which tool should turn speech into text?", "We compared 19 speech-to-text tools from ElevenLabs, OpenAI, Google, Deepgram, AssemblyAI and others, on all 50 recordings.",
     "ElevenLabs Scribe (its medical version) caught the most: 93% of the details, and 86% on the hardest radio and noisy recordings."),
    ("Should we clean up the noise first?", "We tried four tools that remove background noise before the speech-to-text step.",
     "It made things worse on noisy recordings (86% fell to about 80%). The cleaning also removes bits of words. So we send the original recording."),
    ("Does it help to say which words to expect?", "We gave the speech-to-text tool a list of words it will hear: TXA, IV, tourniquet, unit names.",
     "Yes. Drug and equipment words went from 90% to 97% correct. Kept."),
    ("Which AI should fill in the card?", "We compared 14 AI models from OpenAI, Google, Qwen, DeepSeek, Mistral and others, on the same write-ups.",
     "The best six were effectively tied (about 95%). We picked Gemini Flash because it did best on recordings it had never seen and made up the fewest answers."),
    ("Would a second AI checking the first one help?", "We had two different AI models fill in the same cards and compared them.",
     "No. They agreed on 99.6% of answers and made the same mistakes, because the mistakes come from what was heard, not from the reading."),
    ("Would a second listener help?", "We added a second, different speech-to-text tool and gave the reader both write-ups.",
     "Yes. It catches details the first one missed (21 of 80). When the two disagree, the box is flagged instead of guessed. Accuracy on unseen recordings rose from 92.5% to 93.8%."),
    ("Would extra medical rules catch more?", "We tested rules on drug doses and on timings (for example a tourniquet applied before the injury).",
     "They caught none of the remaining 25 mistakes, which are believable but misheard values. Not added."),
    ("How do we know the score is honest?", "We set aside half the recordings at the start and only tested on them once, at the end, like an exam the system had not seen.",
     "93.8% on those unseen recordings, 94.7% across all 50. The first is the one to trust for real use."),
)


@app.get("/how")
def how():
    flow = "".join(f"<div class='layer{' code' if i in (4, 5) else ''}'><span class=n>{i:02d}</span><b>{t}</b><p>{esc(d)}</p>"
                   f"<span class=tool>{esc(tool)}</span></div>" for i, (t, d, tool) in enumerate(LAYERS, 1))
    tried = "".join(f"<div class=try><span class=n>{i}</span><div><b>{esc(q)}</b><p>{esc(what)}</p><p class=res>{esc(res)}</p></div></div>"
                    for i, (q, what, res) in enumerate(TRIED, 1))
    return page("how", f"""<div class=head><div class=grow><h1>How it works</h1><p class=lede>A recorded handover becomes a signed TCCC card in
six steps, in about 20 seconds. AI does the listening and the reading. Fixed rules do the checking. A person always signs.</p></div></div>
<div class=panel style='padding:24px 28px;margin-bottom:20px'><h2>The situation</h2><div class=legend>
<b>Where</b><span>03:00, an abandoned farmhouse used as a trauma ward. Fifty casualties have come through since the last evacuation.</span>
<b>The handover</b><span>The <b>first responder</b>, the soldier or medic who treated the casualty where they were hurt, hands them over, in person
or by radio. They say what hit the casualty, where they are hurt, their vital signs, what treatment was given and how urgently they need
to move (often in the order Mechanism, Injuries, Signs, Treatment: "MIST"). Every handover was recorded.</span>
<b>The problem</b><span>Each casualty needs a <b>TCCC card</b> attached before the evacuation vehicle arrives in 3 to 4 hours. It is the only
record of care that travels with them, and the surgeon at the next stop decides what to do first from it. Nobody has time to write 50 cards
by hand while still treating, and a missed or made-up detail can cost a limb or cause an overdose.</span>
<b>What this does</b><span>Turns each recorded handover into a filled card in about 20 seconds, and tells the medic what is missing or
needs checking, so they only deal with the gaps.</span>
<b>Who uses it</b><span>The medic at the trauma point reviews and signs each card; the evacuation coordinator uses the totals by urgency;
the receiving surgeon reads the card.</span></div></div>
<div class=flow>{flow}</div>
<div class=panel style='padding:24px 28px;margin-bottom:16px'><h2>Why two listeners?</h2><p class=lede style='max-width:none'>Noisy radio
messages get misheard. One listener might write 1420 where the other hears 1422. When they agree, we can be more confident. When they
disagree, the system does not pick one: it leaves the box empty and tells the medic exactly what to check ("Listener 1 heard 1420,
listener 2 heard 1422"). On a casualty card, a question is safer than a wrong number.</p></div>
<div class=panel style='padding:24px 28px;margin-bottom:16px'><h2>What we tried, and how we landed here</h2>
<p class=sub style='margin:0 0 14px'>Every choice was tested against the correct answers supplied with the 50 recordings.</p>
<div class=tried>{tried}</div></div>
<div class=panel style='padding:22px 28px'><h2>A few terms</h2><div class=legend>
<b>Speech-to-text</b><span>A tool that turns spoken words into written text.</span>
<b>AI model (language model)</b><span>Software that reads text and answers questions about it; here, it fills in the card's boxes.</span>
<b>Answer key</b><span>The correct card for each recording, supplied with the task. Used only to measure accuracy.</span>
<b>Accuracy</b><span>Of the boxes that should have something in them, how many our card got right, also counting anything we wrote that should not be there.</span></div></div>""")


@app.get("/guide")
def guide():
    return page("guide", """<div class=head><div class=grow><h1>Guide</h1>
<p class=lede>For the casualty collection point: many casualties, little time, one medic writing cards. The system writes the card from the
handover, so the medic only deals with the gaps.</p></div></div><div class=guide>
<div class=panel><h2>At the handover</h2><ol>
<li><b>Record the whole handover</b>, start to finish. Corrections ("six fifteen, correction six fifty") and read-backs matter.</li>
<li><b>Upload it</b> with <i>New handover</i>. The card is ready in about 20 seconds.</li>
<li><b>Read the status before the person handing over leaves.</b> <i>Missing information</i> names what to ask for ("say again tourniquet time").</li>
<li><i>Needs checking</i>: compare the value with what you heard. Both transcripts are on the card page.</li>
<li><b>Print, check, sign, attach</b> where it can be seen (wrist or belt loop). The card travels with the casualty.</li></ol></div>
<div class=panel><h2>From card to evacuation</h2><div class=legend>
<span class=sub>Who</span><span>The medic or casualty collection point lead reviews cards; the evacuation coordinator uses the totals; the
surgeon at the next stop reads the card.</span>
<span><b>1 · Record</b></span><span>Each handover, in full. The card is ready in about 20 seconds.</span>
<span><b>2 · Close the gaps</b></span><span><i>Missing information</i>: ask the sender before they leave. <i>Needs checking</i>: confirm against the recording.</span>
<span><b>3 · Sign and attach</b></span><span>Print, check, sign, fasten to the casualty (wrist or belt loop). The card travels with them.</span>
<span><b>4 · Request evacuation</b></span><span>The Casualties page gives the totals by priority (Urgent, Priority, Routine) for the evacuation
request, and lists who still has no priority stated.</span>
<span><b>5 · Hand over</b></span><span>Give each casualty's MIST from the card to the evacuation crew. The card and both transcripts are the record of care.</span></div></div>
<div class=panel><h2>Where "Urgent" comes from</h2><p>The evacuation category is what the first responder said: <i>urgent</i>, <i>Cat A</i> or
<i>T1</i> become Urgent; <i>priority</i> and <i>routine</i> as said. The system never decides triage itself. Checked against the answer
key, 49 of 50 categories are right and none is wrong; the 50th, a recording lost to radio static, is left as <i>Not stated</i> so
the medic asks.</p><p class=sub>Worth a second look: casualties sent as Priority with a tourniquet on (8 here). TCCC guidance is to
reassess or convert a tourniquet within about two hours, so confirm the category if evacuation is delayed.</p></div>
<div class=panel><h2>What the labels mean</h2><div class=legend>
<span><span class='tag ok'><span class='dot ok'></span>Complete</span></span><span>Everything a surgeon needs was said and nothing is in doubt.</span>
<span><span class='tag get'><span class='dot get'></span>Missing information</span></span><span>Not said: who the casualty is, evacuation priority, a tourniquet time, a drug's dose or route.</span>
<span><span class='tag conf'><span class='dot conf'></span>Needs checking</span></span><span>Garbled, corrected, or heard differently by the two listens. Left blank, not guessed.</span>
<span><span class='tag u'><span class='dot u'></span>Urgent</span></span><span>Evacuation priority from the handover (also Cat A or T1). Shown first; then Priority, Routine, Not stated.</span>
<span class=sub>Answer key</span><span>Testing only: how closely a card agrees with the official answer for that recording.</span></div></div>
<div class=panel><h2>Rules the system follows</h2><ul>
<li><b>Blank means not said.</b> It never fills a value it did not hear.</li>
<li><b>No name, no guess.</b> If no name, battle roster number or last four was said, take them from the casualty's ID tags.</li>
<li><b>Corrections win; retractions are dropped</b> ("ignore that, other casualty").</li>
<li><b>Two listens.</b> Where they disagree on a value, it is flagged for you rather than chosen.</li></ul></div>
<div class=panel><h2>What it does not do</h2><ul><li>Replace the medic's judgement or signature. Every card is checked by a person before it is attached.</li>
<li>Work offline yet. A local speech model captures about 80% of the values with no network; that is the next step for forward use.</li></ul></div></div>""")


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
