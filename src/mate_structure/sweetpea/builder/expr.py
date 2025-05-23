from __future__ import annotations
import re
from typing import List, Tuple

_OPERATORS = {"and", "or", "not", "True", "False", "None", "in", "is"}


def _unique(seq: List[str]) -> List[str]:
    seen = set();
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x);
            out.append(x)
    return out


# ----------------------------------------------------------------------
def _strip_strings(expr: str) -> str:
    """Remove single- or double-quoted string literals from expr."""
    return re.sub(r"(\"[^\"]*\"|'[^']*')", " ", expr)


def _vars_within(expr: str) -> List[str]:
    """
    Identifiers in a within-trial expression, excluding operators *and*
    anything that was inside quotes.
    """
    expr_no_strings = _strip_strings(expr)
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr_no_strings)
    return [t for t in dict.fromkeys(tokens) if t not in _OPERATORS]


def _vars_window(expr: str) -> List[str]:
    """
    Identifiers (base names) that appear before a bracket *or* bare,
    again stripping string literals first.
    """
    expr_no_strings = _strip_strings(expr)
    indexed = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", expr_no_strings)
    bare = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", expr_no_strings)
    return [t for t in dict.fromkeys(indexed + bare) if t not in _OPERATORS]


# ------------------------------------------------------------------ #
# public builders
# ------------------------------------------------------------------ #
def build_within(expr: str) -> tuple[str, str, list[str], int]:
    """
    builds within expression

    Examples:
        >>> build_within('color==word')
        'WithinTrial(lambda color, word: color==word, [color, word])'

        >>> build_within('color=="red" and word=="green"')
        'WithinTrial(lambda color, word: color=="red" and word=="green", [color, word])'

        >>> build_within('color=="red" or word==1')
        'WithinTrial(lambda color, word: color=="red" or word==1, [color, word])'

        >>> build_within('size>2')
        'WithinTrial(lambda size: size>2, [size])'
    """
    vars_ = _vars_within(expr)
    varlist = ", ".join(vars_)
    lam = f"lambda {varlist}: {expr}"
    call = f"WithinTrial({lam}, [{', '.join(vars_)}])"
    return call, lam, vars_, 0


def build_window(expr: str) -> tuple[str, str, list[str], int]:
    """
    >>> build_window('color[-1]==color[0]')
    'Window(lambda color: color[-1]==color[0], [color], 2)'

    >>> build_window('color[-1]==word[0] and word[-1]=="green"')
    'Window(lambda color, word: color[-1]==word[0] and word[-1]=="green", [color, word], 2)'

    >>> build_window('color[-2]==color[0] and color[-1]==color[0]')
    'Window(lambda color: color[-2]==color[0] and color[-1]==color[0], [color], 3)'

    """
    # factor names that appear before a bracket (string-literals already stripped)
    base = _vars_window(expr)                 # e.g. ['color']
    params = ", ".join(base)                  # 'color'
    lam = f"lambda {params}: {expr}"          # 'lambda color: color[-1]==color[0]'

    # find negative indices → window size = largest |index|
    neg_indices = [int(i) for i in re.findall(r"\[(-?\d+)\]", expr) if int(i) < 0]
    width = max(abs(i) for i in neg_indices) + 1   # default 1

    call = f"Window({lam}, [{', '.join(base)}], {width})"         # stride=1
    return call, lam, base, width
