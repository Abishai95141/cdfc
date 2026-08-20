"""P13-B0 — criterion A6. **The day this lands, the model-free claim stops being an intention.**

Two tests, and neither is sufficient alone.
"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from negative.importgraph import (
    BANNED_IN_VERDICT,
    BOUNDED_DYNAMIC_IMPORTS,
    VERDICT_ROOTS,
    DynamicImportUnresolvable,
    banned_in,
    import_closure,
)

SRC = Path("src")


def test_nc__A04a_no_model_import_reachable() -> None:
    """The AST closure of every verdict root reaches nothing banned.

    Catches the static import that no test input happens to exercise — which is most of them,
    because a client added to a module nobody calls is still a client that ships.
    """
    for root in VERDICT_ROOTS:
        closure = import_closure(root, src=SRC)
        assert banned_in(closure) == (), (
            f"{root} reaches {banned_in(closure)}. The verdict path must be computable with the "
            "network unplugged and with no model available."
        )


def test_nc__A04a_the_closure_is_not_empty() -> None:
    """**The control on the control.** A closure of one is a gate that checked nothing.

    The first version of `import_closure` seeded with the root alone, and six of the seven verdict
    roots are packages whose `__init__.py` imports nothing — so it returned a clean closure of
    size 1 for each and passed. A guard whose denominator is one is R3's finding, inside the guard.
    """
    for root in VERDICT_ROOTS:
        closure = import_closure(root, src=SRC)
        assert len(closure) > 25, f"{root} closure is {len(closure)} modules — it checked nothing"


def test_nc__A04a_a_planted_import_is_caught(tmp_path: Path) -> None:
    """The positive control: the walker DOES go red when a banned import is present.

    Without this, a walker that silently returned an empty set would pass the test above.
    """
    pkg = tmp_path / "cdfc" / "verdict"
    pkg.mkdir(parents=True)
    (tmp_path / "cdfc" / "__init__.py").write_text("")
    (pkg / "__init__.py").write_text("")
    (pkg / "leak.py").write_text("import httpx\n")
    closure = import_closure("cdfc.verdict", src=tmp_path)
    assert "httpx" in banned_in(closure)


def test_nc__A04a_a_dynamic_import_raises_rather_than_being_skipped(tmp_path: Path) -> None:
    """An unresolvable dynamic import is exactly where a client would hide."""
    pkg = tmp_path / "cdfc" / "verdict"
    pkg.mkdir(parents=True)
    (tmp_path / "cdfc" / "__init__.py").write_text("")
    (pkg / "__init__.py").write_text("")
    (pkg / "sneaky.py").write_text(
        "import importlib\n\n\ndef go(name):\n    return importlib.import_module(name)\n"
    )
    with pytest.raises(DynamicImportUnresolvable):
        import_closure("cdfc.verdict", src=tmp_path)


def test_nc__A04a_every_declared_bound_still_exists() -> None:
    """A declared bound whose file is gone is a bound nobody is relying on — and a stale licence.

    The table would keep passing while the site it excuses no longer exists, and the next dynamic
    import added to a file with the same name would inherit an exemption nobody granted it.
    """
    for rel, bound in BOUNDED_DYNAMIC_IMPORTS.items():
        assert (SRC / rel).is_file(), f"{rel} is declared bounded and does not exist"
        assert (SRC / bound.replace(".", "/")).is_dir(), f"{bound} is not a package"
        # And the bound must actually be enforced in the file that relies on it.
        text = (SRC / rel).read_text(encoding="utf-8")
        assert bound in text, f"{rel} declares the bound {bound} and never mentions it"


def test_nc__A04b_verdict_runs_with_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """A full run with `socket.socket` patched to raise. **Catches what the static walk cannot.**

    The static closure cannot see a call made through a name it never resolved. This can — and it
    is the reason `injectors/DynamicHttpInHostFn` exists: it puts a network call behind a runtime
    branch precisely to prove the static test alone would pass.
    """

    def _refuse(*a: object, **k: object) -> None:
        raise AssertionError(
            "the verdict path opened a socket. Every number this system publishes must be "
            "derivable from the artifact under test and the pinned blank, with the network down."
        )

    monkeypatch.setattr(socket, "socket", _refuse)
    monkeypatch.setattr(socket, "create_connection", _refuse)

    # Importing and exercising the surface layer is the cheapest full traversal that touches the
    # renderer, the band, the panel and the label registry -- the four places a "phone home for
    # the latest thresholds" would most plausibly be added.
    from cdfc.surface.drop import drop_page
    from cdfc.surface.stylesheet import stylesheet

    assert stylesheet()
    assert drop_page()


def test_nc__A04b_the_patch_actually_bites() -> None:
    """The control on the control: prove the monkeypatch would catch a socket if one were opened."""
    with pytest.MonkeyPatch.context() as m:
        opened = []
        m.setattr(socket, "socket", lambda *a, **k: opened.append(1))
        socket.socket()
        assert opened == [1]


def test_nc__A04_the_ban_is_one_rule_not_a_vendor_list() -> None:
    """`cdfc.model` is banned as a PACKAGE. An enumeration is a list somebody forgets to extend."""
    assert "cdfc.model" in BANNED_IN_VERDICT
    assert (SRC / "cdfc" / "model" / "__init__.py").is_file(), (
        "the package must exist for the ban to be a ban about something testable"
    )
    # UPDATED 20 Aug 2026. This asserted propose.py's ABSENCE, which was a proxy for the ban and
    # not the ban itself. E6 now reads RETAIN-PROVISIONAL and `ci/barrier5.sh` — which owns that
    # question — admits the file. What this control exists for is that `cdfc.model` is banned as a
    # PACKAGE rather than by enumerating vendors, and that is asserted above and by A04a's walk of
    # the actual import closure. Keeping the absence assertion here would have made a second gate
    # silently responsible for a decision barrier 5 is the declared owner of.
    barrier = (SRC.parent / "ci" / "barrier5.sh").read_text(encoding="utf-8")
    assert "src/cdfc/model/propose.py" in barrier, (
        "barrier 5 no longer names the proposer, so nothing owns the question of whether one may "
        "ship. This control deliberately does NOT re-answer it — two gates owning one decision is "
        "how a rule comes to be enforced by whichever happens to run."
    )


# --- B3: the POSITIVE form. Added 20 Aug 2026 -------------------------------------------------
#
# B3 adds `docling` as a build-time PDF reader. The obvious place for a PDF reader is
# `cdfc.qualify`, which is a VERDICT ROOT, and nothing in `BANNED_IN_VERDICT` would have caught it
# -- a denylist only refuses what somebody remembered to write down. These three tests are the
# allowlist: undeclared is refused, the list is not vacuous, and the guard flips.


def test_nc__A04c_no_undeclared_third_party_in_the_verdict_closure() -> None:
    """The verdict closure's third-party imports ARE the declared runtime set."""
    from negative.importgraph import third_party_in

    closure: set[str] = set()
    for root in VERDICT_ROOTS:
        closure |= set(import_closure(root, src=SRC))
    undeclared = third_party_in(frozenset(closure))
    assert not undeclared, (
        f"{len(undeclared)} undeclared third-party package(s) in the verdict closure: "
        f"{list(undeclared)}. The runtime closure is deliberately tiny and widening it is an "
        f"architecture decision, not a pip install. Add a row to RUNTIME_THIRD_PARTY -- with the "
        f"reason -- or take the import out."
    )


