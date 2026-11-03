#!/usr/bin/env python3
"""Recover the 32-byte AES script-encryption key from a Godot engine binary.

The Godot 2.x engine stores the script encryption key as a 32-byte global
array (static const uint8_t). We slide a 32-byte window across the whole exe
and test each candidate: decrypt one block of a known .gde payload and check
whether the result contains the u32 plaintext length + GDC magic.

Usage: python find_key.py <exe-path> <gde-path> [start-offset] [end-offset]
"""
import struct
import sys

from Crypto.Cipher import AES

def load_gde_payload(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"GDEC", "not a GDEC file"
    payload = data[24:]
    return payload[:16], payload[16:32]  # iv, first ciphertext block

def main():
    exe_path = sys.argv[1]
    gde_path = sys.argv[2]
    start = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4], 0) if len(sys.argv) > 4 else None

    iv, ct = load_gde_payload(gde_path)
    with open(exe_path, "rb") as f:
        blob = f.read()
    end = len(blob) if end is None else min(end, len(blob))

    sys.stderr.write(f"testing {end - start} candidate offsets...\n")
    for off in range(start, end - 32):
        key = blob[off:off + 32]
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
        pt = cipher.decrypt(ct)
        real, = struct.unpack("<I", pt[:4])
        if 0 < real <= 0x200000 and pt[4:8] in (b"GDSC", b"GDCS"):
            print(f"KEY FOUND at exe offset 0x{off:x}: {key.hex()}")
            return
        # progress marker every 2M
        if off % 0x200000 == 0:
            sys.stderr.write(f"  0x{off:x}\n")
    print("no key found in range")

if __name__ == "__main__":
    main()
