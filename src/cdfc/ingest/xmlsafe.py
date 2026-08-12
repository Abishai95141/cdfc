"""The ONE lxml parser factory.

Every XML byte in this system enters through `fromstring` here. That is not style: the
NC-P05a negative control installs a spy on THIS function to prove the container guard ran
before any parse, and a spy can only watch one door. A second `etree.fromstring` call
site anywhere in `src/cdfc/` defeats the control silently, so
`test_nc__P08_only_one_parser_factory` walks the AST and fails the build if one appears.

The hardening is the standard XXE set: no entity resolution, no network, no DTD, no
`huge_tree`, no `recover`. `recover=False` matters most — a recovering parser turns a
malformed document into a partial one and reports success, which is this project's
failure mode in a library call.
"""

from __future__ import annotations

from lxml import etree


def safe_parser() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
        huge_tree=False,
        recover=False,
    )


def fromstring(b: bytes) -> etree._Element:
    """The ONLY sanctioned entry point for parsing XML in this codebase."""
    return etree.fromstring(b, parser=safe_parser())
