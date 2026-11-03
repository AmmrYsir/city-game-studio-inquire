# Progress Log

## 2026-11-03 — Full static decryption + core mechanics extracted ✅

**Milestones:**

1. **AES key recovered.** Godot 2.x `FileAccessEncrypted` = AES-256-ECB, no IV.
   Sliding-window search over the engine binary found the key at exe offset
   `0xf47010` — ASCII password `McQfTjWnZr4u7x!A%D*G-JaNdRgUkXp2`. All 907 `.gde`
   scripts decrypt with MD5 verification (`tools/gde_decrypt.py`).
2. **GDC bytecode toolchain built.** `tools/gdc_disasm.py` + `tools/gdc_decompile.py`
   port Godot 2.1's `GDTokenizerBuffer` format (BYTECODE_VERSION=10). All 907
   scripts decompile to `decompiled/` (~39k lines of GDScript-ish source).
3. **Score pipeline fully mapped** (`scripts/controllers/game.gd`):
   capacity-point distribution scoring → theme/genre/platform match ratios →
   duration factor (5–20) → platform-library comparison → combo-repeat penalty →
   4 magazine notes at ±10% jitter. See `docs/mechanics/score-and-reviews.md`.
4. **Monthly sales model mapped** (`scripts/controllers/game-sales.gd`):
   saturation-curve base pool × review-note^pow × fanbase ratio, hype/marketing
   add-ons, digital-store split, piracy ÷3, fanbase gain/loss rules.
   See `docs/mechanics/sales-model.md`.
5. **Size data table extracted** (indie/normal/big/aaa: max_note 85/90/95/100,
   max_sales 100k/500k/2.5M/10M, staff 1/5/25/100, etc.).
   See `docs/mechanics/data-tables.md`.

**Next candidates:**

- `data/game-type.gd` (3372 lines) — genre step-capacity expectations (feeds
  `compute_capacity_note` expected values)
- `data/game-theme.gd` (585) + `data/game-platform.gd` (4118) — match tables
- `scripts/utils/match-utils.gd` — match ratio math
- Difficulty data (`data/player.gd`) — notation ratios, taxes, sales scalars
- `controllers/remake.gd`, `game-port.gd`, `game-update.gd`, `game-of-the-year.gd`
- A–E grade cutoffs in review UI presentation

## 2026-11-03 — Workspace initialized

Recon results in docs/TECH-NOTES.md. Initial commit `5315cbd`.
