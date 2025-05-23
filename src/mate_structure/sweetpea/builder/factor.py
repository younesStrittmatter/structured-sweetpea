from mate_structure.sweetpea.builder.level import level_builder

def _py(name: str) -> str:
    """Sanitise for a valid Python identifier if needed."""
    return name.strip().replace(" ", "_").replace("-", "_")


def factor_build(data: dict):
    """
    Build a single Factor declaration.

    Returns
    -------
    factor_code : str        # e.g.  color = Factor("color", [...])
    deps        : set[str]   # other factor names referenced in *any*
                             # derived level of this factor
    """
    name   = data.get("name")
    levels = data.get("levels")

    if not name:
        raise ValueError("Factor name cannot be None")
    if not levels:
        raise ValueError("Factor levels cannot be None")

    level_codes = []
    deps = set()

    # build each level, collect code + deps
    for lv in levels:
        lv_code, lv_deps = level_builder(lv)
        level_codes.append(lv_code)
        deps.update(lv_deps)

    factor_code = (
        f'{_py(name)} = Factor("{name}", [\n    '
        + ",\n    ".join(level_codes)
        + "\n])"
    )

    return factor_code, deps
