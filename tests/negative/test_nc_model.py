"""P12's negative controls — and they guard a different thing from every phase below.

**P12 produces no verdict.** It produces a number and an ORDERING: `k of 20`, and the fact that the
criterion which decides what `k` means was written, hashed and committed before the model ran.
So these controls are not about a filing being wrongly passed. They are about whether the criterion
could have been written to fit the result — and about the four ways a denominator, a baseline, a
threshold or a retry could quietly move the number in our favour.

Every entry here has an **admission-side positive control**, because a pre-registration checker that
refuses everything passes every rejection-side test while making the experiment unrunnable.
"""

from __future__ import annotations

import ast
import inspect
import shutil
import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment import decide as decide_mod  # noqa: E402
from cdfc.experiment import power, prereg  # noqa: E402
from cdfc.experiment.draw import Obligation, Pool, TableOracle, draw  # noqa: E402
from cdfc.experiment.funnel import planned_count  # noqa: E402

PREREG = REPO / "experiments" / "E6" / "PREREGISTRATION.md"
LOCK = REPO / "experiments" / "E6" / "preregistration.lock.json"


def _pool(n: int = 400) -> Pool:
    return Pool(
        obligations=tuple(
            Obligation(ordinal=i, reg_no=i, sub_clause=(), quote=f"{i} shall x",
                       char_span=(i * 10, i * 10 + 8), source_sha256="s")
            for i in range(n)
        ),
        excluded=(), source_sha256="s", chapters=("c",),
    )


def _oracle(n: int = 400, every: int = 6) -> TableOracle:
    return TableOracle(
        assignment={i: ("A" if i % every == 0 else "B") for i in range(n)},
        assigner={i: "a.person" for i in range(n)},
    )


# --- NC-M02 — the pre-registration is edited after the run ------------------------------


def test_nc__M02a_h0_mismatch_fails_the_build() -> None:
    """The lock's `h0` is over the file's BYTES, and a moved threshold moves it.

    Under `PreregEditThreshold` the committed document says `RETAIN1 = 4` while the lock still
    records the hash of the document that said 6 — so this comparison is what turns an edit into
    a build failure rather than into a quieter criterion.
    """
    assert LOCK.is_file(), "there is no lock; this assertion would be vacuous"
    assert prereg._read(LOCK).h0 == prereg.h0_of(PREREG), (
        "the pre-registration on disk does not hash to the h0 in the lock. The criterion moved "
        "after it was fixed, and every number the experiment produces is now a number whose "
        "meaning was decided afterwards."
    )


def test_nc__M02b_the_committed_threshold_is_the_one_the_code_uses() -> None:
    """The document and the module must agree, in both directions.

    A threshold that lives only in code is outside the lock and editable without touching the
    hashed file; a threshold that lives only in the document enforces nothing.
    """
    from cdfc.experiment.criterion import assert_machine_evaluable

    declared = assert_machine_evaluable(PREREG)
    assert declared["RETAIN1"] == power.RETAIN1 == 6
    assert declared["DELETE1"] == power.DELETE1 == 2
    assert declared["RETAIN2"] == power.RETAIN2 == 12


def _synthetic_criterion(tmp_path: Path) -> Path:
    """A minimal lockable document, built FROM THE MODULE CONSTANTS rather than copied.

    The admission-side controls below must be independent of the committed pre-registration,
    because `PreregEditThreshold` edits exactly that file — and a positive control that read it
    would go red under the injector for the right reason, which still makes it the wrong control.
    A `flips: false` guard has to be green under the injection or it is not distinguishing a
    working lock from a broken one.
    """
    from cdfc.experiment.criterion import THRESHOLDS

    lines = []
    for name, (mod, attr) in sorted(THRESHOLDS.items()):
        lines.append(f"{name} = {getattr(__import__(mod, fromlist=[attr]), attr)}")
    doc = tmp_path / "P.md"
    doc.write_text(
        "# a synthetic criterion\n\n```cdfc-criterion\n" + "\n".join(lines) + "\n```\n",
        encoding="utf-8",
    )
    return doc


def test_nc__M02c_appending_an_artefact_hash_is_allowed(tmp_path: Path) -> None:
    """THE ADMISSION-SIDE CONTROL. The lock is append-only, **not frozen**.

    Without this, a lock that refused every write would satisfy both tests above while making the
    experiment impossible to run — which is the reject-everything gate this project keeps finding
    in other people's systems.
    """
    doc = _synthetic_criterion(tmp_path)
    lock_path = tmp_path / "lock.json"
    prereg.lock(doc, lock_path, committed_at="2026-08-15")
    prereg.append(lock_path, textsource_sha256="b" * 64)
    prereg.append(lock_path, exclusion_rule_sha256="c" * 64)
    after = prereg.append(lock_path, draw_sha256="a" * 64)
    assert after["draw_sha256"] == "a" * 64
    assert after.h0 == prereg.h0_of(doc), "appending moved h0"


