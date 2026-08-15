"""Gate 14 — no model client is reachable from the verdict path.

**Registered PENDING at P0 because its subject did not exist. It exists now**, and the audit at P6
found it still marked PENDING — which is the state that lets a gate avoid demonstration. A gate
whose subject has shipped and which is still PENDING is a gate nobody has to keep green.

The verdict path is `cdfc.verdict`, `cdfc.evaluate` and `cdfc.facts`: the modules that turn a
filing into states, counts and a fraction. **Nothing in that closure may reach a model client.**
A model in the verdict path would make the headline number depend on a sampling temperature, and
the whole coverage claim rests on the number being re-derivable from the filing's own bytes.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

VERDICT_PATH = ("cdfc/verdict", "cdfc/evaluate", "cdfc/facts")

# Any client that would put a sampled answer inside a verdict. The list is deliberately broad on
# vendors and narrow on generic words: a false positive costs one rename, a false negative ships a
# verdict nobody can re-derive.
MODEL_CLIENTS = frozenset({
    "anthropic", "openai", "cohere", "mistralai", "google.generativeai", "genai", "ollama",
    "llama_cpp", "transformers", "torch", "langchain", "langchain_openai", "litellm",
    "vertexai", "boto3", "sagemaker", "replicate", "huggingface_hub",
})

# Network stacks. A verdict path that can open a socket can reach a model even without a client.
NETWORK = frozenset({"requests", "httpx", "urllib.request", "urllib3", "aiohttp", "socket", "http.client"})


def _imports_of(path: Path) -> set[str]:
    out: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:                      # a relative import stays inside the package
                continue
            out.add(node.module or "")
    return out


def _closure() -> dict[Path, set[str]]:
    """Every module of the verdict path, and everything it imports — transitively within cdfc."""
    seen: dict[Path, set[str]] = {}
    frontier = [
        p for root in VERDICT_PATH for p in sorted((REPO / "src" / root).rglob("*.py"))
    ]
    while frontier:
        path = frontier.pop()
        if path in seen:
            continue
        imports = _imports_of(path)
        seen[path] = imports
        for mod in imports:
            if not mod.startswith("cdfc."):
                continue
            candidate = REPO / "src" / (mod.replace(".", "/") + ".py")
            pkg = REPO / "src" / mod.replace(".", "/") / "__init__.py"
            for c in (candidate, pkg):
                if c.is_file() and c not in seen:
                    frontier.append(c)
    return seen


def test_no_model_in_verdict_path() -> None:
    closure = _closure()
    assert len(closure) > 12, (
        f"the closure walk found only {len(closure)} modules; it is not reaching the verdict path "
        "and would report success over nothing"
    )
    offenders = []
    for path, imports in sorted(closure.items()):
        for mod in sorted(imports):
            root = mod.split(".")[0]
            if mod in MODEL_CLIENTS or root in MODEL_CLIENTS:
                offenders.append(f"{path.relative_to(REPO)}: {mod}")
    assert offenders == [], (
        f"a model client is reachable from the verdict path: {offenders}. The headline number "
        "would then depend on a sampling temperature, and the coverage claim rests on it being "
        "re-derivable from the filing's own bytes."
    )


def test_no_network_stack_in_verdict_path() -> None:
    """A path that can open a socket can reach a model without importing a client."""
    offenders = []
    for path, imports in sorted(_closure().items()):
        for mod in sorted(imports):
            if mod in NETWORK or mod.split(".")[0] in NETWORK:
                offenders.append(f"{path.relative_to(REPO)}: {mod}")
    assert offenders == [], f"a network stack is reachable from the verdict path: {offenders}"


def test_the_walk_can_see_an_import_when_there_is_one() -> None:
    """The admission-side control: a walk that matches nothing is not a guard.

    Without it, a `_closure()` that silently returned an empty set would make both tests above
    pass forever — which is exactly the shape of defect this repository keeps finding.
    """
    closure = _closure()
    all_imports = {m for imports in closure.values() for m in imports}
    assert "cdfc.canon" in all_imports or any(m.startswith("cdfc.") for m in all_imports), (
        "the walk sees no cdfc imports at all; it is not reading what it claims to"
    )
    # And it must be able to name a banned module when one is present.
    fake = ast.parse("import anthropic\nfrom openai import OpenAI\n")
    found = set()
    for node in ast.walk(fake):
        if isinstance(node, ast.Import):
            found |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            found.add(node.module or "")
    assert found & MODEL_CLIENTS == {"anthropic", "openai"}


# ==============================================================================================
# P11 — the two prohibitions the attestation layer adds, and both are about DISCLOSURE
# ==============================================================================================

# Sigstore's keyless flow and everything that reaches a transparency log. The list is broad on
# purpose: the cost of a false positive is one rename, and the cost of a false negative is a
# permanent public record of a named entity's compliance activity.
KEYLESS = frozenset({
    "sigstore", "fulcio", "rekor", "cosign", "tuf", "securesystemslib", "in_toto",
})

# The office suite, as EXECUTABLE NAMES and IMPORTABLE MODULES. It computes the
# independently-computed fixture's derived cells, which is a CORPUS GENERATION step — and it must
# never be reachable from a verdict.
#
# **`uno` was in this set as a substring and matched inside `unobservable`**, turning every
# docstring in `qualify/` into a violation. That is the seventh time in this build a check has
# been defeated by prose, and the fix is the same one every time: look at what the code DOES.
# A verdict can only invoke LibreOffice by RUNNING it, so the scan is over subprocess argument
# lists and imports — not over string constants at large.
OFFICE_BINARIES = frozenset({"soffice", "libreoffice", "unoconv"})
OFFICE_MODULES = frozenset({"uno", "unohelper", "pyoo", "unoconv"})
SPAWNERS = frozenset({"run", "Popen", "call", "check_call", "check_output", "system", "execv",
                      "execvp", "spawnv"})

ATTEST_PATH = ("cdfc/attest",)


def _attest_closure() -> dict[Path, set[str]]:
    """The attestation package's own closure, walked the same way the verdict path is."""
    seen: dict[Path, set[str]] = {}
    frontier = [
        p for root in ATTEST_PATH for p in sorted((REPO / "src" / root).rglob("*.py"))
    ]
    while frontier:
        path = frontier.pop()
        if path in seen or not path.is_file():
            continue
        imports = _imports_of(path)
        seen[path] = imports
        for mod in imports:
            if not mod.startswith("cdfc."):
                continue
            candidate = REPO / "src" / (mod.replace(".", "/") + ".py")
            pkg = REPO / "src" / mod.replace(".", "/") / "__init__.py"
            for c in (candidate, pkg):
                if c.is_file() and c not in seen:
                    frontier.append(c)
    return seen


