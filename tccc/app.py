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

from .config import LLM_MODEL, OUT, ROOT, SECOND_MODEL, STT_MODEL, slug
from .extract import SPLITS
from .openrouter import guard_budget, load_key
from .pipeline import process
from .score import TRUTH, prf, score_card
from .textnorm import spoken_to_digits, squash
from .validate import BOOLS, label

SETS = {"eval": OUT / slug(LLM_MODEL) / "all", "live": OUT / "live"}
LOGO = (Path(__file__).parent / "static" / "logo.svg").read_text()
DIAGRAM = (ROOT / "docs" / "how-it-works.svg").read_text()
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
          "conf": ("Needs checking", "A value was unclear, corrected or heard differently by the two listeners. Check it against the recording.")}
app = FastAPI(title="TCCC Casualty Cards")
esc = html.escape

CSS = (Path(__file__).parent / "static" / "app.css").read_text()


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
            [line[2:] for line in body.splitlines() if line.startswith("- ") and line[2:] not in ("nothing missing", "nothing flagged")]
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


def heard_by(value, text):
    """Did this listener hear the value? Same digits (however spelled: "one twenty" = 120) and same key words."""
    sq, words = squash(text), spoken_to_digits(text)
    nums = re.findall(r"\d+", value)
    keys = [w for w in re.findall(r"[a-z]{3,}", value.lower()) if w not in ("not", "and", "the")]
    return all(n in sq or n.lstrip("0") in sq for n in nums) and all(w in words for w in keys)


