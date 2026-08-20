"""BOILERPLATE VARIETY — the discriminator that separates document furniture from structure.

A running header or page footer repeats one line verbatim except for its number; a division
heading does not. Mask the numeral out of the containing line and count how many DISTINCT
remainders there are. Nothing is enumerated; the measure is taken on the document.

TWO CORRECTIONS, both found by running it:

  * **Mask the TOKEN, not `str(ordinal)`.** `CHAPTER II` carries a two-character token whose
    ordinal renders as one digit, so masking one character left `chapter #i.` and made 61 identical
    chapter headings look 38% varied. Every non-arabic system was mis-measured.

  * **A marker alone on its line has no line to vary.** GDPR writes a recital as `(1)` on its own
    line with the text following, so the masked line is `(#)` for all 173 and the measure called
    the entire recital sequence boilerplate — the correct top-level structure, destroyed by the
    filter meant to protect it. The window therefore extends to the next non-empty line when what
    remains is too short to carry a heading.
"""
import re
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from induct import occurrences, templates, stable_chain, MIN_CHAIN

MIN_REMNANT = 4     # chars of masked line below which the heading must live on the next line

def _bounds(text, pos):
    a = text.rfind("\n", 0, pos) + 1
    b = text.find("\n", pos); b = len(text) if b < 0 else b
    return a, b

def masked_context(text, o):
    a, b = _bounds(text, o.numeral_at)
    line = text[a:b]
    i = o.numeral_at - a
    m = (line[:i] + "#" + line[i + o.token_len:]).strip()
    if len(m.replace("#", "").strip(" .()[]-")) < MIN_REMNANT:
        c, d = _bounds(text, b + 1) if b + 1 < len(text) else (b, b)
        m = (m + " " + text[c:d].strip())[:160]
    return m.lower()

def variety(text, occs, stable, key):
    """Variety of what the marker drags along BEYOND its own template.

    THE THIRD CORRECTION, and it is the one that makes the measure mean what it says. Masking the
    numeral alone left `chapter #.` identical across all 61 chapters of a novel, so the filter
    demoted the correct answer as boilerplate — the same mistake it had just been built to stop,
    pointed the other way.

    The template ALREADY captures the constant word: `page`, `chapter`, `article` are in the
    grouping key. What decides furniture is whether there is FURTHER constant text — `fielding, et
    al. standards track` rides along with every page number and nothing rides along with a chapter
    heading. So the template's own tokens are removed before the variety is taken, and a marker
    that drags nothing else is NEUTRAL rather than condemned.
    """
    own = {str(x).strip().lower() for x in key[1] if isinstance(x, str) and x.strip()}
    ms = []
    for j in stable:
        m = masked_context(text, occs[j])
        words = [w for w in re.findall(r"[a-z0-9]+", m) if w not in own]
        ms.append(" ".join(words))
    residue = max(len(x) for x in ms)
    if residue == 0:
        return 1.0, "(marker carries no further text - neutral)"
    return len(set(ms)) / len(ms), Counter(ms).most_common(1)[0][0][:56]

def rank(text, groups):
    R = len(text); out = []
    for k, v in groups.items():
        vals = [o.ordinal for o in v]
        L, st = stable_chain(vals)
        if len(st) < MIN_CHAIN: continue
        ords = [vals[j] for j in st]; anch = [v[j].numeral_at for j in st]
        spread = ords[-1] - ords[0] + 1
        base = L * (L / len(v)) * ((anch[-1] - anch[0]) / R) * (len(st) / spread if spread else 0)
        var, common = variety(text, v, st, k)
        out.append({"score": base * var, "base": base, "variety": var, "chain": L,
                    "cands": len(v), "key": k, "common": common,
                    "first": text[v[st[0]].offset:v[st[0]].offset + 60].replace("\n", "/")})
    out.sort(key=lambda r: -r["score"])
    return out

if __name__ == "__main__":
    TEXT = Path(__file__).resolve().parent / "corpora_text"
    for p in sorted(TEXT.glob("*.txt")):
        t = p.read_text(); rows = rank(t, templates(occurrences(t)))
        print(f"\n=== {p.stem}")
        for r in rows[:4]:
            view, key = r["key"]
            print(f"   {r['score']:8.2f} var{r['variety']:5.2f} chain{r['chain']:5}/{r['cands']:<5} "
                  f"{view}:{'|'.join(str(x) for x in key)[:30]:30} {r['first'][:50]!r}")
