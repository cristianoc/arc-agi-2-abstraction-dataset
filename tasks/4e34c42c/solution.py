"""Solver for ARC-AGI-2 task 4e34c42c."""

from collections import Counter, deque


def most_frequent_color(grid):
    """Return the color that appears most often in the grid."""
    cnt = Counter()
    for row in grid:
        cnt.update(row)
    color, _ = max(cnt.items(), key=lambda item: (item[1], item[0]))
    return color


def pad_vertical(block, background, height=5):
    """Pad or sample rows so the block has exactly `height` rows."""
    current = len(block)
    if current == height:
        return [row[:] for row in block]
    if current > height:
        if current == 1:
            idxs = [0] * height
        else:
            idxs = [round(i * (current - 1) / (height - 1)) for i in range(height)]
        return [block[i][:] for i in idxs]
    top_pad = (height - current) // 2
    bottom_pad = height - current - top_pad
    width = len(block[0]) if block else 0
    pad_row = [background] * width
    result = []
    result.extend(pad_row[:] for _ in range(top_pad))
    result.extend(row[:] for row in block)
    result.extend(pad_row[:] for _ in range(bottom_pad))
    return result


def extract_components(grid, background):
    """Return connected components (4-neighbour) of non-background cells."""
    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]
    components = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] == background or visited[r][c]:
                continue
            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            min_r = max_r = r
            min_c = max_c = c
            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                if rr < min_r:
                    min_r = rr
                if rr > max_r:
                    max_r = rr
                if cc < min_c:
                    min_c = cc
                if cc > max_c:
                    max_c = cc
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] != background:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            block = [grid[row][min_c : max_c + 1] for row in range(min_r, max_r + 1)]
            components.append(
                {
                    "bbox": (min_r, max_r, min_c, max_c),
                    "block": [row[:] for row in block],
                }
            )
    return components


def classify(block):
    height = len(block)
    width = len(block[0]) if block else 0
    if height < 5:
        return "wide_short" if width > 3 else "small_short"
    return "tall"


def dominant_color(block, background):
    cnt = Counter()
    for row in block:
        for value in row:
            if value != background:
                cnt[value] += 1
    if not cnt:
        return background
    return max(cnt.items(), key=lambda item: (item[1], item[0]))[0]


def normalize_block(block, block_type, background):
    height = len(block)
    width = len(block[0]) if block else 0
    if block_type == "wide_short":
        dom = dominant_color(block, background)
        valid_cols = []
        for col in range(width):
            column_values = [block[row][col] for row in range(height)]
            if dom not in column_values:
                continue
            if any(val not in (background, dom) for val in column_values):
                continue
            valid_cols.append(col)
        if valid_cols:
            block = [row[valid_cols[0] : valid_cols[-1] + 1] for row in block]
            width = len(block[0]) if block else 0
        filtered = []
        for row in block:
            filtered.append([val if val == dom else background for val in row])
        return pad_vertical(filtered, background)
    if block_type == "small_short":
        return pad_vertical(block, background)
    return pad_vertical(block, background)


def column_signatures(block):
    return {tuple(block[row][col] for row in range(len(block))) for col in range(len(block[0]))}


def merge_blocks(left, right):
    if not right or not right[0]:
        return [row[:] for row in left]
    if not left or not left[0]:
        return [row[:] for row in right]
    height = len(left)
    overlap = min(len(left[0]), len(right[0]))
    best = 0
    for k in range(1, overlap + 1):
        matches = True
        for row in range(height):
            if left[row][-k:] != right[row][:k]:
                matches = False
                break
        if matches:
            best = k
    merged = []
    for row in range(height):
        merged.append(left[row][:] + right[row][best:])
    return merged


def assemble_components(components, background):
    if not components:
        return []
    tall = []
    wide_short = []
    small_unique = []
    small_redundant = []

    # Pre-compute column signatures of every block for redundancy tests.
    all_columns = []
    for comp in components:
        all_columns.append(column_signatures(comp["normalized"]))

    for idx, comp in enumerate(components):
        comp_type = comp["type"]
        if comp_type == "tall":
            tall.append(comp)
        elif comp_type == "wide_short":
            wide_short.append(comp)
        else:
            # Determine if every column already appears elsewhere.
            other_cols = set().union(*(all_columns[j] for j in range(len(components)) if j != idx))
            target_cols = all_columns[idx]
            if target_cols.issubset(other_cols):
                small_redundant.append(comp)
            else:
                small_unique.append(comp)

    ordered = []
    ordered.extend(sorted(small_unique, key=lambda comp: comp["min_col"]))
    ordered.extend(sorted(wide_short, key=lambda comp: comp["y0"]))
    ordered.extend(sorted(tall, key=lambda comp: -comp["y0"]))
    ordered.extend(sorted(small_redundant, key=lambda comp: comp["min_col"]))

    if not ordered:
        return []

    result = ordered[0]["normalized"]
    for comp in ordered[1:]:
        result = merge_blocks(result, comp["normalized"])
    return result


def solve_4e34c42c(grid):
    background = most_frequent_color(grid)
    components = extract_components(grid, background)
    enriched = []
    for comp in components:
        y0, y1, x0, x1 = comp["bbox"]
        block = comp["block"]
        comp_type = classify(block)
        normalized = normalize_block(block, comp_type, background)
        enriched.append(
            {
                "bbox": comp["bbox"],
                "type": comp_type,
                "normalized": normalized,
                "y0": y0,
                "min_col": x0,
            }
        )

    assembled = assemble_components(enriched, background)
    if not assembled:
        return [row[:] for row in grid]
    return [row[:] for row in assembled]


p = solve_4e34c42c
