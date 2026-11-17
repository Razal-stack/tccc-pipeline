"""Fill the TCCC card PDF (DD Form 1380) from a card dict in the ground-truth shape.

    python -m tccc.fill_pdf card.json out.pdf
"""
import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject, BooleanObject

DATA = Path(__file__).resolve().parent.parent / "data"
BLANK = DATA / "tccc-card-blank.pdf"
FIELD_MAP = json.loads((DATA / "field_map.json").read_text())


def _full_name(annot):
    parts, obj = [], annot
    while obj is not None:
        if "/T" in obj:
            parts.append(str(obj["/T"]))
        parent = obj.get("/Parent")
        obj = parent.get_object() if parent is not None else None
    return ".".join(reversed(parts))


def _field_values(card: dict) -> dict:
    """Map PDF field name -> value (str for text/choice, bool for checkboxes)."""
    out = {}
    for key, pdf_name in FIELD_MAP["fields"].items():
        if key in card:
            out[pdf_name] = card[key]
    for key, pdf_name in FIELD_MAP["repeated_on_back"].items():
        if key in card:
            out[pdf_name] = card[key]
    ticked = set(card.get("injury_boxes", []))
    for box, pdf_name in FIELD_MAP["injury_boxes"].items():
        out[pdf_name] = box in ticked
    return out


def fill(card: dict, out_path, blank=BLANK):
    values = _field_values(card)
    writer = PdfWriter(clone_from=PdfReader(str(blank)))
    for page in writer.pages:
        for ref in page.get("/Annots") or []:
            annot = ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            name = _full_name(annot)
            if name not in values:
                continue
            value = values[name]
            target = annot if "/T" in annot else annot["/Parent"].get_object()
            if isinstance(value, bool):
                state = NameObject("/1" if value else "/Off")
                target[NameObject("/V")] = state
                annot[NameObject("/AS")] = state
            else:
                target[NameObject("/V")] = TextStringObject(str(value or ""))
                if "/AP" in annot:  # stale appearance would hide the new value
                    del annot["/AP"]
    acro = writer._root_object.get("/AcroForm")
    if acro is not None:
        acro = acro.get_object()
        acro[NameObject("/NeedAppearances")] = BooleanObject(True)
        if "/XFA" in acro:  # the XFA layer would override AcroForm values in Acrobat
            del acro["/XFA"]
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_path


def read_back(pdf_path) -> dict:
    """Read a filled PDF back into the ground-truth shape (used to verify the filler)."""
    reader = PdfReader(str(pdf_path))
    raw = {}
    for page in reader.pages:
        for ref in page.get("/Annots") or []:
            annot = ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            holder = annot if "/V" in annot else (annot.get("/Parent") or {})
            v = holder.get("/V")
            raw[_full_name(annot)] = v
    card = {}
    for key, pdf_name in FIELD_MAP["fields"].items():
        v = raw.get(pdf_name)
        if v is None:
            card[key] = None
        elif str(v) in ("/1", "/Off"):
            card[key] = str(v) == "/1"
        else:
            card[key] = str(v)
    card["injury_boxes"] = sorted(b for b, n in FIELD_MAP["injury_boxes"].items() if str(raw.get(n)) == "/1")
    return card


if __name__ == "__main__":
    fill(json.loads(Path(sys.argv[1]).read_text()), sys.argv[2])
    print("wrote", sys.argv[2])
