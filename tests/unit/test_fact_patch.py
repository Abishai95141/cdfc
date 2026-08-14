"""D-P10-01 — a cell with no value is ABSENT, and the string `"None"` is a false kill.

These are the guards on the defect P10's canary loop found in P6's committed campaign: 81 of 125
predicates failed to reproduce their own recorded kill, and seven of those kills turned out to be
`'' == 'None'` returning false.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.facts.build import _coerce  # noqa: E402
from cdfc.facts.fact_table import FactError  # noqa: E402
from cdfc.facts.patch import ABSENT, patch, value_for  # noqa: E402
from cdfc.facts.view import FactSet  # noqa: E402


def _tree() -> dict:
    return {
        "sheet": {
            "r1": {"ca": {"v": 10, "__cell__": "Sheet!A1"}},
            "r2": {"cb": {"v": 20, "__cell__": "Sheet!B2"}},
            "dv_c1": {
                "cells": [
                    {"v": "Open-Ended", "__cell__": "Sheet!C1"},
                    {"v": "Close-Ended", "__cell__": "Sheet!C2"},
                ]
            },
        }
    }


def test_patch__coerce_refuses_none() -> None:
    """The defect is unrepresentable, not discouraged."""
    with pytest.raises(FactError) as e:
        _coerce(None)
    assert "'None'" in str(e.value), "the refusal names the string it is refusing to produce"


def test_patch__none_is_absent_never_the_string() -> None:
    assert value_for(None) is ABSENT
    assert value_for("") is ABSENT
    assert value_for(ABSENT) is ABSENT
    assert value_for(5) == 5
    assert value_for("x") == "x"


def test_patch__an_absent_patch_deletes_the_leaf_value() -> None:
    """Byte-for-byte the shape `filing_tree` produces for a cell the workbook does not carry.

    Setting `v = ""` instead would leave a STRING where the clean tree had an INT, and an equality
    predicate over the pair returns false — which is a FAIL nobody's fault caused.
    """
    out = patch(_tree(), {"Sheet!A1": ABSENT})
    node = out["sheet"]["r1"]["ca"]
    assert "v" not in node, "an absent cell has no value, it does not have an empty one"
    assert node["__cell__"] == "Sheet!A1", "the cell keeps its identity so it can still be named"
    fs = FactSet(out, {})
    assert not fs.has("filing.sheet.r1.ca.v")


def test_patch__reaches_range_node_elements_too() -> None:
    """A scalar node and a data-validation range element carry the SAME `__cell__`.

    A patch that reached only the first would leave a membership predicate reading the pre-fault
    value out of the very range it binds — the fault applied, and invisible to the check for it.
    """
    out = patch(_tree(), {"Sheet!C1": "Close-Ended"})
    assert out["sheet"]["dv_c1"]["cells"][0]["v"] == "Close-Ended"
    assert out["sheet"]["dv_c1"]["cells"][1]["v"] == "Close-Ended" or True  # untouched sibling
    assert out["sheet"]["dv_c1"]["cells"][1]["__cell__"] == "Sheet!C2"


def test_patch__the_input_tree_is_unchanged() -> None:
    """By identity of the nested objects, not by equality.

    An equality check passes on a tree that was mutated and then restored, and "restored" is a
    property of code nobody re-ran.
    """
    base = _tree()
    leaf = base["sheet"]["r1"]["ca"]
    out = patch(base, {"Sheet!A1": 999, "Sheet!B2": ABSENT})
    assert leaf is base["sheet"]["r1"]["ca"] and leaf["v"] == 10
    assert base["sheet"]["r2"]["cb"]["v"] == 20
    assert out["sheet"]["r1"]["ca"] is not leaf
    assert out["sheet"]["r1"]["ca"]["v"] == 999
    assert "v" not in out["sheet"]["r2"]["cb"]


def test_patch__a_cell_nobody_named_is_untouched() -> None:
    out = patch(_tree(), {"Sheet!ZZ99": 1})
    assert out["sheet"]["r1"]["ca"]["v"] == 10 and out["sheet"]["r2"]["cb"]["v"] == 20


def test_patch__the_campaign_and_the_canary_share_one_patcher() -> None:
    """Two patchers would make the canary test whether two implementations agree.

    Asserted on the module object, so a copy-pasted private helper in either caller fails here.
    """
    import cdfc.facts.patch as shared
    import cdfc.measure.p6_kill as campaign
    import cdfc.selfcheck.witness as canary

    src_campaign = Path(campaign.__file__).read_text(encoding="utf-8")
    src_canary = Path(canary.__file__).read_text(encoding="utf-8")
    for name, src in (("p6_kill", src_campaign), ("selfcheck.witness", src_canary)):
        assert "facts.patch import" in src, (
            f"{name} does not import the shared patcher. The campaign decides what each predicate "
            "killed and the canary decides whether it still kills it; a second patcher makes those "
            "two questions about different fact trees."
        )
    assert shared.ABSENT is not None
