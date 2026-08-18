"""P14-B3 — the route table. **One declaration, read by the app, the auth test and the OpenAPI.**

`plan/07` fixes ~18 paths and requires that the token test be *table-driven over the route table*
rather than over a hand-written list. That is the whole reason this module exists separately: a
mutating path added without a token must fail the build, and it can only do that if the test and
the dispatcher read the SAME object. A second list would be a list that drifts.

**`mutating` is declared per route, not inferred from the method.** Inferring it from `POST` looks
equivalent and is not: the inference is a rule about HTTP, and what needs guarding is a rule about
*this system* — whether the call changes something an operator is accountable for. A future
`POST /v1/verify` that only recomputes and compares would be a POST that mutates nothing, and a
method-derived rule would demand a token for it while teaching everyone that the token is noise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Route:
    method: str
    path: str
    handler: str          # the name of the function in `handlers`
    mutating: bool        # requires an operator bearer token
    summary: str


ROUTES: Final[tuple[Route, ...]] = (
    Route("POST", "/v1/filings", "post_filings", False,
          "submit a filing; 413 over cap, 415 non-zip, 422 template_unbound with the COMPUTED "
          "fingerprint, 501 when it binds because no run happens over HTTP"),
    Route("GET", "/v1/runs/{id}", "get_run", False, "the full run record"),
    Route("GET", "/v1/runs/{id}/checks", "get_checks", False, "?state=&reason=&predicate_id="),
    Route("GET", "/v1/runs/{id}/cells", "get_cells", False, "the closure table"),
    Route("GET", "/v1/runs/{id}/report.html", "get_report", False, "byte-identical to disk"),
    Route("GET", "/v1/runs/{id}/attestation.json", "get_attestation", False, "the signed payload"),
    Route("GET", "/v1/runs/{id}/log.jsonl", "get_log", False, "the run log"),
    Route("GET", "/v1/runs/{id}/unchecked", "get_unchecked", False, "the panel, grouped"),
    Route("POST", "/v1/runs/{id}/overrides", "post_overrides", True,
          "operator token; BOTH states retained, counted separately"),
    Route("POST", "/v1/verify", "post_verify", False,
          "501; re-derivation is a command-line tool and is not wired to a request"),
    Route("GET", "/v1/templates", "get_templates", False,
          "the nine pinned blanks and their real digests; NO settledFractionCeiling field, "
          "because none is computed per template in this build"),
    Route("GET", "/v1/templates/{sha}/schema", "get_template_schema", False,
          "404 for an unpinned sha, 501 for a pinned one: no induced schema is served here"),
    Route("POST", "/v1/templates", "post_templates", True,
          "operator token; 501, template admission is not implemented in this build"),
    Route("GET", "/v1/predicates", "get_predicates", False,
          "the qualification block incl. g4_corpus_provenance. Public by design"),
    Route("GET", "/v1/predicates/{id}/versions/{v}", "get_predicate_version", False, "one version"),
    Route("GET", "/v1/rejections", "get_rejections", False,
          "every candidate a gate refused, with the number that decided it"),
    Route("GET", "/v1/registry/roots", "get_registry_roots", False, "the registry roots"),
    Route("GET", "/v1/funnel", "get_funnel", False,
          "the five-gate attrition funnel; three integers per stage and NOT RUN is a fourth state"),
    Route("GET", "/v1/settled-fraction/history", "get_history", False, "MUST be able to step down"),
    Route("GET", "/v1/churn", "get_churn", False,
          "the template-bump sweep: which predicates stopped settling, and why each one moved"),
    Route("GET", "/v1/portfolio", "get_portfolio", False,
          "the administrator's table. NO TOTAL ROW -- see handlers.get_portfolio"),
    Route("GET", "/v1/healthz", "get_healthz", False, "liveness"),
    Route("GET", "/v1/openapi.json", "get_openapi", False, "the generated document"),
)

MUTATING: Final[tuple[Route, ...]] = tuple(r for r in ROUTES if r.mutating)


def by_method_and_path(method: str, path: str) -> Route | None:
    """Exact match first, then one templated segment at a time. No regex, no ordering surprise."""
    for r in ROUTES:
        if r.method == method and r.path == path:
            return r
    want = path.strip("/").split("/")
    for r in ROUTES:
        if r.method != method:
            continue
        have = r.path.strip("/").split("/")
        if len(have) != len(want):
            continue
        if all(h == w or (h.startswith("{") and h.endswith("}")) for h, w in zip(have, want)):
            return r
    return None


def path_params(route: Route, path: str) -> dict[str, str]:
    have = route.path.strip("/").split("/")
    want = path.strip("/").split("/")
    return {h[1:-1]: w for h, w in zip(have, want) if h.startswith("{") and h.endswith("}")}
