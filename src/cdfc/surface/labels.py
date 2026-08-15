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
