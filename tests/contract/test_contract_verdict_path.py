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
