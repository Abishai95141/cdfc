-- migrations/001_qualification.sql — P7-B1. The qualification tables.
--
-- R5 APPEND-ONLY. Supersession is a NEW ROW, never an UPDATE. There are no `UPDATE` statements
-- against `predicate`, `qualification` or `registry_root` anywhere in this system, and
-- `test_registry__append_only` asserts the old row is byte-unchanged after a supersession.
--
-- D-P4-01 / E7.3: THERE IS NO `REJECTED` PREDICATE STATE. The enum is four-valued. A rejected
-- candidate never acquires a `predicate_id`; it becomes a `rejection` row keyed by
-- `candidate_sha256` with `predicate_id NULL`. That is asserted in
-- `tests/contract/test_contract_qualification.py::test_contract__no_rejected_predicate_state`
-- rather than believed, because this schema was written on the strength of that belief.

CREATE TABLE IF NOT EXISTS obligation (
    obligation_id  TEXT PRIMARY KEY,
    source         TEXT NOT NULL CHECK (source IN ('STATUTE', 'TEMPLATE')),  -- C2, closed
    instrument_id  TEXT NOT NULL,
    frbr_uri       TEXT,            -- NULL until L1b (P13-B2); ALWAYS NULL for source=TEMPLATE
    eId            TEXT,
    quote          TEXT NOT NULL,   -- VERBATIM
    span_lo        INTEGER NOT NULL,
    span_hi        INTEGER NOT NULL,
    -- HOW THE ROW GOT HERE, which is a different question from what it IS. Neither field is
    -- derived from the other; C2 renamed the original `source` to make room for the discriminator.
    ingest_source  TEXT NOT NULL CHECK (ingest_source IN ('hand', 'l1b', 'harvest')),
    CHECK (span_hi >= span_lo),
    CHECK (source <> 'TEMPLATE' OR frbr_uri IS NULL),
    CHECK (source <> 'TEMPLATE' OR instrument_id LIKE 'template-%'),
    CHECK (source <> 'STATUTE'  OR instrument_id NOT LIKE 'template-%')
);

CREATE TABLE IF NOT EXISTS predicate (
    predicate_id   TEXT NOT NULL,
    version        INTEGER NOT NULL,
    code_sha256    TEXT NOT NULL UNIQUE,
    obligation_id  TEXT NOT NULL REFERENCES obligation(obligation_id),
    -- Four states. REJECTED IS NOT ONE OF THEM.
    state          TEXT NOT NULL CHECK (state IN ('ACTIVE','PROVISIONAL','QUARANTINED','WITHDRAWN')),
    withdrawn_reason TEXT,
    severity_tier  TEXT NOT NULL CHECK (severity_tier IN ('BLOCKING','ADVISORY')),
    admitted_at    TEXT NOT NULL,   -- RFC 3339, an argument, never a clock read
    signer         TEXT NOT NULL,   -- R7. 'UNSIGNED' is a value, and every surface renders it
    signature      BLOB,
    batch_manifest_sha256 TEXT NOT NULL,
    PRIMARY KEY (predicate_id, version),
    CHECK (state <> 'WITHDRAWN' OR withdrawn_reason IS NOT NULL),
    CHECK (state =  'WITHDRAWN' OR withdrawn_reason IS NULL)
);

-- BARRIER 3, in the schema: a predicate row without a qualification row is not loadable.
-- `registry.load()` enforces it at runtime as well, because a foreign key is a lint and the
-- runtime invariant is the one you can demonstrate to a reviewer.
CREATE TABLE IF NOT EXISTS qualification (
    code_sha256    TEXT PRIMARY KEY REFERENCES predicate(code_sha256),
    g0             TEXT NOT NULL,   -- the GateOutcome.measured mapping, verbatim, as JCS
    g1             TEXT NOT NULL,
    g3p            TEXT NOT NULL,
    g2             TEXT NOT NULL,   -- carries BOTH kr_claimed AND kr_all_classes (F1)
    g3e            TEXT NOT NULL,
    g4             TEXT,            -- NULL at P7: the blind-fill corpus arrives at P8
    campaign_id    TEXT NOT NULL,
    qualified_at   TEXT NOT NULL,
    -- Every element is part of the predicate's IDENTITY: a predicate qualified against one
    -- evaluator, fault model and corpus is not the same predicate when any of the three moves.
    evaluator_version   TEXT NOT NULL,
    fault_model_version TEXT NOT NULL,
    corpus_sha256       TEXT NOT NULL,
    template_sha256     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rejection (
    candidate_sha256 TEXT NOT NULL,
    predicate_id     TEXT,          -- NULL. There is no REJECTED predicate state (E7.3).
    obligation_id    TEXT NOT NULL REFERENCES obligation(obligation_id),
    rejecting_gate   TEXT NOT NULL CHECK (rejecting_gate IN ('G0','G1','G3p','G2','G3e','G4')),
    measured         TEXT NOT NULL,
    -- NOT optional and NOT cosmetic: this is what turns a rejection into
    -- no_predicate.failed_qualification and into the report's counterEvidence[].
    cells_would_have_covered INTEGER NOT NULL CHECK (cells_would_have_covered >= 0),
    rejected_at      TEXT NOT NULL,
    PRIMARY KEY (candidate_sha256, rejecting_gate),
    CHECK (predicate_id IS NULL)
);

-- The closed host-function registry (admission rule R2). A reference outside it is
-- `g1.host_fn_unregistered`, not a dynamic lookup.
CREATE TABLE IF NOT EXISTS host_function (
    name           TEXT PRIMARY KEY,
    arity          INTEGER NOT NULL,
    snapshot_sha256 TEXT,           -- a host function never resolves live (NC-Q49)
    registered_at  TEXT NOT NULL
);

-- Merkle over sorted code_sha256. leaf = sha256(0x00 || h); internal = sha256(0x01 || l || r);
-- odd node promoted. DOMAIN SEPARATION IS NOT DECORATION — without it two different admitted sets
-- can share a root and the attestation's registryRoot stops identifying what ran (NC-Q38).
CREATE TABLE IF NOT EXISTS registry_root (
    root           TEXT PRIMARY KEY,
    n_leaves       INTEGER NOT NULL,
    computed_at    TEXT NOT NULL,
    batch_manifest_sha256 TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rejection_gate ON rejection(rejecting_gate);
CREATE INDEX IF NOT EXISTS idx_predicate_obligation ON predicate(obligation_id);
