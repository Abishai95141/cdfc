"""The one scan-root list, and the banned user-facing vocabulary.

R5: `SCAN_ROOTS` is defined HERE and nowhere else. P14 extends it; nothing replaces it.
`ci/no-green-tick.sh` and `ci/no-bare-except.sh` read it rather than hard-coding a path,
because two lists drift and the one that drifts is the one nobody is reading.

A grep over a MISSING root exits 0 and reports success — NC-D01's mechanism applied to CI.
`ci/scan-roots-exist.sh` therefore asserts existence before any grep runs, and
`test_nc__CI01_missing_scan_root_fails` proves that assertion can go red.
"""

from __future__ import annotations

# Extended by P14, never replaced.
#
# DECIDED 11 Aug 2026, and the reason is the point of this file.
# The specification says two different things about this constant: the P0-B1 file list
# calls the thirteen sub-packages "the CI scan roots (R5)", while the same build's
# interface block writes `SCAN_ROOTS = ("src/cdfc",)`. They are not interchangeable.
#
# Under the single top-level form, NC-CI01's injector (which deletes
# `src/cdfc/evaluate/`) does not remove a *declared* root, the gate stays green, and the
# flagship negative control of P0 CANNOT BE OBSERVED RED. The test would have asserted
# a property nothing was checking — which is precisely the defect the gate exists to
# catch, in the gate itself.
#
# So the roots are enumerated. A package that is deleted, renamed, or never created is
# a gate failure rather than a silently skipped grep.
# Alternative it beat: `("src/cdfc",)` plus a separate existence manifest — rejected
# because two lists drift, and the one that drifts is the one nobody is reading.
SCAN_ROOTS: tuple[str, ...] = (
    "src/cdfc",
    "src/cdfc/ingest",
    "src/cdfc/schema",
    "src/cdfc/facts",
    "src/cdfc/calc",
    "src/cdfc/predicates",
    "src/cdfc/evaluate",
    "src/cdfc/verdict",
    "src/cdfc/probes",
    "src/cdfc/selfcheck",
    "src/cdfc/attest",
    "src/cdfc/surface",
    "src/cdfc/qualify",
    "src/cdfc/measure",
)

# Directories inside a scan root that are searched for user-facing copy.
SURFACE_ROOTS: tuple[str, ...] = ("src/cdfc/surface",)

# ---------------------------------------------------------------------------
# THE BANNED VOCABULARY
#
# There is no green tick anywhere in this product, and the commitment is a system
# property rather than a preference only because this list is greppable and the
# grep is a build gate (ci/no-green-tick.sh, registry row 1).
#
# The list is deliberately over-broad on glyphs and narrow on words: a false
# positive costs one rename, a false negative ships an all-clear.
# ---------------------------------------------------------------------------
BANNED_GLYPHS: tuple[str, ...] = (
    "✓",  # ✓ check mark
    "✔",  # ✔ heavy check mark
    "✅",  # ✅ white heavy check mark
    "☑",  # ☑ ballot box with check
    "\U0001f7e2",  # 🟢 green circle
    "✨",  # ✨
)

BANNED_PHRASES: tuple[str, ...] = (
    "all clear",
    "all-clear",
    "no issues found",
    "no problems found",
    "looks good",
    "everything checks out",
    "verified clean",
    "certified clean",
    "passed all checks",
    "fully compliant",
    "100% compliant",  # rate-ok: this list IS the banned vocabulary
    # From the SUPERSEDED DESIGN.md (Meta commerce), excluded by docs/DESIGN-ADAPTATION.md. That
    # system shipped `badge-success` for "In stock / Verified / Free shipping" — an affirmative
    # green pill, which is precisely the all-clear this product refuses to render.
    #
    # THESE THREE STAY BANNED THOUGH THEIR SOURCE IS GONE. DESIGN.md is now Ecosystem
    # Visualization and defines none of them. A banned token whose source has been removed is
    # exactly the entry somebody deletes as tidy-up — and the list would then be one design system
    # behind forever, which is how a gate dies quietly rather than loudly.
    "badge-success",
    "badge-promo-yellow",
    "promo-banner",
    # ADDED 15 Aug 2026 with the Ecosystem Visualization adaptation. Its genre is the operations
    # dashboard, whose reassurance does not live in a component that can be banned — it lives in
    # the composition. These are the words that genre reaches for, and each is an all-clear in one
    # word. The list is narrow because the scan root is narrow: it runs over src/cdfc/surface only.
    "all systems",
    "systems normal",
    "systems nominal",
    "operational",
    "uptime",
    "healthy",
    "nominal",
    "in good standing",
)

