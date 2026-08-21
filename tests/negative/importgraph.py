"""P13-B0 — the AST import-closure walker. **The model-free claim, made mechanical.**

Criterion A6. Until this exists, *"no model is in the verdict path"* is a design intention that
happens to be true; after it, it is a property of a running system that CI re-establishes on every
commit. The spec listed `test_no_model_in_verdict_path` as a build gate and recorded it **not yet
written** — this is the file that closes that.

## A NON-LITERAL `importlib` argument is a HARD ERROR, not a skip

`importlib.import_module(name)` where `name` is a variable cannot be resolved statically. The
tempting behaviour is to skip it and carry on, and that is precisely wrong: **an unresolvable
dynamic import is exactly where a client would hide**, and skipping it makes the walk report a
clean closure it did not compute. That is NC-E01's swallowed-exception failure applied to our own
guard, and it is the difference between a check and a reassurance.

So `DynamicImportUnresolvable` is raised. If a legitimate dynamic import ever appears in a verdict
root, the repair is to make it a literal or to move the code out of the closure — not to widen the
walker.

## Why the STATIC walk is not sufficient on its own, and neither is the dynamic one

`test_nc__A04a` builds this closure and asserts `BANNED_IN_VERDICT` is absent. It catches the
static import no test input happens to exercise. It **cannot** see a call made through a name it
never resolved — a `getattr(__import__("hcaeh"[::-1] ...))`, or an `httpx.get` inside a host
function reached only at runtime.

`test_nc__A04b` monkeypatches `socket.socket` to raise and runs a full FME filing, asserting the
verdict is still produced. It catches the dynamic call the static walk cannot see, and it cannot
see an import that no test input exercises.

**Neither test is sufficient alone and the pair is the guard.** `injectors/DynamicHttpInHostFn`
puts a network call behind a runtime branch precisely to prove the static test alone would pass.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys
from typing import Final

# The verdict roots. `cdfc.api` is DELIBERATELY ABSENT and that is a decision, not an oversight:
# an API is a transport and it binds a socket by definition. Putting it in this set would make the
# set unsatisfiable, and the honest response to "the rule cannot hold here" is to say where the
# rule applies rather than to weaken it everywhere. `tests/unit/test_api.py` carries the API's own
# narrower rule -- no socket in the DISPATCHER, only in the server.
VERDICT_ROOTS: Final[tuple[str, ...]] = (
    "cdfc.evaluate", "cdfc.verdict", "cdfc.probes", "cdfc.selfcheck", "cdfc.attest",
    "cdfc.qualify", "cdfc.surface",
    # A2 adds two. `cdfc.pathm` executes rules a REGULATOR wrote and publishes a coverage
    # declaration over them, and the headline claim on it is "zero model calls" -- which is a
    # property of this graph or it is a promise. `cdfc.evidence` adjudicates a model's proposals
    # and must not be able to consult the model it is adjudicating.
    "cdfc.pathm", "cdfc.evidence",
    # A5 adds one. `cdfc.fill` decides which fields get a proposed VALUE, and its whole discipline
    # is that the trigger is MECHANICAL -- does a grounded observation re-verify byte-exact -- and
    # never a model's confidence. A fill lane able to consult the model whose proposals it
    # adjudicates could not be trusted to refuse one.
    "cdfc.fill",
    # C6 adds one. `cdfc.ask` turns a refusal into a question and an answer into a value stamped
    # `resolved_by: human`. That stamp is a claim about WHO produced the value, and a layer able to
    # call a model while making it would make the label forgeable -- the asserted lane and the
    # derived lane would become the same lane wearing two names.
    "cdfc.ask",
)

# ONE RULE, no per-vendor enumeration. `cdfc.model` is banned as a package rather than by naming
# every SDK that could live in it, because an enumeration is a list somebody has to remember to
# extend and this project has been bitten by exactly that shape four times.
BANNED_IN_VERDICT: Final[frozenset[str]] = frozenset({
    "anthropic", "openai", "google", "google_genai", "genai", "cohere", "mistralai",
    "httpx", "requests", "aiohttp", "urllib.request", "urllib3", "http.client", "socket",
    "cdfc.model",
})


# THE POSITIVE FORM OF THE SAME RULE, added at B3 on 20 Aug 2026.
#
# `BANNED_IN_VERDICT` above is a DENYLIST, and its own comment says why that shape is weak: an
# enumeration is a list somebody has to remember to extend, and this project has been bitten by
# exactly that four times. B3 walked into the fifth instance. It adds `docling` as a build-time PDF
# reader, and the natural place to put a PDF reader is `cdfc.qualify` -- which is a VERDICT ROOT.
# Nothing in the denylist would have stopped it, because nobody had written "docling" down.
#
# So the rule is inverted. `CLAUDE.md` already asserts *"the runtime closure is deliberately
# tiny"*; this makes that a gate instead of a sentence. Anything not on this list -- docling,
# torch, pdfplumber, a package that does not exist yet -- is refused BY DEFAULT.
#
# THE LIST WAS MEASURED, NOT COPIED FROM THE PROSE. `CLAUDE.md` named three; the closure holds
# six. `z3` and `yaml` are load-bearing and were simply missing from the description, which is the
# defect this file exists to make impossible: a claim about the import graph that the import graph
# does not support. The alignment file was corrected to match the tree, not the other way round.
RUNTIME_THIRD_PARTY: Final[frozenset[str]] = frozenset({
    "celpy",     # cel-python. THE predicate evaluator; a regulator's rule is CEL or it is nothing
    "lark",      # celpy's parser generator, transitive and unavoidable
    "lxml",      # XML that is parsed rather than pattern-matched; the whole xmlsafe discipline
    "openpyxl",  # READER only -- ci/no-openpyxl-writer.sh is the gate on the other half
    "yaml",      # the predicate/obligation authoring format, read by cdfc.predicates.loader
    "z3",        # SMT. cdfc.qualify.g3_degeneracy decides degeneracy by PROOF, not by sampling
})


def third_party_in(closure: frozenset[str]) -> tuple[str, ...]:
    """Top-level distributions in `closure` that are neither stdlib, nor `cdfc`, nor allowed.

    Returned sorted. A non-empty result means somebody widened the runtime closure, which
    `CLAUDE.md` calls an architecture decision rather than a `pip install`.
    """
    tops = {m.split(".")[0] for m in closure}
    return tuple(sorted(tops - sys.stdlib_module_names - {"cdfc"} - RUNTIME_THIRD_PARTY))


class DynamicImportUnresolvable(RuntimeError):
    """`importlib.import_module` with a non-literal argument, inside a verdict root."""


# DECLARED dynamic import sites, each mapped to the package its target is PROVABLY bounded to.
#
# `relations/registry.py` loads a relation's expression builder by dotted name, and refuses any
# name not beginning with `cdfc.probes.relations.` before it calls `import_module`. So the target
# is unknown but the REACHABLE SET is not, and the walker adds that whole package to the closure.
#
# This is not the skip the docstring above forbids -- a skip removes modules from the closure and
# reports clean; this ADDS every module the site could possibly reach, which is strictly more
# conservative than resolving the literal would have been. An UNDECLARED dynamic import still
# raises. The table is the visible diff: adding a row is somebody stating a bound and signing for
# it, which is the same discipline as ci/no-denied-build-tool.sh's licence table.
BOUNDED_DYNAMIC_IMPORTS: Final[dict[str, str]] = {
    "cdfc/probes/relations/registry.py": "cdfc.probes.relations",
    "cdfc/probes/qualify.py": "cdfc.probes.relations",
}


def _module_path(module: str, *, src: Path) -> Path | None:
    rel = module.replace(".", "/")
    for candidate in (src / f"{rel}.py", src / rel / "__init__.py"):
        if candidate.is_file():
            return candidate
    return None


def _imports_of(path: Path, module: str) -> set[str]:
    """Every module name this file imports. Relative imports are resolved against `module`."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: set[str] = set()
    pkg = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg.split(".")
                base = base[: len(base) - (node.level - 1)] if node.level > 1 else base
                target = ".".join([*base, node.module] if node.module else base)
            else:
                target = node.module or ""
            if target:
                out.add(target)
                # `from cdfc.qualify import textsource` imports a MODULE, not just a name, and a
                # walk that only recorded `cdfc.qualify` would stop at the package __init__ and
                # miss everything the submodule pulls in.
                out.update(f"{target}.{a.name}" for a in node.names)
        elif isinstance(node, ast.Call):
            fn = node.func
            is_import_module = (
                (isinstance(fn, ast.Attribute) and fn.attr == "import_module")
                or (isinstance(fn, ast.Name) and fn.id in ("import_module", "__import__"))
            )
            if is_import_module:
                if not node.args:
                    continue
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    out.add(arg.value)
                else:
                    key = next(
                        (k for k in BOUNDED_DYNAMIC_IMPORTS if str(path).endswith(k)), None
                    )
                    if key is None:
                        raise DynamicImportUnresolvable(
                            f"{path}: a dynamic import whose argument is not a string literal "
                            f"({ast.dump(arg)[:80]}). This RAISES rather than being skipped: an "
                            "unresolvable dynamic import is exactly where a client would hide, "
                            "and skipping it makes this walk report a closure it did not compute. "
                            "If the target is provably bounded, declare the bound in "
                            "BOUNDED_DYNAMIC_IMPORTS -- do not widen the walker."
                        )
                    # Resolve to the declared UPPER BOUND: every module in that package.
                    out.add(BOUNDED_DYNAMIC_IMPORTS[key])
    return out