# --- NC-M03 — the decidable fraction over a truncated denominator -----------------------


def test_nc__M03_decidable_fraction_uses_all_drawn() -> None:
    """`|drawn|` is `|A| + |B_all|`, never `|A| + |B_generated|`.

    Under `TruncateBDenominator` the generation cap becomes the denominator, so `|A|/|drawn|` rises
    from roughly 20/120 to 20/30. **The error is in the flattering direction**, which is what makes
    it the dangerous one: nobody re-derives a number that looks better than expected.
    """
    d = draw(_pool(), seed=20260815, strata=_oracle())
    a, drawn, excluded = d.decidable_fraction()
    assert a == len(d.stratum_a) == 20
    assert drawn == len(d.stratum_a) + len(d.stratum_b_all)
    assert len(d.stratum_b_all) > len(d.stratum_b_generated), (
        "this pool was built so the cap bites; if it does not, the control tests nothing"
    )
    assert drawn > a + len(d.stratum_b_generated), (
        "the drawn set has been truncated to the generation cap — NC-D01's mechanism applied to "
        "this phase's headline number"
    )
    assert excluded == 0


def test_nc__M03b_the_generation_cap_still_bites() -> None:
    """THE ADMISSION-SIDE CONTROL: the cap must still cap *generation*.

    Without it, "the cap never touches the denominator" would be satisfiable by removing the cap,
    which would send 90 Stratum-B obligations to the model at ten candidates each.
    """
    d = draw(_pool(), seed=20260815, strata=_oracle())
    assert len(d.stratum_b_generated) == 10


# --- NC-M04 — inverse-sampling estimates reported as if exact ---------------------------


def test_nc__M04a_both_estimators_are_reported_and_labelled() -> None:
    """Two numbers, and the unbiased one is strictly smaller.

    Drawing until a fixed number of successes is inverse sampling, under which `a/n` is biased
    **upward**. `NaiveRatioEstimator` returns the naive ratio under both labels, which publishes
    the biased figure as the corrected one.
    """
    naive, unbiased = power.inverse_sampling_estimate(20, 101)
    assert naive == Fraction(20, 101)
    assert unbiased == Fraction(19, 100)
    assert unbiased < naive, (
        "the unbiased estimator is not below the naive one, so the bias correction is doing "
        "nothing and the label is the only thing that changed"
    )


def test_nc__M04b_interval_carries_the_approximate_label() -> None:
    """A Wilson interval is **not exact** under inverse sampling, and the label says so."""
    assert "APPROXIMATE" in power.INVERSE_SAMPLING_LABEL
    assert "inverse sampling" in power.INVERSE_SAMPLING_LABEL
    assert "not exact" in power.INVERSE_SAMPLING_LABEL


# --- NC-M10 — retry ----------------------------------------------------------------------


def test_nc__M10a_retry_is_impossible_not_merely_banned() -> None:
    """No `attempt` parameter anywhere on the path, and the client refuses a non-zero retry count.

    Either alone is a convention. Together they are a rule: there is no call site that takes an
    attempt count and no configuration that permits one.
    """
    from cdfc.experiment.client import MAX_RETRIES, ClientConfig
    from cdfc.experiment.run import propose

    assert MAX_RETRIES == 0
    params = " ".join(inspect.signature(propose).parameters)
    for word in ("attempt", "retry", "retries"):
        assert word not in params, f"propose() takes a {word} parameter"
    with pytest.raises(ValueError):
        ClientConfig(max_retries=1)


def test_nc__M10b_a_malformed_candidate_appears_as_a_discard() -> None:
    """THE ADMISSION-SIDE CONTROL: rubbish becomes a ROW, and `parse` never raises on it.

    An exception here would end the batch and make the discard rate a function of where in the
    batch the rubbish landed.
    """
    from cdfc.experiment.parse import DISCARD_REASONS, parse

    out = parse("{[not yaml at all")
    assert out.envelope is None
    assert out.discard is not None and out.discard.reason in DISCARD_REASONS


# --- NC-M11 — the discard pile leaves the funnel -----------------------------------------


def test_nc__M11_funnel_stage_zero_equals_the_planned_count() -> None:
    """`|obligations| × |regimes| × k`, **discards included**.

    Under `FunnelDropsDiscards` stage 0 reads `planned − discards`, and then a run with 300
    malformed candidates and a run with none produce the same funnel.
    """
    assert planned_count(obligations=30, regimes=2, k=10) == 600


