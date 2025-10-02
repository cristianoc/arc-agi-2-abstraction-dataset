# Task b10624e5 – Abstraction Notes

- **naive** – copies horizontal and vertical ornaments from the reference 2-components but treats vertical inner/outer colours as distinct even when identical; passes 1/2 train grids (fails train[0] where the duplicated colour shortens the outer 8 stripe).
- **refined** – same template inference with a guard that drops the vertical inner colour when it matches the outer stripe; 2/2 train grids, no ground-truth available for test, and arc-gen is absent.

The final solver uses the refined template expansion and therefore matches all available evaluation cases for the task.
