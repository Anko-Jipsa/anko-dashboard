import pandas as pd
import numpy as np
import datetime
from typing import Callable, Tuple, Union
from pathlib import Path


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


def qq_yy_convert(date_array: Union[np.ndarray, list]) -> list:
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

    return date_list


def df_append_dates(df_dict: dict, date_list: list,
                    transform_func: Callable) -> pd.DataFrame:
    """ Transform DataFrames with heterogeneous dates then
    append all to create a unified DataFrame.
    
    NOTE:
    Sorted by Firm name then Date.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates for difference.
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
    return table


def summary_tb_firm(df_dict: dict, date_list: list, transform_func: Callable):
    """ Generate a dictionary that contains multiple transformed DataFrames.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates for difference.
        transform_func (Callable): A callable function to transform DataFrame.

    Returns:
        [type]: [description]
    """

    table = df_append_dates(df_dict, date_list, transform_func)

    summary_firm = dict()
    firm_list = table.index.unique().to_list()

    # Summary loop.
    for i in firm_list:
        sub_table = table.loc[i, :].T

        # Convert to Date column.
        sub_table.columns = sub_table.loc["Date", :]
        sub_table = sub_table.drop(["Date"], axis=0)

        # Change to float.
        sub_table = sub_table.apply(pd.to_numeric)
        sub_table["Last QtQ Change"] = df_diff_calc(sub_table)

        summary_firm[i] = sub_table
        del sub_table
    return summary_firm


def summary_tb_portfolio(df_dict, date_list, transform_func):
    """ JOIN the list of DataFrames by list of dates

    Args:
        df_dict ([type]): [description]
        date_list ([type]): [description]
        transform_func ([type]): [description]

    Returns:
        [type]: [description]
    """
    # JOINED table.
    table = df_append_dates(df_dict, date_list, transform_func)
    summary_firm = dict()  # Initialise the group dictionary.

    for i in table.columns[:-1]:
        sub_table = table.pivot(columns='Date', values=i)
        sub_table = sub_table.apply(pd.to_numeric)
        sub_table["Last QtQ Change"] = df_diff_calc(sub_table)
        summary_firm[i] = sub_table

    return pd.concat(summary_firm, axis=1)


def change_summary(df_dict: dict, date_list: list, transform_func: Callable,
                   firm_list: list):
    """ Summary of % between given dates.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates for difference.
        transform_func (Callable): Aggregation function for summary table.
        firm_list (list): A list of firms.

    Returns:
        pd.DataFrame: Summary table for difference.
    """
    # QtoQ difference summary table.
    df = summary_tb_portfolio(df_dict, date_list, transform_func)

    # Filter for Q to Q change.
    mask = df.columns.get_level_values(1) == "Last QtQ Change"
    df = df[df.columns[mask]]
    df.columns = df.columns.droplevel(1)
    df = df.dropna(axis=0, how="all")

    # Filter dataframe by firms and portfolios.
    df = df.reindex(index=firm_list,
                    columns=[
                        "Total", "Mortgages",
                        "Consumer Lending (including Auto Finance)",
                        "Corporate & Commercial"
                    ])
    return df


PATH = Path(__file__).parents[1] / "dataset"
DATA_PATH = {"UK": r"dataset/UK/", "GROUP": r"dataset/GROUP/"}

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