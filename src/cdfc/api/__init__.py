"""P14-B3 — the `/v1/*` API. **A transport, not a verdict surface.**

## Why this is `cdfc.api` and not `cdfc.surface.api`, which is where `plan/07` puts it

`cdfc.surface` is a VERDICT ROOT. `plan/06` P13-B0 bans `socket`, `httpx`, `http.client` and
`urllib.request` from the import closure of every verdict root, and enforces it with an AST walk
plus a run under a patched `socket.socket`. FastAPI reaches `socket` through starlette/anyio, and
its TestClient needs `httpx`. Putting the API where the plan says would have made
`test_nc__A04a_no_model_import_reachable` unpassable **by construction**, and nothing would have
noticed today only because B0 is not written yet.

Two things follow, and both are deviations recorded rather than taken quietly:

1. **The package is `cdfc.api`.** An API is a transport. The report renderer stays in
   `cdfc.surface` and keeps its clean closure.
2. **There is no FastAPI and no pydantic.** `app.dispatch()` is a pure function from a `Request`
   to a `Response`; it opens no socket, and a socket appears only in `serve.py`, which is not
   imported by anything under test. This is B1's argument applied again: Jinja was refused because
   its escaping is a constructor argument and "a flag is what somebody sets on a Friday", and
   pydantic's `extra="forbid"` is the same shape of promise. Here the schema is GENERATED from the
   dataclasses and walked by the gate, so the prohibition is a property of the emitted document
   rather than of a keyword somebody remembered.

The cost is real and is not hidden: no automatic OpenAPI from type hints, no dependency-injection,
no async. The plan's own note applies — at 3.4 filings per working day a throughput target would
be theatre — and the deterministic core is ~30 ms.
"""