def test_nc__A04c_the_allowlist_is_not_vacuous() -> None:
    """Every allowed package is ACTUALLY reachable. An allowlist of ghosts refuses nothing.

    This is the `count is not a reading` rule applied to a gate's own table: a row nobody reaches
    is a row that could name anything, and the gate would still be green.
    """
    from negative.importgraph import RUNTIME_THIRD_PARTY

    closure: set[str] = set()
    for root in VERDICT_ROOTS:
        closure |= set(import_closure(root, src=SRC))
    tops = {m.split(".")[0] for m in closure}
    unreached = sorted(RUNTIME_THIRD_PARTY - tops)
    assert not unreached, (
        f"RUNTIME_THIRD_PARTY allows {unreached}, which no verdict root actually imports. "
        f"Remove the row: an allowlist entry that nothing reaches is not a permission, it is an "
        f"unexamined claim."
    )


def test_nc__A04c_a_planted_pdf_import_is_caught(tmp_path: Path) -> None:
    """THE GUARD. Plant `import docling` in a verdict root and the allowlist must go red.

    Written because B3 is exactly the change that would have planted it for real.
    """
    from negative.importgraph import third_party_in

    src = tmp_path / "src"
    pkg = src / "cdfc" / "qualify"
    pkg.mkdir(parents=True)
    (src / "cdfc" / "__init__.py").write_text("")
    (pkg / "__init__.py").write_text("from cdfc.qualify import textsource\n")
    (pkg / "textsource.py").write_text("import docling\nimport lxml.etree\n")

    closure = import_closure("cdfc.qualify", src=src)
    undeclared = third_party_in(closure)
    assert "docling" in undeclared, (
        "a planted `import docling` in a verdict root was NOT reported undeclared; the allowlist "
        "does not bite and every green run of it means nothing."
    )
    assert "lxml" not in undeclared, "lxml is declared and must not be reported"
