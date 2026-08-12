"""P5-B1 — F3: binding a filing to a pinned template by STRUCTURAL fingerprint.

**Formula content is deliberately not in the fingerprint.** A filer who overwrote a formula cell
with a literal must fail a PREDICATE, not the BINDING — because a binding failure says *we cannot
tell what form this is* and produces no findings at all, while the overwrite is exactly the defect
`TEMPLATE_DIFF` exists to name. Putting formulas in the fingerprint would convert the flagship
finding into a refusal to look.

**Unbound ESCALATES into BOTH vocabularies.** `run_state = INVALID(invalid.template_unbound)` at
the run level AND every cell carries `NOT_RUN(not_run.template_unbound)` at the item level. Audit
§V.7.3: they are not alternatives. A report carrying one and not the other has lost either the
location or the run-level consequence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cdfc.schema.fingerprint import structural_projection


@dataclass(frozen=True, slots=True)
class Bound:
    template_sha256: str
    schema: Any                      # TemplateSchema
    fingerprint: str


@dataclass(frozen=True, slots=True)
class Unbound:
    fingerprint: str
    # (template_sha256, number of projection facets that matched) — descending. A refusal that
    # cannot say WHAT IT WAS NEAREST TO sends the filer to guess which form they filed.
    nearest: tuple[tuple[str, int], ...]

    def explain(self) -> str:
        if not self.nearest:
            return (
                "this filing matches no pinned template, and the catalogue is empty. Nothing was "
                "compared, so 'unbound' here says nothing about the filing."
            )
        best, score = self.nearest[0]
        return (
            f"this filing matches no pinned template. Nearest is {best[:8]} on {score} of "
            f"{FACETS} structural facets. It is NOT bound to it: a partial structural match is "
            "how a filing gets checked against the wrong form."
        )


# The facets compared, named once. Formula content is not among them, and that is the point.
FACET_NAMES: tuple[str, ...] = ("sheets", "merged_ranges", "defined_names", "unlocked_mask")
FACETS: int = len(FACET_NAMES)


@dataclass(frozen=True, slots=True)
class TemplateCatalogue:
    """The pinned blanks a filing may bind to. Built from the vendored corpus, never from a filing."""

    entries: Mapping[str, Mapping[str, Any]]     # template_sha256 -> structural projection
    schemas: Mapping[str, Any] = None            # type: ignore[assignment]

    @staticmethod
    def from_corpus(corpus: Path, schemas: Mapping[str, Any] | None = None) -> TemplateCatalogue:
        import hashlib

        entries = {}
        for p in sorted(corpus.glob("*.xlsx")):
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            entries[digest] = structural_projection(p)
        return TemplateCatalogue(entries=entries, schemas=dict(schemas or {}))

    def fingerprints(self) -> dict[str, str]:
        from cdfc.canon import digest as _digest

        return {sha: _digest(proj) for sha, proj in self.entries.items()}


def project(blob: Path) -> Mapping[str, Any]:
    return structural_projection(blob)


def _score(a: Mapping[str, Any], b: Mapping[str, Any]) -> int:
    return sum(1 for k in FACET_NAMES if a.get(k) == b.get(k))


def bind_template(blob: Path, catalogue: TemplateCatalogue) -> Bound | Unbound:
    """Exact structural match, or `Unbound` naming what it was nearest to."""
    from cdfc.canon import digest as _digest

    proj = project(blob)
    fp = _digest(proj)
    for sha, pinned in catalogue.entries.items():
        if _digest(pinned) == fp:
            return Bound(
                template_sha256=sha,
                schema=(catalogue.schemas or {}).get(sha),
                fingerprint=fp,
            )
    nearest = sorted(
        ((sha, _score(proj, pinned)) for sha, pinned in catalogue.entries.items()),
        key=lambda t: (-t[1], t[0]),
    )
    return Unbound(fingerprint=fp, nearest=tuple(nearest[:3]))
