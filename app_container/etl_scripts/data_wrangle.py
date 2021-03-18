import pandas as pd
import numpy as np
import datetime
from typing import Callable, Tuple, Union, List
from pathlib import Path
from itertools import combinations


def data_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # Forward filling the EMPTY portfolio type.
    df.iloc[1, :] = df.iloc[1, :].fillna(method='ffill')

    # Remove irrelevant rows.
    df = df.iloc[1:, :]

    # Create multi-index columns for this high dimension dataset.
    # Excel Template shold not change in any case.
    items = []
    for i in df.columns:
        if "Unnamed" in i:
            items.append(i)
        elif int(i[6:]) < 58:
            items.append("Assets")
        elif (int(i[6:]) >= 58) & (int(i[6:]) < 110):
            items.append("ECL")
        elif (int(i[6:]) >= 110) & (int(i[6:]) < 135):
            items.append("Staging balances (%)")
        elif (int(i[6:]) >= 135) & (int(i[6:]) < 141):
            items.append("Stage 2 Analysis")
        elif (int(i[6:]) >= 141) & (int(i[6:]) < 171):
            items.append("Coverage (%)")
        elif (int(i[6:]) >= 171) & (int(i[6:]) <= 194):
            items.append("Loss rates")
    items = [items]
    _ = [items.append(df.iloc[i, :].values) for i in range(0, 2)]

    # Set multi-index columns.
    df.columns = items

    # Reset index with firm name.
    df.index = df.iloc[:, 0]
    df = df.iloc[:, 1:]

    # Remove NaN columns.
    df = df.loc[:, df.iloc[1, :].notna()]

    # Remove irrelevant rows.
    df = df.iloc[2:, :]

    # Rename index.
    df.index.name = "Firm"
    # Remove the last 2 impairment & exposure columns.
    df = df.iloc[:, :-2]
    # Replace Excel generated "-" value to NaN.
    df = df.replace(['-'], np.NaN)

    return df


def df_diff_calc(df: pd.DataFrame) -> pd.Series:
    """ Function to retrieve the % difference of last two columns.

    Args:
        df (pd.DataFrame): 2d DataFrame with at least 2 columns.

    Returns:
        pd.Series: % Difference of last two columns.
    """
    if len(df.columns) < 2:
        raise IndexError("DataFrame column length must be greater than 1.")

    return df.iloc[:, -1].div(df.iloc[:, -2]) - 1


def qq_yy_convert(date_array: Union[np.ndarray, list]) -> List[datetime.date]:
    """ Convert QQYY format date series to machine readable date format.

    Args:
        date_array (Union[np.ndarray, list]): QQYY format date list or array.

    Returns:
        list: A machine readable date format.
    """
    date_list = [
        datetime.date(year=int(date.split("Q")[1]) + 2000,
                      month=int(date.split("Q")[0]) * 3,
                      day=1) for date in date_array
    ]
    date_list.sort()

    return date_list


def pivot_transform_df(df_dict: dict, date_list: list, firm_list,
                       transform_func: Callable) -> pd.DataFrame:
    """ Return the pivoted DataFrame after appending 
    all the DataFrames by date values.
    
    NOTE:
    Sorted by Firm name then Date.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates.
        transform_func (Callable): A callable function to transform DataFrame.

    Returns:
        pd.DataFrame: DataFrame with multiple dates.
    """
    table = []
    for date in date_list:
        df = transform_func(df_dict[date])
        df["Date"] = date
        df["Date"] = qq_yy_convert(df["Date"])
        table.append(df)
    table = pd.concat(table)

    # Sort by Firm name then Date.
    table = table.sort_values(by=['Firm', 'Date'], ascending=[True, True])
    table = table.pivot(columns="Date")

    # Multi-index columns order: Date -> Portfolios.
    table.columns = table.columns.swaplevel(0, 1)
    table.sort_index(axis=1, level=0, inplace=True)
    return table


def df_filter(df: pd.DataFrame, firm_list: List[str],
              portfolios: List[str]) -> pd.DataFrame:
    """ Filter the pivoted DataFrame with:
    1. Firms
    2. Portfolios

    Args:
        df (pd.DataFrame): Pivoted table 
            (Multi-index columns = (Date, Portfolios), index = firms).
        firm_list (List[str]): A list of firms.
        portfolios (List[str]): A list of portfolios.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """

    mask = np.in1d(df.columns.get_level_values(1), portfolios)
    return df.loc[firm_list, mask]


def relative_change_df(df_dict: dict, date_list: List[str],
                       firm_list: List[str], portfolios: List[str],
                       transform_func: Callable) -> pd.DataFrame:
    """ Return the DataFrame with % difference given the aggregation function.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates for difference.
        firm_list (List[str]): A list of firms.
        portfolios (List[str]): A list of portfolios.
        transform_func (Callable): A callable function to transform DataFrame.

    Returns:
        pd.DataFrame: DataFrame with relative difference of metrics given dates.
    """
    table = pivot_transform_df(df_dict, date_list, firm_list, transform_func)
    table = df_filter(table, firm_list, portfolios)

    # A combination of different dates for difference calculations.
    date_comb = list(
        combinations(table.columns.get_level_values(0).unique(), 2))
    tab_list = []  # List of DataFrames
    for i in date_comb:
        # Current vs previous dates.
        mask_old = table.columns.get_level_values(0) == i[0]
        mask_new = table.columns.get_level_values(0) == i[1]
        tab_old = table[table.columns[mask_old]]
        tab_new = table[table.columns[mask_new]]
        tab = tab_new / tab_old.values - 1

        # Sensible column names.
        col_name = (
            f"{i[1].year}-Q{i[1].month//3} vs {i[0].year}-Q{i[0].month//3}")
        new_cols = pd.MultiIndex.from_tuples([(col_name, tup[1])
                                              for tup in tab.columns])
        tab.columns = new_cols
        tab_list.append(tab)

    return pd.concat(tab_list, axis=1)


PATH = Path(__file__).parents[1] / "dataset"
DATA_PATH = {"UK": r"dataset/UK/", "GROUP": r"dataset/GROUP/"}
PORTFOLIOS = [
    "Total Loans & Advances", "Mortgages",
    "Consumer Lending (including Auto Finance)", "Corporate & Commercial"
]
data_list = {
    'UK': ['4Q20.xlsx', '4Q19.xlsx', '2Q20.xlsx'],
    'GROUP': ['4Q20.xlsx', '4Q19.xlsx', '2Q20.xlsx']
}


def initiate_df() -> Tuple[dict, dict]:
    """ Create DataFrame and pre-process all data-sets
    for analysis. 

    Returns:
        Tuple[dict, dict]: Dictionaries containing multiple 
            DataFrames for each segment 
    """

    df_uk = dict()
    df_group = dict()
    for key, item in data_list.items():
        for file in item:
            _df = pd.read_excel(DATA_PATH[key] + f"{file}", skiprows=2)

            date = file.split(".")[0]
            # UK / Group separation.
            if key == "GROUP":
                df_group[f"{date}"] = data_preprocess(_df)
            else:
                df_uk[f"{date}"] = data_preprocess(_df)

    return df_uk, df_group


def df_extract(segment, date_list):
    df_dict = dict()
    for date in date_list:
        df_dict[date] = data_preprocess(
            pd.read_excel(r"dataset/" + segment + f"/{date}.xlsx", skiprows=2))

    return df_dict