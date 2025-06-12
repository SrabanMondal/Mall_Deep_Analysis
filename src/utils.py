from mlxtend.preprocessing import TransactionEncoder
from itertools import chain, combinations
import pandas as pd
def encode_transactions(transactions):
    """Encode transactions into a binary matrix."""
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    return pd.DataFrame(te_ary, columns=te.columns_)

def all_non_empty_subsets(s):
    """Generate all non-empty subsets of a set."""
    return [tuple(subset) for subset in chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))]