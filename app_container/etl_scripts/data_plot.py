import plotly.graph_objs as go
import plotly
import app_container.etl_scripts.data_wrangle as dw
from app_container.etl_scripts.df_transform import AGG_FUNC_DICT
from typing import Callable, List
import pandas as pd


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


def mult_bar_chart_produce(df: pd.DataFrame, y_axis: str) -> List[object]:
    """ Produce multiple bar charts for DataFrame with Multi-index columns.

    Args:
        df (pd.DataFrame): DataFrame with Multi-index columns
        y_axis (str): Y-axis name.

    Returns:
        List[plotly.graph_objs._figure.Figure]: A list of multiple bars chart.
    """
    # Identify the list of multi-index column.
    items = df.columns.get_level_values(0).unique()[::-1]
    plot_list = []
    for i in items:
        tab = df[[i]]
        tab.columns = tab.columns.get_level_values(1)
        fig = multiple_bar_chart(tab, y_axis, i)
        plot_list.append(fig)
    return plot_list