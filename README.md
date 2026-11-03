# City Game Studio — Game Mechanics Research

Reverse-engineering workspace for **City Game Studio** (offline/singleplayer Steam game by
Society of Secret Developers / gamesandbox). Goal: extract and document the game's internal
mechanics — score metrics, review calculation, game-development outcome formulas, genre/topic
data, platform data, and any other rules that drive gameplay results.

All findings are documented from the shipped game files for personal, educational use.

## Objectives

1. **Score / quality metrics** — how a game's quality score (A–E grades) is computed from
   developer skills, team composition, genre/topic fit, budget, etc.
2. **Review system** — how magazine/website reviews and their scores are generated.
3. **Sales / outcome model** — how review scores, fanbase, marketing, and platform translate
   into units sold and revenue.
4. **Static data tables** — genres, topics, platforms, research/unlocks, achievements.
5. **Anything else load-bearing** — bugs, formulas, and hidden constants discovered along
   the way.

## Target

| Item | Value |
|------|-------|
| Game | City Game Studio |
| Engine | Godot 2.1 (custom build, 64-bit) |
| Main data file | `data.pck` (~376 MB, 6869 entries, legacy PCK "format 0" layout) |
| Game logic | ~925 `.gde` script files (Godot `GDEC` encrypted compiled GDScript) |

The game installation directory is resolved from `.local/game-dir` (git-ignored; see
AGENTS.md). **Never write the real local path into any committed file.**

## Workspace layout

```
docs/           Findings, written for humans (start here)
tools/          Local helper scripts (python etc.) for pack parsing / decryption
extracted/      Extracted & decrypted game assets (git-ignored)
snapshots/      rea analysis snapshots / evidence JSON (git-ignored)
.local/         Machine-local config, incl. the real game install path (git-ignored)
```

## Status / progress

See [docs/PROGRESS.md](docs/PROGRESS.md) for the running log, and
[docs/TECH-NOTES.md](docs/TECH-NOTES.md) for the reverse-engineering technical notes
(pack format, script encryption, tooling constraints).
