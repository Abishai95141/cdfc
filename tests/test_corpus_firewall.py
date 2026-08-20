"""P8-B1 — the corpus firewall, mechanised wherever the procedure leaves a trace.

**F16 — the contamination grep cannot run inside the firewall it tests.** `test_corpus_is_not_importable`
asserts that nothing under `src/` or `tests/` reads the corpus except through
`fixtures/corpus_manifest.json`; a grep of the corpus TREE for predicate ids would require that
tree checked out beside the predicate set — **which is the contamination the firewall exists to
prevent**. So the grep runs in the corpus repository's own CI over its own tree and publishes a
SIGNED result whose digest enters the manifest; the main repo asserts the digest and never sees the
tree.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

MANIFEST = REPO / "fixtures" / "corpus_manifest.json"
BRIEF = REPO / "corpus" / "blind-fill" / "FILL-BRIEF.md"
SLICES = REPO / "corpus" / "blind-fill" / "SLICES.md"

SEVEN_KEYS = (
    "repo_url", "commit_sha", "manifest_sha256", "brief_sha256", "slices_sha256",
    "person_a_kind", "contamination_result_sha256",
)


def test_contract__corpus_manifest_shape():
    """All SEVEN keys. A missing `brief_sha256`, `slices_sha256` or
    `contamination_result_sha256` fails the build — **absent is not the same as null**: `null` with
    a reason is a declared state, and a missing key is a section nobody wrote."""
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    missing = [k for k in SEVEN_KEYS if k not in doc]
    assert not missing, f"fixtures/corpus_manifest.json is missing {missing}"
    assert doc["person_a_kind"], "person_a_kind renders wherever the FFR renders; it is never empty"


# The corpora a verdict path MAY name. `corpus/blind-fill` is the one this firewall
# quarantines -- it is the withheld ground truth. `corpus/instruments` is P7's pinned
# statute and `corpus/rules` is A2's pinned REGULATOR-PUBLISHED rule set: both are public
# artefacts with published digests, and naming them is the opposite of contamination.
# PUBLIC corpora: artefacts a regulator PUBLISHES, which carry no blind-fill answer and are
# meant to be read directly. `corpus/regulators` joined on 20 Aug 2026 with FinCEN's BSA XML
# schema (D2). Each addition is a deliberate line here, so the exemption list stays readable —
# the failure this rule already had once was two undocumented exemptions that between them
# covered every subdirectory `corpus/` had.
PUBLIC_CORPORA = ("corpus/instruments", "corpus/rules", "corpus/regulators")


def test_corpus_is_not_importable():
    """**RULE 1.** Nothing under `src/` or `tests/` reads the corpus except through
    `fixtures/corpus_manifest.json`. Asserted by AST over every module, not by convention.

    **THE RULE EXEMPTED THE CORPUS IT EXISTS FOR.** The predicate carried an undocumented
    `"corpus/blind-fill" not in v` clause — and `corpus/` has exactly two subdirectories, both
    exempted — so the offenders list was empty BY EXEMPTION rather than by the rule holding.
    Demonstrated: appending `CONTAMINATION = "corpus/blind-fill/fills/fill_001.json"` to
    `src/cdfc/qualify/wilson.py`, which is precisely what RULE 1 forbids, left the test PASSING.
    Neither exemption carried a comment, and none of `docs/GATE-CHANGES.md`, `D-P8-01` or the
    module docstring recorded them.

    What is exempt now, and why, is per-FILE and named — never a path substring:

      - `tools/corpus/*` BUILDS the corpus. A builder that may not name its own output directory
        cannot exist, and this is the boundary the rule is about: `src/` EVALUATES and must not
        see it; `tools/corpus/` PRODUCES it.
      - `mask_vs_filler.py` reads the manifest by design (F36).
      - this file names the paths it forbids, and a firewall that trips on its own rule statement
        gets "fixed" by deleting the rule statement.

    `corpus/instruments` is P7's instrument store — a different corpus, with its own rules — and
    it stays out of scope by NAME rather than by a substring that also swallowed blind-fill.
    """
    offenders: list[str] = []
    for root in ("src", "tests", "tools"):
        for f in sorted((REPO / root).rglob("*.py")):
            rel = f.relative_to(REPO).as_posix()
            if f.name in ("mask_vs_filler.py", "test_corpus_firewall.py"):
                continue
            if rel.startswith("tools/corpus/"):
                continue
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                    continue
                v = node.value
                if v.startswith("corpus/") and not v.startswith(PUBLIC_CORPORA):
                    offenders.append(f"{rel}: {v!r}")
    assert not offenders, (
        "a module reaches the blind-fill corpus directly rather than through "
        f"fixtures/corpus_manifest.json: {offenders}"
    )


def test_corpus__rule_one_can_actually_fail():
    """**THE CONTROL THAT DID NOT EXIST.** There was no injector and no negative control for RULE
    1 at all, so the exemption that disabled it was invisible for a whole phase. This plants the
    contamination the rule forbids and asserts the predicate reports it."""
    forbidden = "corpus/blind-fill/fills/fill_001.json"
    allowed = "corpus/instruments/x.json"

    def flags(value: str) -> bool:
        return value.startswith("corpus/") and not value.startswith(PUBLIC_CORPORA)

    assert flags(forbidden), "a src module naming the blind-fill corpus must be an offender"
    assert not flags(allowed), "the instrument store is a different corpus and stays out of scope"


def test_corpus__brief_and_slices_are_hashed_and_published():
    """**RULES 3 and 4.** Both exist NOW, before any workbook is filled, so the ancestry the
    firewall rests on holds by construction rather than by discipline."""
    assert BRIEF.is_file() and SLICES.is_file()
    assert "HASHED AND PUBLISHED BEFORE THE FIRST WORKBOOK IS FILLED" in BRIEF.read_text(encoding="utf-8")
    assert "DECLARED BEFORE THE CORPUS EXISTS" in SLICES.read_text(encoding="utf-8")


def test_corpus__brief_predates_any_filled_workbook():
    """**RULE 3, from the COMMIT GRAPH rather than from an assertion.**

    There is no filled workbook, so the test asserts the two things that make the rule checkable
    the day there is one: the brief is committed, and no filled workbook exists yet. When one does,
    this test compares the two commits with `git merge-base --is-ancestor`.
    """
    import subprocess

    r = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(BRIEF.relative_to(REPO))],
                       cwd=REPO, capture_output=True, text=True)
    brief_commit = r.stdout.strip()
    filled = sorted((REPO / "corpus" / "blind-fill").glob("filled/*.xlsx"))
    if not filled:
        assert brief_commit or not (REPO / ".git").exists(), (
            "the brief must be committed BEFORE the first workbook; it is not committed at all"
        )
        return
    first = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "--", str(filled[0].relative_to(REPO))],
        cwd=REPO, capture_output=True, text=True).stdout.split()[0]
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", brief_commit, first],
                         cwd=REPO, capture_output=True)
    assert anc.returncode == 0, (
        "the fill brief's commit is not an ancestor of the first filled workbook's. A commitment "
        "made after seeing the result is not a commitment."
    )


def test_corpus__person_a_kind_renders_with_the_ffr():
    """**RULE 5.** The fallback is weaker than a human and the record says so, wherever the rate
    renders."""
    from cdfc.qualify.corpus.provenance import person_a_kind_note

    assert person_a_kind_note("human") == ""
    note = person_a_kind_note("model-instance")
    assert "weaker than a human" in note and "model-instance" in note
    doc = (REPO / "docs" / "measurements" / "P8-ffr.md").read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["person_a_kind"] in doc or "D-P8-01" in doc, (
        "the FFR surface must carry what produced the corpus"
    )


def test_corpus__n_is_filings_not_cells():
    """**RULE 7 / NC-Q08d.** The exchangeable unit is the FILING. `n = F`, never `n = 3,747·F` —
    cells within one filing are not independent draws, and treating them as such would shrink every
    interval by a factor of sixty."""
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert doc["n"] == len(doc["filings_sha256"])
    assert doc["n"] < 3_747, "n is a count of filings; a number this large is a count of cells"
    from cdfc.qualify.g4_ffr import CleanCorpus

    src = (REPO / "src/cdfc/qualify/g4_ffr.py").read_text(encoding="utf-8")
    assert "FILINGS. never cells." in src
    assert "n" in CleanCorpus.__dict__ or hasattr(CleanCorpus, "n")


def test_corpus__the_blind_fill_corpus_is_declared_absent_not_forgotten():
    """D-P8-01 is a decision with a consequence, not a gap. The manifest says so and the FFR
    surface says so."""
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert doc["brief_sha256"] is None and doc["contamination_result_sha256"] is None
    assert "D-P8-01" in doc["person_a_kind"]
    assert doc["n_non_synthetic"] == 0
    decision = (REPO / "docs/decisions/D-P8-01-no-blind-fill-corpus.md").read_text(encoding="utf-8")
    assert "BLOCKING` count is `0` by construction" in decision


def test_corpus__mask_check_publishes_two_integers_or_says_it_did_not():
    """**F36.** The test asserts the two integers are COMPUTED AND PUBLISHED, not that they are
    zero. Today they are `NOT MEASURED`, and that is published as their value."""
    sys.path.insert(0, str(REPO / "tools"))
    doc = (REPO / "docs/measurements/P8-mask-external-check.md").read_text(encoding="utf-8")
    assert "cells a filler wrote OUTSIDE the mask" in doc
    assert "cells inside the mask no filler wrote" in doc
    assert "3747" in doc.replace(",", "") or "3,747" in doc

    from corpus.mask_vs_filler import compare

    outside, unwritten = compare(frozenset({"S!A1", "S!B1"}), frozenset({"S!B1", "S!C1"}))
    assert (outside, unwritten) == (1, 1), "the comparison itself is exercised, not just its report"
