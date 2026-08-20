# DEPRECATED — superseded by `web/` at the repository root

*20 Aug 2026.*

This package generated 12–13 screens as Python-built markup. It is **retained, not deleted**: the
report renderer (`src/cdfc/surface/render.py`, `templates/report.html.j2`) and the design tokens
(`src/cdfc/surface/design.py`) are still live and still gated, and `design.py` carries the MEASURED
contrast ratios that the new surface inherits.

**Use `web/` for the product surface.** It is seven screens over one snapshot, one screen per stage
of the flow a filer actually walks, with no build step and no framework.

What moved and what did not:

* the **tokens** did not move — `web/app.css` restates `design.py`'s palette with the ratios in
  comments, so the two cannot silently diverge without the numbers disagreeing in the diff
* the **report** did not move — `cdfc report` still renders the self-contained HTML file
* the **screens** are superseded; the new set is smaller on purpose, because the old set had
  screens for phases rather than for the user's flow
