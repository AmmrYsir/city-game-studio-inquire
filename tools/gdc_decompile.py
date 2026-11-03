#!/usr/bin/env python3
"""Reconstruct GDScript source from Godot 2.x GDC bytecode.

Turns the token stream back into readable source using the line table
(token index -> source line) to place newlines correctly.
Usage: python gdc_decompile.py <file.gdc> [more.gdc ...]
"""
import sys
from gdc_disasm import load, fmt, TOKENS, BUILTINS

# tokens that end a statement when a newline follows at same/greater indent
SIMPLE = {
    "TK_OP_EQUAL": "==", "TK_OP_NOT_EQUAL": "!=", "TK_OP_LESS": "<",
    "TK_OP_LESS_EQUAL": "<=", "TK_OP_GREATER": ">", "TK_OP_GREATER_EQUAL": ">=",
    "TK_OP_AND": "and", "TK_OP_OR": "or", "TK_OP_NOT": "not",
    "TK_OP_ADD": "+", "TK_OP_SUB": "-", "TK_OP_MUL": "*", "TK_OP_DIV": "/",
    "TK_OP_MOD": "%", "TK_OP_SHIFT_LEFT": "<<", "TK_OP_SHIFT_RIGHT": ">>",
    "TK_OP_ASSIGN": "=", "TK_OP_ASSIGN_ADD": "+=", "TK_OP_ASSIGN_SUB": "-=",
    "TK_OP_ASSIGN_MUL": "*=", "TK_OP_ASSIGN_DIV": "/=", "TK_OP_ASSIGN_MOD": "%=",
    "TK_OP_ASSIGN_SHIFT_LEFT": "<<=", "TK_OP_ASSIGN_SHIFT_RIGHT": ">>=",
    "TK_OP_ASSIGN_BIT_AND": "&=", "TK_OP_ASSIGN_BIT_OR": "|=",
    "TK_OP_ASSIGN_BIT_XOR": "^=", "TK_OP_BIT_AND": "&", "TK_OP_BIT_OR": "|",
    "TK_OP_BIT_XOR": "^", "TK_OP_BIT_INVERT": "~", "TK_OP_IN": "in",
    "TK_CF_IF": "if", "TK_CF_ELIF": "elif", "TK_CF_ELSE": "else",
    "TK_CF_FOR": "for", "TK_CF_DO": "do", "TK_CF_WHILE": "while",
    "TK_CF_SWITCH": "switch", "TK_CF_CASE": "case", "TK_CF_BREAK": "break",
    "TK_CF_CONTINUE": "continue", "TK_CF_PASS": "pass", "TK_CF_RETURN": "return",
    "TK_PR_FUNCTION": "func", "TK_PR_CLASS": "class", "TK_PR_EXTENDS": "extends",
    "TK_PR_ONREADY": "onready", "TK_PR_TOOL": "tool", "TK_PR_STATIC": "static",
    "TK_PR_EXPORT": "export", "TK_PR_SETGET": "setget", "TK_PR_CONST": "const",
    "TK_PR_VAR": "var", "TK_PR_ENUM": "enum", "TK_PR_PRELOAD": "preload",
    "TK_PR_ASSERT": "assert", "TK_PR_YIELD": "yield", "TK_PR_SIGNAL": "signal",
    "TK_PR_BREAKPOINT": "breakpoint", "TK_BRACKET_OPEN": "[", "TK_BRACKET_CLOSE": "]",
    "TK_CURLY_BRACKET_OPEN": "{", "TK_CURLY_BRACKET_CLOSE": "}",
    "TK_PARENTHESIS_OPEN": "(", "TK_PARENTHESIS_CLOSE": ")",
    "TK_COMMA": ",", "TK_SEMICOLON": ";", "TK_PERIOD": ".",
    "TK_QUESTION_MARK": "?", "TK_COLON": ":",
}

def decompile(path):
    ver, ids, consts, lt, toks, end, total = load(path)
    # build line->indent map from TK_NEWLINE tokens (payload = indent)
    out = []
    cur = ""
    for i, tok in enumerate(toks):
        base = tok & 0xFF
        payload = tok >> 8
        name = TOKENS.get(base, f"T{base}")
        if name == "TK_NEWLINE":
            out.append((payload, cur.strip()))
            cur = ""
            continue
        if name == "TK_IDENTIFIER":
            cur += ids[payload] + " "
        elif name == "TK_CONSTANT":
            c = consts[payload]
            cur += (f'"{c}"' if isinstance(c, str) else repr(c)) + " "
        elif name == "TK_BUILT_IN_FUNC":
            cur += (BUILTINS[payload] if payload < len(BUILTINS) else f"builtin{payload}") + " "
        elif name == "TK_SELF":
            cur += "self "
        elif name in SIMPLE:
            cur += SIMPLE[name] + " "
        else:
            cur += f"<{name}:{payload}> "
    out.append((0, cur.strip()))
    return "\n".join(("    " * ind) + txt if txt else "" for ind, txt in out)

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"# ─── {p} ───")
        print(decompile(p))
        print()
