"""P4-B3 — the fact view a CEL program is evaluated against, instrumented.

**One object does three jobs, and that is deliberate.** Every read of a fact goes through the same
proxy, so the proxy is the only place that needs to (a) count steps, (b) poll the deadline and
(c) record which keys were actually read. Three separate mechanisms would be three things that can
disagree about what happened.

**(c) is the control on the phase's headline number.** `ast_walker.read_keys` is a static
over-approximation, and the settled fraction is only honest if it is a genuine *over*-approximation:
every key a program reads at runtime must be inside the declared set, or pre-flight is guarding the
wrong keys. `observed_keys()` is what makes that checkable rather than asserted —
`tests/differential/test_diff__static_keys_cover_dynamic_reads.py`.

**Blank is not zero, and the distinction is in the fault model.** A blank TEXT or ENUM cell maps to
the empty string, because a predicate must be able to say `r.scheme_type == ""`. A blank numeric
cell is **absent**: there is no integer that means "empty", and mapping it to `0` is exactly F05's
blank-and-zero conflation, which the taxonomy carries as two operators rather than one.
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import Any

from celpy import celtypes

from cdfc.facts.units import Unit

REPEATED = "[*]"


class BudgetExceeded(Exception):
    """Raised INSIDE evaluation and converted to a value by `CelRuntime`. Never escapes it."""

    def __init__(self, kind: str, limit: int, observed: int) -> None:
        self.kind = kind
        self.limit = limit
        self.observed = observed
        super().__init__(f"{kind} budget exceeded: limit {limit}, observed {observed}")


class Meter:
    """Step counter, deadline poll, and read recorder. One per evaluation, never shared."""

    __slots__ = ("steps", "limit", "_deadline", "_poll_every", "reads")

    def __init__(self, *, limit: int, deadline: Callable[[], bool] | None = None) -> None:
        self.steps = 0
        self.limit = limit
        self._deadline = deadline
        # Polled every 64 ticks rather than every tick: the poll is the only non-deterministic
        # thing in the loop, and calling it less often keeps the step count — which IS
        # deterministic — the primary control.
        self._poll_every = 64
        self.reads: set[str] = set()

    def tick(self, n: int = 1) -> None:
        self.steps += n
        if self.steps > self.limit:
            raise BudgetExceeded("steps", self.limit, self.steps)
        if self._deadline is not None and self.steps % self._poll_every == 0 and self._deadline():
            raise BudgetExceeded("wall", -1, self.steps)

    def record(self, path: str) -> None:
        self.reads.add(path)


def _dotted(root: str, path: tuple[str, ...]) -> str:
    return ".".join((root, *path)) if path else root


class _RecMap(celtypes.MapType):
    """A fact-model node. Reading a SCALAR out of it records the key; reading a container does not.

    That asymmetry mirrors `read_keys` exactly: `filing.rows[*].x` already says the collection was
    traversed, so recording `filing.rows` beside it would report a container nobody read as a value.
    """

    def __init__(self, data: Mapping[Any, Any], *, root: str, path: tuple[str, ...], meter: Meter) -> None:
        super().__init__(data)
        object.__setattr__(self, "_root", root)
        object.__setattr__(self, "_path", path)
        object.__setattr__(self, "_meter", meter)

    def __getitem__(self, key: Any) -> Any:
        meter: Meter = object.__getattribute__(self, "_meter")
        meter.tick()
        value = super().__getitem__(key)
        root: str = object.__getattribute__(self, "_root")
        path: tuple[str, ...] = object.__getattribute__(self, "_path")
        child = (*path, str(key))
        if isinstance(value, (_RecMap, _RecList)):
            return value
        if isinstance(value, celtypes.MapType):
            return _RecMap(value, root=root, path=child, meter=meter)
        if isinstance(value, celtypes.ListType):
            return _RecList(value, root=root, path=child, meter=meter)
        meter.record(_dotted(root, child))
        return value

    def __contains__(self, key: Any) -> bool:
        meter: Meter = object.__getattribute__(self, "_meter")
        meter.tick()
        root: str = object.__getattribute__(self, "_root")
        path: tuple[str, ...] = object.__getattribute__(self, "_path")
        present = super().__contains__(key)
        # `has(filing.a.b)` is a presence test on a key, and presence IS the fact it reads.
        meter.record(_dotted(root, (*path, str(key))))
        return present


class _RecList(celtypes.ListType):
    """A repeated node. `size()` records the collection; iteration records nothing by itself."""

    def __init__(self, data: Any, *, root: str, path: tuple[str, ...], meter: Meter) -> None:
        super().__init__(data)
        object.__setattr__(self, "_root", root)
        object.__setattr__(self, "_path", path)
        object.__setattr__(self, "_meter", meter)

    def _wrap(self, value: Any) -> Any:
        meter: Meter = object.__getattribute__(self, "_meter")
        root: str = object.__getattribute__(self, "_root")
        path: tuple[str, ...] = object.__getattribute__(self, "_path")
        starred = (*path[:-1], path[-1] + REPEATED) if path else path
        if isinstance(value, celtypes.MapType):
            return _RecMap(value, root=root, path=starred, meter=meter)
        if isinstance(value, celtypes.ListType):
            return _RecList(value, root=root, path=starred, meter=meter)
        return value

    def _is_leaf_list(self) -> bool:
        """A list of SCALARS is a vocabulary: reading it is reading a value.

        A list of maps is a table body: the values read are its rows' leaves, and recording the
        container beside them would report a key no predicate reads as a value. The distinction
        matches `read_keys` exactly — `template.vocab.scheme_type` is a declared key, and
        `filing.rows` is not when the body reads through the binding.
        """
        for item in list.__iter__(self):
            return not isinstance(item, (celtypes.MapType, celtypes.ListType))
        return True  # an empty list was still read, and its emptiness is the fact

    def _record_self(self) -> None:
        meter: Meter = object.__getattribute__(self, "_meter")
        root: str = object.__getattribute__(self, "_root")
        path: tuple[str, ...] = object.__getattribute__(self, "_path")
        meter.record(_dotted(root, path))

    def __iter__(self) -> Any:
        meter: Meter = object.__getattribute__(self, "_meter")
        if self._is_leaf_list():
            self._record_self()
        for item in list.__iter__(self):
            meter.tick()
            yield self._wrap(item)

    def __contains__(self, value: Any) -> bool:
        # `x in template.vocab.scheme_type` reads the vocabulary. Without this the membership
        # predicate — the whole reason the two-document model exists — recorded no template-side
        # read at all, and the dynamic arm of the both-ways check silently covered nothing.
        meter: Meter = object.__getattribute__(self, "_meter")
        meter.tick()
        self._record_self()
        return list.__contains__(self, value)

    def __getitem__(self, index: Any) -> Any:
        meter: Meter = object.__getattribute__(self, "_meter")
        meter.tick()
        return self._wrap(list.__getitem__(self, index))

    def __len__(self) -> int:
        meter: Meter = object.__getattribute__(self, "_meter")
        meter.tick()
        root: str = object.__getattribute__(self, "_root")
        path: tuple[str, ...] = object.__getattribute__(self, "_path")
        meter.record(_dotted(root, path))
        return list.__len__(self)


def _to_cel(value: Any, unit: Unit | str | None = None) -> Any:
    """One fact to one CEL value. Refuses floats, as every other hashed or compared path does."""
    if isinstance(value, bool):
        return celtypes.BoolType(value)
    if isinstance(value, float):
        raise TypeError(
            "a float reached the fact view. Money is an int64 count of 10^-3 USD Million; a "
            "float here is a tolerance nobody declared."
        )
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise TypeError(f"{value} is not an integer; scale it at the fact-model boundary")
        return celtypes.IntType(int(value))
    if isinstance(value, int):
        if not (-(2**63) <= value < 2**63):
            # celpy raises a bare `ValueError: overflow` with no value in it. A fact model that
            # refuses a number must say which number, or the reader goes looking through 3,747
            # cells for it.
            raise TypeError(
                f"{value} does not fit in int64 and cannot enter the fact model. Money is an "
                "int64 count of 10^-3 USD Million; a quantity this large is a unit error or a "
                "bound copied into a value."
            )
        return celtypes.IntType(value)
    if isinstance(value, _dt.date):
        return celtypes.StringType(value.isoformat())
    if isinstance(value, str):
        return celtypes.StringType(value)
    if value is None:
        # Callers drop absent numeric leaves before reaching here; a None that gets this far is a
        # blank text cell, which is a real value a predicate can test against "".
        return celtypes.StringType("")
    raise TypeError(f"no CEL mapping for {type(value).__name__}")


def _build(node: Any) -> Any:
    if isinstance(node, Mapping):
        return celtypes.MapType({celtypes.StringType(str(k)): _build(v) for k, v in node.items()})
    if isinstance(node, (list, tuple)):
        return celtypes.ListType([_build(v) for v in node])
    return _to_cel(node)


class FactView:
    """One document's facts, as a CEL activation value.

    `tree` is a plain nested mapping of segment -> value | mapping | list. The harvest and the run
    assembly build it from the fact model; nothing here reads a workbook.
    """

    def __init__(self, tree: Mapping[str, Any], *, root: str) -> None:
        if root not in ("filing", "template"):
            raise ValueError(
                f"a fact view binds one of the two document names, not {root!r}. A third name is "
                "a way for a predicate to read something nobody declared."
            )
        self.root = root
        self._cel = _build(tree)

    def bind(self, meter: Meter) -> Any:
        return _RecMap(self._cel, root=self.root, path=(), meter=meter)

    def __repr__(self) -> str:
        return f"FactView(root={self.root!r}, top={sorted(map(str, self._cel))!r})"


# --- the two documents, addressable by the key grammar ---------------------------------------


class FactSet:
    """`filing` and `template`, addressable by D-P4-02's dotted key grammar.

    Pre-flight needs to ask *is `filing.a.b[*].c` present, and what type is it* — over the same
    tree the runtime evaluates against, because a pre-flight that consults a different structure
    guards something other than what runs.

    A `[*]` segment means "every element of this repeated node": present iff the collection exists
    AND every element carries the remaining path. **A repeated node with no elements is PRESENT and
    empty** — that is not a missing key, it is an empty table, and conflating them would make
    pre-flight refuse to run on a filing with no rows rather than letting the predicate see zero.
    """

    def __init__(self, filing: Mapping[str, Any], template: Mapping[str, Any]) -> None:
        self._trees = {"filing": dict(filing), "template": dict(template)}
        self._views: dict[str, FactView] = {}

    def view(self, root: str) -> FactView:
        """Built ONCE per root and reused for the whole run.

        Not an optimisation. `evaluate_one` asks for the views on every predicate, and rebuilding
        the 3,747-cell celtypes tree 351 times exhausted memory and the run was killed. The trees
        are immutable within a run, and the recording proxy is created fresh per evaluation by
        `bind(meter)` — so the cache holds the DATA, never the instrumentation.
        """
        if root not in self._views:
            self._views[root] = FactView(self._trees[root], root=root)  # type: ignore[arg-type]
        return self._views[root]

    def _walk(self, key: str) -> tuple[bool, list[Any]]:
        """`(present, values)` — every value the key resolves to, or `(False, [])`."""
        parts = key.split(".")
        root, segments = parts[0], parts[1:]
        if root not in self._trees:
            return False, []
        nodes: list[Any] = [self._trees[root]]
        for seg in segments:
            repeated = seg.endswith(REPEATED)
            name = seg[: -len(REPEATED)] if repeated else seg
            nxt: list[Any] = []
            for node in nodes:
                if not isinstance(node, Mapping) or name not in node:
                    return False, []
                value = node[name]
                if repeated:
                    if not isinstance(value, (list, tuple)):
                        return False, []
                    nxt.extend(value)
                else:
                    nxt.append(value)
            nodes = nxt
            if not nodes:
                # A repeated node with NO elements. The key is present; there is nothing under it.
                return True, []
        return True, nodes

    def has(self, key: str) -> bool:
        present, _ = self._walk(key)
        return present

    def type_of(self, key: str) -> str | None:
        """`STRING` | `INT` | `LIST` | `BOOL` | **`MIXED`**, or None when the key resolves to
        nothing.

        **`MIXED` was added 14 Aug 2026 and it closes a hang, not a cosmetic gap.** A mixture used
        to return `None`, and `preflight` reads `None` as *"the fact side cannot decide either;
        still presence only"* — so it PROCEEDED. A blind-filled return whose `2. Summary!F` column
        held 45 numbers and 125 numeric STRINGS was therefore handed to the CEL runtime, where
        `c.v >= 0` is a type error on 125 of 170 elements, and evaluating that ONE predicate took
        the process from 85 MB to **6 GB without returning** — with `Budget(steps=2000)` unable to
        stop it, because the step meter only ticks on fact-tree access and the blow-up is inside
        the runtime.
        
        Two individually-reasonable decisions joined into a defect: reporting a mixture as *not one
        type* is right, and reading *not one type* as *proceed* is wrong. **A column that is half
        text cannot satisfy one numeric comparison**, and that is a decidable fact, not an unknown
        one.
        """
        present, values = self._walk(key)
        if not present or not values:
            return None
        kinds = set()
        for v in values:
            if isinstance(v, bool):
                kinds.add("BOOL")
            elif isinstance(v, int):
                kinds.add("INT")
            elif isinstance(v, str):
                kinds.add("STRING")
            elif isinstance(v, (list, tuple)):
                kinds.add("LIST")
            elif isinstance(v, Mapping):
                kinds.add("OBJECT")
            else:
                kinds.add("OTHER")
        if len(kinds) == 1:
            return kinds.pop()
        # NOT None. `None` means *nobody can tell*; this is *we can tell, and they disagree*.
        return "MIXED"
