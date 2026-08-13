#!/usr/bin/env python
"""P8-B2 — take ONE pinned snapshot of the IFSCA register's detail endpoint.

    make register-snapshot

**This is a TOOL, not part of the product.** `src/` must never reach the network: a host function
resolves against a SNAPSHOT and never live (NC-X01), because a verdict that depends on what a
remote server said at verdict time is a verdict nobody can re-derive.

**What it fetches and why that is the whole point.** The register's LIST endpoint returns
`RegistrationNumber = null` on 650 of 650 fund rows; only the DETAIL endpoint returns it. So the
snapshot is 229 detail reads keyed by the `EncryptedId` the committed list already carries — and
the trap is on the same payload: `EncryptDId` is `null` on every record while `EncryptedId` is
populated on every record, so a reader that takes the first plausible field gets a 302 on all of
them, for ever.

Polite by construction: one request at a time, a declared User-Agent, a delay between reads, and it
is run ONCE and committed. Nothing here polls.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
LIST = REPO / "research/probe/fme.json"
OUT = REPO / "fixtures/register"
DETAIL = "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet?EncryptedId="
UA = "cdfc-research/1.0 (one-off snapshot for a false-failure-rate measurement)"
FME_SUBCATEGORIES = frozenset(
    {"Registered FME (Non-Retail)", "Registered FME (Retail)", "Authorised FME"}
)
DELAY_S = 0.35

# The fields kept. The detail payload carries ~90 keys of framework scaffolding; a snapshot that
# vendored all of them would be 90% noise and would carry contact emails and addresses this
# measurement has no use for. **Minimising what is stored is part of taking it.**
KEEP = ("Title", "RegistrationNumber", "DateOfRegistration", "ValidityFromDate",
        "ValidityToDate", "DirSubCategoryName", "IsActive")


def live_fmes() -> list[tuple[str, str, str]]:
    rows = json.loads(LIST.read_text(encoding="utf-8"))["data"]
    return [(r["EncryptedId"], (r.get("Title") or "").strip(), r["DirSubCategoryName"])
            for r in rows if r.get("DirSubCategoryName") in FME_SUBCATEGORIES]


def main() -> int:
    ids = live_fmes()
    print(f"{len(ids)} live FMEs in the committed list")
    records, errors = [], []
    for i, (eid, title, sub) in enumerate(sorted(ids), start=1):
        url = DETAIL + urllib.parse.quote(eid, safe="")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 - a pinned https host
                d = json.loads(r.read().decode("utf-8"))
            records.append({"encrypted_id": eid, "list_title": title, "list_subcategory": sub,
                            **{k: d.get(k) for k in KEEP}})
        except Exception as e:  # noqa: BLE001 - a fetch error is RECORDED, never dropped
            errors.append({"encrypted_id": eid, "list_title": title, "error": f"{type(e).__name__}: {e}"})
        if i % 25 == 0:
            print(f"  {i}/{len(ids)}  ok={len(records)} err={len(errors)}")
        time.sleep(DELAY_S)

    payload = {
        "source": "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet",
        "list_source": "research/probe/fme.json (DirectoryGetList, committed)",
        "fetched_by": "tools/corpus/fetch_register.py",
        "note": "A ONE-OFF snapshot. Nothing in src/ reaches the network; a host function resolves "
                "against this file and never live (NC-X01). Fields are minimised to the seven the "
                "measurement uses.",
        "n_attempted": len(ids),
        "n_resolved": len(records),
        "n_errors": len(errors),
        "errors": errors,
        "records": sorted(records, key=lambda r: r["encrypted_id"]),
    }
    blob = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"fme-register__{digest[:8]}.json"
    path.write_text(blob, encoding="utf-8")
    print(f"\nwrote {path.relative_to(REPO)}")
    print(f"  attempted {len(ids)} · resolved {len(records)} · errors {len(errors)}")
    print(f"  sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
