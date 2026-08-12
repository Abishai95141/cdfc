"""P4-B3 — the CEL runtime and the host-function registry."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import Budget, CelRuntime, Outcome  # noqa: E402
from cdfc.facts.view import FactView  # noqa: E402
from cdfc.measure.perf.deadline import wall_deadline_factory  # noqa: E402
from cdfc.predicates.cel_profile import ADMITTED_HOST_FNS  # noqa: E402
from cdfc.predicates.errors import (  # noqa: E402
    RegistryNotFrozen,
    SubsetViolation,
    UnregisteredHostFn,
)
from cdfc.predicates.host_fns import (  # noqa: E402
    UNDERSPECIFIED,
    HostFn,
    HostFnError,
    HostFnRegistry,
    default_registry,
    load_vectors,
    vector_digest,
)

FILING = {
    "a": {"b": 1},
    "rows": [{"x": 1, "__cell__": "S!A1"}, {"x": -2, "__cell__": "S!A2"}],
    "total": 3,
    "reg_no": "IFSCA-FME-001",
}
TEMPLATE = {"v": {"k": ["a", "b"]}}


@pytest.fixture()
def rt() -> CelRuntime:
    return CelRuntime(profile_version="P4", host_fns=default_registry())


@pytest.fixture()
def views() -> tuple[FactView, FactView]:
    return FactView(FILING, root="filing"), FactView(TEMPLATE, root="template")


# --- outcomes are values, not exceptions ------------------------------------------------


def test_evaluate__error_returns_ERROR_outcome_not_an_exception(rt, views) -> None:
    f, t = views
    r = rt.evaluate(rt.compile("filing.a.b / 0 == 1", slot="expr"), filing=f, template=t)
    assert r.outcome is Outcome.ERROR
    assert r.value is None
    assert isinstance(r.error, str), "the CEL error TEXT, never an exception object"


def test_evaluate__an_absent_key_is_an_ERROR_not_a_false(rt, views) -> None:
    """A missing key returning False would be a PASS produced by absence."""
    f, t = views
    r = rt.evaluate(rt.compile("filing.nope.x == 1", slot="expr"), filing=f, template=t)
    assert r.outcome is Outcome.ERROR


def test_evaluate__the_ok_path_returns_the_value(rt, views) -> None:
    """The admission side. Without it every test above passes on a runtime that only errors."""
    f, t = views
    assert rt.evaluate(rt.compile("filing.a.b == 1", slot="expr"), filing=f, template=t).value is True
    assert rt.evaluate(rt.compile("filing.a.b == 2", slot="expr"), filing=f, template=t).value is False
    w = rt.evaluate(
        rt.compile("filing.rows.filter(r, r.x < 0).map(r, r.__cell__)", slot="witness"),
        filing=f, template=t,
    )
    assert w.outcome is Outcome.OK and w.value == ("S!A2",)


# --- the two budgets --------------------------------------------------------------------


def test_evaluate__step_budget_returns_BUDGET_EXCEEDED(views) -> None:
    _, t = views
    big = FactView({"rows": [{"x": i} for i in range(5000)]}, root="filing")
    rt = CelRuntime(profile_version="P4", host_fns=default_registry(), budget=Budget(steps=1000))
    r = rt.evaluate(rt.compile("filing.rows.all(r, r.x >= 0)", slot="expr"), filing=big, template=t)
    assert r.outcome is Outcome.BUDGET_EXCEEDED
    assert r.budget == "steps"
    assert r.deterministic is True, "a step budget is re-derivable; that is why it is the default"


def test_evaluate__wall_clock_kill_fires_independently_of_the_step_budget(views) -> None:
    _, t = views
    big = FactView({"rows": [{"x": i} for i in range(200_000)]}, root="filing")
    rt = CelRuntime(
        profile_version="P4", host_fns=default_registry(),
        budget=Budget(steps=10**9, wall_ms=1), deadline_factory=wall_deadline_factory(1),
    )
    r = rt.evaluate(rt.compile("filing.rows.all(r, r.x >= 0)", slot="expr"), filing=big, template=t)
    assert r.outcome is Outcome.BUDGET_EXCEEDED
    assert r.budget == "wall"
    assert r.deterministic is False, (
        "a wall kill depends on machine load, so the item cannot be re-derived from its own bytes "
        "— and a runtime that reported one BUDGET_EXCEEDED for both would hide that"
    )


def test_budget__a_wall_budget_with_nothing_to_enforce_it_is_refused() -> None:
    with pytest.raises(ValueError, match="bounds nothing"):
        CelRuntime(profile_version="P4", host_fns=default_registry(), budget=Budget(wall_ms=5))


def test_budget__zero_steps_is_refused() -> None:
    with pytest.raises(ValueError, match="before it starts"):
        Budget(steps=0)


# --- compilation ------------------------------------------------------------------------


def test_compile__is_cached_by_source_digest_and_not_by_object_identity(rt) -> None:
    a = rt.compile("filing.a.b == 1", slot="expr")
    before = rt.cache_size
    b = rt.compile("".join(["filing.a.b", " == 1"]), slot="expr")  # equal string, new object
    assert a is b and rt.cache_size == before


def test_compile__the_same_source_in_a_different_slot_is_a_different_program(rt) -> None:
    a = rt.compile("filing.rows.map(r, r.__cell__)", slot="witness")
    assert a.slot == "witness"
    with pytest.raises(SubsetViolation):
        rt.compile("filing.rows.map(r, r.__cell__)", slot="expr")


def test_evaluate__binds_exactly_two_names(rt) -> None:
    with pytest.raises(SubsetViolation, match="unbound name"):
        rt.compile("registry.a == 1", slot="expr")
    rt.compile("filing.a.b == template.v.k", slot="expr")


# --- the host-function registry ---------------------------------------------------------


def test_registry__unregistered_call_raises_UnregisteredHostFn() -> None:
    reg = HostFnRegistry()
    with pytest.raises(UnregisteredHostFn):
        reg.get("sum")


def test_registry__register_after_freeze_raises() -> None:
    reg = default_registry()
    with pytest.raises(RegistryNotFrozen, match="frozen"):
        reg.register(HostFn(
            name="sum", version="2", signature="x", returns_tristate=False, fn=lambda x: x,
            test_vector_sha256="d", mutation_score_json="m", authored_by="a",
        ))


def test_registry__bindings_before_freeze_are_refused() -> None:
    reg = default_registry(frozen=False)
    with pytest.raises(RegistryNotFrozen, match="CLOSED"):
        reg.bindings()


def test_registry__refuses_a_function_with_no_vectors_or_no_mutation_score() -> None:
    for missing in ("test_vector_sha256", "mutation_score_json", "authored_by"):
        reg = HostFnRegistry()
        kwargs = dict(
            name="sum", version="1", signature="s", returns_tristate=False, fn=lambda x: x,
            test_vector_sha256="d", mutation_score_json="m", authored_by="a",
        )
        kwargs[missing] = ""
        with pytest.raises(HostFnError):
            reg.register(HostFn(**kwargs))  # type: ignore[arg-type]


def test_registry__an_implementation_the_grammar_does_not_admit_is_refused() -> None:
    reg = HostFnRegistry()
    with pytest.raises(HostFnError, match="grammar does not admit"):
        reg.register(HostFn(
            name="unadmitted", version="1", signature="s", returns_tristate=False, fn=lambda x: x,
            test_vector_sha256="d", mutation_score_json="m", authored_by="a",
        ))


def test_registry__the_grammar_and_the_registry_name_the_same_functions() -> None:
    """Two lists, and the one that drifts is the one nobody is reading."""
    assert default_registry().names() == ADMITTED_HOST_FNS


# --- reg_resolves cannot resolve live ---------------------------------------------------


def test_reg_resolves__with_no_snapshot_the_run_is_INPUT_UNAVAILABLE_never_a_fetch(views) -> None:
    f, t = views
    rt = CelRuntime(profile_version="P4", host_fns=default_registry())
    r = rt.evaluate(rt.compile('reg_resolves(filing.reg_no) == "TRUE"', slot="expr"), filing=f, template=t)
    assert r.outcome is Outcome.INPUT_UNAVAILABLE
    assert "live" in (r.error or "")


def test_reg_resolves__with_a_snapshot_bound_it_answers(views) -> None:
    f, t = views
    reg = default_registry()
    reg.bind_snapshot("deadbeef", {"IFSCA-FME-001": True})
    rt = CelRuntime(profile_version="P4", host_fns=reg)
    r = rt.evaluate(rt.compile('reg_resolves(filing.reg_no) == "TRUE"', slot="expr"), filing=f, template=t)
    assert r.outcome is Outcome.OK and r.value is True


def test_reg_resolves__has_no_http_client_in_its_import_closure() -> None:
    """An AST import walk. A verdict that depends on a live endpoint cannot be re-derived."""
    banned = {"http", "httplib", "http.client", "urllib", "urllib3", "requests", "httpx",
              "socket", "aiohttp", "ssl", "ftplib", "telnetlib", "smtplib"}
    seen: set[str] = set()
    todo = [REPO / "src" / "cdfc" / "predicates" / "host_fns" / "reg_resolves.py"]
    offenders: list[str] = []
    while todo:
        path = todo.pop()
        if str(path) in seen or not path.is_file():
            continue
        seen.add(str(path))
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for n in names:
                if n.split(".")[0] in banned:
                    offenders.append(f"{path.name}: {n}")
                if n.startswith("cdfc."):
                    todo.append(REPO / "src" / (n.replace(".", "/") + ".py"))
                    todo.append(REPO / "src" / n.replace(".", "/") / "__init__.py")
    assert offenders == [], f"a network client is reachable from reg_resolves: {offenders}"


# --- the third value --------------------------------------------------------------------


def test_nav_interval__close_ended_restricted_returns_UNDERSPECIFIED() -> None:
    from cdfc.predicates.host_fns.nav_interval import UNKNOWN_COMBINATION, nav_interval

    assert str(nav_interval("Restricted", "Close-ended", "NA")) == UNDERSPECIFIED
    assert str(nav_interval("Retail", "Open-ended", "NA")) == "P1M", "the admission side"
    # The two kinds of unknown are different facts and carry different reason codes.
    assert str(nav_interval("Not A Named Type", "Open-ended", "NA")) == UNKNOWN_COMBINATION
    assert UNDERSPECIFIED != UNKNOWN_COMBINATION


# --- the published vectors --------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(ADMITTED_HOST_FNS))
def test_host_fn__every_published_vector_holds(name: str) -> None:
    import importlib

    module_name, attr = MODULE_OF[name]
    module = importlib.import_module(module_name)
    reg = HostFnRegistry() if name == "reg_resolves" else None
    if reg is not None:
        module.bind_registry(reg)
    fn = getattr(module, attr)
    for v in load_vectors(name):
        if "snapshot" in v and reg is not None:
            if v["snapshot"] is None:
                reg._snapshot_sha256, reg._records = None, {}
            else:
                reg.bind_snapshot("vectors", v["snapshot"])
        if "raises" in v:
            with pytest.raises(Exception) as e:  # noqa: B017 — the type is asserted next
                fn(*v["args"])
            assert type(e.value).__name__ == v["raises"], f"{name} {v['args']}"
            continue
        got = fn(*v["args"])
        expect = v["expect"]
        got = bool(got) if isinstance(expect, bool) else (int(got) if isinstance(expect, int) else str(got))
        assert got == expect, f"{name} {v['args']}: expected {expect!r}, got {got!r}"


MODULE_OF = {
    "sum": ("cdfc.predicates.host_fns.sum_units", "sum_units"),
    "gstin_valid": ("cdfc.predicates.host_fns.gstin_valid", "gstin_valid"),
    "template_current": ("cdfc.predicates.host_fns.template_current", "template_current"),
    "nav_interval": ("cdfc.predicates.host_fns.nav_interval", "nav_interval"),
    "reg_resolves": ("cdfc.predicates.host_fns.reg_resolves", "reg_resolves"),
}


@pytest.mark.parametrize("name", sorted(ADMITTED_HOST_FNS))
def test_host_fn__the_registered_digest_is_the_published_file(name: str) -> None:
    assert default_registry().get(name).test_vector_sha256 == vector_digest(name)


@pytest.mark.parametrize("name", sorted(ADMITTED_HOST_FNS))
def test_host_fn__the_mutation_score_is_a_measured_file_not_a_promise(name: str) -> None:
    """NC-X04c's subject: a host function whose score is a placeholder does not load."""
    path = REPO / default_registry().get(name).mutation_score_json
    assert path.is_file(), (
        f"{name} declares {path.name} and it does not exist. Run tools/host_fn_mutation.py — and "
        "note that a file saying 'PENDING' would satisfy the registry's check while measuring "
        "nothing, which is why the check is against a produced measurement."
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["mutants_generated"] > 0, "a score over zero mutants is not a score"
    assert data["unexplained_survivors"] == 0, (
        f"{name} has {data['unexplained_survivors']} surviving mutant(s) with no argument in "
        "docs/EQUIVALENT-MUTANTS.md. A survivor is either a hole in the vectors or an equivalent "
        "program, and only reading it tells you which."
    )
    assert "score" in data and "score_excluding_declared_equivalent" in data, (
        "both denominators, always. One of them can be moved by argument, and hiding which is "
        "how a score rises without anyone deciding it should"
    )
