# The cdfc application

**Eight screens, and every one of them is a request.** This replaces the seven-screen snapshot
surface, which rendered `web/data/state.json` — a file somebody else computed — and in which
nothing could be done.

| # | screen | what you do there |
|---|---|---|
| 01 | **Intake** | upload a rules corpus, a template, evidence exports and proposals; open a return |
| 02 | **Corpus** | the provisions, addressable, with the two agreement vectors kept apart |
| 03 | **Template** | the induced field surface, or the REASON it is not derivable |
| 04 | **Map** | the driver: provisions × proposals × the five gates, and what they refused |
| 05 | **Graph** | the real nodes and typed edges, four populations never merged |
| 06 | **Return** | what was placed, with the document, page and span for each value |
| 07 | **Questions** | **what we ASK, and what we refuse to pretend is a question** |
| 08 | **Certificate** | the roots, the lanes, the answers, and what the certificate does NOT say |

## Run it

```bash
python tools/serve_app.py --port 8777
```

The launcher prints an operator token if `CDFC_OPERATOR_TOKEN` is unset. Paste it into the
sidebar — three paths mutate (uploading an artefact, opening a return, and **answering a
question**, which is a named human asserting a value that goes into a regulator's return). The
token is held in memory only: it is never written to disk and never put in a URL.

There is a **Load the sample filing** button on Intake. It uploads the vendored IFSCA blank, the
pinned FM Regulations 2025, a plain-text corpus, two custodian exports that disagree with each
other, and 172 model-written proposals — through exactly the same `POST /v1/artefacts` path a file
picker uses. Nothing in it is a fixture the pipeline treats specially.

## Why there is no snapshot, and why the old rule still holds

The old README's rule was right: *"a screen that recomputes is a screen that can disagree with the
run it claims to show."* It obeyed the rule by never recomputing, which is also why nothing in it
could be done.

The resolution is not to store more. It is to store **only what a human supplied**:

    STORED   the artefact digests · the subject · THE ANSWERS
    DERIVED  the field surface · the binding · the fill declaration · the questions
             · the graph · the coverage · the certificate

Answers are stored because a person's assertion is an INPUT — nothing can re-derive what somebody
said. Everything else is a function of those inputs, so no screen can disagree with the run: there
is no second copy to disagree with. That is the same decision `D-A3-01` made for the evidence
graph, which is a re-derived projection and not a store.

## The questioning flow

`FillRefusal` is a closed vocabulary of eight reasons. **Six are questions and two are not.**

`cdfc.ask.ASKABLE` is an allowlist of the six; `NOT_ASKABLE` names the other two and says why each
is not a question. The distinction is not cosmetic. On the pinned FME return `field_not_labelled`
is **3,615 of 3,735** refusals, so a screen that headlines the refusal total as *"needs your
judgement"* overstates the answerable work by a factor of twenty-nine. The Questions screen shows
both numbers, always, and never the total alone.

**An answered question becomes a value, and it is never evidence.** It lands in the `asserted` lane
carrying `resolved_by: human`, the person, the instant and the question id; `filled()` includes it
and `admitted()` does not. Watch the Return screen while you answer: *placed* moves and *evidenced*
does not. Gates 136 and 137 guard each half of that.

## Nothing here invents a number

Where the API has no value, the screen says so rather than falling back to zero: a zero is a
measurement and an absence is not. A template whose surface cannot be induced is reported as a
refusal with its reason, never as a template with no fields in it.

## No network

No fonts are fetched, no CDN is used, and no script is loaded from anywhere but this directory. The
CSP is `script-src 'self'` with no host in any directive.
