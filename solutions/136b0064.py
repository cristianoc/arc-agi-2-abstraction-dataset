"""Solver for ARC task 136b0064."""

from collections import Counter


GLYPHS = {
    1: [[1, 1, 1]],
    2: [[2, 2]],
    3: [[3, 3, 3, 3]],
    6: [[6], [6]],
}


def split_blocks(grid):
    """Return (start, end) row indices for each non-empty left block."""
    blocks = []
    start = None
    for r, row in enumerate(grid):
        has_left = any(row[c] != 0 for c in range(7))
        if has_left:
            if start is None:
                start = r
        elif start is not None:
            blocks.append((start, r))
            start = None
    if start is not None:
        blocks.append((start, len(grid)))
    return blocks


def dominant_color(grid, row_range, col_range):
    counts = Counter()
    start, end = row_range
    for r in range(start, end):
        for c in col_range:
            val = grid[r][c]
            if val != 0:
                counts[val] += 1
    return counts.most_common(1)[0][0] if counts else 0


def extract_digits(grid):
    left_digits = []
    right_digits = []
    for start, end in split_blocks(grid):
        left_digits.append(dominant_color(grid, (start, end), range(3)))
        right_digits.append(dominant_color(grid, (start, end), range(4, 7)))
    left_digits = [d for d in left_digits if d]
    right_digits = [d for d in right_digits if d]
    return left_digits, right_digits


def glyph_size(digit):
    pattern = GLYPHS[digit]
    return len(pattern), len(pattern[0])


def compute_candidates(prev_cols, width, total_width):
    return [c0 for c0 in range(0, total_width - width + 1) if prev_cols & set(range(c0, c0 + width))]


def select_positions(grid, left_digits, right_digits):
    if not left_digits and not right_digits:
        return []

    width = 7
    right_part = [row[8:] for row in grid]
    top_cols = [c for c, val in enumerate(right_part[0]) if val != 0]
    if not top_cols:
        top_cols = [width // 2]
    prev_cols = set(top_cols)

    anchor = top_cols[0]
    center = width // 2
    direction = 1 if anchor <= center else -1

    seq = []
    prev_start = None
    prev_digit = None
    left_len = len(left_digits)
    digits = left_digits + right_digits

    for idx, digit in enumerate(digits):
        height, glyph_width = glyph_size(digit)
        candidates = compute_candidates(prev_cols, glyph_width, width)
        if not candidates:
            candidates = [prev_start if prev_start is not None else 0]
        candidates.sort()

        if idx == left_len:
            last_left = prev_start if prev_start is not None else anchor
            direction = -1 if last_left >= center else 1

        def enforce_monotonic(choice):
            if prev_start is None:
                return choice
            if direction > 0 and choice < prev_start:
                feas = [c for c in candidates if c >= prev_start]
                return feas[0] if feas else choice
            if direction < 0 and choice > prev_start:
                feas = [c for c in candidates if c <= prev_start]
                return feas[0] if feas else choice
            return choice

        if idx == 0:
            if direction > 0:
                choice = candidates[-1] if anchor > 1 else candidates[0]
            else:
                choice = candidates[0]
        elif idx == left_len - 1:
            choice = candidates[-1] if direction > 0 else candidates[0]
        elif idx == left_len:
            if digit == 6 and prev_start in candidates:
                choice = prev_start
            else:
                if direction > 0:
                    feas = [c for c in candidates if prev_start is None or c >= prev_start]
                    choice = feas[0] if feas else candidates[-1]
                else:
                    feas = [c for c in candidates if prev_start is None or c <= prev_start]
                    choice = feas[0] if feas else candidates[0]
        elif prev_digit == digit and glyph_width > 1:
            target = prev_start + direction * (glyph_width - 1)
            if target in candidates:
                choice = target
            else:
                choice = candidates[-1] if direction > 0 else candidates[0]
        elif digit in (2, 3):
            choice = candidates[0]
        elif digit == 1:
            choice = candidates[-1]
            if prev_start in candidates:
                if idx < left_len and anchor <= 1:
                    choice = prev_start
                elif abs(prev_start - choice) < abs(choice - prev_start):
                    choice = prev_start
        elif digit == 6:
            if prev_digit == digit and glyph_width == 1 and prev_start in candidates:
                choice = prev_start
            else:
                choice = candidates[-1] if direction > 0 else candidates[0]
        else:
            choice = candidates[0]

        choice = enforce_monotonic(choice)
        seq.append(choice)
        prev_digit = digit
        prev_start = choice
        prev_cols = set(range(choice, choice + glyph_width)) if height == 1 else {choice}

    return seq


def paint_digit(grid, row, start, digit):
    pattern = GLYPHS[digit]
    for dr, line in enumerate(pattern):
        for dc, value in enumerate(line):
            grid[row + dr][start + dc] = value


def solve_136b0064(grid):
    left_digits, right_digits = extract_digits(grid)
    height = len(grid)
    right_part = [row[8:] for row in grid]
    output = [row[:] for row in right_part]

    sequence = select_positions(grid, left_digits, right_digits)
    if not sequence:
        return output

    digits = left_digits + right_digits
    row = 1  # leave top row as copied from input
    for start, digit in zip(sequence, digits):
        glyph_height, glyph_width = glyph_size(digit)
        if row + glyph_height > height:
            break
        paint_digit(output, row, start, digit)
        row += glyph_height

    return output


p = solve_136b0064
