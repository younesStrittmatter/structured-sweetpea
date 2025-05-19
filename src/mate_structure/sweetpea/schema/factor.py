from dataclasses import dataclass
from typing import List, Union
from mate_strategy.schema import Schema, AnnotatedSchema
from src.mate_structure.sweetpea.schema.level import LevelSchema, WindowDerivedLevelSchema, WithinDerivedLevelSchema


@dataclass
class FactorSchema(AnnotatedSchema):
    """
    A factor in a factorial experimental design

    name: The name of the factor
    levels: A list of levels the factor can assume

    Examples:
        >>> print(FactorSchema.prompt()) # doctest: +NORMALIZE_WHITESPACE
        Fill in **valid JSON** for the fields below. – **A factor in a factorial experimental design**
        <BLANKLINE>
        Rules
        - name  – The name of the factor
          • string
            (ex: "example")
        - levels  – A list of levels the factor can assume
          • choose **one** of:
            1. list of LevelSchema – A static `level` of a `factor`.
              - levels[].name  – Concrete value used in the experiment (e.g., "red" for a color `factor`)
                • string
                  (ex: "example")
              - levels[].weight  – Sampling weight (default is 1)
                • (Optional) Key can be *missing* or:
                  - integer (>= 1)
                  - None
            2. list of WithinDerivedLevelSchema – A within level becomes active when a logical condition
             over other factors *within one trial* evaluates to **True**.
              - levels[].name  – Value the factor assumes when `expr` is True
                • string
                  (ex: "example")
              - levels[].expr  – Predicate (the variables must be names of other `factors` of this experimental design)
                • boolean expression **within a single trial**
                  allowed operators: == != < > <= >= and or not
                  e.g. "color==word" or "size>10 and color!='red'"
                  (ex: "color==word")
              - levels[].weight  – Sampling weight (default is 1)
                • (Optional) Key can be *missing* or:
                  - integer (>= 1)
                  - None
            3. list of WindowDerivedLevelSchema – A window level becomes active when a logical condition
             over other factors *between different trials* evaluates to **True**
              - levels[].name  – Value the factor assumes when `expr` is True
                • string
                  (ex: "example")
              - levels[].expr  – Predicate (the variables must be names of other `factors` of this experimental design)
                • boolean expression that may reference **indexed trials**
                  allowed operators: == != < > <= >= and or not
                  (0 = current, -1 = previous, …)
                  e.g. "response[-1]==response[0]" or "task[0]!=task[-3]"
                  (ex: "color[0]==word[-1]"…)
              - levels[].weight  – Sampling weight (default is 1)
                • (Optional) Key can be *missing* or:
                  - integer (>= 1)
                  - None
        <BLANKLINE>
        Example 1:
        {
          "name": "color",
          "levels": [
            {
              "name": "red",
              "weight": 2
            },
            {
              "name": "green"
            },
            {
              "name": "grey"
            }
          ]
        }
        <BLANKLINE>
        Example 2:
        {
          "name": "congruency",
          "levels": [
            {
              "name": "congruent",
              "expr": "color==word and color!='grey'"
            },
            {
              "name": "incongruent",
              "expr": "color!=word and color!='grey'"
            },
            {
              "name": "neutral",
              "expr": "color=='grey'"
            }
          ]
        }
        <BLANKLINE>
        Example 3:
        {
          "name": "response transition",
          "levels": [
            {
              "name": "repeat",
              "expr": "response[-1]==response[0]"
            },
            {
              "name": "switch",
              "expr": "response[-1]!=response[0]"
            }
          ]
        }
        <BLANKLINE>
        Return **only** the JSON object — no code-fences, no comments.

    """
    name: str
    levels: Union[List[LevelSchema], List[WithinDerivedLevelSchema], List[WindowDerivedLevelSchema]]

    __example_overrides__ = {
        "name": "color",
        "levels": [
            {"name": "red", "weight": 2},
            {"name": "green"},
            {"name": "grey"}
        ]
    }

    __additional_examples__ = [
        {
            "name": "congruency",
            "levels": [
                {"name": "congruent", "expr": "color==word and color!='grey'"},
                {"name": "incongruent", "expr": "color!=word and color!='grey'"},
                {"name": "neutral", "expr": "color=='grey'"}

            ]
        },
        {
            "name": "response transition",
            "levels": [
                {"name": "repeat", "expr": "response[-1]==response[0]"},
                {"name": "switch", "expr": "response[-1]!=response[0]"}
            ]
        }
    ]
