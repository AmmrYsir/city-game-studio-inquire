# Technical Notes — City Game Studio reverse engineering

## Target identification

- `CityGameStudio64.exe` — custom-built Godot 2.1 (x64) engine runtime. Not the
  interesting target by itself.
- `data.pck` — ~376 MB Godot resource pack containing everything: scripts, scenes,
  textures, data tables, fonts, audio.

## PCK format (legacy Godot 2.x, "format 0")

Confirmed by direct parsing:

```
offset 0x00:  magic "GDPC"            (4 bytes)
offset 0x04:  u32 format version = 0  (pack version field, little-endian)
offset 0x05:  u16 godot major = 2
offset 0x07:  u16 godot minor = ...
offset 0x54:  u32 entry count
then, per entry (repeated entry-count times):
    u32  pathLength
    char path[pathLength]          # e.g. "res://data/score.gde"
    u64  offset                    # absolute offset of file data in the pack
    u64  size                      # uncompressed size
    16 bytes digest                # MD5 of the file data
...file data blobs...
last 4 bytes: magic "GDPC" (trailing magic, as in Godot 2.x)
```

`rea inspect-artifact` rejects this as "Godot PCK format 0" (it supports only the
newer plain formats 2/3/4), so extraction is done by `tools/pck_extract.py` which
implements the layout above.

## Script encryption (`.gde`)

```
offset 0:  magic "GDEC"   (4 bytes)
offset 4:  u32 version = 1
offset 8:  16 bytes digest
offset 24: AES-256-CFB encrypted GDC bytecode (rest of file)
```

Godot 2.x script encryption works like this: the engine contains a 32-byte AES-256
key; encrypted scripts are AES-256-CFB encrypted compiled GDScript (`.gdc` bytecode).
Stock engine builds embed a well-known default key; custom builds rotate it. First
attempt: the public default key. Verification: successful decryption must yield a
valid GDC payload starting with `GDSC` (compiled GDScript magic) or parseable GDC
bytecode headers.

If the default key fails, the key can be recovered from `CityGameStudio64.exe`:
search the `.data`/`.rdata` section for 32-byte high-entropy constants referenced
near AES key-schedule setup, or diff against a stock Godot 2.1.6 build.

## GDC bytecode (compiled GDScript, Godot 2.1)

Decompiling options once decrypted:

- Adapt a Godot 2.x GDC parser (the bytecode format is documented in
  godot-source `modules/gdscript/gd_script_tokenizer.cpp` —
  `GDScriptTokenizerBuffer` / `gdscript_byte_codegen`).
- The bytecode is a stack-machine format with a fixed opcode table per engine
  version; strings/constants/identifiers are stored in tables at the top of the
  file, making formulas recoverable even from a disassembly listing.

## rea tooling notes

- `rea inspect <exe>`: fails — no native analysis providers configured on this
  machine (Ghidra, IDA, Kuna absent; Hopper not supported on Windows).
- `rea inspect-artifact <data.pck>`: fails — PCK format 0 unsupported.
- Usable rea commands for this target: `rea search` (strings/names in the exe),
  `rea inspect-pe-imports`, `rea inspect-pe-resources` on the exe if needed for
  key recovery.
- General fallback: python scripts in `tools/` (pack parsing, AES decryption via
  `cryptography`/`pycryptodome`).

## Data files of interest (from pack index)

- `res://data/*.gde` — score, review, game, concurrent-game, event-game logic.
- `res://scripts/models/*.gde` — data models.
- `res://scripts/game/reviews/*.gde` — review UI/logic.
- `res://scripts/game/release/released-game.gde` — release/sales logic.
- `res://scripts/json/schema/*.gde` — JSON schemas (mod-loading related).
- `.pbm` files (285) — likely data tables (portable bitmap or custom format; TBD).
- `.xl` files (17) — possibly spreadsheet-like data tables; TBD.
- 5 `.cfg` files — plaintext; addon/plugin configs (already readable).

## Environment notes

- Windows, Git Bash, python 3 available with struct/stdlib; AES needs
  `cryptography` or `pycryptodome` (check availability before relying on it).
