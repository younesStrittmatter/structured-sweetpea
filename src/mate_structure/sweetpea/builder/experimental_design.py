from __future__ import annotations
import pprint
from typing import Dict, List, Tuple

from mate_structure.sweetpea.builder.factor import factor_build


# --------------------------------------------------------------------
def _py(name: str) -> str:
    """Safe Python identifier for a factor variable."""
    return name.strip().replace(" ", "_").replace("-", "_")


def _topo_order(built: Dict[str, Tuple[str, set]]) -> List[str]:
    """
    Kahn topological sort on the *deps* we already collected.
    built[name] = (factor_code, deps_set)
    """
    remaining = {k: v[1] for k, v in built.items()}   # name -> deps
    resolved, ordered = set(), []

    while remaining:
        progress = False
        for name, deps in list(remaining.items()):
            if deps <= resolved:          # all deps satisfied?
                ordered.append(name)
                resolved.add(name)
                remaining.pop(name)
                progress = True
        if not progress:
            raise ValueError(
                f"Cyclic dependency among factors: {', '.join(remaining)}")
    return ordered


def _crossing_to_code(crossing: List, ordered_names: List[str]) -> str:
    """
    Turn the user-supplied crossing (list or list-of-lists of *strings*)
    into a Python expression using the variable identifiers produced by
    _py().  Keeps original structure.
    """
    def convert(x):
        return _py(x)

    if isinstance(crossing[0], list):         # nested/multicross
        outer = [
            "[" + ", ".join(convert(f) for f in block) + "]"
            for block in crossing
        ]
        return "[" + ", ".join(outer) + "]"
    else:                                     # fully crossed
        return "[" + ", ".join(convert(f) for f in crossing) + "]"


# --------------------------------------------------------------------
def experimental_design_builder(data: dict, minimum_trials: int = 1, strategy='RandomGen') -> str:
    """
    Build runnable SweetPea code for an *ExperimentSchema*-validated dict.

    Returns the complete Python source as a single string.
    """
    factors   = data.get("factors")
    crossing  = data.get("crossing")

    if not factors:
        raise ValueError("Factors cannot be None")
    if not crossing:
        raise ValueError("Crossing cannot be None")

    # ---------- build each factor once, collect deps -----------------
    built: Dict[str, Tuple[str, set]] = {}
    for f in factors:
        code, deps = factor_build(f)        # deps already bubbled up
        built[f["name"]] = (code, set(deps))

    # ---------- order by dependencies --------------------------------
    ordered_names = _topo_order(built)      # list of factor *names*
    factor_decls  = "\n\n".join(built[n][0] for n in ordered_names)

    # ---------- design / crossing / block ----------------------------
    design_code   = "[" + ", ".join(_py(n) for n in ordered_names) + "]"
    crossing_code = _crossing_to_code(crossing, ordered_names)
    constraints   = f"[MinimumTrials({minimum_trials})]"

    block_cls = "CrossBlock" if isinstance(crossing[0], str) else "MultiCrossBlock"
    block_decl = (
        f"block = {block_cls}(design=design, crossings=crossing, constraints=constraints)"
    )

    header = (
        f"from sweetpea import Factor, DerivedLevel, WithinTrial, Window, "
        f"Level, CrossBlock, MultiCrossBlock, MinimumTrials, "
        f"synthesize_trials, print_experiments, tabulate_experiments,"
        f"{strategy}\n"
    )

    footer = (
        f"\nexperiments = synthesize_trials(block, 1, sampling_strategy={strategy})\n"
        "print_experiments(block, experiments)\n"

    )
    if block_cls == "CrossBlock":
        footer += "tabulate_experiments(block, experiments)\n"

    full_source = (
        header
        + "\n# ---------- factor declarations ----------\n"
        + factor_decls
        + "\n\n# ---------- design / crossing / block ----------\n"
        + f"design   = {design_code}\n"
        + f"crossing = {crossing_code}\n"
        + f"constraints = {constraints}\n"
        + block_decl
        + footer
    )

    return full_source
