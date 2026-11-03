# AGENTS.md — Operating rules for agents in this workspace

## Mission

Extract and document the internal game mechanics of **City Game Studio** (singleplayer,
offline) — score metrics, review/sales formulas, and static data tables — using the
`rea` reversing tooling and complementary local scripts. Deliverables are human-readable
documents in `docs/`.

## Hard rules

1. **The game installation folder is strictly read-only.** Never create, modify, delete,
   or move anything inside it. No exceptions. All extraction/analysis output goes into
   this workspace (`extracted/`, `snapshots/`, `docs/`).
2. **Never expose the user's local paths, username, or other personal information in any
   committed file or report.** The real game directory is stored in `.local/game-dir`
   (git-ignored). In documentation, refer to it as `<GAME_DIR>`. The generic Steam
   sub-path `steamapps/common/City Game Studio` is acceptable; drive letters and user
   directories are not.
3. **This is a singleplayer/offline game being analyzed by its owner.** No network
   attack surface, no online services, no cheats distributed. Keep it to analysis.
4. **Evidence-based reporting.** Distinguish clearly between *confirmed* (read from
   game data/decompiled code) and *inferred* (hypothesis). Cite the source file for
   every formula/constant. Never present a guess as fact.
5. **Tools are read-first.** `rea` inspect/analyze commands don't execute the game.
   Do not launch the game or attach debuggers unless the user explicitly approves
   dynamic analysis in a given session.

## Environment facts (verified 2026-11)

- `rea` v6.x is installed and healthy, but **no native decompiler engines are
  configured** (Ghidra/IDA/Kuna/Hopper all absent). This is fine: the game is a Godot
  2.1 title, so the `.exe` is just the engine runtime — the actual game logic is in
  `data.pck`.
- `rea inspect-artifact` **cannot parse this pack** ("Godot PCK format 0 unsupported;
  only 2/3/4 supported"). Pack parsing must be done with the local scripts in `tools/`
  (see TECH-NOTES.md for the reverse-engineered index layout).
- 64-bit Windows, Git Bash, python available.

## Target facts (confirmed)

- `data.pck`: legacy Godot 2.x PCK. Magic `GDPC` at offset 0 and again at the very end
  of the file; entry count at offset `0x54`; index entries are
  `u32 pathLen + path + u64 offset + u64 size + 16-byte digest`, followed by the next
  entry. 6869 entries total.
- File mix: ~2891 `.tex`, ~1554 `.png`, **925 `.gde`** (encrypted compiled scripts),
  552 `.scn`, 525 `.tres`, 285 `.pbm`, plus `.cfg/.xl/.ttf/.ogg` etc.
- `.gde` files start with `GDEC` magic, `u32` version (1), 16-byte digest, then AES
  payload — Godot 2.x encrypted compiled GDScript (`gdc` bytecode). Decryption key is
  AES-256 embedded in the engine binary; stock Godot builds ship a well-known default
  key — try the public default key first (see TECH-NOTES.md).
- High-value targets identified in the pack index:
  - `res://data/score.gde`, `res://data/review.gde`, `res://data/game.gde`
  - `res://scripts/models/*.gde`, `res://scripts/game/reviews/*.gde`,
    `res://scripts/game/release/released-game.gde`
  - `res://data/` and `res://scripts/json/schema/` for data tables

## Workflow

1. Read `.local/game-dir` for the install path. If missing, stop and ask the user.
2. Extract/decrypt with `tools/` scripts into `extracted/` — never in-place.
3. Use `rea` where it works (`inspect`, `search`, `inspect-artifact` on non-pck files)
   and plain python/GDScript-bytecode tooling where it doesn't. Record what tool
   produced what.
4. Document findings in `docs/` (one topic per file), update `docs/PROGRESS.md`.
5. Keep `extracted/` and `snapshots/` out of git (see `.gitignore`).

## Conventions

- Dates in PROGRESS.md use ISO format.
- Formulas are written in plain math or Python-ish pseudocode with named constants and
  their source `res://` path.
- If an analysis dead-ends, write down what was tried and what blocked it — that is
  progress too.