# Words that may appear in code but never in rendered user-facing copy.
BANNED_IN_COPY: tuple[str, ...] = (
    "clean",
    "compliant",
)


def banned_tokens() -> tuple[str, ...]:
    """Everything the surface grep looks for, in one tuple, for the shell gate."""
    return BANNED_GLYPHS + BANNED_PHRASES


# =====================================================================================
# P14-B1 — THE THREE REGISTRIES, AND WHY THEY ARE APPEND-ONLY
#
# The exit gate reads `surfaces_passing_all_four_gates == len(SURFACES)` — and this build
# writes SURFACES. A surface that cannot be made to pass can be DELETED from the registry
# and the gate goes green with the sweep still reporting caught == active.
#
# **That is M1, this plan's founding defect — the numerator choosing its own denominator —
# sitting inside the gate written to prevent it.** The residue entry NC-N09 declares the
# registry's INCOMPLETENESS honestly and says nothing about its SHRINKAGE, which is a
# different and much cheaper failure.
#
# So: append-only, with a growth log; a row may be RETIRED with a dated argument and never
# deleted; both cardinalities publish as a time series, so a registry that shrinks the day
# before a gate is read is visible in the artifact the gate is read from. A retired surface
# leaves the gate's DENOMINATOR and stays in the SCAN — we may give up auditing a surface,
# never on prohibiting an all-clear on it.
# =====================================================================================

from collections.abc import Callable, Mapping  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Any, Final, Literal  # noqa: E402

Renders = Literal["SETTLED_COUNT", "FFR", "VERDICT_NAME", "STATE", "RATE", "NONE"]


@dataclass(frozen=True, slots=True)
class Label:
    id: str
    binding: str          # the exact run-record path this label reads
    template: str
    surfaces: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SurfaceSpec:
    id: str
    kind: Literal["HTML", "JSON", "STDOUT", "DOC"]
    renders: frozenset[Renders]
    entrypoint: str
    retired_on: str = ""
    retired_because: str = ""

    def __post_init__(self) -> None:
        if bool(self.retired_on) != bool(self.retired_because):
            raise ValueError(
                f"{self.id}: a retirement carries BOTH a date and an argument. A row retired with "
                "no reason is a row deleted with extra steps."
            )

    @property
    def retired(self) -> bool:
        return bool(self.retired_on)


@dataclass(frozen=True, slots=True)
class NumberSpec:
    id: str
    extract: Callable[[Any], str]     # the rendered string, canonical formatting
    surfaces: tuple[str, ...]         # where it MUST appear


# --- the label registry: the hero cannot drift, because it is data ---------------------
#
# `hero.left` and `hero.right` take the SAME type token, the SAME weight and the SAME ink
# (cdfc.surface.design.HERO_TOKEN / HERO_INK). The moment one is larger or more coloured
# than the other, the reader has been told which matters — and the one they would be told
# to ignore is the count of fields nobody checked.
LABEL_REGISTRY: Final[Mapping[str, Label]] = {
    lb.id: lb for lb in (
        Label("hero.left", "fraction.settled.failed + fraction.settled.total",
              "{F} failures across {S} checks", ("S02.report-hero",)),
        Label("hero.right",
              "fraction.unsettled.indeterminate + notRun + noPredicate + error",
              "{U} fields were not checked", ("S02.report-hero",)),
        Label("hero.admission", "surface.admission.admission_state(run)",
              "predicate set: {A}", ("S02.report-hero",)),
        # REQUIRED IN THE SAME BLOCK AS ANY SETTLED COUNT. A count whose denominator rule is
        # somewhere else on the page is a count whose denominator a reader will not find.
        Label("hero.denominator_rule", "fraction.denominator.generatorRule",
              "denominator: {R}", ("S02.report-hero",)),
        Label("strapline.predicates", "len(run.selection)",
              "{N} predicates", ("S03.report-strapline",)),
        Label("strapline.fraction", "fraction.fraction",
              "settled fraction {P}", ("S03.report-strapline",)),
    )
}

# --- the surface registry: THE DENOMINATOR OF THIS PHASE'S NUMBER. APPEND-ONLY. --------
SURFACES: Final[tuple[SurfaceSpec, ...]] = (
    SurfaceSpec("S01.report-file", "HTML", frozenset({"NONE"}),
                "cdfc.surface.render.render_report"),
    SurfaceSpec("S02.report-hero", "HTML", frozenset({"SETTLED_COUNT", "STATE"}),
                "cdfc.surface.render.render_report"),
    SurfaceSpec("S03.report-strapline", "HTML", frozenset({"SETTLED_COUNT", "RATE"}),
                "cdfc.surface.render.render_report"),
    SurfaceSpec("S04.report-band", "HTML", frozenset({"SETTLED_COUNT"}),
                "cdfc.surface.band.band_segments"),
    SurfaceSpec("S05.report-openitems", "HTML", frozenset({"NONE"}),
                "cdfc.surface.openitems.standing_open_items"),
    SurfaceSpec("S06.cli-version", "STDOUT", frozenset({"NONE"}), "cdfc.cli.main"),
)

