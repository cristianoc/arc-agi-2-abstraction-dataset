d35bdbdc abstraction summary
============================

- identity: left the grid unchanged; fails all train cases (0/3) because the task expects selective pruning of ring gadgets.
- propagate_without_sinks: rewired ring centres via a simple colour map; hits wrong targets on every train case (0/3) due to keeping rings that should be deleted.
- sink_pairing: iteratively keeps rings whose border colour no longer appears as a centre, pairing them with donors and zeroing the rest; matches all train samples (3/3) and is stable on test inputs.
- final solver: same sink-based pairing as above, reused as the production solver; test predictions (three grids) keep the paired ring colours while pruning the others, matching the observed pattern.
