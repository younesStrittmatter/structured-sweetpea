from dataclasses import dataclass
from typing import List

from mate_strategy.schema import AnnotatedSchema
from mate_strategy.rules.predefined import OneOf

@dataclass
class VariableSchema(AnnotatedSchema):
    """
    A single variable used in an experiment.

    name: The name of the variable as it appears in the text
    level: The level at which the variable varies in the experiment:
        • "trial-wise": different on every trial
        • "block-wise": different across blocks
        • "subject-wise": differs per participant
        • "experiment-wise": constant throughout the entire experiment
    type: The data type of the variable, which informs analysis and simulation:
        • "numeric": continuous values (e.g., RT)
        • "categorical": non-ordered discrete labels (e.g., condition)
        • "ordinal": ordered categories (e.g., Likert scales)
        • "binary": exactly two levels (e.g., correct/incorrect)
    """

    name: str
    level: OneOf["trial-wise", "block-wise", "subject-wise", "experiment-wise"]
    type: OneOf["numeric", "categorical", "ordinal", "binary"]


@dataclass
class AnalyzedExperiment(AnnotatedSchema):
    """
    A statistical analysis performed on a single experiment.

    analysis_method: The primary statistical method used (e.g., ANOVA).
    dependent: List of variables analyzed as dependent variables.
    independent: List of independent variables (factors or covariates).
    other: Additional variables mentioned (e.g., controls, covariates, or unused).
    """
    analysis_method: OneOf['ANOVA', 't-test', 'regression', 'other', 'logistic regression']
    dependent: List[VariableSchema]
    independent: List[VariableSchema]
    other: List[VariableSchema]

@dataclass
class AllExperiments(AnnotatedSchema):
    """
    A list of analyzed experiments.

    Examples:
        >>> print(AllExperiments.prompt()) # doctest: +NORMALIZE_WHITESPACE
        Fill in **valid JSON** for the fields below. – **A list of analyzed experiments.**
    <BLANKLINE>
    Rules
    - experiments
      • list of AnalyzedExperiment – A statistical analysis performed on a single experiment.
      - experiments[].analysis_method  – The primary statistical method used (e.g., ANOVA).
        • one of 'ANOVA', 't-test', 'regression', 'other', 'logistic regression'
          (ex: "t-test")
      - experiments[].dependent  – List of variables analyzed as dependent variables.
        • list of VariableSchema – A single variable used in an experiment.
        - experiments[].dependent[].name  – The name of the variable as it appears in the text
          • string
            (ex: "example")
        - experiments[].dependent[].level  – The level at which the variable varies in the experiment:
          • one of 'trial-wise', 'block-wise', 'subject-wise', 'experiment-wise'
            (ex: "block-wise")
        - experiments[].dependent[].type  – The data type of the variable, which informs analysis and simulation:
          • one of 'numeric', 'categorical', 'ordinal', 'binary'
            (ex: "categorical")
      - experiments[].independent  – List of independent variables (factors or covariates).
        • list of VariableSchema – A single variable used in an experiment.
        - experiments[].independent[].name  – The name of the variable as it appears in the text
          • string
            (ex: "example")
        - experiments[].independent[].level  – The level at which the variable varies in the experiment:
          • one of 'trial-wise', 'block-wise', 'subject-wise', 'experiment-wise'
            (ex: "experiment-wise")
        - experiments[].independent[].type  – The data type of the variable, which informs analysis and simulation:
          • one of 'numeric', 'categorical', 'ordinal', 'binary'
            (ex: "ordinal")
      - experiments[].other  – Additional variables mentioned (e.g., controls, covariates, or unused).
        • list of VariableSchema – A single variable used in an experiment.
        - experiments[].other[].name  – The name of the variable as it appears in the text
          • string
            (ex: "example")
        - experiments[].other[].level  – The level at which the variable varies in the experiment:
          • one of 'trial-wise', 'block-wise', 'subject-wise', 'experiment-wise'
            (ex: "subject-wise")
        - experiments[].other[].type  – The data type of the variable, which informs analysis and simulation:
          • one of 'numeric', 'categorical', 'ordinal', 'binary'
            (ex: "binary")
    <BLANKLINE>
    Example 1:
    {
      "experiments": [
        {
          "analysis_method": "ANOVA",
          "dependent": [
            {
              "name": "reaction time",
              "level": "trial-wise",
              "type": "numeric"
            }
          ],
          "independent": [
            {
              "name": "sound condition",
              "level": "trial-wise",
              "type": "categorical"
            },
            {
              "name": "task modality",
              "level": "block-wise",
              "type": "categorical"
            },
            {
              "name": "serial position",
              "level": "trial-wise",
              "type": "ordinal"
            }
          ],
          "other": [
            {
              "name": "task order",
              "level": "subject-wise",
              "type": "categorical"
            }
          ]
        },
        {
          "analysis_method": "logistic regression",
          "dependent": [
            {
              "name": "error rate",
              "level": "trial-wise",
              "type": "numeric"
            }
          ],
          "independent": [
            {
              "name": "congruency",
              "level": "trial-wise",
              "type": "categorical"
            },
            {
              "name": "task",
              "level": "trial-wise",
              "type": "categorical"
            },
            {
              "name": "difficulty",
              "level": "block-wise",
              "type": "numeric"
            }
          ],
          "other": []
        }
      ]
    }
    <BLANKLINE>
    Return **only** the JSON object — no code-fences, no comments.

    """
    experiments: List[AnalyzedExperiment]

    __example_overrides__ = {
        'experiments': [
            {
                "analysis_method": "ANOVA",
                "dependent": [
                    {
                        "name": "reaction time",
                        "level": "trial-wise",
                        "type": "numeric"
                    }
                ],
                "independent": [
                    {
                        "name": "sound condition",
                        "level": "trial-wise",
                        "type": "categorical"
                    },
                    {
                        "name": "task modality",
                        "level": "block-wise",
                        "type": "categorical"
                    },
                    {
                        "name": "serial position",
                        "level": "trial-wise",
                        "type": "ordinal"
                    }
                ],
                "other": [
                    {
                        "name": "task order",
                        "level": "subject-wise",
                        "type": "categorical"
                    }
                ]
            },
            {
                "analysis_method": "logistic regression",
                "dependent": [
                    {
                        "name": "error rate",
                        "level": "trial-wise",
                        "type": "numeric"
                    }
                ],
                "independent": [
                    {
                        "name": "congruency",
                        "level": "trial-wise",
                        "type": "categorical"
                    },
                    {
                        "name": "task",
                        "level": "trial-wise",
                        "type": "categorical"
                    },
                    {
                        "name": "difficulty",
                        "level": "block-wise",
                        "type": "numeric"
                    }
                ],
                "other": []
            }
        ]
    }
