"""The cross-cutting components. **Each one is a rule that cannot be got wrong by forgetting.**

`docs/FRONTEND-SCOPE.md` §9 asks for these to be *impossible to omit in the type system, not merely
a convention*. Python has no JSX-style required props, so the equivalent is: the constructor
raises. A caller who forgets the admission state does not render a settled count without it — they
get an exception, at build time, with the argument attached.

| component | the rule | what raises |
|---|---|---|
| `fraction` | R2 — both integers, on one line | `BareRate` |
| `settled_count` | R3 — no settled count without its admission state, in the same block | `AdmissionStateMissing` |
| `count` | R5 — absent ≠ empty ≠ zero, and the absent case carries NO DIGIT | `UnnamedAbsence` |
| `reason_code` | only the closed thirty | `UnknownReasonCode` |
| `empty_state` | no affirmative verdict; an empty list of failures is not an empty list of unchecked cells | `BannedAffirmation` |

The banned vocabulary is imported from `cdfc.surface.labels` rather than restated, so this file
cannot fall behind the gate that scans for it.
"""

from __future__ import annotations

from typing import Any, Final

from cdfc.surface.markup import esc

# The three admission states, and each renders its own caveat. `PRE-GATE` is not a warning badge to
# be styled small: it says the predicates producing the number are unqualified.
ADMISSION_CAVEAT: Final[dict[str, str]] = {
    "PRE-GATE": (
        "PRE-GATE — none of the predicates producing this number is admitted under G4. The number "
        "says how much of the denominator a check ran over, not that any check is right."
    ),
    "PARTIALLY-ADMITTED": (
        "PARTIALLY-ADMITTED — some predicates producing this number carry a G4 record and some do "
        "not. The mixture is not summarised into a single confidence."
    ),
    "POST-GATE": (
        "POST-GATE — every predicate producing this number carries a measured false-failure rate "
        "under a corpus that licenses one."
    ),
}


class BareRate(ValueError):
    """A percentage with no fraction beside it. R2.

    A percentage carries no evidence of its own arithmetic, and on this surface the arithmetic is
    the product. The v0 harness printed one to two decimal places over a denominator nobody could
    reconstruct — `ci/no-bare-rate.sh` and `docs/measurements/` carry the actual figure, and it is
    deliberately not repeated here, because this module is inside that gate's scan root.
    """


class AdmissionStateMissing(ValueError):
    """A settled count with no admission state in the same block. R3."""


class UnnamedAbsence(ValueError):
    """A `None` count with no reason. R5 — and the absent case must carry NO DIGIT."""


class UnknownReasonCode(ValueError):
    """A reason code outside the closed thirty. An unknown code is an error, never a row."""


class BannedAffirmation(ValueError):
    """An affirmative verdict reached a screen. R1.

    The vocabulary lives in `cdfc.surface.labels`, the ONE file exempt from
    `ci/no-green-tick.sh`. Naming a banned token here — even to explain the rule — puts it inside
    the gate's scan root, and the gate is right to refuse: a rendered template importing this
    module has no way to know a token appeared in a docstring rather than in a string. Two of the
    tokens and one banned rate went red on the first draft of this file, in exactly that way.
    """


def _banned() -> frozenset[str]:
    """Read from `labels`, never restated. A second copy would fall behind the gate."""
    from cdfc.surface.labels import BANNED_IN_COPY, banned_tokens

    return frozenset(t.lower() for t in (*banned_tokens(), *BANNED_IN_COPY))


