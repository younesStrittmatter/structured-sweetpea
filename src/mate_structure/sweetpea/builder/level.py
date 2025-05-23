import re
from typing import List, Tuple

from mate_structure.sweetpea.builder.expr import build_within, build_window


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def regular_level_builder(data) -> Tuple[str, List[str]]:
    """
    Build a static level.

    >>> regular_level_builder({"name": "level1", "weight": 2})
    ('Level(name="level1", weight=2)', [])
    >>> regular_level_builder({"name": None, "weight": 2})  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Level name cannot be None
    """
    name = data.get("name")
    weight = data.get("weight", 1)
    if not name:
        raise ValueError("Level name cannot be None")
    return f'Level(name="{name}", weight={weight})', []


def within_derived_level_builder(data) -> Tuple[str, List[str]]:
    """
    >>> within_derived_level_builder(
    ...     {"name": "level1", "expr": "color==word", "weight": 2})
    ('DerivedLevel("level1", WithinTrial(lambda color, word: color==word, [color, word]), 2)', ['color', 'word'])
    """
    name = data.get("name")
    expr = data.get("expr")
    weight = data.get("weight", 1)
    if not name or not expr:
        raise ValueError("Level name or expr cannot be None")

    call, _, deps, _ = build_within(expr)  # deps bubbles up
    return f'DerivedLevel("{name}", {call}, {weight})', deps


def window_derived_level_builder(data) -> Tuple[str, List[str]]:
    """
    >>> window_derived_level_builder(
    ...     {"name": "level1", "expr": "color[-1]==color[0]", "weight": 2})
    ('DerivedLevel("level1", Window(lambda color: color[-1]==color[0], [color], 2), 2)', ['color'])
    """
    name = data.get("name")
    expr = data.get("expr")
    weight = data.get("weight", 1)
    if not name or not expr:
        raise ValueError("Level name or expr cannot be None")

    call, _, deps, _ = build_window(expr)
    return f'DerivedLevel("{name}", {call}, {weight})', deps


# ----------------------------------------------------------------------
# dispatcher with indexing test
# ----------------------------------------------------------------------
_INDEX_PATTERN = re.compile(r"\[-?\d+\]")  # matches [0] , [-1] , ...


def level_builder(data: dict) -> Tuple[str, List[str]]:
    """
    Dispatch to the correct builder and return *(level_code, deps)*.

    >>> level_builder({"name": "red"})
    ('Level(name="red", weight=1)', [])
    >>> level_builder({"name": "rep", "expr": "color==word"})
    ('DerivedLevel("rep", WithinTrial(lambda color, word: color==word, [color, word]), 1)', ['color', 'word'])
    >>> level_builder({"name": "switch", "expr": "color[-1]!=color[0]"})
    ('DerivedLevel("switch", Window(lambda color: color[-1]!=color[0], [color], 2), 1)', ['color'])
    """
    if "expr" not in data:  # static level
        return regular_level_builder(data)

    if _INDEX_PATTERN.search(data["expr"]):  # window derived
        return window_derived_level_builder(data)

    return within_derived_level_builder(data)  # within derived
