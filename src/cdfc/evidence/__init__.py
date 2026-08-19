"""The semantic layer: rules corpus + template -> proposals -> gates -> graph -> coverage.

**THE MODEL IS NOT IN THIS PACKAGE.** It never was and it must not arrive. A model proposes
`rule -> field` bindings by writing a JSON file; `proposal.load` reads that file as untrusted
DATA and `gates.adjudicate` decides. Nothing here imports a model client, and
`tests/negative/importgraph.py` walks this package's closure to say so.

The layering is the point, and each layer is named by what it is allowed to decide:

    provisions.py   DETERMINISTIC   corpus  -> Provision nodes with an eId and an exact span
    fields.py       DETERMINISTIC   template-> Field nodes with a type read from the workbook
    proposal.py     UNTRUSTED DATA  a model's bindings, loaded and validated for SHAPE only
    gates.py        DETERMINISTIC   five gates decide admission; refusals carry a closed reason
    graph.py        DETERMINISTIC   nodes and edges built ONLY from admitted proposals
    query.py        DETERMINISTIC   coverage over the graph, with its denominator declared
    run.py          the driver

**Only admitted proposals become nodes**, so a query over the graph cannot return an
ungrounded claim: the refusals are not in it.
"""
