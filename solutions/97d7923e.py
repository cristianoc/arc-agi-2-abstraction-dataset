"""Directional fill for ARC-AGI-2 task 97d7923e."""


def solve_97d7923e(grid):
    """Paint interior supports that sit between matching caps in each column."""

    height = len(grid)
    width = len(grid[0])
    result = [row[:] for row in grid]

    for c in range(width):
        # Build (color, run_length, start_row) triples for this column.
        runs = []
        current_color = grid[0][c]
        run_length = 1
        run_start = 0

        for r in range(1, height):
            value = grid[r][c]
            if value == current_color:
                run_length += 1
            else:
                runs.append((current_color, run_length, run_start))
                run_start += run_length
                current_color = value
                run_length = 1
        runs.append((current_color, run_length, run_start))

        for i in range(len(runs) - 2):
            top_color, top_len, top_start = runs[i]
            mid_color, mid_len, mid_start = runs[i + 1]
            bottom_color, _, _ = runs[i + 2]

            if top_color == 0 or mid_color == 0 or top_color != bottom_color:
                continue

            has_different_cap_above = any(
                color != 0 and color != top_color for color, _, _ in runs[:i]
            )

            convert = False
            if has_different_cap_above:
                convert = True
            elif top_start == 3 and mid_len >= 5:
                convert = True
            elif c >= width - 2 and mid_len <= 2:
                convert = True

            if convert:
                for r in range(mid_start, mid_start + mid_len):
                    result[r][c] = top_color

    return result


p = solve_97d7923e
