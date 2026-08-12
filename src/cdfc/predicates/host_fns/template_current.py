"""`template_current(string) -> bool` — is this digest one of the pinned blanks?

The check a harvested predicate needs when its relation was derived from a specific template
version: a filing prepared on last quarter's blank may satisfy every relation this quarter's blank
encodes and still be answering a different form.

The pinned set is read from `fixtures/prescribed/MANIFEST.json` — the same hash-verified vendored
corpus every other reading is validated against, never from the filing.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from celpy import celtypes

from cdfc.predicates.host_fns import HostFn, vector_digest

NAME = "template_current"
VERSION = "1"
SIGNATURE = "template_current(string) -> bool"

_MANIFEST = Path(__file__).resolve().parents[4] / "fixtures" / "prescribed" / "MANIFEST.json"


@lru_cache(maxsize=1)
def pinned_digests() -> frozenset[str]:
    data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    return frozenset(f["sha256"] for f in data["files"])


def template_current(value: Any) -> Any:
    return celtypes.BoolType(str(value) in pinned_digests())


def register_into(reg: Any) -> None:
    reg.register(HostFn(
        name=NAME, version=VERSION, signature=SIGNATURE, returns_tristate=False,
        fn=template_current, test_vector_sha256=vector_digest(NAME),
        mutation_score_json=f"reports/host_fns/{NAME}.mutation.json",
        authored_by="cdfc P4-B3",
    ))