# --- the number registry: THE DENOMINATOR OF "renders every number". APPEND-ONLY. ------
REQUIRED_NUMBERS: Final[tuple[NumberSpec, ...]] = (
    NumberSpec("settledFraction.settled.passed",
               lambda r: f"{int(r.fraction.settled.passed):,}", ("S04.report-band",)),
    NumberSpec("settledFraction.settled.failed",
               lambda r: f"{int(r.fraction.settled.failed):,}",
               ("S02.report-hero", "S04.report-band")),
    NumberSpec("settledFraction.unsettled.indeterminate",
               lambda r: f"{int(r.fraction.unsettled.indeterminate):,}", ("S04.report-band",)),
    NumberSpec("settledFraction.unsettled.notRun",
               lambda r: f"{int(r.fraction.unsettled.notRun):,}", ("S04.report-band",)),
    NumberSpec("settledFraction.unsettled.noPredicate",
               lambda r: f"{int(r.fraction.unsettled.noPredicate):,}", ("S04.report-band",)),
    NumberSpec("settledFraction.unsettled.error",
               lambda r: f"{int(r.fraction.unsettled.error):,}", ("S04.report-band",)),
    NumberSpec("settledFraction.inScope",
               lambda r: f"{int(r.fraction.inScope):,}",
               ("S02.report-hero", "S03.report-strapline")),
    NumberSpec("settledFraction.cellsTotal",
               lambda r: f"{int(r.fraction.cellsTotal):,}", ("S03.report-strapline",)),
)


def live_surfaces() -> tuple[SurfaceSpec, ...]:
    """The gate's DENOMINATOR — retired rows excluded."""
    return tuple(s for s in SURFACES if not s.retired)


def scanned_surfaces() -> tuple[SurfaceSpec, ...]:
    """The SCAN set — retired rows INCLUDED.

    A surface we gave up on auditing is not a surface we gave up on prohibiting an all-clear on.
    """
    return SURFACES


@dataclass(frozen=True, slots=True)
class FfrCell:
    text: str
    digits: bool


UNINFORMATIVE: Final[str] = "uninformative"


def render_ffr(q: Any | None) -> FfrCell:
    """A false-failure rate, or the refusal to print one. **THREE uninformative cases, not one.**

    (a) there is no qualification row at all;
    (b) the corpus provenance is `SELF-AUTHORED`;
    (c) **the corpus is not computed-independent of the predicate** — the COMPUTED field, true
        whenever the generator's import closure meets the predicate's evaluation closure, or the
        predicate's `read_keys` intersect the corpus's `computed_cells`.

    **(c) is the one that matters.** A clean corpus whose derived cells are computed by the same
    evaluator an arithmetic predicate re-checks makes that predicate's false-failure rate **zero by
    construction, regardless of its quality** — and the generator is deterministic from a seed, so
    the `n ≥ 189` that buys `BLOCKING` costs one command. This function is the last place that can
    refuse to print it, and the refusal must not be keyed on the provenance LABEL alone.

    **There is no code path here that formats a float in any of the three cases.**
    """
    if q is None:
        return FfrCell(UNINFORMATIVE, False)
    provenance = str(
        getattr(q, "corpus_provenance", None)
        or getattr(getattr(q, "g4", None), "corpus_provenance", "")
    ).upper()
    if not provenance or "SELF-AUTHORED" in provenance:
        return FfrCell(UNINFORMATIVE, False)
    independent = (
        getattr(q, "clean_corpus_independent_of_predicate", None)
        if getattr(q, "clean_corpus_independent_of_predicate", None) is not None
        else getattr(getattr(q, "g4", None), "clean_corpus_independent_of_predicate", None)
    )
    if independent is not True:
        return FfrCell(UNINFORMATIVE, False)
    rate = getattr(q, "false_failure_rate", None)
    if rate is None:
        return FfrCell(UNINFORMATIVE, False)
    # Reached only when all three preconditions hold. `n` travels with the rate, always.
    n = getattr(q, "n", None) or getattr(getattr(q, "g4", None), "n", None)
    return FfrCell(f"{rate} of {n}" if n else str(rate), True)
