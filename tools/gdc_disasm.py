#!/usr/bin/env python3
"""Disassembler for Godot 2.x compiled GDScript ('GDSC' bytecode), ported from
godot 2.1 modules/gdscript/gd_tokenizer.cpp GDTokenizerBuffer::set_code_buffer.

Layout:
  0x00 'GDSC', 0x04 version(=10), 0x08 ident_count, 0x0c constant_count,
  0x10 line_count, 0x14 token_count, payload at 0x18:
    identifiers: u32 len + (bytes ^ 0xb6, last forced 0), NO padding in 2.1? (2.1 pads: none - strings are not aligned)
    constants: binary Variants (4-byte aligned)
    line table: line_count * (u32 token_index, u32 packed line|col<<TOKEN_LINE_BITS)
    token stream: per token: byte; if &0x80 -> u32 & ~0x80.
Token values: base token type in low TOKEN_BITS(8); payload (ident index,
constant index, builtin-func id, type id, newline indent) in high 24 bits.
"""
import struct
import sys

# TokenType enum from gd_tokenizer.h (2.1), value = index
TOKENS = """TK_EMPTY TK_IDENTIFIER TK_CONSTANT TK_SELF TK_BUILT_IN_TYPE
TK_BUILT_IN_FUNC TK_OP_IN TK_OP_EQUAL TK_OP_NOT_EQUAL TK_OP_LESS
TK_OP_LESS_EQUAL TK_OP_GREATER TK_OP_GREATER_EQUAL TK_OP_AND TK_OP_OR
TK_OP_NOT TK_OP_ADD TK_OP_SUB TK_OP_MUL TK_OP_DIV TK_OP_MOD
TK_OP_SHIFT_LEFT TK_OP_SHIFT_RIGHT TK_OP_ASSIGN TK_OP_ASSIGN_ADD
TK_OP_ASSIGN_SUB TK_OP_ASSIGN_MUL TK_OP_ASSIGN_DIV TK_OP_ASSIGN_MOD
TK_OP_ASSIGN_SHIFT_LEFT TK_OP_ASSIGN_SHIFT_RIGHT TK_OP_ASSIGN_BIT_AND
TK_OP_ASSIGN_BIT_OR TK_OP_ASSIGN_BIT_XOR TK_OP_BIT_AND TK_OP_BIT_OR
TK_OP_BIT_XOR TK_OP_BIT_INVERT TK_CF_IF TK_CF_ELIF TK_CF_ELSE TK_CF_FOR
TK_CF_DO TK_CF_WHILE TK_CF_SWITCH TK_CF_CASE TK_CF_BREAK TK_CF_CONTINUE
TK_CF_PASS TK_CF_RETURN TK_PR_FUNCTION TK_PR_CLASS TK_PR_EXTENDS
TK_PR_ONREADY TK_PR_TOOL TK_PR_STATIC TK_PR_EXPORT TK_PR_SETGET TK_PR_CONST
TK_PR_VAR TK_PR_ENUM TK_PR_PRELOAD TK_PR_ASSERT TK_PR_YIELD TK_PR_SIGNAL
TK_PR_BREAKPOINT TK_BRACKET_OPEN TK_BRACKET_CLOSE TK_CURLY_BRACKET_OPEN
TK_CURLY_BRACKET_CLOSE TK_PARENTHESIS_OPEN TK_PARENTHESIS_CLOSE TK_COMMA
TK_SEMICOLON TK_PERIOD TK_QUESTION_MARK TK_COLON TK_NEWLINE TK_CONST_PI
TK_ERROR TK_EOF TK_CURSOR TK_MAX""".split()
TOKENS = {i: n for i, n in enumerate(TOKENS)}

TOKEN_BITS = 8

# GDScript built-in function names (gd_functions.h 2.1), enum order
BUILTINS = """sin cos tan sinh cosh tanh asin acos atan atan2 sqrt fmod
fposmod floor ceil round abs sign pow log exp isnan isinf ease decimals
stepify lerp dectime randomize rand randf random seed randseed deg2rad
rad2deg linear2db db2linear max min clamp nearest_po2 weakref funcref
convert typeof type_exists str print printt prints printerr printraw
var2str str2var var2bytes bytes2var range load inst2dict dict2inst hash
color8 colorn print_stack instance_from_id""".split()

