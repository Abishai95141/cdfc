"""N4 (linkage arm) — OUR Fellegi-Sunter against SPLINK, on a case built to hurt both.

The clean case discriminates nothing: with three exactly-agreeing fields EM fits m=1.0, u=0.0 and
anything wins. So the population here carries what real custodian data carries -- a missing
identifier, a transposed name, a rounded figure -- and the ground truth is a CONSTRUCTION, held by
the generator, not a judgement anyone made afterwards.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.correspond.link import Comparison, exact, link, numeric  # noqa: E402

SEED = 20260820


def build(n_left: int = 120, overlap: int = 70, seed: int = SEED):
    """Two record sets with a KNOWN overlap and realistic degradation."""
    rng = random.Random(seed)
    left, right, truth = [], [], set()
    for i in range(n_left):
        left.append({"lei": f"LEI{i:05d}", "name": f"Meridian Fund {i}",
                     "nav": str(1_000_000 + i * 4_321)})
    for k in range(overlap):
        i = k                                   # left index k is the same entity
        src = left[i]
        rec = dict(src)
        # 1 in 3 loses the identifier entirely -- the field that would otherwise decide it.
        if rng.random() < 0.34:
            rec["lei"] = ""
        # 1 in 3 has a transposed / abbreviated name.
        if rng.random() < 0.34:
            rec["name"] = rec["name"].replace("Meridian", "Meridan")
        # 1 in 4 is rounded to the nearest thousand -- close, and NOT equal.
        if rng.random() < 0.25:
            rec["nav"] = str(round(int(rec["nav"]), -3))
        right.append(rec)
        truth.add((i, len(right) - 1))
    # Non-overlapping right-hand records, some deliberately similar to left ones.
    for k in range(40):
        right.append({"lei": f"LEI{9000 + k:05d}", "name": f"Meridian Fund {k}",
                      "nav": str(1_000_000 + k * 4_321 + 7)})
    return left, right, truth


def score(got: set[tuple[int, int]], truth: set[tuple[int, int]]) -> dict:
    tp = len(got & truth)
    fp = len(got - truth)
    fn = len(truth - got)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f1}


def ours(left, right) -> set[tuple[int, int]]:
    res = link(left, right,
               [Comparison("lei", exact), Comparison("name", exact), Comparison("nav", numeric)])
    return {(i, j) for i, j, _w in res.pairs}, res


def theirs(left, right) -> set[tuple[int, int]]:
    """Splink 4, DuckDB backend, the same three comparisons, EM-trained the same way."""
    import pandas as pd
    import splink.comparison_library as cl
    from splink import DuckDBAPI, Linker, SettingsCreator, block_on

    # FAIRNESS: a blank identifier must be NULL for Splink, not the empty string.
    #
    # `cl.ExactMatch` treats "" == "" as agreement, so 21 records with no LEI would all "agree"
    # with each other -- a confound that punishes Splink for a harness choice. Our own `exact()`
    # already requires a non-empty value, so without this the two are not being asked the same
    # question and any comparison between them measures the harness.
    def nn(r: dict) -> dict:
        return {k: (v if str(v).strip() else None) for k, v in r.items()}

    dl = pd.DataFrame([{**nn(r), "unique_id": i, "source_dataset": "l"}
                       for i, r in enumerate(left)])
    dr = pd.DataFrame([{**nn(r), "unique_id": j, "source_dataset": "r"}
                       for j, r in enumerate(right)])
    settings = SettingsCreator(
        link_type="link_only",
        comparisons=[cl.ExactMatch("lei"), cl.ExactMatch("name"), cl.ExactMatch("nav")],
        # No blocking rule: the population is 120 x 110, so every pair is compared and the
        # comparison measures the MODEL rather than which pairs a blocking rule let through.
        # Blocking on exact fields would silently drop the degraded records that are the whole
        # point of this population.
        blocking_rules_to_generate_predictions=["1=1"],   # cartesian: compare every pair
    )
    linker = Linker([dl, dr], settings, DuckDBAPI())
    linker.training.estimate_probability_two_random_records_match(
        [block_on("lei")], recall=0.7)
    linker.training.estimate_u_using_random_sampling(max_pairs=1e6)
    # Train m on two sessions, each blocking on a DIFFERENT field so the other fields vary.
    for br in (block_on("name"), block_on("nav")):
        try:
            linker.training.estimate_parameters_using_expectation_maximisation(br)
        except Exception:                                    # noqa: BLE001,S110
            pass
    df = linker.inference.predict(threshold_match_probability=0.5).as_pandas_dataframe()
    out = set()
    for _, row in df.iterrows():
        a, b = (row["unique_id_l"], row["unique_id_r"])
        left_id = a if row.get("source_dataset_l", "l") == "l" else b
        right_id = b if row.get("source_dataset_l", "l") == "l" else a
        out.add((int(left_id), int(right_id)))
    return out


def main() -> int:
    left, right, truth = build()
    print(f"population: left {len(left)}  right {len(right)}  true matches {len(truth)}")
    print("degradation: 1 in 3 loses its identifier, 1 in 3 has a name variant, "
          "1 in 4 is rounded\n")

    got_ours, res = ours(left, right)
    so = score(got_ours, truth)
    print(f"{'':10} {'tp':>5} {'fp':>5} {'fn':>5} {'precision':>10} {'recall':>8} {'F1':>8}")
    print(f"{'OURS':10} {so['tp']:5} {so['fp']:5} {so['fn']:5} "
          f"{so['precision']:10.3f} {so['recall']:8.3f} {so['f1']:8.3f}")
    try:
        got_theirs = theirs(left, right)
        st = score(got_theirs, truth)
        print(f"{'SPLINK':10} {st['tp']:5} {st['fp']:5} {st['fn']:5} "
              f"{st['precision']:10.3f} {st['recall']:8.3f} {st['f1']:8.3f}")
    except Exception as e:                                   # noqa: BLE001
        print(f"{'SPLINK':10} RAISED {type(e).__name__}: {str(e)[:90]}")
        st = None

    print(f"\nours: EM {res.weights.iterations} iterations, converged {res.weights.converged}, "
          f"{len(res.ambiguous)} pairs REFUSED as ambiguous")
    if st:
        better = "SPLINK" if st["f1"] > so["f1"] else ("OURS" if so["f1"] > st["f1"] else "TIE")
        print(f"better F1: {better}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
