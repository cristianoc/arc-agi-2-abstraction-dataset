# eee78d87 Abstraction Summary

- **plus_bias** – naive template reuse; matches only 1/3 train grids (fails starting at train[1]).
- **or_only** – neighbor-classified but restricted to OR templates; improves to 2/3 (fails on diagonal train[2]).
- **final_template** – neighbor-classified selection among {plus, H, X} templates with XOR handling; 3/3 train, produces the expected striped-and-crossed 16×16 output for the test input shown in `analysis/taskeee78d87_abstractions.py`.
