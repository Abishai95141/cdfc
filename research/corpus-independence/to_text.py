"""Convert every acquired corpus to ONE uniform plain-text form, so the division recovery is
what is being compared and not ten different HTML parsers.

The rule is the same for every corpus: strip markup, split on line breaks, strip each line, drop
empty lines, join with a single LF. That preserves LINE STRUCTURE (which markers are anchored to)
and discards everything else. It is deliberately dumb: a smarter per-corpus extractor would be the
corpus-specific tuning this whole exercise exists to avoid.
"""
import html, json, re, sys, unicodedata, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent / "corpora"
OUT = Path(__file__).resolve().parent / "corpora_text"
OUT.mkdir(exist_ok=True)

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
BLOCK = re.compile(r"</(p|div|li|tr|h[1-6]|section|article|br|P|DIV)\s*>|<br\s*/?>", re.I)

def from_markup(raw: str) -> str:
    raw = SCRIPT.sub(" ", raw)
    raw = BLOCK.sub("\n", raw)
    raw = TAG.sub(" ", raw)
    return html.unescape(raw)

def from_pdf(path: Path) -> str:
    import pdfplumber
    with pdfplumber.open(path) as doc:
        return "\n".join(p.extract_text() or "" for p in doc.pages)

def normalise_lines(text: str) -> str:
    text = text.replace("­", "")
    text = unicodedata.normalize("NFKC", text)
    lines = []
    for ln in text.split("\n"):
        ln = " ".join(ln.split())
        if ln:
            lines.append(ln)
    return "\n".join(lines)

def main() -> int:
    rows = []
    for p in sorted(HERE.iterdir()):
        if p.name.startswith("."): continue
        if p.suffix in (".html", ".htm", ".xml", ".xhtml"):
            body = from_markup(p.read_text(encoding="utf-8", errors="replace"))
        elif p.suffix == ".pdf":
            body = from_pdf(p)
        elif p.suffix == ".txt":
            body = p.read_text(encoding="utf-8", errors="replace")
        else:
            continue
        t = normalise_lines(body)
        q = OUT / (p.stem + ".txt")
        q.write_text(t, encoding="utf-8")
        rows.append({"corpus": p.stem, "source_file": p.name,
                     "source_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                     "chars": len(t), "lines": t.count("\n") + 1,
                     "text_sha256": hashlib.sha256(t.encode()).hexdigest()})
        print(f"  {p.stem:26} {len(t):9,} chars  {t.count(chr(10))+1:7,} lines")
    (OUT / "MANIFEST.json").write_text(json.dumps(rows, indent=1))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
