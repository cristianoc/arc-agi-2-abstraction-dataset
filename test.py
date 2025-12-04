#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from importlib import util
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

Grid = List[List[int]]
Solver = Callable[[Grid], Sequence[Sequence[int]]]


@dataclass
class ExampleFailure:
    split: str
    index: int
    reason: str


@dataclass
class TaskResult:
    task_id: str
    total_examples: int
    failures: List[ExampleFailure]
    predicted: dict
    load_error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run task solutions against the ARC-AGI-2 ground truth data."
    )
    parser.add_argument(
        "--data-root",
        default="ARC-AGI-2/data/evaluation",
        help="Directory containing task JSON files (default: %(default)s)",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Optional list of task ids to run. Defaults to every directory under tasks/.",
    )
    parser.add_argument(
        "--skip-train", action="store_true", help="Skip checking training examples."
    )
    parser.add_argument(
        "--skip-test", action="store_true", help="Skip checking test examples."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failing tasks and the final summary.",
    )
    return parser.parse_args()


def discover_tasks(root: Path, selected: set[str] | None) -> tuple[list[tuple[str, Path]], set[str]]:
    tasks: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for bundle in sorted(p for p in root.iterdir() if p.is_dir()):
        task_id = bundle.name
        seen.add(task_id)
        if selected and task_id not in selected:
            continue
        solution_path = bundle / "solution.py"
        if solution_path.exists():
            tasks.append((task_id, solution_path))
    missing = set() if not selected else selected - seen
    return tasks, missing


def load_solver(task_id: str, path: Path) -> Solver:
    module_name = f"tasks.{task_id}.solution"
    spec = util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module for {task_id} from {path}")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func_name = f"solve_{task_id}"
    solver = getattr(module, func_name, None) or getattr(module, "p", None)
    if solver is None:
        raise AttributeError(f"{path} does not expose {func_name} or p")
    return solver


def load_task_json(data_root: Path, task_id: str) -> dict:
    json_path = data_root / f"{task_id}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Missing task data: {json_path}")
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def copy_grid(grid: Sequence[Sequence[int]]) -> Grid:
    return [list(row) for row in grid]


def compare_grids(expected: Sequence[Sequence[int]], actual: Sequence[Sequence[int]]) -> str | None:
    if len(expected) != len(actual):
        return f"height mismatch (expected {len(expected)}, got {len(actual)})"
    for r, (exp_row, act_row) in enumerate(zip(expected, actual)):
        if len(exp_row) != len(act_row):
            return f"row {r} width mismatch (expected {len(exp_row)}, got {len(act_row)})"
        for c, (exp, act) in enumerate(zip(exp_row, act_row)):
            if exp != act:
                return f"cell ({r},{c}) expected {exp}, got {act}"
    return None


def run_examples(
    task_id: str,
    solver: Solver,
    pairs: Iterable[dict],
    split: str,
) -> tuple[list[ExampleFailure], list[Grid | None]]:
    failures: list[ExampleFailure] = []
    outputs: list[Grid | None] = []
    for idx, pair in enumerate(pairs):
        try:
            raw_output = solver(copy_grid(pair["input"]))
            output = copy_grid(raw_output)
        except Exception as exc:  # pragma: no cover - defensive
            reason = f"exception: {exc.__class__.__name__}: {exc}"
            failures.append(ExampleFailure(split, idx, reason))
            outputs.append(None)
            continue
        try:
            reason = compare_grids(pair["output"], output)
        except Exception as exc:  # pragma: no cover - defensive
            reason = f"invalid output: {exc.__class__.__name__}: {exc}"
        if reason:
            failures.append(ExampleFailure(split, idx, reason))
        outputs.append(output)
    return failures, outputs


def run_task(
    task_id: str,
    solution_path: Path,
    data_root: Path,
    check_train: bool,
    check_test: bool,
) -> TaskResult:
    predicted: dict = {"train": [], "test": []}
    result = TaskResult(task_id=task_id, total_examples=0, failures=[], predicted=predicted)
    try:
        solver = load_solver(task_id, solution_path)
    except Exception as exc:  # pragma: no cover - defensive
        result.load_error = f"solver load failed: {exc}"
        return result

    try:
        task_data = load_task_json(data_root, task_id)
    except Exception as exc:  # pragma: no cover - defensive
        result.load_error = f"data load failed: {exc}"
        return result

    if check_train:
        train_pairs = task_data.get("train", [])
        result.total_examples += len(train_pairs)
        train_failures, train_outputs = run_examples(task_id, solver, train_pairs, "train")
        result.failures.extend(train_failures)
        for pair, output in zip(train_pairs, train_outputs):
            entry = {"input": pair["input"], "output": pair.get("output")}
            if output is not None:
                entry["actual"] = output
            predicted["train"].append(entry)
    else:
        predicted["train"] = []
    if check_test:
        test_pairs = task_data.get("test", [])
        result.total_examples += len(test_pairs)
        test_failures, test_outputs = run_examples(task_id, solver, test_pairs, "test")
        result.failures.extend(test_failures)
        for pair, output in zip(test_pairs, test_outputs):
            entry = {"input": pair["input"], "output": pair.get("output")}
            if output is not None:
                entry["actual"] = output
            predicted["test"].append(entry)
    else:
        predicted["test"] = []
    return result


def print_task_result(result: TaskResult, quiet: bool) -> None:
    if result.load_error:
        print(f"{result.task_id}: FAIL ({result.load_error})")
        return
    if result.failures:
        first = result.failures[0]
        print(
            f"{result.task_id}: FAIL ({len(result.failures)} of {result.total_examples} examples, "
            f"first: {first.split}[{first.index + 1}] {first.reason})"
        )
        if not quiet:
            for failure in result.failures[1:]:
                print(f"    {failure.split}[{failure.index + 1}] {failure.reason}")
    else:
        status = "PASS" if result.total_examples else "SKIP"
        print(f"{result.task_id}: {status} ({result.total_examples} examples)")


def write_predictions(task_id: str, predicted: dict, out_root: Path) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    out_path = out_root / f"{task_id}.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(predicted, handle, indent=2)


def main() -> int:
    args = parse_args()
    if args.skip_train and args.skip_test:
        print("Nothing to run: both train and test splits were skipped.")
        return 1

    task_ids = set(args.tasks) if args.tasks else None
    tasks_root = Path("tasks")
    tasks, missing = discover_tasks(tasks_root, task_ids)
    if missing:
        print(f"Requested task ids not found under tasks/: {', '.join(sorted(missing))}")
    if not tasks:
        print("No task solutions found to run.")
        return 1

    data_root = Path(args.data_root)
    print(f"Evaluating {len(tasks)} task(s) using data from {data_root}")
    results: list[TaskResult] = []
    out_root = Path("out")
    for task_id, solution_path in tasks:
        result = run_task(
            task_id,
            solution_path,
            data_root,
            check_train=not args.skip_train,
            check_test=not args.skip_test,
        )
        if not result.load_error:
            write_predictions(task_id, result.predicted, out_root)
        results.append(result)

    failed = [res for res in results if res.load_error or res.failures]
    passed = [res for res in results if not res.load_error and not res.failures]
    total_examples = sum(res.total_examples for res in results)
    for res in results:
        if not args.quiet or res in failed:
            print_task_result(res, quiet=args.quiet)

    print()
    print(f"Tasks run   : {len(results)}")
    print(f"Passed      : {len(passed)}")
    print(f"Failed      : {len(failed)}")
    print(f"Examples run: {total_examples}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
