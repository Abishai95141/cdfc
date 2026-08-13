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

from cdfc.qualify.campaign import Campaign, CampaignArithmeticError, ClassTally
from cdfc.qualify.fault_model import FAULT_MODEL_VERSION

CAMPAIGNS: Path = Path("reports/campaigns")


class CampaignNotFound(LookupError):
    """The campaign a qualification cites is not on disk. Never substituted."""


@dataclass(frozen=True, slots=True)
class StoredCampaign:
    campaign: Campaign
    #  predicate_id -> fault_class -> number of OBSERVABLE mutants of that class it killed
    kills_by_predicate: Mapping[str, Mapping[str, int]]
    #  predicate_id -> the mutant digests it killed. MARGINAL KILL IS A SET DIFFERENCE, not a
    #  difference of two counts: `|kills(p)| - |kills(B0)|` can be negative while `p` still
    #  catches mutants `B0` misses, and it is the mutants `B0` misses that make `p` worth having.
    mutants_by_predicate: Mapping[str, frozenset[str]]
    #  mutant digest -> its fault class, so a baseline's kill set can be tallied per class
    class_of_mutant: Mapping[str, str]
    commit: str  # the commit the campaign id resolves to, for the ancestry check (F1)
    n_killed_rows: int

    def kills(self, predicate_id: str, fault_class: str) -> int:
        return self.kills_by_predicate.get(predicate_id, {}).get(fault_class, 0)

    def mutants(self, predicate_id: str) -> frozenset[str]:
        return self.mutants_by_predicate.get(predicate_id, frozenset())

    def mutants_in(self, digests: frozenset[str], classes: Sequence[str]) -> frozenset[str]:
        keep = set(classes)
        return frozenset(d for d in digests if self.class_of_mutant.get(d) in keep)

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
    )

    kills: dict[str, dict[str, int]] = {}
    mutants: dict[str, set[str]] = {}
    class_of: dict[str, str] = {}
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
        class_of[row["mutant_sha256"]] = row["fault_class"]
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
        class_of_mutant=dict(sorted(class_of.items())),
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
