"""P7-B3 — reading a stored campaign back, with PER-PREDICATE kill vectors.

**Why this exists, and it is a correction to the plan's own snippet.** `plan/04` writes G2's
computation as

    K = sum(campaign.by_fault_class[c].K for c in claimed)
    O = sum(campaign.by_fault_class[c].O for c in claimed)

and `by_fault_class[...].K` is the count of mutants killed by **any** predicate. Under that
arithmetic every candidate that reaches G2 gets the SAME score, and the bar — *"is this check good
enough to apply to a regulated filing"* — stops being about the check. The numerator has to be
this predicate's kills.

**So `K` is per-predicate and `O` is per-class, and that asymmetry is the point.** The denominator
is *how many mutants of the classes you claim were observable at all*; the numerator is *how many
of them you caught*. A predicate is measured against the opportunity, not against its own
successes — which is the same discipline `O = G − U − I` enforces one level up.

`killed_by` is written per mutant by P6's campaign runner, so nothing new is measured here: this
module re-reads evidence that is already on disk and committed.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cdfc.predicates.canonical import code_sha256
from cdfc.qualify.campaign import Campaign, CampaignArithmeticError, ClassTally
from cdfc.qualify.fault_model import FAULT_MODEL_VERSION

CAMPAIGNS: Path = Path("reports/campaigns")


class CampaignNotFound(LookupError):
    """The campaign a qualification cites is not on disk. Never substituted."""


class StalePredicateSet(CampaignArithmeticError):
    """The campaign credited predicate ids that no longer denote those predicates."""


def predicate_set_digest(candidates: Sequence[Any]) -> str:
    """A digest over `(id, code_sha256)` for every candidate. **An id is not an identity.**

    `killed.jsonl` credits kills to predicate IDS, and G2 joins them to the current candidate set.
    Ids are re-assigned whenever the harvest changes — P7-B1 added the `<F|V>` construct
    discriminator, P8-B1 removed the wildcard COUNTIF — and after both, 125 of the 126 ids the
    committed campaign credited carried a different `expr`. `P-0009` had been a COUNTIF tally over
    `G54:G63`; it became a vocabulary membership check on a different range, and G2 went on scoring
    it with the tally's evidence.

    Nothing detected it: the only guard on the join was the fault-model version string, and the
    fault model had not moved.
    """
    import hashlib

    h = hashlib.sha256()
    for c in sorted(candidates, key=lambda x: x.id):
        h.update(f"{c.id}\x00{code_sha256(c)}\x00".encode())
    return h.hexdigest()


def assert_predicate_set(stored: "StoredCampaign", candidates: Sequence[Any]) -> None:
    """Refuse a join whose predicates have moved since the campaign was recorded.

    A campaign with no digest is a campaign recorded before this check existed; it raises with
    the command that re-records it rather than being waved through, because "older than the guard"
    is exactly the state the guard exists to catch.
    """
    want = predicate_set_digest(candidates)
    have = stored.campaign.predicate_set_digest
    if not have:
        raise StalePredicateSet(
            f"{stored.campaign.campaign_id} carries no `predicate_set_digest`, so the ids it "
            "credits cannot be shown to denote the predicates being scored. Re-run the campaign "
            "(`make campaign`) — an id is not an identity."
        )
    if have != want:
        raise StalePredicateSet(
            f"{stored.campaign.campaign_id} was recorded against predicate set {have[:12]} and "
            f"this build is {want[:12]}. Every per-predicate kill vector G2 would score is "
            "evidence about a different predicate. Re-run the campaign."
        )


@dataclass(frozen=True, slots=True)
class StoredCampaign:
    campaign: Campaign
    #  predicate_id -> fault_class -> number of OBSERVABLE mutants of that class it killed
    kills_by_predicate: Mapping[str, Mapping[str, int]]
    #  predicate_id -> the mutant digests it killed. MARGINAL KILL IS A SET DIFFERENCE, not a
    #  difference of two counts: `|kills(p)| - |kills(B0)|` can be negative while `p` still
    #  catches mutants `B0` misses, and it is the mutants `B0` misses that make `p` worth having.
    mutants_by_predicate: Mapping[str, frozenset[str]]
    #  mutant digest -> the fault CLASSES it belongs to, so a baseline's kill set can be tallied
    #  per class.
    #
    #  **A SET, and it was a single string.** One seeded workbook can be reached by operators from
    #  two different classes — a blank-out (F05) and a row omission (F07) can produce the same
    #  bytes — so a digest legitimately carries more than one class. Storing one and overwriting
    #  made `mutants_in` return ∅ for any predicate whose only claimed-class kills landed on an
    #  overwritten digest, and it rejected it with `g2.no_margin_over_baselines` — a reason naming
    #  a baseline that was never consulted. Measured on the committed campaign: 48 of 210
    #  observable digests carry two classes, and all 71 of that funnel's no-margin rejections were
    #  this and not a baseline.
    class_of_mutant: Mapping[str, frozenset[str]]
    commit: str  # the commit the campaign id resolves to, for the ancestry check (F1)
    n_killed_rows: int

    def kills(self, predicate_id: str, fault_class: str) -> int:
        return self.kills_by_predicate.get(predicate_id, {}).get(fault_class, 0)

    def mutants(self, predicate_id: str) -> frozenset[str]:
        return self.mutants_by_predicate.get(predicate_id, frozenset())

    def classes_of(self, digest: str) -> frozenset[str]:
        """Every class this digest belongs to. Tolerates the old single-string shape on disk."""
        v = self.class_of_mutant.get(digest)
        if v is None:
            return frozenset()
        return frozenset({v}) if isinstance(v, str) else frozenset(v)

    def mutants_in(self, digests: frozenset[str], classes: Sequence[str]) -> frozenset[str]:
        keep = set(classes)
        return frozenset(d for d in digests if self.classes_of(d) & keep)

    def observable(self, fault_class: str) -> int:
        t = self.campaign.by_fault_class.get(fault_class)
        return t.O if t else 0

    def predicates_that_killed(self) -> tuple[str, ...]:
        return tuple(sorted(self.kills_by_predicate))


def load(campaign_id: str, root: Path = CAMPAIGNS) -> StoredCampaign:
    d = root / campaign_id
    manifest = d / "manifest.json"
    killed = d / "killed.jsonl"
    if not manifest.is_file():
        raise CampaignNotFound(
            f"{campaign_id!r} is not in {root}. A qualification cites a campaign by id and the "
            "campaign is the evidence; substituting another one would score a predicate against "
            "mutants it never saw."
        )
    m = json.loads(manifest.read_text(encoding="utf-8"))
    if m.get("fault_model_version") != FAULT_MODEL_VERSION:
        raise CampaignArithmeticError(
            f"{campaign_id}: campaign ran under fault model {m.get('fault_model_version')!r} and "
            f"this build is {FAULT_MODEL_VERSION!r}. A kill rate is only comparable within one "
            "taxonomy."
        )
    campaign = Campaign(
        campaign_id=m["campaign_id"],
        by_fault_class={k: ClassTally(**v) for k, v in sorted(m["by_fault_class"].items())},
        fault_model_version=m["fault_model_version"],
        fault_model_digest=m.get("fault_model_digest", ""),
        harness_version=m.get("harness_version", ""),
        site_set_digest=m.get("site_set_digest", ""),
        evaluator_version=m.get("evaluator_version", ""),
        base_sha256=m.get("base_sha256", ""),
        sampling_rule=m.get("sampling_rule", ""),
        predicate_set_digest=m.get("predicate_set_digest", ""),
    )

    kills: dict[str, dict[str, int]] = {}
    mutants: dict[str, set[str]] = {}
    class_of: dict[str, set[str]] = {}
    n = 0
    for line in (killed.read_text(encoding="utf-8").splitlines() if killed.is_file() else ()):
        if not line.strip():
            continue
        row = json.loads(line)
        n += 1
        if row.get("observability") != "OBSERVABLE":
            # A mutant nobody could observe cannot credit a predicate. `O = G − U − I` already
            # removes it from the denominator; letting it into a numerator would be the same
            # error with the sign flipped.
            continue
        class_of.setdefault(row["mutant_sha256"], set()).add(row["fault_class"])
        for pid in row.get("killed_by") or ():
            kills.setdefault(pid, {}).setdefault(row["fault_class"], 0)
            kills[pid][row["fault_class"]] += 1
            mutants.setdefault(pid, set()).add(row["mutant_sha256"])

    # THE ARITHMETIC IS CHECKED AGAINST THE MANIFEST, not trusted. A killed.jsonl that disagrees
    # with the tally it was summarised into is two answers to one question, and G2 would be
    # computing over whichever file it happened to read.
    for cls, tal in campaign.by_fault_class.items():
        rows = sum(v.get(cls, 0) for v in kills.values())
        if tal.K == 0 and rows:
            raise CampaignArithmeticError(
                f"{campaign_id}/{cls}: the manifest reports K=0 and killed.jsonl carries {rows} "
                "credit(s). The summary and the evidence disagree."
            )
    return StoredCampaign(
        campaign=campaign,
        kills_by_predicate={k: dict(sorted(v.items())) for k, v in sorted(kills.items())},
        mutants_by_predicate={k: frozenset(v) for k, v in sorted(mutants.items())},
        class_of_mutant={k: frozenset(v) for k, v in sorted(class_of.items())},
        commit=_commit_of(d),
        n_killed_rows=n,
    )


def _commit_of(path: Path) -> str:
    """The commit that last touched this campaign's directory.

    Used by G2's ancestry check (F1): a `claims_fault_classes` commit that is NOT an ancestor of
    this one means the claim was written after seeing the evidence it is scored against. Returns
    `""` outside a git work tree, and `check()` treats that as *unverifiable* rather than as
    *verified* — the two are not the same and only one of them is a pass.
    """
    import subprocess

    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(path)],
            cwd=path.parent.parent.parent if path.exists() else ".",
            capture_output=True, text=True, check=False,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, ValueError):
        return ""
