# Abstractions for Task 8f3a5a89

- `boundary_only`: marks the four-neighbour frontier of the left-accessible `8` region without further filtering; leaves stray `1` components untouched. Fails (0/3 train) because it colours boundaries around internal holes and preserves noisy `1` islands.
- `boundary_with_diag`: extends the previous idea with a diagonal halo to reach corner-adjacent obstacles. Improves to 1/3 train but still paints hole boundaries and keeps isolated `1`s.
- `final_hybrid`: prunes `1` components that neither touch the left edge nor border the accessible background, and filters the frontier so only neighbours that connect to the exterior (or border-touching obstacles) are painted; adds the diagonal halo afterwards. Matches all train cases (3/3) and serves as the submitted solver. Test inference produces a 12×12 grid consistent with the learned pattern (see abstraction harness output).

