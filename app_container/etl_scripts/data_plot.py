import plotly.graph_objs as go
import app_container.etl_scripts.data_wrangle as dw
from app_container.etl_scripts.df_transform import AGG_FUNC_DICT
from typing import Callable
import pandas as pd


def plot_figures(df_dict: dict, date_list: list, firm_list: list):

    figures = []
    for key, func in AGG_FUNC_DICT.items():
        fig = plot_quarter_diff(df_dict, date_list, func, firm_list,
                                "% Change", key)
        figures.append(dict(data=fig))

    return figures


def multiple_bar_chart(df: pd.DataFrame, y_axis: str, title: str = None):
    """ Plot multiple bars chart given DataFrame.

    Args:
        df (pd.DataFrame): 2d DataFrame.
        y_axis (str): Y-axis name.
        title (str, optional): Title of the plot. Defaults to None.
        
    Returns:
        plotly.graph_objs._figure.Figure: Multiple bars chart.
    """
    # Plotting.
    graph = []
    for item in df.columns:
        x_val = df.index.tolist()
        y_val = df[item].tolist()
        graph.append(go.Bar(name=item, x=x_val, y=y_val))

    custom_layout = go.Layout(template="ggplot2",
                              yaxis_title=y_axis,
                              title=title,
                              legend=dict(orientation="h"))
    fig = go.Figure(data=graph, layout=custom_layout)

    return fig


def plot_quarter_diff(df_dict: dict,
                      date_list: list,
                      transform_func: Callable,
                      firm_list: list,
                      y_axis: str,
                      title: str = None):
    """ Plot a multiple bars chart for quarter to quarter difference.
    
    NOTE:
    1. X-axis = A list of companies.
    2. Y-axis = % change.

    Args:
        df_dict (dict): A dictionary contains multiple DataFrames.
        date_list (list): A list of dates for difference.
        transform_func (Callable): A callable function to transform DataFrame.
        firm_list (list): A list of firms.


    Returns:
        plotly.graph_objs._figure.Figure: Multiple bars chart for
            quarter to quarter difference.
    """

    # QtoQ difference summary table.
    df = dw.change_summary(df_dict, date_list, transform_func, firm_list)

    return multiple_bar_chart(df, y_axis, title)