def assert_no_affirmation(text: str) -> str:
    """R1, at the point of construction rather than only in the CI grep.

    The grep is the backstop and it scans source; this catches a phrase assembled at RUNTIME from
    data — a reason code, a template name, a remedy string — which the grep cannot see at all.

    **The glyphs are read from `labels.BANNED_GLYPHS`, never typed here.** Typing them would put
    them inside `ci/no-green-tick.sh`'s scan root, and the gate would refuse this file — correctly,
    because a rendered template importing it has no way to know a glyph appeared in a comparison
    rather than in a string.
    """
    low = text.lower()
    hit = [b for b in _banned() if b and b in low]
    if hit:
        raise BannedAffirmation(
            f"{hit} reached a screen. This product may say *something is wrong here* and may never "
            f"say the opposite: the whole claim is what was NOT checked, and one affirmative "
            f"verdict undoes it. Text was: {text!r}"
        )
    return text


def fraction(numerator: int, denominator: int, *, unit: str = "", of: str = "of") -> str:
    """**R2. Both integers, one line, and the percentage may not travel alone.**

    There is no parameter that takes a percentage. That is the enforcement: a caller holding only a
    rate has nothing to pass, so the missing denominator surfaces where it was lost rather than on
    the screen.
    """
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        raise BareRate("a boolean is not a count")
    if not isinstance(numerator, int) or not isinstance(denominator, int):
        raise BareRate(
            f"fraction({numerator!r}, {denominator!r}): both parts are INTEGERS. A float here is a "
            "rate whose arithmetic a reader cannot reconstruct, and reconstructing it is the point."
        )
    if denominator < 0 or numerator < 0:
        raise BareRate("counts are not negative")
    # THE UNIT SITS OUTSIDE THE NOWRAP SPAN. `.fr` is `white-space: nowrap` so the two integers
    # and their separator can never be split across a line — a numerator alone at the end of a
    # line is a bare count. Putting the unit inside that span made the whole phrase unbreakable,
    # and at 390px the hero ran off the screen reading `1,849 of 3,747 fields NOT ch`.
    tail = f' <span class="fr-u">{esc(unit)}</span>' if unit else ""
    return (f'<span class="fr"><span class="fr-n">{numerator:,}</span>'
            f'<span class="fr-sep"> {esc(of)} </span>'
            f'<span class="fr-d">{denominator:,}</span></span>{tail}')


def settled_count(settled: int, in_scope: int, admission: str, *, label: str = "checks") -> str:
    """**R3. The count and its admission state, inside ONE element.**

    "Same page" is not the rule and never was — the rule is ancestor distance ≤ 2, because a badge
    in a footer is a badge nobody reads next to the number it qualifies. They are emitted as one
    string here so no layout can separate them.
    """
    if not admission or admission not in ADMISSION_CAVEAT:
        raise AdmissionStateMissing(
            f"a settled count of {settled} was rendered with admission={admission!r}. A count that "
            f"travels without its admission state reads as a verdict. Known states: "
            f"{sorted(ADMISSION_CAVEAT)}"
        )
    return (
        '<div class="settled-block">'
        f'<p class="hero">{fraction(settled, in_scope, unit=esc(label))}</p>'
        f'<p class="admission" data-state="{esc(admission)}">{esc(ADMISSION_CAVEAT[admission])}</p>'
        "</div>"
    )


def count(value: int | None, *, absent_reason: str = "", label: str = "") -> str:
    """**R5. Three renderings, and the absent one carries no digit at all.**

    | value | renders |
    |---|---|
    | `5` | the number |
    | `0` | the number, and it is a MEASUREMENT |
    | `None` | the reason, with **no digit anywhere in the output** |

    A blank where a count should be reads as *nothing to report*, and a reader cannot tell it from
    a genuine zero. So the third case is not a blank either: it is a sentence.
    """
    if value is None:
        if not absent_reason.strip():
            raise UnnamedAbsence(
                "a count is absent and no reason was given. `absent ≠ empty ≠ zero` is this "
                "project's founding distinction and an unexplained blank collapses two of the three."
            )
        if any(ch.isdigit() for ch in absent_reason):
            raise UnnamedAbsence(
                f"the not-measured rendering contains a digit: {absent_reason!r}. A digit in this "
                "state is read as the measurement, which is exactly what has not been taken."
            )
        return f'<span class="count count-absent">{esc(absent_reason)}</span>'
    if isinstance(value, bool) or not isinstance(value, int):
        raise UnnamedAbsence(f"count({value!r}) is not an integer or None")
    tail = f' <span class="count-label">{esc(label)}</span>' if label else ""
    return f'<span class="count figure">{value:,}</span>{tail}'


