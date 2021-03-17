from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired


class SegmentInput(FlaskForm):
    segment = SelectField("Segment", choices=[], validators=[DataRequired()])
    submit1 = SubmitField("Submit")


class UserInput(FlaskForm):
    dates = SelectMultipleField("Segment", choices=[], validators=[])
    firms = SelectMultipleField("Firms", choices=[], validators=[])
    submit2 = SubmitField("Submit")
