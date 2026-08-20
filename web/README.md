# The cdfc surface

Seven screens over ONE snapshot. **This replaces `src/cdfc/surface/web/`**, which is retained but
deprecated — see `DEPRECATED.md` there.

| # | screen | what it answers |
|---|---|---|
| 01 | **Intake** | what did we receive, and under what digest |
| 02 | **Resolve** | which rows in different files are the same entity |
| 03 | **Map** | which statutory provisions govern which template fields |
| 04 | **Return** | what we placed, and the span each value came from |
| 05 | **Judgement** | what we refused, and the reason for each |
| 06 | **Graph** | the evidence, linked, by node kind |
| 07 | **Certificate** | the roots, and what the certificate does NOT say |

## Run it

```bash
python tools/build_frontend_data.py     # runs the REAL flow, writes web/data/state.json
python -m http.server 8777 --directory web
```

Then open <http://localhost:8777>.

## Why a snapshot

The surface renders `web/data/state.json` and never recomputes. A screen that recomputes is a
screen that can disagree with the run it claims to show — the same reason the evidence graph is a
re-derived projection rather than a store.

**Nothing in the surface invents a number.** Where the snapshot has no value, the screen says so
rather than falling back to zero: a zero is a measurement and an absence is not.

## No network

No fonts are fetched, no CDN is used, and no script is loaded from anywhere but this directory. A
surface that renders differently depending on whether a font server answered is a surface whose
evidence depends on the network.