def test_no_tlog() -> None:
    """**There is no keyless code path at all**, and that is a privacy decision, not a default.

    `--tlog-upload=false` is not the mechanism here: the capability does not exist. A keyless
    (Fulcio/Rekor) signature puts *the fact and the timing of a named fund management entity
    running a pre-submission compliance check* into a permanent, public, append-only transparency
    log. That is a disclosure about the filer which the filer did not ask for and cannot retract,
    and it would be made by the tool they ran in order to be careful.

    The filer signs with a detached key; the vendor signs nothing and appears only as
    `assessor.id` with `thirdParty: false`.
    """
    closure = _attest_closure()
    assert len(closure) >= 6, (
        f"the attest closure walk found only {len(closure)} modules — it is scanning nothing"
    )
    offenders = [
        f"{path.relative_to(REPO)}: {mod}"
        for path, imports in sorted(closure.items())
        for mod in sorted(imports)
        if mod in KEYLESS or mod.split(".")[0] in KEYLESS
    ]
    assert offenders == [], (
        f"a transparency-log client is reachable from the attestation layer: {offenders}"
    )

    # And no such capability anywhere in the runtime tree, under any name.
    everywhere = [
        f"{p.relative_to(REPO)}: {mod}"
        for p in sorted((REPO / "src" / "cdfc").rglob("*.py"))
        for mod in sorted(_imports_of(p))
        if mod.split(".")[0] in KEYLESS
    ]
    assert everywhere == [], f"a keyless signing client is in the runtime tree: {everywhere}"


def test_no_libreoffice_online() -> None:
    """**`libreoffice` is not on the verdict path**, which is why it is absent from `tool_versions`.

    It computes the *independently-computed* fixture's derived cells — a corpus generation step
    that happens once, offline, before any verdict exists. Pinning it in the manifest would imply
    the verdict depended on it, and a pin that implies a dependency nobody has is a statement about
    the system that is false.
    """
    import json

    paths = [
        p for p in sorted((REPO / "src" / "cdfc").rglob("*.py"))
        # The corpus generator is where it legitimately lives, and it is not a verdict path.
        if "qualify/corpus" not in str(p)
    ]
    offenders: list[str] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            # (a) SPAWNING it. The only way a verdict can actually invoke the office suite.
            if isinstance(node, ast.Call) and (
                getattr(node.func, "attr", "") in SPAWNERS
                or getattr(node.func, "id", "") in SPAWNERS
            ):
                for token in ast.walk(node):
                    if isinstance(token, ast.Constant) and isinstance(token.value, str):
                        name = Path(token.value).name.lower()
                        if name in OFFICE_BINARIES or token.value.lower() in OFFICE_BINARIES:
                            offenders.append(
                                f"{path.relative_to(REPO)}: spawns {token.value!r}"
                            )
        # (b) IMPORTING its bridge.
        for mod in _imports_of(path):
            if mod.split(".")[0] in OFFICE_MODULES:
                offenders.append(f"{path.relative_to(REPO)}: imports {mod}")
    assert offenders == [], (
        f"libreoffice is reachable outside the corpus generator: {offenders}. It is a corpus "
        "generation step, and a verdict that could invoke it would depend on a tool the manifest "
        "does not pin."
    )

    # And it is absent from the pinned tool versions — over the PROPERTY NAMES, because the
    # schema's own description explains the absence and a text scan its explanation defeats is a
    # check on the comments.
    schema = json.loads(
        (REPO / "src" / "cdfc" / "attest" / "schema" / "attestation.schema.json")
        .read_text(encoding="utf-8")
    )
    tools = set(schema["$defs"]["toolVersions"]["properties"])
    assert tools == {"python", "lxml", "openpyxl", "celpy", "z3"}
    assert not (tools & (OFFICE_BINARIES | OFFICE_MODULES))
