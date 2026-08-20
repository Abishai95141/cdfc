"""A1c — establishing which field HERE is which field THERE.

**One component, three uses.** Aligning a filing to its blank, a source column to a template
field, and a record to a record across documents are the same operation: establish the
correspondence, REFUSE when it is ambiguous, and DECLARE what did not align on either side.

**It cannot align on names, and that is measured rather than assumed.** Of the FME return's 3,747
fields only 132 carry a readable label (`N2`) and only 248 carry a declared type. And aligning by
ADDRESS is worse than useless on the case that matters: after a row insertion 3,544 addresses are
common to both files and **1,451 of them hold a different field** — a name-based align is wrong on
41% of what it matches, silently, which is the wrong-form failure strict binding exists to prevent.

So the alignment is STRUCTURAL. Rows are aligned as sequences by their content signature; a cell
corresponds when its row corresponds and its column matches. That survives insertion, deletion and
reordering, because those are edits to a sequence and a sequence alignment is what reads them.
"""