def reason_code(code: str) -> str:
    """Only the closed thirty. **An unknown code renders as an error, never as a label.**

    An invented code beside real ones is indistinguishable from a real one, which is why the store
    refuses to fabricate `NO_PREDICATE` and why this refuses to display one.
    """
    from cdfc.verdict import ReasonCode

    known = {str(getattr(r, "value", r)) for r in ReasonCode}
    if code not in known:
        raise UnknownReasonCode(
            f"{code!r} is not one of the {len(known)} reason codes. Rendering it beside real codes "
            "would make it indistinguishable from one."
        )
    return f'<code class="reason">{esc(code)}</code>'


def admission_badge(state: str) -> str:
    if state not in ADMISSION_CAVEAT:
        raise AdmissionStateMissing(f"{state!r} is not an admission state")
    return f'<span class="badge" data-state="{esc(state)}">{esc(state)}</span>'


def empty_state(title: str, body: str, *, action: str = "") -> str:
    """**Never "All good!" and never "Nothing to report."**

    An empty list of FAILURES is not an empty list of UNCHECKED CELLS, and the difference is the
    whole product. Every empty state on this surface has to say which of the two it is.
    """
    assert_no_affirmation(title)
    assert_no_affirmation(body)
    tail = f'<div class="empty-action">{action}</div>' if action else ""
    return (f'<div class="empty"><p class="empty-title">{esc(title)}</p>'
            f'<p class="empty-body">{esc(body)}</p>{tail}</div>')


def error_state(title: str, detail: str, *, remedy: str = "") -> str:
    """The server's `detail`, **verbatim**. The backend's messages carry the argument."""
    rem = (f'<p class="err-remedy"><span class="meta">what fixes it</span> '
           f'<code>{esc(remedy)}</code></p>') if remedy else ""
    return (f'<div class="err" role="alert"><p class="err-title">{esc(title)}</p>'
            f'<p class="err-detail">{esc(detail)}</p>{rem}</div>')


def kv(label: str, value: str, *, raw: bool = False) -> str:
    v = value if raw else esc(value)
    return f'<div class="kv"><dt>{esc(label)}</dt><dd>{v}</dd></div>'


