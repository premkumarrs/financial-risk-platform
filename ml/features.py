import numpy as np
import pandas as pd


def engineer_features(df):

    # High amount flag
    df["high_amount_flag"] = (df["amount"] > 15000).astype(int)

    # Foreign transaction flag
    df["is_foreign"] = (~df["location"].isin(["New York", "London"])).astype(int)

    # ATM usage flag
    df["is_atm"] = (df["device"] == "ATM").astype(int)

    # Log transform amount (reduces skew)
    df["amount_log"] = np.log1p(df["amount"])

    return df
