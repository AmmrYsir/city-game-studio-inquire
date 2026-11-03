# Progress Log

## 2026-11-03 — Workspace initialized, initial recon complete

**Done:**

- Initialized git workspace with README.md, AGENTS.md, docs/, tools/ conventions.
- Ran `rea inspect` on `CityGameStudio64.exe` → provider unavailable (no Ghidra/IDA
  engines configured) — noted as environment limitation, not a blocker.
- Ran `rea inspect` / `inspect-artifact` on `data.pck` → **REA cannot parse this pack**
  ("Godot PCK format 0 unsupported; only formats 2/3/4"). Confirmed by direct byte
  inspection.
- Manually reversed the PCK header: magic `GDPC`, entry count at offset `0x54`,
  6869 entries, per-entry layout confirmed by parsing the full index with a throwaway
  python script.
- Inventory of extensions: 925 `.gde` scripts, 552 `.scn`, 525 `.tres`, 285 `.pbm`,
  5 `.cfg` (plaintext), plus textures/audio/fonts.
- Confirmed `.gde` = Godot 2.x encrypted compiled scripts (`GDEC` magic, version 1,
  16-byte digest, AES payload).
- Identified high-value targets: `res://data/score.gde`, `res://data/review.gde`,
  `res://data/game.gde`, `res://scripts/models/`, `res://scripts/game/reviews/`.

**Conclusion so far:** the game is a Godot 2.1 title. All gameplay logic (scores,
reviews, sales) lives in encrypted `.gde` bytecode inside `data.pck`. Strategy:
extract pack → decrypt `.gde` with the Godot default AES key (or key extracted from
the engine binary if default fails) → decompile GDScript bytecode → document formulas.

**Next steps:**

1. Write `tools/pck_extract.py` — extract entries from `data.pck` into `extracted/`.
2. Write `tools/gde_decrypt.py` — try the stock Godot 2.x default AES-256 key on
   `.gde` payloads; verify by checking for `GDC` bytecode magic after decryption.
3. Write/adapt a Godot 2.x GDC bytecode disassembler/decompiler for the ~40
   mechanics-relevant scripts.
4. Start documenting findings in `docs/mechanics/`.

**Blocked / open questions:**

- None currently. Fallback if default key fails: locate the AES key constant inside
  `CityGameStudio64.exe` with a `rea search` for the 32-byte pattern or by
  diffing against a stock Godot 2.1 binary.
