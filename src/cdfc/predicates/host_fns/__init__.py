"""P4-B3 — the host-function registry. Closed at evaluation time, and nothing enters it unmeasured.

**A host function is where a check that CEL cannot express honestly goes.** That is a privilege,
and the registry charges for it: `register` refuses a function with no published test vectors and
no mutation score, and `freeze` refuses any later addition. A format check inside an envelope has
no place to carry either — which is the whole argument of D-P4-03.

**`reg_resolves` cannot resolve live, by construction rather than by discipline.** It reads only
from the records handed to `bind_snapshot`, and there is no HTTP client in its import closure —
asserted by an AST walk, not by a code-review convention. A registry with no bound snapshot makes
the call raise, which the evaluator maps to `NOT_RUN(not_run.input_unavailable.register)` and never
to a silent live fetch.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from cdfc.predicates.cel_profile import ADMITTED_HOST_FNS
from cdfc.predicates.errors import RegistryNotFrozen, UnregisteredHostFn

VECTORS_DIR: Final[Path] = Path(__file__).resolve().parents[4] / "fixtures" / "host_fns"

# The third value. A host function that cannot say "the regulation does not determine this" has to
# choose between two answers where the regulator gave one, and the report then presents our guess
# as the rule.
UNDERSPECIFIED: Final[str] = "UNDERSPECIFIED"


class HostFnError(ValueError):
    """A host function that may not be registered, with the reason."""


class SnapshotMissing(LookupError):
    """A snapshot-bound host function was called with no snapshot bound. Never a live fetch."""


@dataclass(frozen=True, slots=True)
class HostFn:
    name: str
    version: str
    signature: str
    returns_tristate: bool
    fn: Callable[..., Any]
    test_vector_sha256: str
    mutation_score_json: str
    authored_by: str


@dataclass
class HostFnRegistry:
    _fns: dict[str, HostFn] = field(default_factory=dict)
    _frozen: bool = False
    _snapshot_sha256: str | None = None
    _records: Mapping[str, Any] = field(default_factory=dict)

    # -- registration -------------------------------------------------------------
    def register(self, hf: HostFn) -> None:
        if self._frozen:
            raise RegistryNotFrozen(
                f"the host-function set was frozen before {hf.name!r} was registered. The set is "
                "CLOSED at evaluation time so that a predicate cannot acquire a new capability "
                "between qualification and the run that quotes its kill rate."
            )
        if hf.name in self._fns:
            raise HostFnError(f"{hf.name!r} is already registered; ids are never reused")
        if hf.name not in ADMITTED_HOST_FNS:
            raise HostFnError(
                f"{hf.name!r} has an implementation but the grammar does not admit it. Add it to "
                "cel_profile.ADMITTED_HOST_FNS, or a predicate calling it fails at evaluation "
                "time rather than at compile time."
            )
        if not hf.test_vector_sha256:
            raise HostFnError(
                f"{hf.name!r} has no published test vectors. A host function is where a check "
                "goes that CEL cannot express honestly; admitting one nobody measured moves the "
                "unmeasured check rather than removing it."
            )
        if not hf.mutation_score_json:
            raise HostFnError(f"{hf.name!r} has no mutation score")
        if not hf.authored_by:
            raise HostFnError(f"{hf.name!r} names no author")
        self._fns[hf.name] = hf

    def freeze(self) -> None:
        self._frozen = True

    @property
    def frozen(self) -> bool:
        return self._frozen

    # -- the snapshot -------------------------------------------------------------
    def bind_snapshot(self, snapshot_sha256: str, records: Mapping[str, Any]) -> None:
        """Bind the ONLY data a snapshot-bound host function may read."""
        if not snapshot_sha256:
            raise HostFnError("a snapshot with no digest cannot be cited in a report")
        self._snapshot_sha256 = snapshot_sha256
        self._records = dict(records)

    @property
    def snapshot_sha256(self) -> str | None:
        return self._snapshot_sha256

    def lookup(self, key: str) -> Any:
        if self._snapshot_sha256 is None:
            raise SnapshotMissing(
                "no register snapshot is bound. The call does not fall back to a live fetch: a "
                "verdict that depends on what a remote endpoint said at run time cannot be "
                "re-derived from the filing's bytes."
            )
        return self._records.get(key)

    # -- use ----------------------------------------------------------------------
    def get(self, name: str) -> HostFn:
        if name not in self._fns:
            raise UnregisteredHostFn(
                f"{name!r} is not in the host-function registry "
                f"({sorted(self._fns) or 'the registry is empty'})"
            )
        return self._fns[name]

    def names(self) -> frozenset[str]:
        return frozenset(self._fns)

    def bindings(self) -> dict[str, Callable[..., Any]]:
        """The `{name: callable}` map celpy is handed. Refuses to produce one before freezing."""
        if not self._frozen:
            raise RegistryNotFrozen(
                "the host-function set must be CLOSED before anything is evaluated; call freeze()"
            )
        return {name: hf.fn for name, hf in self._fns.items()}


def vectors_path(name: str) -> Path:
    return VECTORS_DIR / f"{name}.vectors.json"


def vector_digest(name: str) -> str:
    """sha256 of the published vector file's exact bytes. A vector nobody can hash is not published."""
    p = vectors_path(name)
    if not p.is_file():
        raise HostFnError(
            f"{name!r} has no published vectors at {p.name}. `register` refuses it, which is what "
            "makes 'every host function has test vectors' a property rather than a plan."
        )
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_vectors(name: str) -> list[dict[str, Any]]:
    return json.loads(vectors_path(name).read_text(encoding="utf-8"))["vectors"]


def default_registry(*, frozen: bool = True) -> HostFnRegistry:
    """Every host function this build ships, registered and frozen.

    Imported here rather than at module top so that `cdfc.predicates.host_fns` can be imported by
    the registry's own tests without pulling in every implementation.
    """
    from cdfc.predicates.host_fns import (
        gstin_valid,
        nav_interval,
        reg_resolves,
        sum_units,
        template_current,
    )

    reg = HostFnRegistry()
    for mod in (sum_units, reg_resolves, gstin_valid, template_current, nav_interval):
        mod.register_into(reg)
    if frozen:
        reg.freeze()
    return reg
