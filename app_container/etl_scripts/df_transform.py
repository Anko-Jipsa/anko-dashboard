import pandas as pd


def agg_ecl_df(df: pd.DataFrame) -> pd.DataFrame:
    """ Retrieve total ECL value of different porbolios.

    Args:
        df (pd.DataFrame): pre-processed JOINED pd.DataFrame.

    Returns:
        pd.DataFrame: Aggregated table with portfolio-level ECL.
    """
    mask = df["ECL"].columns.get_level_values(1) == "Total"
    df = df["ECL"].iloc[:, mask]
    df.columns = df.columns.get_level_values(0)
    return df


def agg_st2_df(df: pd.DataFrame) -> pd.DataFrame:
    """ Retrieve Stage 2 balance % of different porbolios.

    Args:
        df (pd.DataFrame): pre-processed JOINED pd.DataFrame.

    Returns:
        pd.DataFrame: Aggregated table with portfolio-level Stage 2 balance.
    """
    mask = df["Staging balances (%)"].columns.get_level_values(1) == "S2"
    df = df["Staging balances (%)"].iloc[:, mask]
    df.columns = df.columns.get_level_values(0)

    return df


def agg_st3_df(df: pd.DataFrame) -> pd.DataFrame:
    """ Retrieve Stage 3 balance % of different porbolios.

    Args:
        df (pd.DataFrame): pre-processed JOINED pd.DataFrame.

    Returns:
        pd.DataFrame: Aggregated table with portfolio-level Stage 3 balance.
    """
    mask = df["Staging balances (%)"].columns.get_level_values(1) == "S3"
    df = df["Staging balances (%)"].iloc[:, mask]
    df.columns = df.columns.get_level_values(0)
    return df


def agg_coverage_df(df: pd.DataFrame) -> pd.DataFrame:
    """ Retrieve total coverage ratio of different porbolios.

    Args:
        df (pd.DataFrame): pre-processed JOINED pd.DataFrame.

    Returns:
        pd.DataFrame: Aggregated table with portfolio-level coverage ratio.
    """
    mask = df["Coverage (%)"].columns.get_level_values(1) == "Total"
    df = df["Coverage (%)"].iloc[:, mask]
    df.columns = df.columns.get_level_values(0)
    return df


AGG_FUNC_DICT = {
    "ECL": agg_ecl_df,
    "Stage 2 Balance": agg_st2_df,
    "Stage 3 Balance": agg_st3_df,
    "Coverage": agg_coverage_df,
}
