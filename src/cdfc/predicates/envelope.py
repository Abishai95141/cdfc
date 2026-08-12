"""P4-B1 — the predicate envelope, as two types.

**The two types are the admission barrier, expressed as a type rather than as a check.**
A `Candidate` has not been through the gates. Nothing in `cdfc.evaluate` accepts one:
`evaluate_one(p: Predicate, ...)` will not take a `Candidate`, and a `Candidate` has no
`severity_tier` attribute to hand-set. The runtime check in `loader.load_predicate` is kept
though redundant, for the same reason the post-hoc key guard is kept — **it is the one you can
prove to a reviewer.**

**D-P4-01: there is no `REJECTED` state.** `PredicateState` is four-valued. A rejected candidate
never acquires a `predicate_id`; it becomes a rejection row keyed by `candidate_sha256` with
`predicate_id NULL`. A re-submitted candidate gets a new `candidate_sha256`, and ids are never
reused.

**D-P4-06: `claims_fault_classes` is required, non-empty, and on `Candidate`.** It is the field
that stops a predicate choosing its own denominator. G2's bar is `K/O ≥ 0.80` *on the classes the
predicate claims to cover*, and before this field the only place a class appeared was the witness
set G2 itself selects **after** the campaign, from mutants that already killed — the numerator
choosing its denominator at the gate that exists to catch exactly that. It lives on `Candidate`
rather than `Predicate` because a field only `Predicate` carries is a field written after the
campaign.

**D-P4-07 / arbitration C2: `clause_absent_reason` is required exactly when the obligation is a
TEMPLATE obligation.** A harvested candidate implements a relation the regulator's own pinned blank
encodes; it cites no statute, and it must say why. Keyed on the obligation's `source` rather than on
`clause is None`, the field has one instance per harvested candidate instead of zero — and a required
field with no instances is this project's own definition of a green test with no information in it.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Final, Literal, get_args

Kind = Literal["harvested", "proposed", "hand_authored", "relation"]
PredicateState = Literal["ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN"]
Severity = Literal["BLOCKING", "ADVISORY"]
Disposal = Literal["IMPLEMENTED", "DECLARED"]
ObligationSource = Literal["STATUTE", "TEMPLATE"]
WithdrawnReason = Literal[
    "rule_amended", "ffr_exceeded_threshold", "superseded_by", "source_schema_changed"
]

ClauseAbsentReason = Literal[
    "derived_from_template_formula",  # an <f> element in the pinned blank
    "derived_from_data_validation",  # a dataValidation in the pinned blank
    "derived_from_template_constant",  # a vocabulary or constant
]

KINDS: Final[frozenset[str]] = frozenset(get_args(Kind))
PREDICATE_STATES: Final[tuple[str, ...]] = get_args(PredicateState)
SEVERITIES: Final[frozenset[str]] = frozenset(get_args(Severity))
DISPOSALS: Final[frozenset[str]] = frozenset(get_args(Disposal))
OBLIGATION_SOURCES: Final[frozenset[str]] = frozenset(get_args(ObligationSource))
CLAUSE_ABSENT_REASONS: Final[frozenset[str]] = frozenset(get_args(ClauseAbsentReason))
WITHDRAWN_REASONS: Final[frozenset[str]] = frozenset(get_args(WithdrawnReason))


class EnvelopeSchemaError(ValueError):
    """The envelope is not admissible. Never repaired, never defaulted."""


@dataclass(frozen=True, slots=True)
class Proviso:
    text: str
    disposal: Disposal
    emits: str | None
    span: tuple[int, int]


@dataclass(frozen=True, slots=True)
class Clause:
    instrument: str
    eId: str
    span: tuple[int, int]
    quote: str
    provisos: tuple[Proviso, ...] = ()


@dataclass(frozen=True, slots=True)
class Tolerance:
    """`τ` per summand, in `MILLI_USD_MILLION` units. An INTEGER count, never a percentage.

    A relative tolerance on a total of zero admits everything, and totals of zero are the modal
    case in this corpus. `None` — not `0` — is the right value for a non-arithmetic predicate;
    they are different facts and the schema keeps them apart.
    """

    tau_units_per_summand: int

    def __post_init__(self) -> None:
        if isinstance(self.tau_units_per_summand, bool) or not isinstance(
            self.tau_units_per_summand, int
        ):
            raise EnvelopeSchemaError(
                "tolerance is an integer count of MILLI_USD_MILLION units; a float here is "
                "baked into a content address and can never be re-derived"
            )
        if self.tau_units_per_summand < 0:
            raise EnvelopeSchemaError("a tolerance cannot be negative")


@dataclass(frozen=True, slots=True)
class ExternalDep:
    endpoint: str
    field: str
    snapshot: str
    on_missing: str


@dataclass(frozen=True, slots=True)
class Qualification:
    """Written by the qualification pipeline (P7). Never hand-edited.

    Its presence is what separates a `Predicate` from a `Candidate`, so the fields that carry
    the measured rates are required here rather than optional.
    """

    campaign_id: str
    kill_rate_claimed: str  # "K/O" as two integers, e.g. "37/41" — never a rounded float
    kill_rate_all_classes: str  # the same predicate over all fourteen classes
    false_failure_rate: str  # "f/n" over the blind-fill corpus
    qualified_at: str  # ISO date, an ARGUMENT to the pipeline, never a clock read here


@dataclass(frozen=True, slots=True)
class QualifiedAgainst:
    """Every element is part of the predicate's IDENTITY.

    A predicate qualified against one evaluator, fault model and corpus is not the same predicate
    when any of the three moves. Putting them inside the digest is what makes that true
    mechanically instead of by convention.
    """

    evaluator_version: str
    fault_model_version: str
    corpus_sha256: str
    template_sha256: str


@dataclass(frozen=True, slots=True)
class Candidate:
    """A predicate that has NOT been through the gates. Barrier 3, expressed as a type."""

    id: str
    version: int
    kind: Kind
    template: str
    schema_keys: tuple[str, ...]
    host_fns: tuple[str, ...]
    obligation_id: str
    obligation_source: ObligationSource
    clause: Clause | None
    rationale: str
    clause_absent_reason: ClauseAbsentReason | None
    claims_fault_classes: tuple[str, ...]
    applicable: str
    expr: str
    witness: str
    reason_if_inapplicable: str
    tolerance: Tolerance | None
    external_deps: tuple[ExternalDep, ...] = ()

    def __post_init__(self) -> None:
        _validate_common(self)


@dataclass(frozen=True, slots=True)
class Predicate(Candidate):
    """A candidate that carries its qualification. The only type the run path accepts."""

    # Declared with defaults only because a frozen dataclass may not follow a defaulted field
    # with a non-defaulted one; `__post_init__` refuses every one of these sentinels, so the
    # defaults are unreachable rather than permissive.
    qualification: Qualification | None = None
    qualified_against: QualifiedAgainst | None = None
    severity_tier: Severity | None = None
    state: PredicateState | None = None
    withdrawn_reason: WithdrawnReason | None = None

    def __post_init__(self) -> None:
        _validate_common(self)
        if self.qualification is None:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r} carries no qualification record. A predicate whose "
                "error rate is unknown is not admitted — which is what makes the "
                "settled-fraction claim true by construction rather than by discipline."
            )
        if self.qualified_against is None:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r} does not say what it was qualified against. The "
                "evaluator, the fault model and the corpus are part of its identity."
            )
        if self.severity_tier not in SEVERITIES:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r}: severity_tier must be one of {sorted(SEVERITIES)}; "
                "it is set by the measured false-failure rate, never by hand"
            )
        if self.state not in PREDICATE_STATES:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r}: state must be one of {list(PREDICATE_STATES)} "
                "(D-P4-01: four states, and REJECTED is not one of them)"
            )
        if self.state == "WITHDRAWN" and self.withdrawn_reason is None:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r} is WITHDRAWN with no reason. A withdrawal nobody can "
                "explain is indistinguishable from a predicate that was quietly deleted."
            )
        if self.state != "WITHDRAWN" and self.withdrawn_reason is not None:
            raise EnvelopeSchemaError(
                f"predicate {self.id!r} carries a withdrawn_reason but is {self.state}"
            )


def _validate_common(c: Candidate) -> None:
    from cdfc.predicates.fault_model import FaultModelError, known_ids

    if not c.id:
        raise EnvelopeSchemaError("a predicate envelope with no id cannot be cited")
    if isinstance(c.version, bool) or not isinstance(c.version, int) or c.version < 1:
        raise EnvelopeSchemaError(f"{c.id!r}: version must be a positive integer")
    if c.kind not in KINDS:
        raise EnvelopeSchemaError(f"{c.id!r}: kind must be one of {sorted(KINDS)}")
    if not c.template:
        raise EnvelopeSchemaError(f"{c.id!r}: no template digest; a predicate is bound to a blank")
    if not c.schema_keys:
        raise EnvelopeSchemaError(
            f"{c.id!r}: schema_keys is empty. A predicate that declares no footprint settles "
            "no cells, and the settled fraction would count it for free."
        )
    if len(set(c.schema_keys)) != len(c.schema_keys):
        raise EnvelopeSchemaError(f"{c.id!r}: schema_keys contains a duplicate")

    # --- D-P4-06 -----------------------------------------------------------------
    if not c.claims_fault_classes:
        raise EnvelopeSchemaError(
            f"{c.id!r}: claims_fault_classes is required and non-empty. Without a declared "
            "claim, G2's bar is computed over the set the predicate picks after the campaign, "
            "and a predicate that kills one class of one operator scores 1.00."
        )
    if len(set(c.claims_fault_classes)) != len(c.claims_fault_classes):
        raise EnvelopeSchemaError(f"{c.id!r}: claims_fault_classes contains a duplicate")
    try:
        unknown = sorted(set(c.claims_fault_classes) - known_ids())
    except FaultModelError as e:  # the taxonomy itself is unreadable
        raise EnvelopeSchemaError(f"{c.id!r}: {e}") from e
    if unknown:
        raise EnvelopeSchemaError(
            f"{c.id!r}: claims_fault_classes names {unknown}, which is not in the pinned "
            "fault model v3. A claim against a class nobody defined is not a claim."
        )

    # --- D-P4-07 / C2 ------------------------------------------------------------
    if c.obligation_source not in OBLIGATION_SOURCES:
        raise EnvelopeSchemaError(
            f"{c.id!r}: obligation_source must be one of {sorted(OBLIGATION_SOURCES)}"
        )
    if not c.obligation_id:
        raise EnvelopeSchemaError(
            f"{c.id!r}: every candidate carries an obligation_id, harvested included (C2). "
            "A candidate with none takes SKIPPED at G0, and a gate stage that cannot fail is "
            "this product's own failure mode wearing a gate's clothes."
        )
    if c.obligation_source == "TEMPLATE":
        if c.clause is not None:
            raise EnvelopeSchemaError(
                f"{c.id!r}: a TEMPLATE obligation cites no statutory clause, but this "
                "envelope carries one. Only a STATUTE obligation carries a Clause."
            )
        if c.clause_absent_reason not in CLAUSE_ABSENT_REASONS:
            raise EnvelopeSchemaError(
                f"{c.id!r}: a candidate whose obligation is a TEMPLATE obligation must "
                f"declare why it cites no statute, from {sorted(CLAUSE_ABSENT_REASONS)}. "
                "Published as: no harvested predicate yet implements a statutory clause."
            )
    else:
        if c.clause is None:
            raise EnvelopeSchemaError(
                f"{c.id!r}: a STATUTE obligation must carry the Clause it implements"
            )
        if c.clause_absent_reason is not None:
            raise EnvelopeSchemaError(
                f"{c.id!r}: clause_absent_reason explains an ABSENCE. A candidate that cites a "
                "clause has nothing to explain, and annotating one anyway makes the field's "
                "count meaningless."
            )
        for p in c.clause.provisos:
            if p.disposal not in DISPOSALS:
                raise EnvelopeSchemaError(f"{c.id!r}: proviso disposal must be one of {sorted(DISPOSALS)}")
            if p.disposal == "DECLARED" and not p.emits:
                raise EnvelopeSchemaError(
                    f"{c.id!r}: a DECLARED proviso must name what it emits; a declared proviso "
                    "with no emission is an undisposed proviso with a label"
                )

    # --- the three slots ---------------------------------------------------------
    for slot in ("applicable", "expr", "witness"):
        if not getattr(c, slot):
            raise EnvelopeSchemaError(
                f"{c.id!r}: the {slot!r} slot is empty. All three are required: a predicate "
                "with no `applicable` runs everywhere, and one with no `witness` produces a "
                "finding a filer cannot open."
            )
    if not c.reason_if_inapplicable:
        raise EnvelopeSchemaError(
            f"{c.id!r}: reason_if_inapplicable is required. An item that did not run and "
            "cannot say why is a silent skip."
        )
    if not c.rationale:
        raise EnvelopeSchemaError(f"{c.id!r}: rationale is required")


def candidate_fields() -> tuple[str, ...]:
    """The field names of `Candidate`, read at runtime.

    `envelope_projection` is checked against this, so a field added to the record without
    being added to the projection fails a test rather than silently leaving the identity.
    """
    return tuple(f.name for f in fields(Candidate))


def predicate_fields() -> tuple[str, ...]:
    return tuple(f.name for f in fields(Predicate))
