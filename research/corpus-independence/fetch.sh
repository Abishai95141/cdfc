#!/usr/bin/env bash
# N6 — acquire the eleven corpora. PUBLIC documents, fetched once, NOT vendored: the texts are
# other people's and the point is reproducibility, not redistribution. `corpora-manifest.json`
# carries each file's sha256 as fetched on 20 Aug 2026, so a re-fetch that drifts is visible.
set -euo pipefail
out="${1:-corpora}"; mkdir -p "$out"; cd "$out"
get(){ curl -sS -L --max-time 90 -A "Mozilla/5.0 cdfc-corpus-probe" -o "$2" "$1"; echo "$(shasum -a256 "$2")"; }
get "https://www.rfc-editor.org/rfc/rfc8259.txt"                                      rfc8259.txt
get "https://www.rfc-editor.org/rfc/rfc2616.txt"                                      rfc2616.txt
get "https://www.rfc-editor.org/rfc/rfc5321.txt"                                      rfc5321.txt
get "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"        gdpr.html
get "https://www.ecfr.gov/api/versioner/v1/full/2024-01-01/title-17.xml?part=275"      ecfr_17_275.xml
get "https://www.govinfo.gov/content/pkg/BILLS-117hr3684enr/html/BILLS-117hr3684enr.htm" us_bill_hr3684.htm
get "https://www.constituteproject.org/constitution/India_2015.pdf"                    india_const.pdf
get "https://www.w3.org/TR/2017/REC-html52-20171214/single-page.html"                  w3c_html52.html
get "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"                             gutenberg_prideprejudice.txt
get "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12356"            rbi_circular.html
# The eleventh is `ifsca_gazette`, exported from this repository's own pinned instrument:
#   python -c "import json;print(json.load(open('corpus/instruments/statute-fm-regulations-2025.text.json'))['text'])"