def _seed(root: str, *, src: Path) -> list[str]:
    """`root` plus EVERY module inside it, when `root` is a package.

    **The first version seeded with `root` alone and it was a silent pass.** Six of the seven
    verdict roots are packages whose `__init__.py` imports nothing, so the walk terminated
    immediately and reported a closure of size 1 — clean, and computed over nothing. A gate that
    reports OK having checked nothing is this project's own R3 finding, occurring inside the guard
    written to make the model-free claim mechanical.

    A package's modules are reachable by `from cdfc.verdict import x` from anywhere; the closure
    of a package must therefore be the union over its members, not the closure of its `__init__`.
    """
    out = [root]
    pkg_dir = src / root.replace(".", "/")
    if pkg_dir.is_dir():
        for p in sorted(pkg_dir.rglob("*.py")):
            rel = p.relative_to(src).with_suffix("")
            parts = rel.parts[:-1] if rel.name == "__init__" else rel.parts
            out.append(".".join(parts))
    return out


def import_closure(root: str, *, src: Path) -> frozenset[str]:
    """Every module reachable from `root` by static import, transitively. AST only, never imported.

    Importing the modules to inspect them would EXECUTE them, and a module that opens a socket at
    import time would do so during the test written to prove it does not.
    """
    seen: set[str] = set()
    stack = _seed(root, src=src)
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        # A package reached DYNAMICALLY expands to its members too. Walking only its
        # `__init__.py` would repeat the silent pass `_seed` was written to fix, one level down.
        if (src / module.replace(".", "/")).is_dir():
            stack.extend(m for m in _seed(module, src=src) if m not in seen)
        path = _module_path(module, src=src)
        if path is None:
            continue  # a third-party or stdlib module: recorded, not descended into
        for imported in _imports_of(path, module):
            if imported not in seen:
                stack.append(imported)
    return frozenset(seen)


def banned_in(closure: frozenset[str]) -> tuple[str, ...]:
    """Which banned roots the closure reaches. Matched on the DOTTED PREFIX, not on equality.

    `import socket` and `from socket import socket` and `import urllib.request` must all be
    caught, and a substring test would also flag `websocket_shim` — a false positive that gets a
    gate disabled.
    """
    hits: set[str] = set()
    for module in closure:
        parts = module.split(".")
        for banned in BANNED_IN_VERDICT:
            b = banned.split(".")
            if parts[: len(b)] == b:
                hits.add(banned)
    return tuple(sorted(hits))
