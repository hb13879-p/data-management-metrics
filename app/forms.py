from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    SelectMultipleField,
    PasswordField,
)
from wtforms.validators import DataRequired, Optional


class AppHomePageForm(FlaskForm):
    choices = [("csv", "CSV"), ("db", "SQL Database")]
    connector = SelectField(
        "Connector",
        choices=choices,
        default="db",
        id="connector_f",
        render_kw={"onchange": "showHideField()"},
    )
    db_server = StringField(
        "Host", validators=[Optional()]
    )  # , validators=[DataRequired()])
    db_port = StringField("Port", validators=[Optional()])
    db_name = StringField("Name", validators=[Optional()])
    db_user = StringField("Username", validators=[Optional()])
    db_password = PasswordField("Password", validators=[Optional()])
    db_schema = SelectField(
        "DB Schema", choices=[], id="dbSchema_f", validators=[Optional()]
    )  # ,render_kw={'onchange':"showHideField()"})
    csv_file = FileField(
        "CSV File", id="upload_file_f"
    )  # , validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
