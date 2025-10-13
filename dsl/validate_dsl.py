"""Validation utilities for the ARC-AGI-2 DSL survey.

Checks performed:
1. Every primitive recorded in ``dsl_state.yaml`` appears in at least one
   ``task_log.md`` action entry.
2. Every primitive mentioned in ``task_log.md`` actions exists in
   ``dsl_state.yaml``.
3. Each processed task listed in ``task_progress.yaml`` has a corresponding
   entry in ``task_log.md``.
"""

from __future__ import annotations

import sys
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set


ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "dsl_state.yaml"
LOG_PATH = ROOT / "task_log.md"
PROGRESS_PATH = ROOT / "task_progress.yaml"


class ValidationError(Exception):
    """Raised when a validation rule fails."""


def _parse_yaml_primitives(path: Path) -> List[str]:
    """Minimal YAML reader tailored to the dsl_state.yaml structure."""

    primitives: List[str] = []
    capture = False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped == "primitives:":
                capture = True
                continue
            if stripped == "combinators:":
                break
            if capture and stripped.startswith("- name:"):
                name = stripped.split(":", 1)[1].strip().strip('"')
                primitives.append(name)
    return primitives


@dataclass
class TaskLogEntry:
    task: str
    actions: str


def _parse_task_log(path: Path) -> List[TaskLogEntry]:
    entries: List[TaskLogEntry] = []
    current: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped.startswith("- task:"):
                if current:
                    if "task" in current and "actions" in current:
                        entries.append(TaskLogEntry(current["task"], current["actions"]))
                current = {"task": stripped.split(":", 1)[1].strip()}
            elif stripped.startswith("actions:"):
                current["actions"] = stripped.split(":", 1)[1].strip().strip('"')
        if current and "task" in current and "actions" in current:
            entries.append(TaskLogEntry(current["task"], current["actions"]))
    return entries


_PRIMITIVE_CLAUSE = re.compile(
    r"(?:Added|Introduced)\s+([^.;]+?)\s+primitive(?:s)?",
    re.IGNORECASE,
)


def _split_candidate_names(text: str) -> Iterable[str]:
    text = text.replace(" and ", ", ")
    for fragment in text.split(","):
        name = fragment.strip()
        if not name:
            continue
        if "combinator" in name.lower():
            continue
        name = name.split()[0]
        if not name.isidentifier():
            continue
        if name.lower() in {"added", "introduce", "introduced", "add", "and"}:
            continue
        yield name


def _extract_primitives_from_actions(entries: Iterable[TaskLogEntry]) -> Set[str]:
    primitives: Set[str] = set()
    for entry in entries:
        actions = entry.actions
        for match in _PRIMITIVE_CLAUSE.finditer(actions):
            for name in _split_candidate_names(match.group(1)):
                primitives.add(name)
    return primitives


def _parse_progress_processed(path: Path) -> List[str]:
    processed: List[str] = []
    capture = False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped == "processed:":
                capture = True
                continue
            if stripped == "remaining:":
                break
            if capture and stripped.startswith("- "):
                processed.append(stripped[2:])
    return processed


def _tasks_in_log(entries: Iterable[TaskLogEntry]) -> Set[str]:
    return {entry.task for entry in entries}


def validate() -> None:
    primitives_yaml = _parse_yaml_primitives(STATE_PATH)
    log_entries = _parse_task_log(LOG_PATH)
    primitives_log = _extract_primitives_from_actions(log_entries)
    processed_tasks = _parse_progress_processed(PROGRESS_PATH)
    logged_tasks = _tasks_in_log(log_entries)

    missing_in_log = sorted(set(primitives_yaml) - primitives_log)
    missing_in_yaml = sorted(primitives_log - set(primitives_yaml))
    missing_log_entries = sorted(set(processed_tasks) - logged_tasks)

    errors: List[str] = []
    if missing_in_log:
        errors.append(
            f"Primitives in dsl_state.yaml missing from task log actions: {missing_in_log}"
        )
    if missing_in_yaml:
        errors.append(
            f"Primitives referenced in task log but absent in dsl_state.yaml: {missing_in_yaml}"
        )
    if missing_log_entries:
        errors.append(
            f"Tasks marked processed without log entries: {missing_log_entries}"
        )

    if errors:
        raise ValidationError("\n".join(errors))


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
