#!/usr/bin/env python3
"""Parse a data .gdc containing `static func get_data(): return {...}` into JSON.
Usage: python gdc_data_json.py <in.gdc> <out.json>"""
import json
import sys

from gdc_disasm import load, TOKENS

CI = {v: k for k, v in TOKENS.items()}

class P:
    def __init__(self, toks, ids, consts):
        self.t = toks; self.i = 0; self.ids = ids; self.consts = consts
    def peek(self):
        tok = self.t[self.i]; return tok & 0xFF, tok >> 8
    def next(self):
        tok = self.t[self.i]; self.i += 1; return tok & 0xFF, tok >> 8

def parse(p):
    base, _ = p.peek()
    if base == CI['TK_CURLY_BRACKET_OPEN']:
        p.next(); d = {}
        while True:
            base, pay = p.next()
            if base == CI['TK_CURLY_BRACKET_CLOSE']: return d
            if base in (CI['TK_NEWLINE'], CI['TK_COMMA']): continue
            if base == CI['TK_IDENTIFIER']: key = p.ids[pay]
            elif base == CI['TK_CONSTANT']: key = p.consts[pay]
            else: key = f"?{base}"
            b, _ = p.next()
            if b == CI['TK_COMMA']: d[key] = ""; continue
            assert b == CI['TK_COLON'], f"{key} -> {TOKENS.get(b)}"
            d[key] = parse(p)
    if base == CI['TK_BRACKET_OPEN']:
        p.next(); a = []
        while True:
            base, _ = p.peek()
            if base == CI['TK_BRACKET_CLOSE']: p.next(); return a
            if base == CI['TK_NEWLINE']: p.next(); continue
            a.append(parse(p))
            b, _ = p.peek()
            if b == CI['TK_COMMA']: p.next()
    base, pay = p.next()
    if base == CI['TK_CONSTANT']: return p.consts[pay]
    if base == CI['TK_IDENTIFIER']: return p.ids[pay]
    if base == CI['TK_CF_RETURN']: return parse(p)
    if base in (CI['TK_PR_STATIC'], CI['TK_PR_FUNCTION']): return parse(p)
    if base == CI['TK_PARENTHESIS_OPEN']:
        v = parse(p); p.next(); return v
    return f"<{TOKENS.get(base)}>"

def main():
    data = None
    ver, ids, consts, lt, toks, end, total = load(sys.argv[1])
    for i, t in enumerate(toks):
        if t & 0xFF == CI['TK_CF_RETURN']:
            data = parse(P(toks[i+1:], ids, consts)); break
    json.dump(data, open(sys.argv[2], "w"), indent=1)
    print("written", sys.argv[2])

if __name__ == "__main__":
    main()
