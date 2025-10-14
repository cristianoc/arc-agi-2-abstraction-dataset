"""Lightweight validation for the DSL state registry.

The current registry enumerates typed operations (formerly called primitives)
and combinators gathered from the abstraction notes.  This script performs a
few consistency checks:

1. every typed operation entry must define a name, signature, and at least one
   associated task id;
2. typed-operation task lists must not contain duplicates;
3. the combination of name + signature must be unique within the registry; and
4. each recorded type lists the tasks where it appears (no duplicates, no
   missing names).

Exit status 0 indicates success; any validation error is reported on stderr and
results in a non-zero exit code.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "dsl_state.yaml"


class ValidationError(Exception):
    """Raised when a validation rule fails."""


def _parse_state(path: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    """Parse `dsl_state.yaml` without relying on PyYAML.

    The file structure is intentionally simple, so a hand-rolled parser keeps
    dependencies minimal.  Only the information required for the validation
    checks is extracted.
    """

    primitives: List[Dict[str, object]] = []
    types: List[Dict[str, object]] = []
    combinators: List[Dict[str, object]] = []

    current: Dict[str, object] | None = None
    target: List[Dict[str, object]] | None = None
    section = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if line == "primitives:":
            if current is not None and target is not None:
                target.append(current)
            section = "primitives"
            target = primitives
            current = None
            continue
        if line == "types:":
            if current is not None and target is not None:
                target.append(current)
            section = "types"
            target = types
            current = None
            continue
        if line == "combinators:":
            if current is not None and target is not None:
                target.append(current)
            section = "combinators"
            target = combinators
            current = None
            continue
        if not target:
            continue
        if line.startswith("- name:"):
            if current:
                target.append(current)
            current = {"name": line.split(":", 1)[1].strip()}
        elif line.startswith("signature:") and current is not None:
            current["signature"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("tasks:") and current is not None:
            raw_tasks = line.split(":", 1)[1].strip()
            if raw_tasks.startswith("[") and raw_tasks.endswith("]"):
                raw_tasks = raw_tasks[1:-1]
            tasks = [item.strip() for item in raw_tasks.split(",") if item.strip()]
            current["tasks"] = tasks

    if current and target is not None:
        target.append(current)

    return primitives, types, combinators


def _validate_typed_operations(primitives: List[Dict[str, object]]) -> None:
    errors: List[str] = []
    seen: Counter[Tuple[str, str]] = Counter()

    for entry in primitives:
        name = entry.get("name")
        signature = entry.get("signature")
        tasks = entry.get("tasks")

        if not isinstance(name, str) or not name:
            errors.append("Primitive entry missing `name` field.")
            continue
        if not isinstance(signature, str) or not signature:
            errors.append(f"{name}: missing `signature` field.")
        if not isinstance(tasks, list) or not tasks:
            errors.append(f"{name}: `tasks` list must be present and non-empty.")
        else:
            duplicates = [task for task, count in Counter(tasks).items() if count > 1]
            if duplicates:
                errors.append(f"{name}: duplicate task ids {duplicates}.")

        if isinstance(name, str) and isinstance(signature, str):
            seen[(name, signature)] += 1

    collisions = [f"{name} :: {signature}" for (name, signature), count in seen.items() if count > 1]
    if collisions:
        errors.append(
            "Duplicate (name, signature) pairs found: "
            + ", ".join(sorted(collisions))
        )

    if errors:
        raise ValidationError("\n".join(errors))


def _validate_types(types: List[Dict[str, object]]) -> None:
    errors: List[str] = []
    seen: Counter[str] = Counter()

    for entry in types:
        name = entry.get("name")
        tasks = entry.get("tasks")

        if not isinstance(name, str) or not name:
            errors.append("Type entry missing `name` field.")
            continue
        if not isinstance(tasks, list) or not tasks:
            errors.append(f"{name}: `tasks` list must be present and non-empty.")
        else:
            duplicates = [task for task, count in Counter(tasks).items() if count > 1]
            if duplicates:
                errors.append(f"{name}: duplicate task ids {duplicates}.")

        if isinstance(name, str):
            seen[name] += 1

    collisions = [name for name, count in seen.items() if count > 1]
    if collisions:
        errors.append(
            "Duplicate type names found: " + ", ".join(sorted(collisions))
        )

    if errors:
        raise ValidationError("\n".join(errors))


def validate() -> None:
    primitives, types, _ = _parse_state(STATE_PATH)
    _validate_typed_operations(primitives)
    _validate_types(types)


def main(argv: List[str]) -> int:
    try:
        validate()
    except ValidationError as err:
        print(f"Validation failed:\n{err}", file=sys.stderr)
        return 1
    else:
        print("DSL validation passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
