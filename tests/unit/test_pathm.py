"""Path M — rules a regulator wrote, executed, with a typed reason for every one that is not.

The product claim is one sentence: *of N published at date D we executed M, and here is the typed
reason for each of the other N−M, with zero model calls.* Each clause is tested here against the
pinned EBA validation-rule set, which is the regulator's own artefact and fixes N externally.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.pathm.coverage import declare
from cdfc.pathm.dpmxl import parse
from cdfc.pathm.reader import RuleSetError, read
from cdfc.pathm.statement import NotExecuted

RULES = Path("corpus/rules/eba_validation_rules_4.3_2026_06_23.xlsx")


@pytest.fixture(scope="module")
def ruleset():
    return read(RULES)


@pytest.fixture(scope="module")
def coverage():
    return declare(RULES)


# --- N is the PUBLISHER'S number, and it reproduces ---------------------------------------------

def test_pathm__reproduces_the_published_population(ruleset) -> None:
    """W0-B measured these against the same file months earlier. They are not our numbers."""
    assert len(ruleset) == 12925
    assert len(ruleset.active) == 11056
    assert len(ruleset) - len(ruleset.active) == 1869
    assert ruleset.source_sha256.startswith("9997374c8f60f555")
    assert ruleset.published_at == "2026-06-23", "D comes from the file's own name, not a clock"


def test_pathm__every_published_rule_carries_an_expression(ruleset) -> None:
    """The property that makes Path M possible at all: the regulator published executable rules."""
    assert sum(1 for r in ruleset.rules if r.expression) == len(ruleset)


def test_pathm__null_scope_is_absence_not_a_table_name(ruleset) -> None:
    """E2's single failure across 18,827 addresses, and it is a defect in the PUBLICATION."""
    null = [r for r in ruleset.rules if r.scope_is_null]
    assert len(null) == 1, [r.code for r in null]
    assert not null[0].active, "the one NULL-scope rule is inactive, as E2 recorded"


# --- the declaration ---------------------------------------------------------------------------

def test_pathm__the_declaration_closes(coverage) -> None:
    """executed + every reason == N. A funnel whose stages do not sum has lost rules silently."""
    assert coverage.executed + sum(n for _r, n in coverage.not_executed) == coverage.published
    assert coverage.published == 12925


def test_pathm__we_execute_the_bulk_of_what_was_published(coverage) -> None:
    assert coverage.executed == 10453
    assert coverage.data_points == 31904


def test_pathm__every_reason_is_from_the_closed_vocabulary(coverage) -> None:
    for reason, n in coverage.not_executed:
        assert isinstance(reason, NotExecuted)
        assert n > 0, "a reason with no rules under it should not be rendered at all"


def test_pathm__the_publishers_own_deactivations_are_reported(coverage) -> None:
    """A coverage table that hides them overstates what there was to execute."""
    d = dict(coverage.not_executed)
    assert d[NotExecuted.DEACTIVATED_BY_PUBLISHER] == 1869


def test_pathm__the_two_bans_are_reported_separately(coverage) -> None:
    """'we chose not to' and 'we cannot' are different statements to a supervisor."""
    d = dict(coverage.not_executed)
    assert d[NotExecuted.BANNED_CONSTRUCT_CLOCK] > 0
    assert d[NotExecuted.BANNED_CONSTRUCT_REGEX] > 0
    assert NotExecuted.BANNED_CONSTRUCT_CLOCK is not NotExecuted.BANNED_CONSTRUCT_REGEX


def test_pathm__a_declaration_that_does_not_close_is_refused() -> None:
    """The arithmetic assertion must be able to fire, or it is decoration."""
    from cdfc.pathm.coverage import RuleCoverage

    with pytest.raises(ValueError, match="does not close"):
        RuleCoverage(source_name="x", source_sha256="y", published_at="2026-01-01",
                     published=100, executed=10,
                     not_executed=((NotExecuted.UNPARSEABLE_EXPRESSION, 5),), data_points=0)


# --- the parser, on the three forms that were each reported as "unparseable" first ---------------

def test_pathm__parses_a_parenthesised_row_list() -> None:
    """1,323 rules were called UNPARSEABLE by a comma split that broke `(r0100, r0110)`."""
    p = parse("with {tM_01.00, default: null, interval: false}: "
              "not ( isnull ({(r0100, r0110, r0200), c0010}) )", scope="M_01.00")
    assert p.anchors, "a parenthesised row list must still address a data point"
    a = p.anchors[0]
    assert a.table == "M_01.00"
    assert set(a.rows) == {"0100", "0110", "0200"}
    assert a.cols == ("0010",)


def test_pathm__carries_an_axis_it_does_not_understand() -> None:
    """E2 requirement 3. 114 rules carrying a bare `s*` axis were reported UNPARSEABLE."""
    p = parse("with {tY_01.01, default: null, interval: false}: {r*, c0020, s*} >= 0",
              scope="Y_01.01")
    assert p.anchors
    a = p.anchors[0]
    assert a.rows == ("*",) and a.cols == ("0020",)
    assert ("s", "*") in a.axes, "the unknown axis is CARRIED, not silently dropped"


def test_pathm__a_range_is_named_rather_than_expanded(coverage) -> None:
    """Expanding `{r0850-0860}` would invent axis members the table may not have."""
    d = dict(coverage.not_executed)
    assert d[NotExecuted.NEEDS_RANGE_BINDING] == 513


def test_pathm__the_declared_scope_is_the_fallback_table() -> None:
    """E2: addresses resolve against each rule's OWN declared scope, so that column IS the scope."""
    p = parse("with {default: null, interval: false}: not ( isnull ({c0040}) )", scope="Z_08.02")
    assert p.anchors and p.anchors[0].table == "Z_08.02"


def test_pathm__null_scope_never_becomes_a_table() -> None:
    p = parse("with {default: null}: not ( isnull ({c0040}) )", scope="NULL")
    assert not p.anchors, "NULL is absence; an anchor built on it would address a table nobody has"


# --- zero model calls, as a property of the import graph ----------------------------------------

def test_pathm__no_model_is_reachable() -> None:
    """The claim is not a promise about intent. `cdfc.pathm` is a VERDICT_ROOT."""
    import sys

    sys.path.insert(0, ".")
    from tests.negative.importgraph import VERDICT_ROOTS, banned_in, import_closure

    assert "cdfc.pathm" in VERDICT_ROOTS
    closure = import_closure("cdfc.pathm", src=Path("src"))
    assert len(closure) > 20, "an empty walk would pass this vacuously"
    assert banned_in(closure) == ()


def test_pathm__a_malformed_rule_set_is_refused(tmp_path: Path) -> None:
    """A reader that defaulted a missing column would publish a table over a population it could
    not see."""
    import zipfile

    p = tmp_path / "empty.xlsx"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml",
                   '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   "<sheetData/></worksheet>")
    with pytest.raises(RuleSetError):
        read(p)
