"""Flask application that emulates a third-party auto insurance rater."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

from flask import Flask, render_template, request

from ai_agents import RateOrchestrator

app = Flask(__name__, template_folder="templates", static_folder="static")
orchestrator = RateOrchestrator()


@app.context_processor
def inject_enums():
    return {
        "coverage_levels": {
            "basic": "Basic",
            "standard": "Standard",
            "premium": "Premium",
        },
        "current_year": datetime.now().year,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = _normalize_form(request.form)
        quotes = orchestrator.collect_quotes(form_data)
        return render_template("results.html", form=form_data, quotes=quotes)
    return render_template("index.html")


def _normalize_form(form) -> Dict[str, str]:
    numeric_fields = {
        "driver_age",
        "vehicle_year",
        "credit_score",
        "accidents",
        "annual_mileage",
        "loyalty_years",
    }
    cleaned: Dict[str, str] = {}
    for key in (
        "driver_age",
        "zip_code",
        "vehicle_make",
        "vehicle_model",
        "vehicle_year",
        "credit_score",
        "accidents",
        "annual_mileage",
        "loyalty_years",
        "coverage_level",
        "bundled_home_auto",
        "defensive_driving",
        "telematics_opt_in",
    ):
        value = form.get(key, "").strip()
        if key in numeric_fields:
            cleaned[key] = value or "0"
        else:
            cleaned[key] = value or ""
    cleaned["coverage_level"] = form.get("coverage_level", "standard")
    return cleaned


if __name__ == "__main__":
    port = int(Path(".env").read_text().strip()) if Path(".env").exists() else 5000
    app.run(host="0.0.0.0", port=port, debug=True)
