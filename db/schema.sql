-- cdfc schema. R6: the digest of this file is recorded in meta.schema_sha256 by
-- `cdfc init`, so a run can name the schema it was produced under.

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- A blob is written once and never rewritten: the path IS the digest.
CREATE TABLE IF NOT EXISTS blob (
    sha256   TEXT PRIMARY KEY,
    n_bytes  INTEGER NOT NULL,
    path     TEXT NOT NULL
);

-- A run row exists ONLY on a successful receipt. A refusal (413 over cap, 415 not a
-- zip) creates nothing: a half-created run is a run whose absence of findings means
-- nothing.
CREATE TABLE IF NOT EXISTS run (
    run_id        TEXT PRIMARY KEY,
    filing_sha256 TEXT NOT NULL REFERENCES blob(sha256),
    received_at   TEXT NOT NULL,          -- RFC 3339, an argument, never a clock read
    media_type    TEXT NOT NULL,
    state         TEXT NOT NULL,          -- OK | INVALID
    invalid_cause TEXT                    -- one of the eight run-level invalid.* causes
);

CREATE TABLE IF NOT EXISTS run_part (
    run_id   TEXT NOT NULL REFERENCES run(run_id),
    part     TEXT NOT NULL,
    sha256   TEXT NOT NULL,
    PRIMARY KEY (run_id, part)
);
