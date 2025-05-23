import pandas as pd
from itertools import combinations
from typing import Iterable, Mapping, Tuple, Dict, Any


def report(
    df: pd.DataFrame,
    columns: Iterable[str],
    *,
    crossings: Iterable[Tuple[str, ...]] | None = None,
    normalize: bool = False,
) -> Dict[str | Tuple[str, ...], Mapping[Any, int | float]]:
    """
    Return observed frequencies for…

    • each individual column                    → 1-way counts
    • each requested crossing (joint columns)  → k-way counts

    Parameters
    ----------
    df : DataFrame
        Your data.
    columns : iterable of str
        Columns to analyse.  Order doesn’t matter.
    crossings : iterable of tuple[str, ...] | None, default None
        If None → every possible crossing of the listed columns (2-way, 3-way, …).
        Otherwise supply explicit tuples, e.g.  [("color", "shape"), ("subject",)].
    normalize : bool, default False
        If True, return proportions instead of raw counts.

    Returns
    -------
    dict
        Keys are column names (str) or column-tuples for crossings.
        Values are Counters:  {level_or_tuple: count | proportion}.
    """
    columns = list(columns)
    report: Dict[str | Tuple[str, ...], Mapping[Any, int | float]] = {}

    # 1-way frequencies
    for c in columns:
        vc = df[c].value_counts(normalize=normalize, dropna=False)
        report[c] = vc.to_dict()

    # decide which crossings to compute
    if crossings is None:
        # all non-empty combinations, size ≥ 2
        all_cross = (
            comb for r in range(2, len(columns) + 1)
            for comb in combinations(columns, r)
        )
    else:
        all_cross = crossings

    # k-way frequencies
    for cross in all_cross:
        cross = tuple(cross)            # make hashable / canonical
        vc = (
            df
            .groupby(list(cross))
            .size()
            .pipe(lambda s: s / len(df) if normalize else s)
        )
        report[cross] = vc.to_dict()

    return report
