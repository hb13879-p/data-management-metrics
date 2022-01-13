from flask import (
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    session,
    jsonify,
)
from app import app
import os
import pandas as pd
from werkzeug.utils import secure_filename
import time
import json
import sys

from app.profiler.data_sources import InMemoryDataSource
from app.profiler.tabular_readers import CSVReader
from app.profiler.metrics import *
from app.profiler.dashboards import Dashboard, StandardDashboard
from .forms import AppHomePageForm


@app.route("/error")
def error():
    return render_template("404.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    form = AppHomePageForm()
    if request.form.get("connector") == "db":
        if request.form.get("db_schema") is None:
            session["db_user"] = request.form["db_user"]
            session["db_server"] = request.form["db_server"]
            session["db_password"] = request.form["db_password"]
            session["db_port"] = request.form["db_port"]
            session["db_name"] = request.form["db_name"]
            session["connector"] = "db"
        # prf = SQLProfiler()
        schema_names = [("demo_db", "demo_db")]
        form.db_schema.choices = schema_names
        # session['profiler'] = prf.__dict__
        if request.form.get("db_schema") is None and form.validate_on_submit():
            return render_template("homepage.html", form=form, db_selected="t")

    if request.form.get("connector") == "csv":
        if form.validate_on_submit():
            session["connector"] = "csv"
            f = form.csv_file.data
            session["filename"] = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], session["filename"]))
            return redirect(url_for("profiler_result"), code=307)

    if form.validate_on_submit():
        return redirect(url_for("profiler_result"), code=307)

    return render_template(
        "homepage.html", form=form, db_selected="f", csv_selected="f"
    )


@app.route("/profiler_result", methods=["GET", "POST"])
def profiler_result():
    connector = request.form.get("connector")
    db_input_file = request.form.get("db_input_file")
    schema = request.form.get("db_schema")
    return render_template(
        "calculating.html",
        connector=connector,
        db_input_file=db_input_file,
        db_schema=schema,
    )


@app.route("/basic_profile", methods=["POST"])
def basic_profile():
    time.sleep(3)
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@app.route("/output")
def output():
    bcm_data_source = InMemoryDataSource(
        CSVReader(app.config["DEMO_DATA_SOURCE"], "mortgage_data_v4.csv")
    )
    dashboard = StandardDashboard(
        BasicProfile(bcm_data_source),
        ExtractDataRules(bcm_data_source),
        GroupedZScore(
            bcm_data_source,
            {
                "id_col": "user_id",
                "group_key": "card_type",
                "group_value": "credit_rate",
            },
        ),
        ExtractBadPostcode(
            bcm_data_source, {"id_col": "user_id", "postcd_col": "PostCode"}
        ),
        DetectBadAddress(
            bcm_data_source, {"id_col": "user_id", "address_col": ["address", "city"]}
        ),
        [
            TotalBlankCells(bcm_data_source, {"pc": True}),
            TotalRowsCols(bcm_data_source),
            DuplicateRows(bcm_data_source),
            ExtractPIIAttributes(bcm_data_source),
        ],
        ClassifyClientNotes(
            bcm_data_source, {"id_col": "user_id", "notes_col": "client_notes"}
        ),
    )
    dashboard.calculate_dashboard()
    cols = dashboard.get_column_names()
    (
        headline_metric_results,
        headline_metric_labels,
        headline_metric_icons,
        headline_metric_colours,
    ) = dashboard.get_headline_metrics()
    session["dashboard"] = dashboard
    return render_template(
        "dashboard.html",
        no_headline_metrics=len(headline_metric_results),
        headline_metric_labels=headline_metric_labels,
        headline_metrics=headline_metric_results,
        headline_metric_icons=headline_metric_icons,
        headline_metric_colours=headline_metric_colours,
        cols=cols,
    )


@app.route("/display_col", methods=["POST"])
def display_col():
    col_name = request.form.get("col_name")
    dashboard = session["dashboard"]
    columnview = dashboard.get_columnwise_view(col_name)
    return jsonify(col_name=col_name, columnview=columnview)


@app.route("/get_tabular_data", methods=["GET", "POST"])
def get_tabular_data():
    dashboard = session["dashboard"]
    df = dashboard.get_tabular_view()
    return jsonify(
        tabular=df.to_html(
            table_id="tabular_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )


@app.route("/get_targets_data", methods=["GET", "POST"])
def get_targets_data():
    dashboard = session["dashboard"]
    df = dashboard.get_targets_view()
    return jsonify(
        targets=df.to_html(
            table_id="targets_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )


@app.route("/get_anomaly_data", methods=["GET", "POST"])
def get_anomaly_data():
    dashboard = session["dashboard"]
    df = dashboard.get_anomaly_view()
    df = df.head(10)
    return jsonify(
        anom_data=df.to_html(
            table_id="anomaly_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )


@app.route("/get_ml_address_data", methods=["GET", "POST"])
def get_ml_address_data():
    dashboard = session["dashboard"]
    df = dashboard.get_ml_address_view()
    app.logger.debug(df.loc[df["Validity Score"] < 0.5])
    df = df.drop_duplicates(subset=["addr", "Validity Score"]).head(
        20
    )  # .sort_values('Validity Score')
    return jsonify(
        ml_addr_data=df.to_html(
            table_id="ml_addr_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )


@app.route("/get_postcode_data", methods=["GET", "POST"])
def get_postcode_data():
    dashboard = session["dashboard"]
    df = dashboard.get_postcode_view()
    df = df.head(10)
    return jsonify(
        postcode_data=df.to_html(
            table_id="postcode_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )


@app.route("/get_data_rules_data", methods=["GET", "POST"])
def get_data_rules_data():
    dashboard = session["dashboard"]
    data_rules, ai_rules = dashboard.get_data_rules_view()
    return jsonify(data_rules_data=data_rules, ai_rules_data=ai_rules)


@app.route("/get_client_notes_data", methods=["GET", "POST"])
def get_client_notes_data():
    dashboard = session["dashboard"]
    df = dashboard.get_client_notes_view()
    df = df.loc[df["client_notes"] != ""]
    df = df.drop_duplicates(
        subset=["client_notes", "Confidence Score"]
    )  # .sort_values('Confidence Score', ascending=False)
    app.logger.debug(df)
    return jsonify(
        client_notes_data=df.to_html(
            table_id="client_notes_table",
            classes=["compact", "stripe", "small", "responsive"],
            index=False,
        )
    )