def test_nc__M11b_a_run_with_zero_discards_still_reports_the_row() -> None:
    """THE ADMISSION-SIDE CONTROL: the `parsed` stage exists even when nothing died there.

    It is built from `planned_count`'s OWN output rather than from a literal, so that it stays
    green under `FunnelDropsDiscards`: the injector changes what `planned` means, and this control
    must show the funnel still assembles a full stage list — not re-assert the arithmetic the
    rejection-side guard already owns. A positive control that goes red for the right reason is
    still the wrong control.
    """
    from cdfc.experiment.funnel import STAGE_ORDER, funnel

    n = planned_count(obligations=2, regimes=2, k=1)
    f = funnel([object()] * n, [], obligations=2, regimes=2, k=1)
    names = [s.name for s in f.stages]
    assert names == list(STAGE_ORDER), "a stage vanished from the funnel"
    assert f.stages[names.index("parsed")].entered == n
    assert f.survived == n, "nothing was rejected, so everything must survive"


# --- NC-M13 — a model on the qualification path -------------------------------------------


def _import_closure(root: str) -> set[str]:
    """AST-only closure over `cdfc.*`. Imports nothing, so a banned import cannot run itself.

    **THE WALK IS SEEDED WITH EVERY MODULE FILE UNDER THE ROOT, not with the root's `__init__`.**
    The first version seeded it with the package name alone, and `cdfc/qualify/__init__.py`
    imports almost nothing — so the closure never reached `g2_kill`, the injector that puts a
    model client in the kill gate did not turn this guard red, and the control reported itself
    caught while checking a package boundary nothing crosses. That is this project's own
    recurring defect — a gate that reports OK having looked at nothing — occurring inside the
    gate written to catch it.

    Seeding with the files is also the stronger rule: *no module in this package may import a
    model client*, which cannot be defeated by a module simply not being re-exported.
    """
    src = REPO / "src"
    seen: set[str] = set()
    stack = [root]
    root_dir = src / Path(root.replace(".", "/"))
    if root_dir.is_dir():
        stack += [
            ".".join(p.relative_to(src).with_suffix("").parts)
            for p in root_dir.rglob("*.py")
            if "__pycache__" not in p.parts
        ]
    while stack:
        mod = stack.pop()
        if mod in seen:
            continue
        seen.add(mod)
        for cand in (src / Path(mod.replace(".", "/") + ".py"),
                     src / Path(mod.replace(".", "/")) / "__init__.py"):
            if not cand.is_file():
                continue
            for node in ast.walk(ast.parse(cand.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    stack += [a.name for a in node.names if a.name.startswith("cdfc")]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("cdfc"):
                        stack.append(node.module)
                        stack += [f"{node.module}.{a.name}" for a in node.names]
            break
    return seen


def test_nc__M13a_qualify_import_closure_has_no_model_client() -> None:
    """The gate must not adjudicate using the thing it is adjudicating.

    A model is a measured-poor judge of exactly this failure — false-success detection at
    AUROC ≤ 0.65 and 13% recall at a 10% flag rate — so a model judge would fail silently in the
    same direction as the thing it is judging.

    The closure is walked over **every** qualification module, not only `g2_kill`, because the
    injector puts the import in one place and a guard that only looked there would be a guard
    against that injector rather than against the defect.
    """
    reached: set[str] = set()
    for root in ("cdfc.qualify", "cdfc.evaluate", "cdfc.verdict", "cdfc.attest", "cdfc.selfcheck"):
        reached |= _import_closure(root)
    offenders = sorted(m for m in reached if m.startswith(("cdfc.experiment", "cdfc.model")))
    assert offenders == [], (
        f"the verdict and qualification paths reach {offenders}. `cdfc.experiment.client` is the "
        "only module that may import a model client, and nothing that decides anything about a "
        "filing may reach it."
    )


def test_nc__M13c_run_module_may_import_the_client() -> None:
    """THE ADMISSION-SIDE CONTROL, and it is not decorative.

    A rule banning `cdfc.experiment` from *everything* would pass the test above while forbidding
    the build. `run.py` **must** be able to reach the client, or the guard is banning the wrong
    thing.
    """
    assert "cdfc.experiment.client" in _import_closure("cdfc.experiment.run")


# --- NC-M14 — a third stage ---------------------------------------------------------------


def test_nc__M14_a_third_stage_raises() -> None:
    """There is exactly one extension, and there is no third stage, ever."""
    rows = _rows(beats=True)
    result = decide_mod.SettlingResult(
        k_a=12, n_a=40, k_b=0, n_b=10, beats_baselines=True, per_baseline=rows, stage=2,
    )
    object.__setattr__(result, "stage", 3)
    with pytest.raises(decide_mod.CriterionExhausted):
        decide_mod.decide(result, lock=prereg._read(LOCK))


def _rows(*, beats: bool):
    from cdfc.experiment import marginal as M

    o = frozenset(range(100))
    return M.marginal_kill(
        observable=o,
        candidate_kills=frozenset(range(20)) if beats else frozenset(),
        baseline_kills={"B0": frozenset({0}), "B1": frozenset({1}), "B2": frozenset({2})},
    )


# --- NC-M16 — a criterion revised after the result ------------------------------------------


def test_nc__M16b_inadmissible_arguments_cannot_enter_decide() -> None:
    """The SIGNATURE is the guard, and it has to be.

    A keyword-only `override=None` changes no existing behaviour and passes every behavioural
    test — `DecideTakesAnOverride` adds exactly that. So the assertion is over the parameter list:
    the four inadmissible arguments are unrepresentable rather than merely disallowed.
    """
    params = list(inspect.signature(decide_mod.decide).parameters)
    assert params == ["result", "lock"], (
        f"decide() takes {params}. It takes a result and a lock, and nothing else — no override, "
        "no rationale, no notes, no **kwargs. A function that accepted one is a function somebody "
        "can pass one to on the day the result is unwelcome."
    )
    assert len(decide_mod.INADMISSIBLE_ARGUMENTS) == 4


def test_nc__M16a_decision_is_a_pure_function_of_its_inputs() -> None:
    """THE ADMISSION-SIDE CONTROL: the same inputs give the same verdict, twice."""
    lock = prereg._read(LOCK)
    result = decide_mod.SettlingResult(
        k_a=6, n_a=20, k_b=0, n_b=10, beats_baselines=True, per_baseline=_rows(beats=True), stage=1,
    )
    assert decide_mod.decide(result, lock=lock).as_obj() == decide_mod.decide(result, lock=lock).as_obj()
    assert decide_mod.decide(result, lock=lock).verdict == "RETAIN"


# --- NC-M34 — the pool is re-curated after the draw ------------------------------------------


def test_nc__M34a_textsource_and_exclusion_hashes_precede_the_draw(tmp_path: Path) -> None:
    """`draw_sha256` cannot be appended while a pool hash is absent.

    Under `ExclusionsEditedAfterTheDraw` the required order is reversed, so a draw can be fixed
    over a pool that can still be edited — and then `k of 20` measures our curation of the
    instrument and reports it as a property of the model. The two are indistinguishable in the
    published number, which is why the ordering is code rather than prose.
    """
    doc = tmp_path / "P.md"
    shutil.copy(PREREG, doc)
    lock_path = tmp_path / "lock.json"
    prereg.lock(doc, lock_path, committed_at="2026-08-15")
    with pytest.raises(prereg.PoolNotYetFixed):
        prereg.append(lock_path, draw_sha256="a" * 64)
    assert prereg.APPENDABLE.index("textsource_sha256") < prereg.APPENDABLE.index("draw_sha256")
    assert prereg.APPENDABLE.index("exclusion_rule_sha256") < prereg.APPENDABLE.index("draw_sha256")


def test_nc__M34b_excluded_count_and_pages_are_available_to_the_preregistration() -> None:
    """The excluded count travels as a THIRD INTEGER, never folded into either of the other two."""
    d = draw(_pool(), seed=20260815, strata=_oracle())
    a, drawn, excluded = d.decidable_fraction()
    assert (a, drawn, excluded) == (20, len(d.drawn), 0)
    assert hasattr(Pool, "excluded_pages")


def test_nc__M34c_a_correctly_ordered_exclusion_and_draw_pair_passes(tmp_path: Path) -> None:
    """THE ADMISSION-SIDE TWIN: the ordering rule permits the honest sequence."""
    doc = tmp_path / "P.md"
    shutil.copy(PREREG, doc)
    lock_path = tmp_path / "lock.json"
    prereg.lock(doc, lock_path, committed_at="2026-08-15")
    prereg.append(lock_path, textsource_sha256="b" * 64)
    prereg.append(lock_path, exclusion_rule_sha256="c" * 64)
    after = prereg.append(lock_path, draw_sha256="a" * 64, strata_sha256="d" * 64,
                          baselines_sha256="e" * 64)
    ready, missing = after.has_run_prerequisites()
    assert ready and missing == (), f"a fully appended lock still reports {missing} missing"
