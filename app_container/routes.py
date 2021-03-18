""" Main routes.

# TODO:
    1. Separate analytics page into each components (ECL, Stage 2, Stage 3, Coverage)
    2. Touch the asthetics.
    3. Include deeper analysis.
    4. Include Macroeconomics...
    5. etc...
"""
from app_container.etl_scripts.df_transform import agg_ecl_df, agg_st2_df
from app_container import app

import json
import plotly
from flask import (render_template, request, session, url_for)
from app_container import etl_scripts as etl
from app_container.flask_components.input_form import *
from app_container._input import DATE, DIRTY_DICT

app.config['SECRET_KEY'] = 'abcdefg'


@app.route('/')
def front():
    return render_template("front.html")


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template("dashboard.html")


@app.route('/ecl', methods=['POST', 'GET'])
def ecl():
    segment_form = SegmentInput()
    input_form = UserInput()
    # Update Input choices for the forms.
    segment_form.segment.choices = [(key, key) for key in DIRTY_DICT.keys()]
    input_form.dates.choices = [(item, item) for item in DATE]

    if request.method == 'POST':
        if request.form.get("update_segment"):
            # Request data from the Segment input form.
            session["segment"] = segment_form.segment.data

            # Update Input choices for the form: FIRMS.
            firm_list = DIRTY_DICT[session["segment"]]
            input_form.firms.choices = [(item, item) for item in firm_list]

        elif request.form.get("update_input"):
            session["dates"] = input_form.dates.data
            session["firms"] = input_form.firms.data

        else:
            print("Request form not detected.")  # unknown
    elif request.method == 'GET':
        print("GET")

    if session.get('firms') and session.get('dates') and len(
            session["dates"]) > 1:
        df = etl.df_extract(session["segment"], session["dates"])

        df = etl.relative_change_df(df, session["dates"], session["firms"],
                                    etl.PORTFOLIOS, agg_ecl_df)
        # List of plots.
        figures = etl.mult_bar_chart_produce(df, "% Change in ECL")
        # plot ids for the html id tag
        ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]
        # Convert the plotly figures to JSON for javascript in html template
        plotly_figs = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    else:
        figures = None
        ids = None
        plotly_figs = None

    return render_template('ecl_board.html',
                           ids=ids,
                           plotly_figs=plotly_figs,
                           segment_form=segment_form,
                           input_form=input_form)


@app.route('/stage2', methods=['POST', 'GET'])
def stage2():
    segment_form = SegmentInput()
    input_form = UserInput()
    # Update Input choices for the forms.
    segment_form.segment.choices = [(key, key) for key in DIRTY_DICT.keys()]
    input_form.dates.choices = [(item, item) for item in DATE]

    if request.method == 'POST':
        if request.form.get("update_segment"):
            # Request data from the Segment input form.
            session["segment"] = segment_form.segment.data

            # Update Input choices for the form: FIRMS.
            firm_list = DIRTY_DICT[session["segment"]]
            input_form.firms.choices = [(item, item) for item in firm_list]

        elif request.form.get("update_input"):
            session["dates"] = input_form.dates.data
            session["firms"] = input_form.firms.data

        else:
            print("Request form not detected.")  # unknown
    elif request.method == 'GET':
        print("GET")

    if session.get('firms') and session.get('dates') and len(
            session["dates"]) > 1:
        df = etl.df_extract(session["segment"], session["dates"])

        df = etl.relative_change_df(df, session["dates"], session["firms"],
                                    etl.PORTFOLIOS, agg_st2_df)
        # List of plots.
        figures = etl.mult_bar_chart_produce(df, "% Change in Stage 2 Balance")
        # plot ids for the html id tag
        ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]
        # Convert the plotly figures to JSON for javascript in html template
        plotly_figs = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    else:
        figures = None
        ids = None
        plotly_figs = None

    return render_template('stage2_board.html',
                           ids=ids,
                           plotly_figs=plotly_figs,
                           segment_form=segment_form,
                           input_form=input_form)