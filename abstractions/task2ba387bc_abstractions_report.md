# 2ba387bc Abstraction Notes

- `identity`: returned the input unchanged; 0/4 train matches, failed first on train[0].
- `scan_pairing`: paired components strictly by scan order; 0/4 train matches, failed first on train[0].
- `hollow_vs_solid`: sorted hollows and solids separately, then zipped them into canonical 4×4 pair blocks; 4/4 train matches with no failures and produces the test prediction `[[4,4,4,4,6,6,6,6], …]` shown in the evaluation harness.

Final solver: `hollow_vs_solid` abstraction — converts each hollow component to the left sub-block, each solid to the right sub-block, pairing by ascending top-left position and padding leftovers with zeros. This reproduces every training output and yields the plausible test arrangement of the four component pairs.
