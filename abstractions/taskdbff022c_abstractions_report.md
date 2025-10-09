# Abstraction Notes for dbff022c

- `identity`: Leaves inputs untouched; fails immediately on train because the puzzle requires filling structured cavities.
- `fill_same_color`: Flood-fills zero pockets with their boundary color; still misses coloured partner fills and breaks samples with multi-colour legends (0/3 train).
- `partner_rule`: Detects zero cavities, filters by boundary colour/size, and paints partner colours (3/3 train). Test output aligns qualitatively (no ground truth to score).

Final solver uses the `partner_rule` abstraction.
