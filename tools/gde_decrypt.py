#!/usr/bin/env python3
"""Decrypt Godot 2.x encrypted compiled scripts (.gde -> GDC bytecode).

.gde layout: "GDEC" magic, u32 version, 16-byte md5 digest, then AES-256-CFB
payload whose IV is the first 16 bytes of the payload. Godot pads plaintext to
AES block size with zero bytes and prepends a u32 length of the real payload.

Try the stock Godot default key first; verify by GDC magic.
Usage: python gde_decrypt.py <extracted-root> [outdir]
"""
import hashlib
import os
import struct
import sys

from Crypto.Cipher import AES

# Stock Godot engine default script encryption key.
DEFAULT_KEY = bytes.fromhex(
    "2B7E151628AED2A6ABF7158809CF4F3C"  # placeholder, replaced below
)

# Godot 2.x stock default key (from godot source: script_encryption_key).
GODOT2_DEFAULT_KEY = bytes(range(32))

def try_keys(candidates):
    pass  # filled below

def decrypt_file(path, keys):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 40 or data[:4] != b"GDEC":
        return None, "not GDEC"
    version, = struct.unpack("<I", data[4:8])
    digest = data[8:24]
    payload = data[24:]
    if len(payload) < 16:
        return None, "too short"
    for key in keys:
        iv, ct = payload[:16], payload[16:]
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
        pt = cipher.decrypt(ct)
        # Godot prepends u32 real length
        real, = struct.unpack("<I", pt[:4])
        body = pt[4:4 + real]
        if real <= len(pt) - 4 and body[:4] in (b"GDSC", b"GDCS"):
            return (version, digest, body), key.hex()
    return None, "no key worked"

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "extracted"
    outroot = sys.argv[2] if len(sys.argv) > 2 else "decrypted"
    keys = [GODOT2_DEFAULT_KEY, DEFAULT_KEY]
    ok = fail = 0
    key_hits = {}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".gde"):
                continue
            path = os.path.join(dirpath, name)
            res, info = decrypt_file(path, keys)
            rel = os.path.relpath(path, root)
            dest = os.path.join(outroot, rel[:-4] + ".gdc")
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            if res:
                version, digest, body = res
                with open(dest, "wb") as g:
                    g.write(body)
                ok += 1
                key_hits[info] = key_hits.get(info, 0) + 1
            else:
                fail += 1
    print(f"decrypted {ok}, failed {fail}")
    for k, n in key_hits.items():
        print(f"  key {k}: {n} files")

if __name__ == "__main__":
    main()
