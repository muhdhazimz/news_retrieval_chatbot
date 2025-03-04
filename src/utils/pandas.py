import pandas


def load_transaction_data(path: str = "./data.csv") -> pandas.DataFrame:
    """
    Load transaction data from a CSV.
    """

    return pandas.read_csv(path)
