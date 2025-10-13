- `identity`: baseline that copies the input; 0/2 train cases solved, fails immediately on train[0].
- `two_color_parity`: enforces an alternating two-color pattern inside the ring; reaches 1/2 on train (train[1] still breaks because of three-color stripes).
- `majority_periodic`: majority-vote periodic repair of each inner row (period ≤6); 2/2 train cases solved and becomes the final refinement.

No test or arc_gen samples were available for evaluation.
