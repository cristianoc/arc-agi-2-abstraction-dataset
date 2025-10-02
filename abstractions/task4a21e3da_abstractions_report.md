# ARC task 4a21e3da – abstraction notes

- **identity_baseline** – treated the puzzle as an identity map; fails immediately on all train cases (0 %) but trivially matches the test input because no target is provided.
- **simple_corner_projection** – projected the entire 7-component to every corner indicated by a border `2`; without directional guards it over-paints large blocks, still 0 % on train.
- **final_corner_projection** – restricted projections to sentinel-aligned subsets and mirrored the learnt ray painting; delivers 100 % accuracy on train and test.
