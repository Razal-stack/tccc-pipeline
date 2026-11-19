"""Draw the layered "how it works" diagram: python3 docs/diagram.py  ->  docs/how-it-works.svg (used by the app and README)."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "how-it-works.svg"
KIND = {"ai": ("#eef5fb", "#0065b4"), "rule": ("#f4f3ef", "#868685"), "person": ("#eaf5ee", "#2f7d4f"), "io": ("#ffffff", "#c9c7c2")}


def box(x, y, w, h, title, lines, kind):
    fill, stroke = KIND[kind]
    cx = x + w / 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{y + 30}" text-anchor="middle" class="t">{title}</text>'
            + "".join(f'<text x="{cx}" y="{y + 52 + i * 19}" text-anchor="middle" class="s">{line}</text>' for i, line in enumerate(lines)))


def arrow(x1, y1, x2, y2):
    return (f'<path d="M{x1},{y1} C{x1},{(y1 + y2) / 2} {x2},{(y1 + y2) / 2} {x2},{y2 - 4}" fill="none" stroke="#9a9894" '
            f'stroke-width="1.6" marker-end="url(#a)"/>')


def layer(y, h, step, name, who, color):
    return (f'<rect x="20" y="{y}" width="4" height="{h}" rx="2" fill="{color}"/><text x="36" y="{y + 26}" class="ln">{step}</text>'
            f'<text x="36" y="{y + 46}" class="lt">{name}</text><text x="36" y="{y + 64}" class="lw">{who}</text>')


def note(y, from_x, from_y, title, lines):
    """A side note joined to its box by a dashed line: the 'why' a diagram alone cannot show."""
    return (f'<path d="M{from_x},{from_y} L996,{from_y}" stroke="#c9c7c2" stroke-dasharray="4 4"/>'
            f'<rect x="1000" y="{y}" width="300" height="{34 + 19 * len(lines)}" rx="10" fill="#fffaf2" stroke="#f0dcbc"/>'
            f'<text x="1016" y="{y + 24}" class="nt">{title}</text>'
            + "".join(f'<text x="1016" y="{y + 46 + i * 19}" class="ns">{line}</text>' for i, line in enumerate(lines)))


CHECKS = (("Said in the recording?", "every value must appear", "in what was heard"),
          ("Right format?", "times as 4 digits,", "doses with units"),
          ("Medically plausible?", "SpO2 50 to 100,", "BP top above bottom"),
          ("Anything missing?", "name, evac priority,", "tourniquet time, dose"),
          ("Listeners agree?", "sets each value's", "confidence"))


def draw():
    checks = "".join(
        f'<rect x="{245 + i * 139}" y="465" width="131" height="76" rx="10" fill="#ffffff" stroke="#c9c7c2"/>'
        f'<text x="{310.5 + i * 139}" y="487" text-anchor="middle" class="c">{t}</text>'
        f'<text x="{310.5 + i * 139}" y="507" text-anchor="middle" class="cs">{a}</text>'
        f'<text x="{310.5 + i * 139}" y="524" text-anchor="middle" class="cs">{b}</text>' for i, (t, a, b) in enumerate(CHECKS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 880" role="img" aria-label="How a recorded handover becomes a TCCC card" style="width:100%;height:auto;font-family:Geist,system-ui,-apple-system,sans-serif">
<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#9a9894"/></marker>
<style>.t{{font-size:16px;font-weight:600;fill:#181818}}.s{{font-size:13px;fill:#5f5d5a}}.c{{font-size:12.5px;font-weight:600;fill:#181818}}.cs{{font-size:11.5px;fill:#706e6b}}
.ln{{font-size:11px;font-weight:600;fill:#868685;letter-spacing:.08em}}.lt{{font-size:15px;font-weight:600;fill:#181818}}.lw{{font-size:12px;fill:#868685}}
.nt{{font-size:13px;font-weight:600;fill:#7a4a06}}.ns{{font-size:12.5px;fill:#5f5d5a}}</style></defs>
{layer(20, 70, "INPUT", "Recording", "as recorded", "#c9c7c2")}
{layer(140, 90, "STEP 1", "Listen", "AI, two tools", "#0065b4")}
{layer(280, 90, "STEP 2", "Read", "AI", "#0065b4")}
{layer(420, 140, "STEP 3", "Check", "fixed rules, no AI", "#868685")}
{layer(610, 90, "STEP 4", "Output", "card + to-do list", "#c9c7c2")}
{layer(750, 110, "STEP 5", "Medic", "human in the loop", "#2f7d4f")}
{box(410, 20, 350, 70, "Recorded handover", ["radio crackle, gunfire, two voices: not cut, not cleaned"], "io")}
{arrow(585, 90, 390, 140)}{arrow(585, 90, 780, 140)}
{box(230, 140, 320, 90, "Listener 1: ElevenLabs Scribe", ["medical speech-to-text, told to expect", "words like TXA, IV, tourniquet"], "ai")}
{box(620, 140, 320, 90, "Listener 2: Qwen Omni", ["a second, independent", "speech-to-text listen"], "ai")}
{note(134, 940, 185, "Why two listeners?", ["Noisy radio gets misheard. A value both", "listeners heard is right 98% of the time;", "a value only one heard, 81%. When they", "disagree, the card asks; it never guesses."])}
{arrow(390, 230, 530, 280)}{arrow(780, 230, 640, 280)}
{box(370, 280, 430, 90, "Reader: Gemini Flash", ["fills each box, quoting the words it used;", "if the listeners disagree, leaves it blank and flags it"], "ai")}
{arrow(585, 370, 585, 420)}
<rect x="235" y="420" width="705" height="140" rx="12" fill="#f4f3ef" stroke="#868685" stroke-width="1.5"/>
<text x="587" y="450" text-anchor="middle" class="t">Automatic checks on every value</text>{checks}
{note(440, 940, 490, "If a check fails", ["the value is left blank and listed for", "the medic. Nothing is guessed, and", "every value on the card traces back", "to words in the recording."])}
{arrow(587, 560, 390, 610)}{arrow(587, 560, 780, 610)}
{box(230, 610, 320, 90, "TCCC card (DD Form 1380)", ["filled PDF and body diagram,", "read back to confirm every box"], "io")}
{box(620, 610, 320, 90, "Medic's to-do list", ["what to ask the sender, what to check,", "confidence for each value"], "io")}
{arrow(390, 700, 520, 750)}{arrow(780, 700, 650, 750)}
{box(305, 750, 560, 110, "Human in the loop: the medic decides", ["reviews every card; asks the sender for anything missing;", "confirms flagged values against the recording;", "signs and attaches it. The system only drafts."], "person")}
{note(758, 865, 805, "Review time (planning estimate)", ["1 to 2 minutes a card, plus 0.5 to 1.5", "per item to ask or check; by hand, 5 to", "12 minutes a card. Not yet timed."])}
</svg>'''


if __name__ == "__main__":
    OUT.write_text(draw())
    print("wrote", OUT)
