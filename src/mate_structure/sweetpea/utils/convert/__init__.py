# file: sweetpea_dep_sort.py
from __future__ import annotations

import ast, re, pandas as pd
from typing import Dict, List, Set, Any

from mate_structure.sweetpea.builder.expr import build_within, build_window

# ════════════════════════════════════════════════════════════════════
# utilities for detecting regular / derived kinds
# ════════════════════════════════════════════════════════════════════
def is_regular(factor: dict) -> bool:
    return all("expr" not in lv for lv in factor["levels"])

def is_window(factor: dict) -> bool:
    return any("[-" in lv.get("expr", "") for lv in factor["levels"])

# ════════════════════════════════════════════════════════════════════
# 1 · topological order of factors (unchanged from earlier)
# ════════════════════════════════════════════════════════════════════
def topo_sort_factors(factors: List[dict]) -> List[dict]:
    name2factor = {f["name"]: f for f in factors}
    deps: Dict[str, Set[str]] = {n: set() for n in name2factor}

    for f in factors:
        n = f["name"]
        for lv in f["levels"]:
            if "expr" not in lv:
                continue
            expr = lv["expr"]
            if "[-" in expr:
                _, _, base, _ = build_window(expr)
            else:
                _, _, base, _ = build_within(expr)
            deps[n].update(b for b in base if b in name2factor and b != n)

    waiting = {n: d for n, d in deps.items() if d}
    ordered = [n for n, d in deps.items() if not d]
    resolved = set(ordered)

    while waiting:
        ready = [n for n, d in waiting.items() if d <= resolved]
        if not ready:
            raise ValueError("Cyclic dependency among derived factors: "
                             + ", ".join(waiting))
        for n in ready:
            ordered.append(n)
            resolved.add(n)
            waiting.pop(n)

    for n in name2factor:
        if n not in ordered:
            ordered.insert(0, n)
    return [name2factor[n] for n in ordered]

# ════════════════════════════════════════════════════════════════════
# 2 · token helpers for expression substitution
# ════════════════════════════════════════════════════════════════════
_TOKEN_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(-?\d+)\]")
_VAR_RE   = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
_PY_WORDS = {"and", "or", "not", "in", "is",
             "True", "False", "None"}

def _strip_strings(s: str) -> str:
    """Return *s* with single- or double-quoted literals blanked out."""
    return re.sub(r"(\"[^\"]*\"|'[^']*')", " ", s)

def _compile_tokens(expr: str) -> list[tuple[str, str, int]]:
    """
    Return **every** factor reference in *expr* as a list of
    (token_string, base_name, index).

    * ``color[-1]`` → ('color[-1]', 'color', -1)
    * ``color[0]``  → ('color[0]',  'color',  0)
    * bare ``color`` (no brackets) is treated **exactly like** ``color[0]``.
    Examples:
        >>> _compile_tokens("color[-1] and color[0]")
        [('color[-1]', 'color', -1), ('color[0]', 'color', 0)]

        >>> _compile_tokens("'red' == word[-1]")
        [('word[-1]', 'word', -1)]

        >>> _compile_tokens('color[-1] == "green"')
        [('color[-1]', 'color', -1)]

    """
    tokens: list[tuple[str, str, int]] = []

    # ① indexed tokens (from full expr) ------------------------------
    indexed_bases = set()
    for m in _TOKEN_RE.finditer(expr):
        tok, base, idx = m.group(0), m.group(1), int(m.group(2))
        tokens.append((tok, base, idx))
        indexed_bases.add(base)

    # ② bare variables (scan *without* string literals) --------------
    for var in _VAR_RE.findall(_strip_strings(expr)):
        if var in _PY_WORDS or var in indexed_bases:
            continue
        tokens.append((var, var, 0))

    # longest tokens first → safe replacement order
    tokens.sort(key=lambda t: -len(t[0]))
    return tokens

def _evaluate_expr(
    expr: str,
    current_idx: int,
    df: pd.DataFrame,
    factor_names: set[str]
) -> bool:
    """
    Replace every occurrence of <factor>[k] or bare <factor> with its
    literal value and eval the resulting Python expression.
    """
    expr_sub = expr

    # ① window tokens --------------------------------------------------
    for tok, base, idx in _compile_tokens(expr):
        _idx = current_idx + idx
        if _idx < 0 or _idx >= len(df):
            return None
        val = df[base][_idx]
        lit = repr(val) if isinstance(val, str) else str(val)
        expr_sub = expr_sub.replace(tok, lit)


    try:
        return bool(eval(expr_sub))
    except Exception:
        return False

# ════════════════════════════════════════════════════════════════════
# 3 · dataframe → canonical factors
# ════════════════════════════════════════════════════════════════════
def to_canonical(
    df: pd.DataFrame,
    factors: List[dict],
    *,
    only_factors: bool = False,
    map_regular: Dict[str, Dict[str, str]] | None = None
) -> pd.DataFrame:

    ordered = topo_sort_factors(factors)
    df      = df.copy(deep=True)

    # ---------- regular factor sanity / optional + AUTO remap --------
    for f in ordered:
        if is_regular(f):
            col = f["name"]
            if col not in df.columns:
                raise KeyError(f"Missing factor column '{col}'")
            expected = [lv["name"] for lv in f["levels"]]
            found    = list(df[col].unique())

            # explicit user map
            if map_regular and col in map_regular:
                df[col] = df[col].map(map_regular[col])
                found   = list(df[col].unique())

            # automatic 1-to-1 if sizes equal
            if set(found) != set(expected) and len(found) == len(expected):
                auto_map = {src: dst for src, dst in zip(sorted(found),
                                                         sorted(expected))}
                df[col] = df[col].map(auto_map)
                found   = list(df[col].unique())

            if set(found) != set(expected):
                raise ValueError(f"Levels in '{col}' {found} "
                                 f"do not match design {expected}")

    # ---------- ensure derived columns exist -------------------------
    for f in ordered:
        if not is_regular(f) and f["name"] not in df.columns:
            df[f["name"]] = None


    factor_names = {f["name"] for f in factors}

    # ---------- row-wise evaluation ----------------------------------
    for f in ordered:
        if is_regular(f):
            continue
        res = []
        for idx, _ in df.iterrows():
            is_skip = False
            for lv in f["levels"]:

                expr = lv["expr"]
                if _evaluate_expr(expr, idx, df, factor_names):
                    res.append(lv["name"])
                    is_skip = True
                    break
            if not is_skip:
                res.append(None)


        df[f["name"]]= res


    if only_factors:
        df = df[[f["name"] for f in ordered]]
    return df