def decode_variant(b, o):
    tw = struct.unpack_from("<I", b, o)[0]
    typ, flags = tw & 0xFFFF, tw >> 16
    o += 4
    if typ == 0: return None, o
    if typ == 1: return bool(b[o]), o + 4
    if typ == 2:
        if flags & 1: return struct.unpack_from("<q", b, o)[0], o + 8
        return struct.unpack_from("<i", b, o)[0], o + 4
    if typ == 3:
        if flags & 1: return struct.unpack_from("<d", b, o)[0], o + 8
        return struct.unpack_from("<f", b, o)[0], o + 4
    if typ == 4:
        ln = struct.unpack_from("<I", b, o)[0]; o += 4
        s = b[o:o + ln].decode("utf-8", "replace"); o += ln
        if o % 4: o += 4 - o % 4
        return s, o
    if typ == 20:  # dictionary
        n = struct.unpack_from("<I", b, o)[0]; o += 4
        d = {}
        for _ in range(n):
            k, o = decode_variant(b, o); v, o = decode_variant(b, o); d[k] = v
        return d, o
    if typ == 21:  # array
        n = struct.unpack_from("<I", b, o)[0]; o += 4
        arr = []
        for _ in range(n):
            v, o = decode_variant(b, o); arr.append(v)
        return arr, o
    raise ValueError(f"variant type {typ} flags {flags:#x} at {o:#x}")

def load(path):
    b = open(path, "rb").read()
    assert b[:4] == b"GDSC"
    version, ident_n, const_n, line_n, tok_n = struct.unpack_from("<5I", b, 4)
    o = 24
    identifiers = []
    for _ in range(ident_n):
        ln = struct.unpack_from("<I", b, o)[0]; o += 4
        cs = bytes(c ^ 0xB6 for c in b[o:o + ln]); o += ln
        cs = cs[:-1] + b"\0" if ln else cs
        identifiers.append(cs.rstrip(b"\0").decode("utf-8", "replace"))
    constants = []
    for _ in range(const_n):
        v, o = decode_variant(b, o); constants.append(v)
    line_table = {}
    for _ in range(line_n):
        t, lc = struct.unpack_from("<2I", b, o); o += 8
        line_table[t] = lc
    toks = []
    for _ in range(tok_n):
        if b[o] & 0x80:
            toks.append(struct.unpack_from("<I", b, o)[0] & ~0x80); o += 4
        else:
            toks.append(b[o]); o += 1
    return version, identifiers, constants, line_table, toks, o, len(b)

def fmt(tok, ids, consts):
    base = tok & 0xFF
    payload = tok >> TOKEN_BITS
    name = TOKENS.get(base, f"T{base}")
    if base == 1:  # identifier
        return f"<{ids[payload]}>" if payload < len(ids) else f"<I{payload}>"
    if base == 2:  # constant
        return f"#{consts[payload]!r}" if payload < len(consts) else f"#C{payload}"
    if base == 4:
        return f"@type:{payload}"
    if base == 5:
        return f"@func:{BUILTINS[payload] if payload < len(BUILTINS) else payload}"
    if base == 74:  # newline with indent
        return f"\\n(indent={payload})"
    return name

if __name__ == "__main__":
    ver, ids, consts, lt, toks, end, total = load(sys.argv[1])
    print(f"// version={ver} idents={len(ids)} consts={len(consts)} tokens={len(toks)} consumed={end}/{total}")
    for i, c in enumerate(consts):
        print(f"// const[{i}] = {c!r}")
    for i, t in enumerate(toks):
        line = lt.get(i)
        mark = f"  [line {line & 0xFFFFF}]" if line is not None else ""
        print(f"{i:4d}: {fmt(t, ids, consts)}{mark}")
