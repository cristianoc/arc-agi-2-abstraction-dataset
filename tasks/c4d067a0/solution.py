"""Solver for ARC-AGI-2 task c4d067a0 (split: evaluation)."""

from collections import Counter, defaultdict, deque


def solve_c4d067a0(grid):
    """Populate block columns according to instruction columns."""

    height = len(grid)
    width = len(grid[0]) if grid else 0

    # Determine the background colour so we can ignore it when extracting signals.
    flat = [cell for row in grid for cell in row]
    background = Counter(flat).most_common(1)[0][0]

    # Collect all connected components grouped by colour.
    visited = [[False] * width for _ in range(height)]
    components = []
    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            colour = grid[r][c]
            visited[r][c] = True
            queue = deque([(r, c)])
            cells = [(r, c)]
            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == colour:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))
            components.append((colour, cells))

    # Instruction columns are encoded as singleton components.
    instruction_cols = sorted(
        {cells[0][1] for colour, cells in components if colour != background and len(cells) == 1}
    )
    if not instruction_cols:
        return [row[:] for row in grid]

    sequences = [
        [grid[r][col] for r in range(height) if grid[r][col] != background]
        for col in instruction_cols
    ]

    # Template blocks are the components larger than one cell.
    template_components = [
        (colour, cells)
        for colour, cells in components
        if colour != background and len(cells) > 1
    ]
    if not template_components:
        return [row[:] for row in grid]

    def component_key(item):
        colour, cells = item
        min_col = min(c for _, c in cells)
        min_row = min(r for r, _ in cells)
        return (min_col, min_row)

    template_components.sort(key=component_key)
    base_colour, base_cells = template_components[0]
    base_row = min(r for r, _ in base_cells)
    base_col = min(c for _, c in base_cells)
    mask = [(r - base_row, c - base_col) for r, c in base_cells]
    block_height = 1 + max(dr for dr, _ in mask)
    block_width = 1 + max(dc for _, dc in mask)

    existing_cols = sorted({min(c for _, c in cells) for _, cells in template_components})
    if len(existing_cols) >= 2:
        deltas = [existing_cols[i + 1] - existing_cols[i] for i in range(len(existing_cols) - 1)]
        spacing = Counter(deltas).most_common(1)[0][0]
    else:
        spacing = (
            abs(instruction_cols[1] - instruction_cols[0])
            if len(instruction_cols) >= 2
            else block_width
        )

    step = spacing
    column_count = len(sequences)
    column_positions = [base_col + i * spacing for i in range(column_count)]

    grouped_components = defaultdict(list)
    for colour, cells in template_components:
        col_start = min(c for _, c in cells)
        index = (col_start - base_col) // spacing if spacing else 0
        grouped_components[index].append((colour, cells))

    # Determine the common bottom row so that all columns align at their final block.
    candidate_last_rows = []
    for index, comps in grouped_components.items():
        if not (0 <= index < column_count):
            continue
        sequence = sequences[index]
        for colour, cells in comps:
            top_row = min(r for r, _ in cells)
            for seq_index, value in enumerate(sequence):
                if value == colour:
                    last_row = top_row + (len(sequence) - 1 - seq_index) * step
                    candidate_last_rows.append(last_row)

    def fits(last_row: int) -> bool:
        if not (0 <= last_row <= height - block_height):
            return False
        for sequence in sequences:
            top_row = last_row - (len(sequence) - 1) * step
            if top_row < 0:
                return False
        return True

    feasible_last_rows = [row for row in candidate_last_rows if fits(row)]
    if feasible_last_rows:
        last_row = min(feasible_last_rows)
    else:
        last_row = 0
        for row in range(height - block_height, -1, -1):
            if fits(row):
                last_row = row
                break

    output = [row[:] for row in grid]
    for idx, sequence in enumerate(sequences):
        col_start = column_positions[idx]
        top_row = last_row - (len(sequence) - 1) * step
        for offset, colour in enumerate(sequence):
            anchor_row = top_row + offset * step
            for dr, dc in mask:
                rr = anchor_row + dr
                cc = col_start + dc
                if 0 <= rr < height and 0 <= cc < width:
                    output[rr][cc] = colour

    return output


p = solve_c4d067a0
