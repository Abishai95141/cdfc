"""Hypothesis profiles for the relational suite (P9-B3).

`fast` is CI stage 5's budget and the default. The spec's argument, in integers: of the mutations
a search of this shape finds, 55 of every 100 fall to a single input and 76 of every 100 to the
first twenty. This input space is small and fixed. `deep` runs nightly and is advisory.

`derandomize=True` is the load-bearing setting. Hypothesis is a **search**, and a search with an
unpinned seed makes the report irreproducible in exactly the way P11 must refuse. The seed is an
input recorded in `run.manifest.probe_seed`, and `verify` replays it.
"""

from __future__ import annotations

from hypothesis import HealthCheck, settings

settings.register_profile(
    "fast",
    max_examples=50,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
settings.register_profile(
    "deep",
    max_examples=1_000,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
settings.load_profile("fast")
