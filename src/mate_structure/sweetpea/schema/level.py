from dataclasses import dataclass
from typing import Optional

from mate_strategy.schema import AnnotatedSchema
from mate_strategy.rules.predefined import NaturalNumber

from mate_structure.sweetpea.schema.expr import WithinExpr, WindowExpr



@dataclass
class LevelSchema(AnnotatedSchema):
    """
    A static `level` of a `factor`.

    name: Concrete value used in the experiment (e.g., "red" for a color `factor`)
    weight: Sampling weight (default is 1)

    Examples:
        >>> print(LevelSchema.prompt()) # doctest: +NORMALIZE_WHITESPACE
        Fill in **valid JSON** for the fields below. – **A single `level` of a `factor` within a factorial experimental design.**
        <BLANKLINE>
        Rules
        - name  – The concrete value used in the experiment (e.g., "red" for a color `factor`).
          • string
            (ex: "example")
        - weight  – Sampling weight (default is 1).
          • (Optional) Key can be *missing* or:
            - integer
            - None
        <BLANKLINE>
        Example:
        {
          "name": "example",
          "weight": 42
        }
        <BLANKLINE>
        Return **only** the JSON object — no code-fences, no comments.
        """

    name: str
    weight: Optional[NaturalNumber]

    __example_overrides__ = {
        'weight': 3
    }


@dataclass
class WithinDerivedLevelSchema(AnnotatedSchema):
    """
    A within level becomes active when a logical condition
    over other factors *within one trial* evaluates to **True**.

    name: Value the factor assumes when `expr` is True
    expr: Predicate (the variables must be names of other `factors` of this experimental design)
    weight: Sampling weight (default is 1)

    Examples:
        >>> print(WithinDerivedLevelSchema.prompt())

    """
    name: str
    expr: WithinExpr
    weight: Optional[NaturalNumber]

    __example_overrides__ = {
        'weight': 3
    }


@dataclass
class WindowDerivedLevelSchema(AnnotatedSchema):
    """
    A window level becomes active when a logical condition
    over other factors *between different trials* evaluates to **True**

    name: Value the factor assumes when `expr` is True
    expr: Predicate (the variables must be names of other `factors` of this experimental design)
    weight: Sampling weight (default is 1)

    Examples:
        >>> print(WindowDerivedLevelSchema.prompt())

    """
    name: str
    expr: WindowExpr
    weight: Optional[NaturalNumber]

    __example_overrides__ = {
        'weight': 3
    }
