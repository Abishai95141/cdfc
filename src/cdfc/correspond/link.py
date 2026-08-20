"""A1c use 3 — record ↔ record across documents. Fellegi-Sunter, with weights DERIVED by EM.

**The weights are not a knob and that is the whole reason this is not a similarity threshold.**
`W0-C` measured what happens when a similarity judgement is trusted: values DELETED from the corpus
came back SUPPORTED **20 of 20**, at every threshold tried. A threshold is a number somebody
chooses until the demo passes. A Fellegi-Sunter weight is *estimated from the data itself*:

    m(f) = P(field f agrees | the pair IS a match)
    u(f) = P(field f agrees | the pair is NOT a match)
    w(f) = log2(m/u) when it agrees, log2((1-m)/(1-u)) when it disagrees

Expectation-maximisation fits `m`, `u` and the match prevalence `λ` with **no labelled pairs**,
which is why this is the one part of the identity half that does not wait on a human labeller.

**Splink implements exactly this and we do not import it.** That is a closure decision, not a
quality claim: Splink brings duckdb and pandas into the closure of code that decides which record
is which, and `cdfc.correspond` is reachable from a coverage number. The algorithm is a hundred
lines and `docs/measurements/N4-*.md` is where ours is scored rather than asserted.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Comparison:
    """One field the linkage compares, and how it decides agreement."""

    name: str
    agree: Callable[[str, str], bool]


def exact(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold() and bool(a.strip())


def numeric(a: str, b: str) -> bool:
    """Equality after grouping separators. NOT tolerance -- a tolerance is a threshold."""
    def n(x: str) -> str:
        x = x.strip().replace(",", "").replace(" ", "")
        return x.rstrip("0").rstrip(".") if "." in x else x
    return bool(n(a)) and n(a) == n(b)


@dataclass(frozen=True, slots=True)
class Weights:
    """What EM estimated. Published, because a derived weight nobody can see is still a knob."""

    m: tuple[float, ...]
    u: tuple[float, ...]
    prevalence: float
    iterations: int
    converged: bool

    def score(self, gamma: Sequence[bool]) -> float:
        """The log2 match weight for one agreement vector."""
        total = 0.0
        for agreed, mi, ui in zip(gamma, self.m, self.u):
            if agreed:
                total += math.log2(max(mi, 1e-9) / max(ui, 1e-9))
            else:
                total += math.log2(max(1 - mi, 1e-9) / max(1 - ui, 1e-9))
        return total


@dataclass(frozen=True, slots=True)
class Linkage:
    pairs: tuple[tuple[int, int, float], ...]      # (left index, right index, weight)
    weights: Weights
    ambiguous: tuple[tuple[int, int, int], ...] = field(default_factory=tuple)
    left_total: int = 0
    right_total: int = 0
    # EVERY left record that got no pair, with why. A record that is neither linked nor refused
    # has been DROPPED, and a linkage that drops records silently reports a coverage it does not
    # have. Found by a test where all three comparisons were worthless (m == u), every score was
    # exactly zero, and the result was neither a pair nor a refusal but nothing at all.
    unlinked: tuple[tuple[int, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        seen = len(self.pairs) + len(self.ambiguous) + len(self.unlinked)
        if self.left_total and seen != self.left_total:
            raise ValueError(
                f"{seen} of {self.left_total} left records accounted for. A linkage whose states "
                "do not partition its input has lost records silently."
            )

    def lines(self) -> tuple[str, ...]:
        out = [
            f"left records      {self.left_total}",
            f"right records     {self.right_total}",
            f"LINKED            {len(self.pairs)} of {min(self.left_total, self.right_total)}",
            f"  ambiguous, refused  {len(self.ambiguous)}",
            f"EM  iterations {self.weights.iterations}  converged {self.weights.converged}",
            f"    prevalence {self.weights.prevalence:.4f}",
        ]
        out.append(f"  unlinked            {len(self.unlinked)}")
        out += [f"    m={m:.4f} u={u:.4f}" for m, u in zip(self.weights.m, self.weights.u)]
        return tuple(out)


def _gammas(left: Sequence[dict], right: Sequence[dict],
            comparisons: Sequence[Comparison]) -> list[tuple[int, int, tuple[bool, ...]]]:
    out = []
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out.append((i, j, tuple(c.agree(str(a.get(c.name, "")), str(b.get(c.name, "")))
                                    for c in comparisons)))
    return out


def estimate(gammas: Sequence[tuple[int, int, tuple[bool, ...]]], k: int,
             *, max_iter: int = 200, tol: float = 1e-7) -> Weights:
    """EM over the agreement vectors. No labels, no thresholds, no starting knob that matters.

    The initialisation is deliberately uninformative -- m high, u low, prevalence at the rate a
    one-to-one linkage would imply -- so the fit is driven by the data. A run that does not
    converge says so rather than returning its last guess as an answer.
    """
    m = [0.9] * k
    u = [0.1] * k
    lam = 0.5 / max(1, int(math.sqrt(len(gammas))) or 1)
    converged = False
    it = 0
    prev_ll = float("-inf")
    for it in range(1, max_iter + 1):
        # E step: the posterior that each pair is a match.
        posts = []
        for _i, _j, g in gammas:
            pm = lam
            pu = 1 - lam
            for agreed, mi, ui in zip(g, m, u):
                pm *= mi if agreed else (1 - mi)
                pu *= ui if agreed else (1 - ui)
            posts.append(pm / (pm + pu) if (pm + pu) > 0 else 0.0)
        # M step.
        tot = sum(posts) or 1e-9
        new_lam = tot / len(posts)
        new_m, new_u = [], []
        for f in range(k):
            am = sum(p for p, (_i, _j, g) in zip(posts, gammas) if g[f])
            au = sum((1 - p) for p, (_i, _j, g) in zip(posts, gammas) if g[f])
            new_m.append(min(max(am / tot, 1e-6), 1 - 1e-6))
            new_u.append(min(max(au / max(len(posts) - tot, 1e-9), 1e-6), 1 - 1e-6))
        m, u, lam = new_m, new_u, new_lam

        # CONVERGE ON THE LOG-LIKELIHOOD, not on an absolute parameter delta.
        #
        # The delta test never cleared and the reason is instructive: `u` for a near-unique field
        # is squeezed toward its floor and keeps shrinking by amounts that are tiny in absolute
        # terms and large in relative ones, so a single absolute tolerance cannot serve parameters
        # spanning six orders of magnitude. The fit itself was fine -- m moved 0.7071 to 0.7053
        # over 150 wasted iterations -- but "converged: False" on a sound fit is a result nobody
        # should trust, and trusting it anyway is how a number with no warrant gets published.
        #
        # EM monotonically increases the observed-data log-likelihood, so that is the quantity
        # with a guarantee attached. It is scale-free across parameters by construction.
        ll = 0.0
        for _i, _j, g in gammas:
            pm, pu = lam, 1 - lam
            for agreed, mi, ui in zip(g, m, u):
                pm *= mi if agreed else (1 - mi)
                pu *= ui if agreed else (1 - ui)
            ll += math.log(max(pm + pu, 1e-300))
        if abs(ll - prev_ll) < tol * max(1.0, abs(ll)):
            converged = True
            break
        prev_ll = ll
    return Weights(m=tuple(m), u=tuple(u), prevalence=lam, iterations=it, converged=converged)


def link(left: Sequence[dict], right: Sequence[dict], comparisons: Sequence[Comparison],
         *, margin: float = 1.0) -> Linkage:
    """One-to-one linkage. **A tie within `margin` bits is REFUSED, never broken arbitrarily.**

    `margin` is in log2 units of evidence, so it is a statement about how much better the winner
    must be, not a similarity cut-off. Two candidates of comparable weight is the same hazard as
    two pinned blanks sharing a sheet set.
    """
    gammas = _gammas(left, right, comparisons)
    w = estimate(gammas, len(comparisons))
    scored = sorted(((w.score(g), i, j) for i, j, g in gammas), reverse=True)

    taken_l: set[int] = set()
    taken_r: set[int] = set()
    best_for_l: dict[int, list[float]] = {}
    for s, i, _j in scored:
        best_for_l.setdefault(i, []).append(s)

    pairs: list[tuple[int, int, float]] = []
    ambiguous: list[tuple[int, int, int]] = []
    for s, i, j in scored:
        if i in taken_l or j in taken_r:
            continue
        if s <= 0:
            # No evidence FOR the pair. Not a near miss -- the agreement pattern is as likely
            # between two unrelated records as between two records of the same entity.
            continue
        runners = best_for_l.get(i, [])
        second = runners[1] if len(runners) > 1 else float("-inf")
        if s - second < margin:
            ambiguous.append((i, j, len([r for r in runners if s - r < margin])))
            taken_l.add(i)
            continue
        pairs.append((i, j, s))
        taken_l.add(i)
        taken_r.add(j)

    decided = {i for i, _j, _s in pairs} | {i for i, _j, _n in ambiguous}
    unlinked = tuple(
        (i, "no candidate carries positive evidence" if not best_for_l.get(i)
            or max(best_for_l[i]) <= 0 else "every candidate was already taken")
        for i in range(len(left)) if i not in decided)
    return Linkage(pairs=tuple(sorted(pairs)), weights=w, ambiguous=tuple(ambiguous),
                   left_total=len(left), right_total=len(right), unlinked=unlinked)
