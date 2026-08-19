# tools/spike — the throwaway scripts behind docs/spike/README.md

Run them in order with the probe venv; each writes the JSON the next one reads.
**No derived JSON is committed, deliberately.** `ci/no-bare-rate.sh` scans `tools/` and went red on
`real_provisions.json` — not on anything this project claims, but on the REGULATOR'S OWN WORDS
quoted verbatim: *"at least 80 per cent. (80%) of the corpus"*, *"at least one per cent. (1%)"*.
The gate cannot tell a quotation from an assertion, and it should not have to: the fix is to stop
committing extracted corpus text, which is regenerable in seconds from the pinned instrument, rather
than to teach a gate an exemption that would later hide a real bare rate.

    layer1_deterministic.py   authored corpus -> provisions.json, fields.json
    layer3_gates.py           -> admitted.json, refused.json
    layer4_graph.py           the graph and its queries
    layer5b_precedence.py     precedence outside the engine, chaining inside it
    real_pipeline.py          the same loop over the REAL instrument and template
