"""Fill the TCCC card PDF (DD Form 1380) from a card dict in the ground-truth shape.

    python -m tccc.fill_pdf card.json out.pdf
"""
import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DecodedStreamObject, DictionaryObject, FloatObject,
                           NameObject, TextStringObject)

from .config import DATA

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


def _appearance(writer, annot, text):
    """Draw the text into the field (11pt Helvetica, like the golden cards) so every viewer shows it."""
    x1, y1, x2, y2 = (float(v) for v in annot["/Rect"])
    w, h = x2 - x1, y2 - y1
    size = min(11.0, h - 2)
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = DecodedStreamObject()
    content = f"/Tx BMC q BT /Helv {size:.1f} Tf 0 g 2 {(h - size) / 2 + 1:.2f} Td ({safe}) Tj ET Q EMC"
    stream.set_data(content.encode("latin-1", "replace"))
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
                             NameObject("/BaseFont"): NameObject("/Helvetica"),
                             NameObject("/Encoding"): NameObject("/WinAnsiEncoding")})
    stream.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
                   NameObject("/BBox"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(w), FloatObject(h)]),
                   NameObject("/Resources"): DictionaryObject(
                       {NameObject("/Font"): DictionaryObject({NameObject("/Helv"): font})})})
    annot[NameObject("/AP")] = DictionaryObject({NameObject("/N"): writer._add_object(stream)})


def fill(card: dict, out_path: Path, blank: Path = BLANK) -> Path:
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
                _appearance(writer, annot, str(value or ""))  # Preview and phones ignore NeedAppearances
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
