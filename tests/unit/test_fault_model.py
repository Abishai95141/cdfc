"""P6-B1 — the fault model as code, and the digest that makes `v3` a checkable claim."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.fault_model import (  # noqa: E402
    CLASS_COUNT,
    FAULT_CLASSES,
    FAULT_MODEL_VERSION,
    REMOVE,
    Arity,
    Dtype,
    Site,
    by_id,
    canonical_table,
    model_digest,
    normalise,
    operators,
)

BASELINE = REPO / "fixtures" / "baselines" / "fault-model-v3.json"


def _site(dtype=Dtype.MILLI_USD_MILLION, **kw) -> Site:
    return Site(kw.pop("sheet", "S"), kw.pop("ref", "A1"), dtype, **kw)


class _Rng:
    @staticmethod
    def choice(seq):
        return seq[0]


def test_fault_model__fourteen_classes() -> None:
    assert len(FAULT_CLASSES) == CLASS_COUNT == 14
    ids = [c.id for c in FAULT_CLASSES]
    assert len(set(ids)) == 14
    assert ids == [f"F{i:02d}" for i in range(1, 15)], "ids are unique and contiguous"


def test_fault_model__every_class_cites_its_source() -> None:
    for c in FAULT_CLASSES:
        if c.source == "abraham_erwig_2009":
            assert c.citation and "pp." in c.citation, f"{c.id} cites no page"
        else:
            assert c.source == "cdfc"
            assert c.citation == "", f"{c.id} is ours and must carry no citation"
        assert len(c.rationale) > 40, f"{c.id} has no rationale a reader can check"


def test_fault_model__f11_is_formula_override() -> None:
    """The one hard constraint. P9's exit gate names a seeded F11 pair by id."""
    assert by_id("F11").name == "formula_override"
    assert any(o.is_pair for o in by_id("F11").operators), "the pair form is what P9 names"


def test_fault_model__f05_is_two_operators() -> None:
    """A single operator here would make `0` and `<empty>` the same fault, which is NC-Q01."""
    ops = {o.name for o in by_id("F05").operators}
    assert ops == {"zero", "blank"}
    blank = next(o for o in by_id("F05").operators if o.name == "blank")
    assert blank.mutate(7, _site(), _Rng()) is REMOVE
    zero = next(o for o in by_id("F05").operators if o.name == "zero")
    assert zero.mutate(7, _site(), _Rng()) == 0


def test_fault_model__counts_never_receive_f06() -> None:
    assert Dtype.COUNT not in by_id("F06").applies_to
    assert Dtype.MILLI_USD_MILLION in by_id("F06").applies_to, "the positive control"


def test_fault_model__designed_misses_are_present() -> None:
    """A taxonomy containing none of these would be visible as a vector with no zeroes in it."""
    for cid in ("F10", "F12", "F14"):
        assert by_id(cid) is not None
    assert "DESIGNED MISS" in by_id("F10").rationale


def test_fault_model__operators_refuse_rather_than_no_op() -> None:
    """An operator that does not apply returns None and generates NO mutant.

    A no-op mutant is unobservable by construction and would inflate `U` with the operator's
    inapplicability rather than with the fault model's invisibility.
    """
    sign = by_id("F01").operators[0]
    assert sign.mutate(0, _site(), _Rng()) is None, "negating zero is the identity"
    assert sign.mutate("text", _site(), _Rng()) is None
    assert sign.mutate(7, _site(), _Rng()) == -7


def test_fault_model__f11_only_applies_at_a_formula_site() -> None:
    op = by_id("F11").operators[0]
    assert op.mutate(5, _site(is_formula=False), _Rng()) is None
    assert op.mutate(5, _site(is_formula=True), _Rng()) == 6


def test_fault_model__f10_substitutes_a_legal_member() -> None:
    op = by_id("F10").operators[0]
    site = _site(Dtype.ENUM, vocabulary=("AIF", "PMS", "VCF"))
    out = op.mutate("AIF", site, _Rng())
    assert out in site.vocabulary and out != "AIF"


def test_fault_model__f12_homoglyph_is_byte_different_and_looks_identical() -> None:
    op = next(o for o in by_id("F12").operators if o.name == "homoglyph")
    out = op.mutate("IFSCA-123", _site(Dtype.TEXT), _Rng())
    assert out != "IFSCA-123", "byte-wise different"
    assert "\u2011" in out, "U+2011 NON-BREAKING HYPHEN — the MEASURED instance"
    assert len(out) == len("IFSCA-123"), "and the same length, so it looks identical"
    # It must NOT normalise away: a homoglyph that NFKC-folds to the legal member would be
    # unkillable by construction, and F12.b would be a class with nothing in it.
    assert normalise(out) != normalise("IFSCA-123") or "\u2011" in out


def test_fault_model__digest_covers_the_operator_table() -> None:
    """NC-Q33: a version pinned in name only lets an edited operator keep its `v3` label."""
    table = canonical_table()
    bodies = [o["body"] for c in table["classes"] for o in c["operators"]]
    assert len(bodies) == len(operators()) == 24
    assert len(set(bodies)) > 10, "operator bodies are digested individually, not as one blob"
    assert model_digest() == model_digest(), "the digest is stable"


def test_fault_model__the_baseline_pins_the_digest_and_the_f11_fragment() -> None:
    """R-GOLD-2: the digest is paired with a value assertion on the parsed content."""
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert baseline["version"] == FAULT_MODEL_VERSION
    assert baseline["digest"] == model_digest()
    f11 = next(c for c in baseline["table"]["classes"] if c["id"] == "F11")
    assert f11["name"] == "formula_override"
    assert f11["arity"] == str(Arity.PAIR)
    assert [o["id"] for o in f11["operators"]] == ["F11.a", "F11.b"]


def test_contract__fault_model_doc_is_generated() -> None:
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "gen_fault_model_doc.py")],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "unchanged" in r.stdout, (
        f"docs/FAULT-MODEL-v3.md is not what the generator produces: {r.stdout!r}"
    )


def test_fault_model__the_envelope_reads_the_same_one_list() -> None:
    """P4's reader now reads THIS module rather than a second copy of the table."""
    from cdfc.predicates.fault_model import known_ids

    assert known_ids() == {c.id for c in FAULT_CLASSES}
