-- cdfc P5 run store. The FILE is the artifact, so it hashes and can be named in a manifest.
--
-- `run_cell` is materialised from the FIELD SURFACE before any evaluation, never accumulated
-- from the evaluations. That is the structural reason closure cannot have a hole: the table is
-- built from the denominator.

CREATE TABLE IF NOT EXISTS run (
    run_id           TEXT PRIMARY KEY,
    filing_sha256    TEXT NOT NULL,
    template_sha256  TEXT,                     -- NULL on an UNBOUND run
    registry_root    TEXT NOT NULL,
    profile          TEXT NOT NULL,
    profile_digest   TEXT NOT NULL,
    received_at      TEXT NOT NULL,            -- RFC 3339, an ARGUMENT, never a clock read here
    run_state        TEXT NOT NULL,            -- VALID | INVALID
    field_surface    INTEGER,                  -- NULL when the template ships no mask
    keys_checked     INTEGER NOT NULL DEFAULT 0,
    keys_type_checked INTEGER NOT NULL DEFAULT 0
);

-- The run-level vocabulary, SEPARATE from the item-level reason codes. A run may carry more than
-- one cause; they are rows, not a single column, because a report that keeps only the first has
-- lost the others.
CREATE TABLE IF NOT EXISTS run_invalid (
    run_id  TEXT NOT NULL REFERENCES run(run_id),
    cause   TEXT NOT NULL,                     -- one of the eight invalid.* causes
    detail  TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (run_id, cause)
);

-- One row per EVALUATION: (predicate, version, cell). Not per cell — a cell read by three
-- predicates has three rows, and the roll-up is computed from them rather than replacing them.
CREATE TABLE IF NOT EXISTS run_check (
    run_id        TEXT NOT NULL REFERENCES run(run_id),
    predicate_id  TEXT NOT NULL,
    version       INTEGER NOT NULL,
    state         TEXT NOT NULL,               -- one of the eight item states
    reason        TEXT,                        -- one of the thirty item-level codes, or NULL
    scope_kind    TEXT,                        -- required on out_of_scope.not_applicable
    informational_note TEXT,
    witness       TEXT NOT NULL DEFAULT '',    -- space-separated cell refs
    cells_bound   INTEGER NOT NULL,
    transition_order INTEGER NOT NULL,         -- which contract row produced it
    settles       INTEGER NOT NULL,            -- 0 for PROVISIONAL: it runs and does not settle
    detail        TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (run_id, predicate_id, version)
);

-- MATERIALISED FROM THE FIELD SURFACE, before evaluation. Every cell of the denominator has a
-- row from the start, defaulting to NO_PREDICATE(not_yet_synthesised).
CREATE TABLE IF NOT EXISTS run_cell (
    run_id      TEXT NOT NULL REFERENCES run(run_id),
    stable_key  TEXT NOT NULL,
    state       TEXT NOT NULL,
    reason      TEXT,
    scope_kind  TEXT,
    settled_by  TEXT,                          -- the predicate id that settled it, or NULL
    in_scope    INTEGER NOT NULL,              -- from states.in_scope(), and from nothing else
    requalify   INTEGER NOT NULL DEFAULT 0,    -- a retained degenerate precondition accuses its predicate
    PRIMARY KEY (run_id, stable_key)
);

CREATE TABLE IF NOT EXISTS override (
    run_id      TEXT NOT NULL REFERENCES run(run_id),
    stable_key  TEXT NOT NULL,
    was         TEXT NOT NULL,
    became      TEXT NOT NULL,
    authority   TEXT NOT NULL,                 -- who, and under what record
    PRIMARY KEY (run_id, stable_key)
);

CREATE TABLE IF NOT EXISTS extraction_manifest (
    run_id      TEXT NOT NULL REFERENCES run(run_id),
    construct   TEXT NOT NULL,
    understood  INTEGER NOT NULL,
    reason      TEXT NOT NULL,                 -- a skip with no reason is a coverage lie
    PRIMARY KEY (run_id, construct)
);

CREATE INDEX IF NOT EXISTS idx_run_cell_state ON run_cell(run_id, state);
CREATE INDEX IF NOT EXISTS idx_run_check_state ON run_check(run_id, state);