def confidence(card, transcript):
    """Share of filled values both listeners heard, and the values only one heard. Measured on all 50: values both heard
    are 97.9% correct, values only one heard 81.1% (about nine times the error rate)."""
    if "TRANSCRIPT B" not in transcript:
        return None, []
    a, b = transcript.split("TRANSCRIPT B (second listen):")
    vals = [(k, v) for k, v in card.items() if v and k not in BOOLS and k not in ("file", "notes", "injury_boxes")]
    one = [(k, v) for k, v in vals if heard_by(v, a) != heard_by(v, b)]
    return (1 - len(one) / len(vals) if vals else 1.0), one


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
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


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
        conf, one = confidence(card, rv.get("Transcript", ""))
        conf_cell = "" if conf is None else (f"<span class='dot {'ok' if not one else 'get'}'></span> {conf:.0%}")
        conf_tip = "Heard by only one listener: " + ", ".join(f"{label(k)} {v}" for k, v in one) if one else "Both listeners agree on every value"
        injury = " · ".join(x for x in (", ".join(mechanism(card)), ", ".join(injuries(card)[:2])) if x)
        treat = ", ".join(care(card))
        v, vt = vitals(card)
        allergy = card.get("allergies") if (card.get("allergies") or "").upper() not in ("", "NKA") else ""
        rid = stem.replace("handover-", "")
        al = f" <span class=al title='Allergy: {esc(allergy)}'>allergy</span>" if allergy else ""
        find = " ".join((person, rid, injury, treat)).lower()
        rows += (f"<tr class=row data-st={st} data-ev={ec} data-q='{esc(find)}' onclick=\"location='/card/{name}/{stem}'\">"
                 f"<td><span class='tag {ec}'><span class='dot {ec}'></span>{ev}</span></td>"
                 f"<td title='{esc(person)}'><span class={'who' if known else 'unk'}>{esc(person) if known else 'Name not given'}</span>"
                 f" <span class='rid mono'>{rid}</span>{al}</td>"
                 f"<td title='{esc(injury)}{(' | ' + esc(treat)) if treat else ''}'>{esc(injury) or '<span class=sub>not stated</span>'}</td>"
                 f"<td title='{esc(vt)}'>{esc(v) or '<span class=sub>none given</span>'}</td>"
                 f"<td><span class='tag {st}'><span class='dot {st}'></span>{STATUS[st][0]}</span></td>"
                 f"<td class=next title='{esc(why)}'>{esc(why)}</td>"
                 f"<td class=num title='{esc(conf_tip)}'>{conf_cell}</td>"
                 f"<td class='mono num'>{'' if f1 is None else f'{f1:.0%}'}</td><td class=go>›</td></tr>")
    n = sum(counts[k] for k in STATUS)
    h = next((r for r in reversed(runs()) if r["model"] == LLM_MODEL and r["split"] == "heldout"), None)
    stats = (f"<div><span>Casualties</span><b>{n}</b></div><div><span>Urgent</span><b>{counts['u']}</b></div>"
             f"<div><span>Ready to attach</span><b>{counts['ok']} <small>of {n}</small></b></div>"
             + (f"<div><span title='25 recordings set aside before tuning; prompts and rules were never tuned on them'>Accuracy, held-out recordings</span><b>{h['f1']:.1%}</b></div>" if h else ""))
    tabs = f"<button class='tab on' data-st='' data-hint='Every recorded handover, most urgent first.'>All<i>{n}</i></button>" + "".join(
        f"<button class=tab data-st={k} data-hint='{esc(d)}'><span class='dot {k}'></span>{t}<i>{counts[k]}</i></button>" for k, (t, d) in STATUS.items())
    chips = "<button class='chip on' data-ev=''>Any</button>" + "".join(
        f"<button class=chip data-ev={c}><span class='dot {c}'></span>{lbl}<i>{counts[c]}</i></button>"
        for c, lbl in (("u", "Urgent"), ("p", "Priority"), ("r", "Routine"), ("n", "Not stated")))
    return page("board", f"""<div class=head><div class=grow><h1>Casualties</h1>
<p class=lede>Each recorded handover becomes a filled TCCC card. Most urgent first; open a casualty to see the card and what it still needs.</p></div>
<button class=btn onclick="document.querySelector('.drop').classList.toggle('show')">New handover</button></div>
<form class=drop action=/upload method=post enctype=multipart/form-data>
<label><b>Drop a handover recording, or click to choose one</b><span class=sub>The whole recording, as a WAV file. Ready in about
20 seconds. Nothing is guessed: anything not said stays blank. Runs live on your OpenRouter key from <span class=mono>.env</span>
(about 1.3 cents a card, stops at the spend cap).</span><div class=file></div>
<input type=file name=audio accept="audio/*" required></label><button class=btn>Create card</button></form>
<div class=stats>{stats}</div>
<div class=tabs>{tabs}</div><p class=hint>Every recorded handover, most urgent first.</p>
<div class=panel><div class=bar2><input class=search placeholder="Search by name, roster number, recording, injury or treatment">
<span class=lbl>Evacuation</span>{chips}</div>
<table class=grid><colgroup><col style=width:112px><col style=width:16%><col style=width:17%><col style=width:18%><col style=width:186px><col><col style=width:96px><col style=width:64px><col style=width:28px></colgroup>
<thead><tr><th>Evacuation</th><th>Casualty</th><th>Injury</th><th>Latest vitals</th><th>Status</th><th>Next step</th>
<th class=num title="Share of the card's values both listeners heard. Values heard by only one are about nine times more likely to be wrong">Confidence</th>
<th class=num title="Testing only: agreement with the official answer for that recording">Match</th><th></th></tr></thead>
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
    conf, one = confidence(card, rv.get("Transcript", ""))
    if one:
        todo += (f"<div class='panel box warn'><h3><span class='dot get'></span>Heard by only one listener ({conf:.0%} of values agreed)</h3>"
                 f"<p class=sub style=margin:0>Values only one listener heard are about nine times more likely to be wrong. Check them first.</p><ul>"
                 + "".join(f"<li>{esc(label(k))}: {esc(str(v))}</li>" for k, v in one) + "</ul></div>")
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
    """The two transcripts side by side, named, with why there are two."""
    if "TRANSCRIPT B" not in text:
        return f"<div class=say>{esc(text)}</div>"
    a, b = text.split("TRANSCRIPT B (second listen):")
    a = a.replace("TRANSCRIPT A (medical speech model):", "").strip()
    return (f"<p class=sub style='margin:-4px 0 12px'>Two different models listened to the same recording. Where they heard a value "
            f"differently, the card leaves it blank and asks you to check.</p><div class=listens>"
            f"<div><h4>First listener · ElevenLabs Scribe v2 Medical</h4><div class=say>{esc(a)}</div></div>"
            f"<div><h4>Second listener · Qwen 3.8 Omni Flash</h4><div class=say>{esc(b.strip())}</div></div></div>")


def bar(v, dim=False, places=0):
    return f"<div class=hbar><s class='{'dim' if dim else ''}' style='width:{v * 220:.0f}px'></s><span>{v:.{places}%}</span></div>"


WEAK = .9  # Benchmark bars below this F1 are drawn grey
# score.GROUPS key -> (label, card fields it covers, why it is lower when it is)
GROUP_INFO = {
    "tourniquets": ("Tourniquets", "limb, type and time for each arm and leg, and the extremity tick", ""),
    "medications": ("Drugs and fluids", "painkillers, antibiotics, TXA and other drugs, fluids and blood: name, dose, route, time", ""),
    "evac": ("Evacuation priority", "urgent, priority or routine", ""),
    "vital_signs": ("Vital signs", "each set of obs: time, pulse, blood pressure, breathing rate, oxygen, AVPU, pain", ""),
    "mechanism": ("Mechanism", "what caused the injury: gunshot, IED, blast, fall and so on", ""),
    "identity": ("Who and when", "name, last four, battle roster, sex, date, time of wounding, service, unit, allergies, "
                 "the sender's name and last four",
                 "Mostly blanks rather than wrong values. Names are written the way they sound (\"Kaur\" heard as \"Carr\"), "
                 "one recording is almost all static, and the time of wounding is often not said clearly. The card asks for "
                 "these, and the ID tag settles the name."),
    "treatments": ("Other treatments", "dressings, airway, breathing aids (chest seal, oxygen, needle), splint, eye shield, "
                   "combat pill pack, hypothermia kit",
                   "Small items mentioned in passing (a pill pack, a splint) are the easiest to miss. Nearly all its errors "
                   "are boxes left unticked, not wrong ticks."),
}


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
    groups, key = "", ""
    hs = OUT / slug(LLM_MODEL) / "heldout" / "score.json"
    if hs.exists():
        g = json.loads(hs.read_text())["groups"]
        order = sorted(g.items(), key=lambda kv: -kv[1]["f1"])
        groups = "".join(f"<tr><td>{GROUP_INFO[k][0]}</td><td>{bar(v['f1'], v['f1'] < WEAK, 1)}</td></tr>" for k, v in order if k in GROUP_INFO)
        key = "".join(
            f"<tr><td><b>{GROUP_INFO[k][0]}</b><div class=sub>{GROUP_INFO[k][1]}</div>"
            + (f"<div class=sub style='color:var(--ink2)'>{GROUP_INFO[k][2]}</div>" if v["f1"] < WEAK else "")
            + f"</td><td class=mono>{sum(v.get(o, 0) for o in ('correct', 'wrong', 'missed', 'invented'))}</td>"
            f"<td class=mono>{v.get('correct', 0)} / {v.get('missed', 0)} / {v.get('wrong', 0)} / {v.get('invented', 0)}</td></tr>"
            for k, v in order if k in GROUP_INFO)
    dev, held = (", ".join(f[9:12] for f in SPLITS[s]) for s in ("dev", "heldout"))
    head = (f"<div class=stats><div><span>Accuracy on the 25 held-out recordings</span><b>{h['f1']:.1%}</b></div>"
            f"<div><span>Of what it writes, right</span><b>{h['precision']:.1%}</b></div>"
            f"<div><span>Drugs, tourniquets, vitals, evac</span><b>{h['critical_f1']:.1%}</b></div>"
            f"<div><span>Across all 50 (includes the tuning half)</span><b>{a['f1']:.1%}</b></div></div>"
            f"<div class='panel box' style='margin:-12px 0 24px'><h3>What \"held-out\" means</h3><p style='margin:0'>Before any tuning, the 50 "
            f"recordings were split in two. The file names were sorted alphabetically and every other one was set aside: 25 for "
            f"<b>tuning</b> (every instruction and rule was written from mistakes on these) and 25 <b>held-out</b>, which the "
            f"instructions were never tuned on. The held-out score is the best guide to a new recording. One honest caveat: the "
            f"held-out recordings were also used to choose between the last two or three models, which were tied on the tuning set "
            f"(we picked the one that made up the fewest values), and a list of UK unit names was written after seeing units in "
            f"the answer key. So the held-out number is slightly optimistic. The all-50 number is higher partly because it "
            f"includes the 25 the system was tuned on.</p>"
            f"<details style='margin-top:8px'><summary class=sub style='cursor:pointer'>Which recordings are in each half</summary>"
            f"<p class='sub mono' style='margin:8px 0 0'>Tuning: {dev}<br>Held-out: {held}</p></details></div>") if h and a else ""
    return page("bench", f"""<div class=head><div class=grow><h1>Benchmark</h1><p class=lede>Every choice was measured against the answer key that came
with the recordings. Only fields a handover actually filled are scored, since an empty card already "matches" most of the form. Half
the recordings were held out from all prompt tuning.</p></div></div>{head}
<div class='panel finding'><h2>Drugs and tourniquets are always right. Names are the weak spot.</h2>
<p class=note>Accuracy by part of the card, on the 25 held-out recordings. Each percentage is the same F1 score as the headline, counted
only over the boxes in that part of the card that the handover actually filled (or that we filled). Every part is used and scored.</p>
<div class=groups><div><table>{groups}</table>
<div class=legend2 style='margin-top:12px'><span><s class=sw></s>{WEAK:.0%} or above</span><span><s class='sw dim'></s>below {WEAK:.0%}: the weaker areas, worth a closer look</span></div></div>
<div><table class=gkey><tr><th>Part of the card</th><th>Values scored</th><th title='right / left blank / different / made up'>Right / blank / different / made up</th></tr>{key}</table></div></div></div>
<div class='panel finding'><h2>Listening is the ceiling, so we listen twice.</h2>
<p class=note>19 speech models on all 50 recordings: share of the true values that reached the transcript. Hard audio means radio,
heavy noise or two voices. A second, different model holds 21 of the 80 values the first one misses; where the two disagree, the card
flags the value instead of guessing (held-out accuracy 92.5% to 93.8%). Four denoisers were also tested; all made hard audio worse.</p>
<table><tr><th>Speech model</th><th>All recordings</th><th>Hard audio</th><th>Per audio hour</th></tr>{stt_rows}</table></div>
<div class='panel finding'><h2>Why Gemini 3.8 Flash, when Gemini 4 Argon scored higher</h2>
<p class=note>On the 25 tuning recordings the top six are within 1 point, and their 95% intervals overlap: that gap is noise, not
skill. So the deciding test was the 25 held-out recordings (which makes the held-out score slightly optimistic). There, Gemini 3.8 Flash was as accurate as Argon and made
up 2 values where Argon made up 9 and GPT-6.1 Terra 5. Terra is $0.16 cheaper for all 50 cards; on a casualty card, two and a half
times as many invented values is not worth 16 cents.</p>
<table><tr><th>Language model</th><th>Tuning set</th><th>Held-out</th><th>Made up (held-out)</th><th>Cost for 50 cards</th></tr>{model_rows}</table></div>
<div class='panel finding'><h2>What a run costs</h2>
<p class=note>The final pipeline on all 50 recordings: Scribe v2 Medical $0.15, second listener $0.03, Gemini reading both transcripts
$0.47. About <b>$0.65 for all 50</b>, 1.3 cents a card, about 20 seconds each, all 50 in parallel in about a minute. Every model
call is cached, so re-scoring or changing the checks costs nothing.</p></div>""")


# Planning assumptions, not measured (minutes): (calm best case, busy collection point). See the /how footnote.
TIME = {"hand": (5, 12), "review": (1, 2), "item": (.5, 1.5)}


def time_rows(cards, items):
    """Hours to finish every card, by hand and with the system, for 1 and 2 medics (2 = a perfectly even split)."""
    hand = [cards * m / 60 for m in TIME["hand"]]
    sys_ = [(cards * r + items * i) / 60 for r, i in zip(TIME["review"], TIME["item"])]
    return (("By hand, 1 medic", *hand), ("By hand, 2 medics", *(h / 2 for h in hand)),
            ("With the system, 1 medic", *sys_), ("With the system, 2 medics", *(s / 2 for s in sys_)))


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
    ("Should we clean up the noise first?", "We tried four tools that remove background noise before the speech-to-text step: spectral gating, radio band-pass, DeepFilterNet3 and Meta Denoiser (Demucs).",
     "It made things worse on noisy recordings (86% fell to about 80%). The cleaning also removes bits of words. So we send the original recording."),
    ("Does it help to say which words to expect?", "We gave the speech-to-text tool a list of words it will hear: TXA, IV, tourniquet, unit names.",
     "Yes. Drug and equipment words went from 90% to 97% correct. Kept."),
    ("Which AI should fill in the card?", "We compared 14 AI models from OpenAI, Google, Qwen, DeepSeek, Mistral and others, on the same write-ups.",
     "The best six were effectively tied (about 95%). We picked Gemini Flash because it did best on recordings it had never seen and made up the fewest answers."),
    ("Would a second AI checking the first one help?", "We had two different AI models fill in the same cards and compared them.",
     "No. They agreed on 99.6% of answers and made the same mistakes, because the mistakes come from what was heard, not from the reading."),
    ("Would a second listener help?", "We added a second, different speech-to-text tool and gave the reader both write-ups.",
     "Yes. It catches details the first one missed (21 of 80). When the two disagree, the box is flagged instead of guessed. Accuracy on the held-out recordings rose from 92.5% to 93.8%."),
    ("Would extra medical rules catch more?", "We tested rules on drug doses and on timings (for example a tourniquet applied before the injury).",
     "They caught none of the remaining 25 mistakes, which are believable but misheard values. Not added."),
    ("How do we know the score is honest?", "Before any tuning we sorted the 50 file names and set every other one aside: 25 to tune on, 25 'held-out' recordings that no instruction or rule was ever written from. The held-out set was also used to choose between the last few tied models, so its score is slightly optimistic.",
     "93.8% on the 25 held-out recordings, 94.7% across all 50 (which includes the 25 it was tuned on). The held-out score is the better guide for real use."),
)


@app.get("/how")
def how():
    flow = "".join(f"<div class='layer{' code' if i in (4, 5) else ''}'><span class=n>{i:02d}</span><b>{t}</b><p>{esc(d)}</p>"
                   f"<span class=tool>{esc(tool)}</span></div>" for i, (t, d, tool) in enumerate(LAYERS, 1))
    cards = casualties()
    items = sum(len(rv.get("Ask the sender", [])) + len(rv.get("Check these", [])) + len(confidence(c, rv.get("Transcript", ""))[1])
                for _, _, c, rv in cards)
    rows = time_rows(len(cards), items)
    scale = 11.0  # hours across the full width
    chart = ("<div class=tchart><div class=band style='left:calc(190px + (100% - 190px) * " + f"{3 / scale:.4f});"
             f"width:calc((100% - 190px) * {1 / scale:.4f})'><span>vehicle arrives</span></div>") + "".join(
        f"<div class=trow><span class=tl>{lbl}</span><div class=ttrack><i class='{'sys' if 'system' in lbl else 'hand'}' style='left:{lo / scale:.1%};width:{(hi - lo) / scale:.1%}'></i>"
        f"<b style='left:{hi / scale:.1%}'>{lo:.1f} to {hi:.1f} h</b></div></div>" for lbl, lo, hi in rows) + "".join(
        f"<span class=tick style='left:calc(190px + (100% - 190px) * {h / scale:.3f})'>{h} h</span>" for h in range(0, int(scale) + 1)) + "</div>"
    (h_lo, h_hi), (r_lo, r_hi), (i_lo, i_hi) = TIME["hand"], TIME["review"], TIME["item"]
    tried = "".join(f"<div class=try><span class=n>{i}</span><div><b>{esc(q)}</b><p>{esc(what)}</p><p class=res>{esc(res)}</p></div></div>"
                    for i, (q, what, res) in enumerate(TRIED, 1))
    return page("how", f"""<div class=head><div class=grow><h1>How it works</h1><p class=lede>A recorded handover becomes a draft TCCC card in about 20
seconds per card (all 50 at once take about a minute). AI does the listening and the reading, fixed rules do the checking, and the
medic decides: the system drafts, a person always reviews and signs.</p></div></div>
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
<div class=panel style='padding:24px 28px;margin-bottom:20px'><h2>At a glance</h2>
<p class=sub style='margin:0 0 12px'>Blue is AI, grey is fixed rules, green is the medic (human in the loop). About 20 seconds per card from
recording to draft; all 50 run at the same time.</p>
<div style='max-width:1000px;margin:0 auto'>{DIAGRAM}</div></div>
<div class=flow>{flow}</div>
<div class=panel style='padding:24px 28px;margin-bottom:16px'><h2>Time it saves</h2>
<p class=sub style='margin:0 0 16px'>Planning estimate of the hours a medic team needs to finish all {len(cards)} cards. These are assumptions,
not measurements: nobody has timed medics doing this. Each bar runs from a calm best case to a realistic busy night. The band marks when
the evacuation vehicle arrives (3 to 4 hours).</p>
{chart}
<div class=legend style='margin-top:18px'>
<b>By hand</b><span>{h_lo} to {h_hi} minutes a card. The low end is a quiet desk: recording at hand, listen once, write about 22 boxes, mark the
body diagram. The high end is a busy collection point: finding the right recording, re-listening through static and corrections,
stopping to treat, then printing, signing and attaching the card.</span>
<b>With the system</b><span>{r_lo} to {r_hi} minutes to review every card (the medic still reads and signs all of them), plus {i_lo} to {i_hi}
minutes for each of the <b>{items}</b> things the cards ask the medic to ask or check. That count comes from the cards themselves and
updates with them. The high end allows for re-listening and for chasing a sender who has moved on.</span>
<b>Not included</b><span>Treating casualties, triage decisions, and waiting for an answer that never comes (a sender who has left, a casualty
who cannot say). Those items stay open on the card, flagged. The system's own processing, about a minute for all 50, happens before the review.</span>
<b>Two medics</b><span>Assumes the work splits perfectly evenly, with no handoffs. Real teams lose some time to coordination.</span>
<b>How to measure it</b><span>A short tabletop exercise: two or three medics each write 5 cards by hand from recordings and review 5 system
cards, timed, with a few planned interruptions. Twenty minutes each would replace these assumptions with real numbers.</span></div></div>
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
<span><span class='tag conf'><span class='dot conf'></span>Needs checking</span></span><span>Garbled, corrected, or heard differently by the two listeners. Left blank, not guessed.</span>
<span><span class='tag u'><span class='dot u'></span>Urgent</span></span><span>Evacuation priority from the handover (also Cat A or T1). Shown first; then Priority, Routine, Not stated.</span>
<span class=sub>Answer key</span><span>Testing only: how closely a card agrees with the official answer for that recording.</span></div></div>
<div class=panel><h2>Rules the system follows</h2><ul>
<li><b>Blank means not said.</b> It never fills a value it did not hear.</li>
<li><b>No name, no guess.</b> If no name, battle roster number or last four was said, take them from the casualty's ID tags.</li>
<li><b>Corrections win; retractions are dropped</b> ("ignore that, other casualty").</li>
<li><b>Two listeners.</b> Where they disagree on a value, it is flagged for you rather than chosen.</li></ul></div>
<div class=panel><h2>What it does not do</h2><ul><li>Replace the medic's judgement or signature. Every card is checked by a person before it is attached.</li>
<li>Work offline yet. In the same speech test, NVIDIA Parakeet, a model small enough to run on a laptop with no internet, caught
about 80% of the details against 93% for the online model we use (and only about half on radio and noisy recordings). A device in the
field may have no network, so a model like this is the route to offline use; it costs about 13 points of hearing accuracy, which is why
it is a next step and not the default.</li></ul></div></div>""")


@app.get("/pdf/{name}/{stem}")
def pdf(name: str, stem: str):
    return FileResponse(SETS[name] / "cards" / f"{stem}.pdf", media_type="application/pdf")


@app.post("/upload")
def upload(audio: UploadFile = File(...)):
    dst = SETS["live"] / "uploads" / Path(audio.filename or "recording.wav").name
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(audio.file.read())
    try:
        key = load_key()
        guard_budget(key)  # same hard spend cap as the command line
    except SystemExit as e:  # no key, or the spend cap is reached: say so plainly instead of an error page
        return page("board", f"<h1>Not processed</h1><p class=lede>{esc(str(e))}</p>"
                    "<p><a class='btn ghost' href=/>Back to casualties</a></p>", "Not processed")
    process(dst, SETS["live"], key)
    return RedirectResponse(f"/card/live/{dst.stem}", status_code=303)
