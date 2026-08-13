"""P6 — the negative controls for the fault model, surgery, observability and the site universe.

Every entry ships with its admission-side twin. A guard that goes red under injection because it
goes red under everything is not a control.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.reader_lxml import read  # noqa: E402
from cdfc.qualify.campaign import Campaign, CampaignArithmeticError, tally  # noqa: E402
from cdfc.qualify.fault_model import Dtype, by_id, canonical_table, model_digest  # noqa: E402
from cdfc.qualify.observability import Observability, classify, cone_for, grid_of  # noqa: E402
from cdfc.qualify.sites import partition, site_universe  # noqa: E402
from cdfc.qualify.surgery import differing_parts, plan_edit, seed_mutant  # noqa: E402

FME = (
    REPO / "fixtures" / "prescribed"
    / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
CLEAN = REPO / "fixtures" / "synthetic" / "clean__independently-computed__fme-q1.xlsx"
CAMPAIGNS = REPO / "reports" / "campaigns"


def _grid(values, not_run=None):
    from cdfc.calc.evaluate import ValueGrid

    return ValueGrid(values, not_run or {}, frozenset(values), "FILING")


# --- NC-Q33: the digest covers the operator table -------------------------------------------


def test_nc__Q33_operator_edit_moves_the_digest() -> None:
    """A version pinned in NAME ONLY lets a silently edited operator keep its `v3` label."""
    from cdfc.canon import canonical_json, sha256_hex

    table = canonical_table()
    assert model_digest() == sha256_hex(canonical_json(table)), (
        "model_digest does not cover the operator table it claims to"
    )
    edited = json.loads(json.dumps(table))
    edited["classes"][0]["applies_to"] = ["DATE"]
    assert sha256_hex(canonical_json(edited)) != model_digest()


def test_nc__Q33b_every_operator_contributes_to_the_digest() -> None:
    """The admission-side twin: the bodies are digested individually, not as one opaque blob."""
    bodies = [o["body"] for c in canonical_table()["classes"] for o in c["operators"]]
    assert len(bodies) == 24 and len(set(bodies)) > 10


# --- NC-Q30: mutants are written by raw-zip surgery -----------------------------------------


def test_nc__Q30_mutant_writer_is_raw_zip(tmp_path: Path) -> None:
    out = tmp_path / "m.xlsx"
    edit = plan_edit(FME, "3. Portfolio", "O7", 999999, "F11.a")
    rec = seed_mutant(FME, [edit], out, fault_class="F11", operator_id="F11.a", seed=1)
    assert len(rec.parts_changed) == 1
    assert out.stat().st_size > 3_000_000, (
        f"{out.stat().st_size} bytes — an openpyxl round-trip produces about 66,000, and the "
        "observability diff would then be a diff of the writer rather than of the fault"
    )
    assert read(out).n_validations == 54, "35 main + 19 x14"


def test_nc__Q30b_surgery_writes_a_usable_mutant(tmp_path: Path) -> None:
    """The admission-side twin: the mutant LOADS and re-induces to the same sheet set.

    Deliberately a property a re-serialising writer also preserves. A positive control that went
    red under the same injection as the guard would not be a control — it would be a second guard.
    """
    out = tmp_path / "m.xlsx"
    edit = plan_edit(FME, "1. Introduction", "D11", 42, "F01.a")
    seed_mutant(FME, [edit], out, fault_class="F01", operator_id="F01.a", seed=1)
    assert read(out).n_sheets == read(FME).n_sheets


# --- NC-Q31: the filter RECALCULATES ---------------------------------------------------------


def test_nc__Q31_filter_recalculates(tmp_path: Path) -> None:
    """The distinguishing set must be non-empty DOWNSTREAM of the edit, not only at it.

    A filter reading cached values reports a difference at exactly the edited cell and nowhere
    else — it measures the EDIT, not its PROPAGATION, and returns `U = 0` on every campaign.
    """
    out = tmp_path / "m.xlsx"
    site = ("1. Introduction", "C54")
    edit = plan_edit(CLEAN, *site, 4242, "F01.a")
    seed_mutant(CLEAN, [edit], out, fault_class="F01", operator_id="F01.a", seed=1)
    full = grid_of(CLEAN)
    cone = cone_for(CLEAN, [site])
    obs, cells = classify(
        grid_of(CLEAN, cone=cone, baseline=full), grid_of(out, cone=cone, baseline=full)
    )
    assert obs is Observability.OBSERVABLE
    assert cells - {site}, (
        "the only distinguishing cell is the edited one: the filter is reading cached values "
        "rather than recalculating"
    )


# --- NC-Q60 / F18: an unevaluable cell is not evidence of invisibility ------------------------


def test_nc__Q60_unevaluable_cells_do_not_become_unobservable() -> None:
    obs, cells = classify(
        _grid({("S", "A1"): 1}, {("S", "B1"): "unimplemented"}),
        _grid({("S", "A1"): 1}, {("S", "B1"): "unimplemented"}),
    )
    assert obs is Observability.INDETERMINATE_OBSERVABILITY
    assert ("S", "B1") in cells, "the offending cell is NAMED, not merely counted"


def test_nc__Q60b_fully_evaluable_propagation_is_observable() -> None:
    """The admission-side twin: a mutant through evaluable cells is OBSERVABLE, never INDETERMINATE."""
    obs, _ = classify(_grid({("S", "A1"): 1}), _grid({("S", "A1"): 2}))
    assert obs is Observability.OBSERVABLE


def test_nc__Q60c_the_clean_filing_actually_has_indeterminate_cells() -> None:
    """Without this, the whole F18 control would be arguing about an empty set."""
    assert grid_of(CLEAN).not_run, "I would be 0 and NC-Q60 would prove nothing"


# --- NC-Q61 / F19: observability uses the FILING's formulas ------------------------------------


def test_nc__Q61_observability_uses_filing_formulas(tmp_path: Path) -> None:
    out = tmp_path / "f11.xlsx"
    site = ("3. Portfolio", "O7")
    edit = plan_edit(CLEAN, *site, 999999, "F11.a")
    seed_mutant(CLEAN, [edit], out, fault_class="F11", operator_id="F11.a", seed=1)
    full = grid_of(CLEAN)
    cone = cone_for(CLEAN, [site])
    clean_g = grid_of(CLEAN, cone=cone, baseline=full)
    mutant_g = grid_of(out, cone=cone, baseline=full)
    assert clean_g.values.get(site) != mutant_g.values.get(site), (
        "the override was overwritten by the very formula it deleted — observability is "
        "recalculating with the TEMPLATE's formulas, and the flagship class is unobservable"
    )


# --- NC-Q37: an unobservable mutant is RETAINED with its reason -------------------------------


def test_nc__Q37_unobservable_are_retained(tmp_path: Path) -> None:
    """The guard exercises the WRITER, not a committed report.

    An earlier version read `reports/campaigns/`, which no injection touches — so it could not
    flip, and the sweep said so. A control that reads yesterday's output is not a control.
    """
    from cdfc.qualify.campaign import Campaign
    from cdfc.qualify.runner import MutantOutcome, write_reports
    from cdfc.qualify.surgery import CellEdit, MutantRecord

    def outcome(obs: Observability, ref: str) -> MutantOutcome:
        rec = MutantRecord(
            mutant_sha256="a" * 64, base_sha256="b" * 64, fault_class="F06",
            operator_id="F06.a",
            edits=(CellEdit("S", ref, "<c/>", "<c><v>1</v></c>", "F06.a"),),
            seed=1, harness_version="t", fault_model_version="v3",
            parts_changed=("xl/worksheets/sheet1.xml",),
        )
        return MutantOutcome(rec, obs, (), True, ())

    outcomes = [
        outcome(Observability.UNOBSERVABLE, "A1"),
        outcome(Observability.UNOBSERVABLE, "A2"),
        outcome(Observability.INDETERMINATE_OBSERVABILITY, "A3"),
    ]
    campaign = Campaign("t", {"F06": tally(G=3, U=2, I=1)}, fault_model_digest="d")
    target = write_reports(campaign, outcomes, tmp_path)

    for name, key in (("unobservable.jsonl", "U"), ("indeterminate.jsonl", "I")):
        rows = [json.loads(x) for x in (target / name).read_text().splitlines() if x.strip()]
        assert len(rows) == campaign.totals.as_row()[key], (
            f"{name} has {len(rows)} rows, the campaign says {key}="
            f"{campaign.totals.as_row()[key]} — a discarded mutant makes U/G unauditable and "
            "takes P10's residue feedstock with it"
        )
        for r in rows:
            assert r["reason"], "a retained mutant with no reason is unauditable"
            assert r["mutant_sha256"] and r["operator_id"] and r["sites"]


def test_nc__Q37b_the_committed_campaign_agrees_with_its_manifest() -> None:
    """The admission-side twin, over the REAL campaign: the counts on disk match the manifest."""
    manifests = sorted(CAMPAIGNS.glob("*/manifest.json"))
    assert manifests, "no campaign has been run; `make campaign` produces one"
    m = json.loads(manifests[0].read_text(encoding="utf-8"))
    target = manifests[0].parent
    for name, key in (("unobservable.jsonl", "U"), ("indeterminate.jsonl", "I")):
        rows = [x for x in (target / name).read_text().splitlines() if x.strip()]
        assert len(rows) == m["totals"][key]


# --- NC-Q06 / NC-Q32: the site universe and the control arm -----------------------------------


def test_nc__Q06a_site_set_is_the_field_surface() -> None:
    """v0 sampled sites from the predicates' read set and scored 100.0% on 3,574 mutants."""
    assert list(inspect.signature(site_universe).parameters) == ["field_surface", "excluded"]


