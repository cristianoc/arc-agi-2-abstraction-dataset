- Ray_connect_all: Filled every motif and propagated all guide rays (no filtering); connected component prune left small glyph active, so train hit 75% with first failure at train[3].
- Filtered_scaffold: Added the orange-guide count gate before ray casting; keeps only motifs with paired guides, yielding 100% on train and matching the test projection we expect.

The filtered scaffold abstraction is the final solver: sentinel-led BFS after guide filtering keeps a single connected blue columned scaffold that passes every available case.
