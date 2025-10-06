"""Abstractions explored for ARC task d35bdbdc."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples.d35bdbdc import solve_d35bdbdc

DATA_PATH = ROOT / "analysis" / "arc2_samples" / "d35bdbdc.json"


def _copy_grid(grid):
    return [row[:] for row in grid]


def _find_rings(grid):
    rings = []
    height = len(grid)
    width = len(grid[0])
    for r in range(1, height - 1):
        for c in range(1, width - 1):
            center = grid[r][c]
            ring_value = None
            uniform = True
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    value = grid[r + dr][c + dc]
                    if ring_value is None:
                        ring_value = value
                    elif value != ring_value:
                        uniform = False
                        break
                if not uniform:
                    break
            if not uniform or ring_value == center:
                continue
            rings.append({
                "center": center,
                "ring": ring_value,
                "row": r,
                "col": c,
            })
    return rings


def _zero_block(grid, r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            grid[r + dr][c + dc] = 0


def identity_abstraction(grid):
    return _copy_grid(grid)


def propagate_without_sinks_abstraction(grid):
    out = _copy_grid(grid)
    rings = _find_rings(grid)
    mapping = {ring["ring"]: ring["center"] for ring in rings}
    for ring in rings:
        r = ring["row"]
        c = ring["col"]
        replacement = mapping.get(ring["center"])
        if replacement is None:
            _zero_block(out, r, c)
        else:
            out[r][c] = replacement
    return out


def sink_pairing_abstraction(grid):
    rings = _find_rings(grid)
    if not rings:
        return _copy_grid(grid)

    ring_by_color = {}
    for idx, info in enumerate(rings):
        ring_by_color.setdefault(info["ring"], []).append(idx)

    status = ["unknown"] * len(rings)
    partner = [None] * len(rings)

    while True:
        centers = {rings[i]["center"] for i in range(len(rings)) if status[i] == "unknown"}
        updated = False
        for idx, info in enumerate(rings):
            if status[idx] != "unknown":
                continue
            if info["ring"] in centers:
                continue
            updated = True
            candidates = ring_by_color.get(info["center"], [])
            match = None
            for cid in candidates:
                if cid != idx and status[cid] == "unknown":
                    match = cid
                    break
            if match is not None:
                status[idx] = "keep"
                status[match] = "remove"
                partner[idx] = match
            else:
                status[idx] = "remove"
        if not updated:
            break

    for idx in range(len(rings)):
        if status[idx] == "unknown":
            status[idx] = "remove"

    out = _copy_grid(grid)
    for idx, info in enumerate(rings):
        r = info["row"]
        c = info["col"]
        if status[idx] == "keep":
            out[r][c] = rings[partner[idx]]["center"]
        else:
            _zero_block(out, r, c)
    return out


def final_solver(grid):
    return solve_d35bdbdc(grid)


ABSTRACTIONS = {
    "identity": identity_abstraction,
    "propagate_without_sinks": propagate_without_sinks_abstraction,
    "sink_pairing": sink_pairing_abstraction,
    "final_solver": final_solver,
}


def _load_dataset():
    with DATA_PATH.open() as fp:
        return json.load(fp)


def _evaluate(abstraction, samples):
    matches = 0
    first_failure = None
    comparable = True
    for idx, sample in enumerate(samples):
        prediction = abstraction(sample["input"])
        target = sample.get("output")
        if target is None:
            comparable = False
            continue
        if prediction == target:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    if not comparable:
        return None, len(samples), None
    return matches, len(samples), first_failure


def run_harness():
    data = _load_dataset()
    splits = ("train", "test", "arc_gen")
    for name, fn in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split in splits:
            samples = data.get(split, [])
            if not samples:
                print(f"  {split}: n/a")
                continue
            matched, total, first_failure = _evaluate(fn, samples)
            if matched is None:
                print(f"  {split}: predictions only ({total} grids)")
            else:
                if first_failure is None:
                    status = "all matched"
                else:
                    status = f"first failure at {first_failure}"
                print(f"  {split}: {matched}/{total} ({status})")
        print()


if __name__ == "__main__":
    run_harness()
