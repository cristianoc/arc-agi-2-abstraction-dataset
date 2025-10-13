# DSL Refinement Todo List

The following tasks still rely on bespoke primitives without a shared router/combinator. When resuming the abstraction-review process, work through them and decide whether each primitive should become a parameterised configuration of an existing router or remain a task-specific helper.

## Pending Tasks

- [x] 0934a4d8 — Core geometry primitives (`bbox`, `crop`, `flip`, `count_color`); keep as foundational helpers.
- [ ] 135a2760
- [ ] 136b0064
- [ ] 13e47133
- [ ] 16b78196
- [ ] 16de56c4
- [ ] 1818057f
- [ ] 195c6913
- [ ] 1ae2feb7
- [ ] 20270e3b
- [ ] 20a9e565
- [ ] 221dfab4
- [ ] 247ef758
- [ ] 269e22fb
- [ ] 28a6681f
- [ ] 291dc1e1
- [ ] 2b83f449
- [ ] 2ba387bc
- [ ] 2c181942
- [ ] 2d0172a1
- [ ] 31f7f899
- [ ] 332f06d7
- [ ] 35ab12c3
- [ ] 36a08778
- [ ] 38007db0
- [ ] 3a25b0d8
- [ ] 3dc255db
- [ ] 3e6067c3
- [ ] 409aa875
- [ ] 446ef5d2
- [ ] 45a5af55
- [ ] 4a21e3da
- [ ] 4c3d4a41
- [ ] 4c416de3
- [ ] 4c7dc4dd
- [ ] 4e34c42c
- [ ] 53fb4810
- [ ] 5545f144
- [ ] 581f7754
- [ ] 58490d8a
- [ ] 58f5dbd5
- [ ] 5961cc34
- [ ] 5dbc8537
- [ ] 62593bfd
- [ ] 64efde09
- [ ] 65b59efc
- [ ] cbebaa4b
- [ ] d35bdbdc
- [ ] d59b0160
- [ ] d8e07eb2
- [ ] db0c5428
- [ ] db695cfb
- [ ] dbff022c
- [ ] dd6b8c4b
- [ ] de809cff
- [ ] dfadab01
- [ ] e12f9a14
- [ ] e3721c99
- [ ] e376de54
- [ ] e8686506
- [ ] e87109e9
- [ ] edb79dae
- [ ] f560132c
- [ ] f931b4a8
- [ ] faa9f03d
- [ ] fc7cae8d
- [ ] aa4ec2a5
- [ ] abc82100
- [ ] b0039139
- [ ] b10624e5
- [ ] b5ca7ac4
- [ ] b6f77b65
- [ ] b99e7126
- [ ] b9e38dc0
- [ ] bf45cf4b
- [ ] c4d067a0
- [ ] 67e490f4
- [ ] 6e453dd6
- [ ] 6e4f6532
- [ ] 71e489b6
- [ ] 7666fa5d
- [ ] 78332cb0
- [ ] 7b0280bc
- [ ] 7b3084d4
- [ ] 7b5033c1
- [ ] 7b80bb43
- [ ] 7c66cb00
- [ ] 7ed72f31
- [ ] 800d221b
- [ ] 80a900e0
- [ ] 8698868d
- [ ] 88bcf3b4
- [ ] 88e364bc
- [ ] 89565ca0
- [ ] 898e7135
- [ ] 8b7bacbf
- [ ] 8b9c3697
- [ ] 8e5c0c38
- [ ] 8f215267
- [ ] 8f3a5a89
- [ ] 9385bd28
- [ ] 97d7923e
- [ ] 981571dc
- [ ] 9aaea919
- [ ] 9bbf930d
- [ ] a25697e4
- [ ] a32d8b75
- [ ] a395ee82
- [ ] a47bf94d
- [ ] a6f40cea
- [ ] 65b59efc

## Workflow Instructions

For each task listed below:
1. Open the task’s solver (`tasks/<id>/solution.py`) and the corresponding `abstractions.md`.
2. Identify the primitive(s) introduced for that task and remember the refinement history described in the markdown.
3. Decide whether the behaviour can be expressed by:
   - Passing parameters to an existing router/combinator.
   - Extending a router/combinator with a new hook or variant.
   - Retaining the primitive as a task-specific helper (record the rationale).
4. Update `dsl_state.yaml` and `dsl/task_log.md` accordingly, and rerun `python3 dsl/validate_dsl.py`.
5. If the primitive remains task-specific, consider leaving a brief note in this file or the task log explaining why.


## Example: see tasks/0934a4d8/abstractions.md



Use this format when analysing the remaining tasks: list the typed operations (with short explanations of each type) and add a one-line solver summary.
