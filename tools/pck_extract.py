#!/usr/bin/env python3
"""Extract entries from a legacy Godot 2.x PCK ("format 0").

Usage: python pck_extract.py <game_dir> [outdir] [path-prefix ...]

Reads the real game dir from the argument; never writes to the game dir.
Optionally filters extraction to entries whose path contains one of the
given prefixes (matched as substring on the res:// path).
"""
import os
import struct
import sys

def read_index(f):
    f.seek(0)
    if f.read(4) != b"GDPC":
        sys.exit("not a GDPC pack")
    f.seek(0x54)
    count, = struct.unpack("<I", f.read(4))
    entries = []
    for _ in range(count):
        n, = struct.unpack("<I", f.read(4))
        path = f.read(n).decode("utf-8")
        off, size = struct.unpack("<QQ", f.read(16))
        f.read(16)  # md5
        entries.append((path, off, size))
    return entries

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    game_dir = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "extracted"
    prefixes = [p for p in sys.argv[3:] if not p.startswith("-")]
    pck = os.path.join(game_dir, "data.pck")
    with open(pck, "rb") as f:
        entries = read_index(f)
        done = 0
        for path, off, size in entries:
            if prefixes and not any(p in path for p in prefixes):
                continue
            rel = path[len("res://"):] if path.startswith("res://") else path
            dest = os.path.join(outdir, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            f.seek(off)
            data = f.read(size)
            with open(dest, "wb") as g:
                g.write(data)
            done += 1
    print(f"extracted {done} of {len(entries)} entries -> {outdir}")

if __name__ == "__main__":
    main()
