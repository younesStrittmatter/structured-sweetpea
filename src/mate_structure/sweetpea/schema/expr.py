# expr_rule.py
from mate_strategy.rules import Rule
import re

# --------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------
_index_pattern = re.compile(r"\[[^\]]+\]")      # anything like [0], [-1], [ i ]

def _has_indexing(expr: str) -> bool:
    return bool(_index_pattern.search(expr))


# --------------------------------------------------------------------
# Within-trial expression  (NO indexing allowed)
# --------------------------------------------------------------------
class WithinExpr(Rule):
    @classmethod
    def describe(cls):
        return (
            'boolean expression **within a single trial**\n'
            'allowed operators: == != < > <= >= and or not\n'
            'e.g. "color==word" or "size>10 and color!=\'red\'"'
        )

    @classmethod
    def example(cls):
        return "color==word"

    @classmethod
    def validate(cls, v):
        return (
            isinstance(v, str)
            and bool(v.strip())
            and not _has_indexing(v)     # forbid [...], [-1], etc.
        )


# --------------------------------------------------------------------
# Across-trial / windowed expression  (indexing REQUIRED or at least ALLOWED)
# --------------------------------------------------------------------
class WindowExpr(Rule):
    @classmethod
    def describe(cls):
        return (
            'boolean expression that may reference **indexed trials**\n'
            'allowed operators: == != < > <= >= and or not\n'
            '(0 = current, -1 = previous, …)\n'
            'e.g. "response[-1]==response[0]" or "task[0]!=task[-3]"'
        )

    @classmethod
    def example(cls):
        return "color[0]==word[-1]"

    @classmethod
    def validate(cls, v):
        return (
            isinstance(v, str)
            and bool(v.strip())
            and _has_indexing(v)         # must contain at least one [...]
        )