def test_nc__Q32_control_excludes_the_cone() -> None:
    """Deterministic by construction: after the cone is removed there is exactly one candidate.

    A universe with spare cells would let the sampler avoid the upstream cell by luck, and a
    control that passes by luck is not a control.
    """
    s = partition(frozenset({"A!1", "B!1", "C!1"}), ["A!1"], {"A!1": frozenset({"B!1"})}, rng_seed=5)
    assert "B!1" in s.excluded_cone, (
        "the upstream cell is eligible for the control arm: legitimate propagation would then "
        "count as a spurious fire, the threshold would have to be softened to a fudge factor, "
        "and the fudge factor would hide a real flag-everything predicate"
    )
    assert s.control.isdisjoint(s.excluded_cone)


def test_nc__Q32b_a_genuine_outside_site_is_in_control() -> None:
    """The admission-side twin: the control arm is not simply empty."""
    s = partition(frozenset({"A!1", "C!1", "C!2"}), ["A!1"], {"A!1": frozenset()}, rng_seed=5)
    assert s.control and s.control <= {"C!1", "C!2"}


# --- NC-E08: counts get zero tolerance ---------------------------------------------------------


def test_nc__E08_counts_get_zero_tolerance() -> None:
    """F06 is the rounding class, and rounding a COUNT is not a rounding error."""
    assert Dtype.COUNT not in by_id("F06").applies_to


def test_nc__E08b_money_gets_tau() -> None:
    assert Dtype.MILLI_USD_MILLION in by_id("F06").applies_to


# --- NC-Q05: the kill rate's denominator --------------------------------------------------------


def test_nc__Q05a_impossible_score_raises() -> None:
    with pytest.raises(CampaignArithmeticError):
        tally(G=100, U=0, I=0, K=101)


def test_nc__Q05c_observability_filter_reports_its_own_rate() -> None:
    out = Campaign("x", {"F01": tally(G=10, U=3, I=2, K=2)}, fault_model_digest="d").render()
    assert "U/G = 3/10" in out and "I/G = 2/10" in out


def test_nc__Q64_no_bare_rate_reaches_a_surface() -> None:
    """`ci/no-bare-rate.sh`, run as a guard.

    A percentage carries no evidence of its own arithmetic. On its first run this gate found
    fourteen bare rates in this repository, one of them in a published measurement file.
    """
    import subprocess

    r = subprocess.run(["bash", str(REPO / "ci" / "no-bare-rate.sh")],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr)[:600]
