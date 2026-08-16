"""The screens. Twelve of them, server-rendered, from `docs/FRONTEND-SCOPE.md`.

## The CSP decision, and it is the one that shaped everything else

The served policy was `default-src 'none'` with **no `script-src`** — which is what makes *"no
script reached this page"* enforceable rather than a claim. A real interactive product needs
scripts, so the choice was: keep the guarantee and ship a document, or take the scripts and lose
it everywhere.

**Neither. The policy is now per-route.**

| routes | policy | why |
|---|---|---|
| `/v1/runs/{id}/report.html`, all of `/v1/*` | `default-src 'none'`, **no `script-src`** | the report is the ATTESTED artifact. Its digest is what a third party verifies, and a script inside it is a script inside the trust boundary |
| the twelve screens | `default-src 'none'; script-src 'self'` | an app shell, from one same-origin file, with no `unsafe-inline` and no `unsafe-eval` |

The guarantee did not weaken; it stopped being global and started being asserted where it is
claimed. `test_web__the_report_route_still_forbids_script` checks the header AND the bytes of
`report.html`, which is stronger than the old blanket header ever was — a blanket header says
nothing about what is in the file.

## Server-rendered, and the script is an enhancement

**Every number, row, reason and count is in the HTML before any script runs.** That is not a
preference: `design.py`'s rule one already forbids gating content on an animation, for the reason
that a reader who scrolls past a findings group mid-reveal must not see fewer findings than exist.
The same argument applies with more force to a fetch — a coverage screen that renders its counts
after an XHR is a screen that shows *nothing checked* for as long as the request takes.

So `script.py` adds drag-and-drop, upload progress, copy buttons, chart hover readouts, disclosure
toggles and keyboard navigation. It adds **no data**, and it never filters a paginated list on the
client: filtering happens server-side through ordinary form GETs, because a client-side filter over
one page of a capped list is precisely how a truncated list gets read as a complete one.
"""

from __future__ import annotations

from cdfc.surface.web.router import NOT_FOUND, SCREENS, render_path

__all__ = ["NOT_FOUND", "SCREENS", "render_path"]
