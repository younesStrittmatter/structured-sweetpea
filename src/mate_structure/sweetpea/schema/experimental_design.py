# experiment_schema.py
from dataclasses import dataclass
from typing import List, Optional

from mate_strategy.schema import AnnotatedSchema, constraint

from mate_structure.sweetpea.schema.factor import FactorSchema


@dataclass
class ExperimentSchema(AnnotatedSchema):
    """
    A complete factorial experiment:
    Factors plus crossing information.

    factors: List of factors that fully define the design.
    crossing: List of blocks defining a crossing; each block is a list of *factor names*
        that must all exist in `factors`.

    Examples:
        >>> print(ExperimentSchema.prompt()) # doctest: +NORMALIZE_WHITESPACE

    """
    factors: List[FactorSchema]
    crossing: List[List[str]]
    __example_overrides__ = {
        "factors": [
            {
                "name": "color",
                "levels": [
                    {"name": "red"},
                    {"name": "green"},
                    {"name": "blue"},
                    {"name": "grey", "weight": 3}
                ]
            },
            {
                "name": "word",
                "levels": [
                    {"name": "red"},
                    {"name": "green"},
                    {"name": "blue"}
                ]
            },
            {
                "name": "congruency",
                "levels": [
                    {"name": "congruent", "expr": "color==word and color!='grey'"},
                    {"name": "incongruent", "expr": "color!=word and color!='grey'"},
                    {"name": "neutral", "expr": "color=='grey'"},
                ]
            },
            {
                "name": "congruency_transition",
                "levels": [
                    {"name": "cc", "expr": "congruency[-1]=='congruent' and congruency[0]=='congruent'"},
                    {"name": "ci", "expr": "congruency[-1]=='congruent' and congruency[0]=='incongruent'"},
                    {"name": "cn", "expr": "congruency[-1]=='congruent' and congruency[0]=='neutral'"},
                    {"name": "ic", "expr": "congruency[-1]=='incongruent' and congruency[0]=='congruent'"},
                    {"name": "ii", "expr": "congruency[-1]=='incongruent' and congruency[0]=='incongruent'"},
                    {"name": "in", "expr": "congruency[-1]=='incongruent' and congruency[0]=='neutral'"},
                    {"name": "nc", "expr": "congruency[-1]=='neutral' and congruency[0]=='congruent'"},
                    {"name": "ni", "expr": "congruency[-1]=='neutral' and congruency[0]=='incongruent'"},
                    {"name": "nn", "expr": "congruency[-1]=='neutral' and congruency[0]=='neutral'"},
                ]

            }
        ],
        "crossing": [["color", "congruency"], ["congruency_transition"]],
    }

    @constraint("crossing",
                "all factor names referenced in crossing must appear in factors")
    def _(data):
        names = {f["name"] for f in data["factors"]}
        return all(all(n in names for n in block) for block in data["crossing"])
