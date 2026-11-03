# Reverse-engineering technical notes — City Game Studio

## Target

- Engine: Godot 2.1 custom build (x64). Main data in `data.pck` (~376 MB, 6869 files).
- `.exe` is just the engine runtime; all game logic is GDScript inside the pack.

## PCK format (legacy "format 0")

```
0x00 'GDPC'  0x04 u32 version=0 ... 0x54 u32 entry_count
entry: u32 pathLen, path bytes, u64 offset, u64 size, 16B md5
data blobs follow; trailing 'GDPC' magic at EOF.
```

Extractor: `tools/pck_extract.py`.

## Script encryption (.gde)

Header (32 bytes): `'GDEC'`, u32 mode(=1), 16-byte MD5-of-plaintext, u64 plaintext
length. Then AES-256-**ECB** (no IV; Godot 2.x `FileAccessEncrypted`), zero-padded
to 16-byte blocks. Plaintext = GDSC bytecode. Integrity = MD5 check.

### Key recovery

The engine stores the 32-byte key as a static array in `.data`. Recovered with a
sliding-window search: for each 32-byte window in the exe, decrypt the first
ciphertext block of `data/score.gde` and test for `GDSC` magic.

**Recovered key (ASCII password):** `McQfTjWnZr4u7x!A%D*G-JaNdRgUkXp2`
(exe file offset `0xf47010`; offset is build-specific, re-run `tools/find_key.py`
for other builds). Note the ECB oracle in the first version of `find_key.py`
(CFB with IV) was wrong — the current file implements ECB.

Decryptor: `tools/gde_decrypt.py` (all 907 scripts verify via MD5).

## GDSC bytecode (Godot 2.1, BYTECODE_VERSION=10)

Ported from `gd_tokenizer.cpp GDTokenizerBuffer::set_code_buffer`:

```
0x00 'GDSC'  u32 version(=10)  u32 ident_count  u32 const_count
u32 line_count  u32 token_count  → payload at 0x18
identifiers: u32 len + bytes^0xb6 (last byte forced 0), no alignment padding
constants: binary Variants (type word: low16=type, high16=flags; int64/float64
           flags=1; strings len-prefixed, 4-byte aligned)
line table: line_count × (u32 token_index, u32 packed line/column)
tokens: 1 byte each; if byte & 0x80 → u32 & ~0x80
token value: base type in low 8 bits, payload in high 24 (identifier index,
constant index, builtin-func id, type id, or newline indent)
```

- Base-token enum: `TK_IDENTIFIER=1, TK_CONSTANT=2, TK_SELF=3, TK_BUILT_IN_TYPE=4,
  TK_BUILT_IN_FUNC=5, ...` (full list in `tools/gdc_disasm.py`, from gd_tokenizer.h).
- Built-in function table = `gd_functions.h` enum order (MATH_SIN … INSTANCE_FROM_ID).

Tools: `tools/gdc_disasm.py` (token dump), `tools/gdc_decompile.py`
(token stream → GDScript-ish source using the line table for indentation).
All 907 scripts round-trip (parser consumes exactly the file length).

Caveats of the quick decompiler: no operator-precedence reconstruction (prints
tokens with spaces), no block-structure inference beyond newline indents, and a
few clamp-style helpers are called with the game's own argument order. Semantics
are exact though — it's the literal token stream.

## rea tooling notes

- `rea inspect` on the exe: no native provider configured (Ghidra/IDA absent) —
  wasn't needed; pure-python analysis sufficed.
- `rea inspect-artifact data.pck`: rejects PCK format 0 (supports only 2/3/4).

## Key game-logic files (decompiled)

- `scripts/controllers/game.gd` — scoring pipeline (compute_notation etc.)
- `scripts/controllers/game-sales.gd` — monthly sales/fanbase/income
- `scripts/controllers/gameport.gd`, `remake.gd`, `game-update.gd` — ports/remakes/DLC
- `data/game.gd` — size table; `data/score.gd` — point-cost table
- `data/game-type.gd`, `data/game-theme.gd`, `data/game-platform.gd`,
  `data/game-engine.gd` — genre/theme/platform/engine data tables
- `scripts/utils/match-utils.gd` — theme/genre/platform match ratio math
- Difficulty data via `models/player.gd get_difficulty_data()` (data/player.gd)

## Environment

- Windows, Git Bash, python 3 + pycryptodome (installed for this project).
- Workspace layout: `extracted/` (raw pack files), `decrypted/` (.gdc),
  `decompiled/` (.gd) — all git-ignored; docs and tools are committed.
