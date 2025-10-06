"""Solver for ARC-AGI-2 task d35bdbdc."""


def _detect_rings(grid):
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


def solve_d35bdbdc(grid):
    rings = _detect_rings(grid)
    if not rings:
        return [row[:] for row in grid]

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

    out = [row[:] for row in grid]
    for idx, info in enumerate(rings):
        r = info["row"]
        c = info["col"]
        if status[idx] == "keep":
            out[r][c] = rings[partner[idx]]["center"]
        else:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    out[r + dr][c + dc] = 0

    return out


p = solve_d35bdbdc
