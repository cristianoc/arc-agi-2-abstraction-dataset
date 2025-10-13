# Abstractions for ARC task b99e7126

- `identity`: direct copy of the input; fails every split (0/3 train) and serves as the control.
- `square_fill`: paint the minority tile into the entire 3x3 macro window that contains the observed tiles; fills the target window indiscriminately; every train case ends up over-painted (0/3).
- `mask_completion`: place the minority tile only where the tile’s majority colour appears, which matches all train/test/arc-gen pairs.

The final solver reuses the `mask_completion` abstraction: detect the minority tile, read its majority-colour mask to recover the intended 3×3 letter, align the mask with the observed tiles, and repaint every required cell with the original tile pattern.