def table(headers: list[tuple[str, str]], rows: list[list[str]], *, caption: str = "") -> str:
    """Rows are pre-escaped by the caller. **A column's class lands on its cells, not just its
    header.**

    The first version put the alignment class on `<th>` only, so a numeric column had a
    right-aligned heading over left-aligned digits — which is worse than no alignment at all,
    because the eye is told there is a column rule and then finds none.

    A wide table scrolls INSIDE its own container: the page body must never scroll horizontally,
    because a horizontal scrollbar on the page is how a column of counts leaves the screen without
    anybody noticing it was there. **The caption sits OUTSIDE that container**, so the sentence
    explaining a cap is never itself cut off by the cap's own scrollbar.
    """
    head = "".join(f'<th class="{esc(cls)}" scope="col">{esc(h)}</th>' for h, cls in headers)
    classes = [cls for _h, cls in headers]
    body = "".join(
        "<tr>" + "".join(
            f'<td class="{esc(classes[i]) if i < len(classes) else ""}">{c}</td>'
            for i, c in enumerate(row)
        ) + "</tr>"
        for row in rows
    )
    cap = f'<p class="table-caption">{esc(caption)}</p>' if caption else ""
    return (f'{cap}<div class="tablewrap"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def bar(segments: list[tuple[str, int, str, bool]], total: int, *,
        floor_permille: int = 12) -> str:
    """The coverage band. **It never fills, and `always` is what makes that true.**

    Each segment is `(css_class, count, title, always_drawn)`. A segment with a count gets a
    `flex-grow` proportional to it, floored so that one cell in three thousand is still visible.

    **A segment marked `always` is drawn at the floor even at zero.** The first version dropped
    every zero-count segment, which quietly removed `NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE` —
    the two terms whose whole job is to be there. The band then reached its own far edge, which is
    the one thing it must never do: it would say the field surface has been fully accounted for
    when two of its terms have never been measured.
    """
    if total <= 0:
        return '<div class="band band-empty"></div>'
    out = []
    for cls, n, title, always in segments:
        grow = max(n * 1000 // total, floor_permille if (n or always) else 0)
        if not grow:
            continue
        out.append(
            f'<div class="seg {esc(cls)}" style="flex-grow:{grow}" '
            f'title="{esc(title)}" data-n="{n}"></div>'
        )
    return f'<div class="band" role="img" aria-label="coverage band">{"".join(out)}</div>'


def sparkline(points: list[dict[str, Any]], *, width: int = 640, height: int = 200) -> str:
    """The settled-fraction series. **Step-downs are styled as DATA, not as warnings.**

    Drawn as inline SVG with one `<circle>` per point and no library. The y-axis is anchored at
    zero and at the field surface — never at the data range — because a chart auto-scaled to its
    own values turns a 36-cell fall into a cliff and a reader cannot tell it from a collapse.
    """
    if len(points) < 2:
        return ""
    pad, left = 28, 92
    top = max(p["fieldSurface"] for p in points) or 1
    n = len(points) - 1
    xs = [left + (width - left - pad) * i // n for i in range(len(points))]
    ys = [height - pad - (height - 2 * pad) * p["settled"] // top for p in points]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(zip(xs, ys)))
    # THE AXIS IS LABELLED, because an unlabelled flat line is unreadable in the honest direction:
    # a reader who cannot see the anchor cannot tell "barely moved" from "auto-scaled to nothing".
    axis_labels = (
        f'<text class="tick" x="{left - 8}" y="{height - pad + 4}" text-anchor="end">0</text>'
        f'<text class="tick" x="{left - 8}" y="{pad + 4}" text-anchor="end">{top:,}</text>'
        f'<text class="tick" x="{left - 8}" y="{pad + 20}" text-anchor="end">field surface</text>'
        # `start` and `end`, not `middle`: a centred label on the last point overflows the
        # viewBox and is clipped, and a clipped date is a date a reader cannot check.
        f'<text class="tick" x="{xs[0]}" y="{height - 6}" text-anchor="start">'
        f'{esc(points[0]["at"])}</text>'
        f'<text class="tick" x="{xs[-1]}" y="{height - 6}" text-anchor="end">'
        f'{esc(points[-1]["at"])}</text>'
    )
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="{5 if p.get("steppedDown") else 4}" '
        f'class="dot{" dot-down" if p.get("steppedDown") else ""}" '
        f'data-at="{esc(p["at"])}" data-settled="{p["settled"]}" '
        f'data-surface="{p["fieldSurface"]}" data-cause="{esc(p.get("cause") or "")}"><title>'
        f'{esc(p["at"])} — {p["settled"]:,} of {p["fieldSurface"]:,}'
        f'{(" ▼ " + esc(p["cause"])) if p.get("cause") else ""}</title></circle>'
        for p, x, y in zip(points, xs, ys)
    )
    return (
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="settled cells over time, anchored at zero and at the field surface">'
        f'<line class="axis" x1="{left}" y1="{height - pad}" x2="{width - pad}" '
        f'y2="{height - pad}"></line>'
        f'<line class="axis axis-y" x1="{left}" y1="{pad}" x2="{left}" y2="{height - pad}"></line>'
        f"{axis_labels}"
        f'<path class="series" d="{path}"></path>{dots}</svg>'
    )
