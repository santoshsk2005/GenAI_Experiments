"""AI-inspired agents that simulate on-site insurance quoting."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "snapshots"


class _QuoteSnapshotParser(HTMLParser):
    """Simple HTML parser for the saved insurer quote snapshots."""

    def __init__(self) -> None:
        super().__init__()
        self._in_quote_section = False
        self.base_rates: Dict[str, float] = {}

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        attr_map = dict(attrs)
        if tag == "section" and attr_map.get("id") == "quote-summary":
            self._in_quote_section = True
        elif self._in_quote_section and tag == "div":
            coverage = attr_map.get("data-coverage")
            premium = attr_map.get("data-premium")
            if coverage and premium:
                try:
                    self.base_rates[coverage] = float(premium)
                except ValueError:
                    pass

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._in_quote_section:
            self._in_quote_section = False


@dataclass
class AgentComputation:
    """Represents the detailed computation of a quote."""

    base: float
    adjustments: Dict[str, float]

    @property
    def total(self) -> float:
        return max(self.base + sum(self.adjustments.values()), 0)


class InsuranceAgent:
    """Base class with shared utilities for the insurer agents."""

    company_name: str = "Generic Insurance"
    snapshot_file: str = ""
    risk_bias: float = 0.0
    loyalty_discount: float = 0.0

    def __init__(self) -> None:
        self.snapshot_path = DATA_DIR / self.snapshot_file

    COVERAGE_ALIAS = {
        "basic": "basic",
        "standard": "standard",
        "premium": "premium",
    }

    def get_quote(self, driver_profile: Dict[str, str]) -> Dict[str, float | Dict[str, float]]:
        base_rates = self._extract_base_rates()
        coverage_level = driver_profile.get("coverage_level", "standard")
        base = base_rates.get(self.COVERAGE_ALIAS.get(coverage_level, "standard"), base_rates["standard"])
        adjustments = self._compute_adjustments(driver_profile, base)
        computation = AgentComputation(base=base, adjustments=adjustments)
        return {
            "company": self.company_name,
            "base": base,
            "adjustments": adjustments,
            "total": round(computation.total, 2),
        }

    def _extract_base_rates(self) -> Dict[str, float]:
        parser = _QuoteSnapshotParser()
        parser.feed(self.snapshot_path.read_text(encoding="utf-8"))
        if not parser.base_rates:
            raise ValueError(f"No base rates found in snapshot {self.snapshot_path}")
        return parser.base_rates

    def _compute_adjustments(self, driver_profile: Dict[str, str], base: float) -> Dict[str, float]:
        adjustments: Dict[str, float] = {}
        age = int(driver_profile.get("driver_age", 35))
        credit_score = int(driver_profile.get("credit_score", 700))
        accidents = int(driver_profile.get("accidents", 0))
        annual_mileage = int(driver_profile.get("annual_mileage", 12000))
        loyalty_years = int(driver_profile.get("loyalty_years", 0))

        adjustments["age"] = base * self._age_adjustment(age)
        adjustments["credit_score"] = base * self._credit_adjustment(credit_score)
        adjustments["accidents"] = base * (0.1 * accidents)
        adjustments["annual_mileage"] = base * self._mileage_adjustment(annual_mileage)
        adjustments["company_bias"] = base * self.risk_bias
        if loyalty_years:
            adjustments["loyalty"] = -base * min(loyalty_years * self.loyalty_discount, 0.15)
        return {k: round(v, 2) for k, v in adjustments.items() if abs(v) > 0.01}

    @staticmethod
    def _age_adjustment(age: int) -> float:
        if age < 25:
            return 0.35
        if age < 35:
            return 0.15
        if age > 65:
            return 0.2
        return 0.05

    @staticmethod
    def _credit_adjustment(score: int) -> float:
        if score >= 780:
            return -0.08
        if score >= 720:
            return -0.04
        if score >= 650:
            return 0.02
        return 0.08

    @staticmethod
    def _mileage_adjustment(annual_mileage: int) -> float:
        if annual_mileage <= 8000:
            return -0.05
        if annual_mileage <= 12000:
            return 0.0
        if annual_mileage <= 18000:
            return 0.05
        return 0.12


class NationwideAgent(InsuranceAgent):
    company_name = "Nationwide"
    snapshot_file = "nationwide.html"
    risk_bias = 0.04
    loyalty_discount = 0.02

    def _compute_adjustments(self, driver_profile: Dict[str, str], base: float) -> Dict[str, float]:
        adjustments = super()._compute_adjustments(driver_profile, base)
        if driver_profile.get("bundled_home_auto") == "yes":
            adjustments["bundling"] = round(-base * 0.07, 2)
        return adjustments


class GeicoAgent(InsuranceAgent):
    company_name = "GEICO"
    snapshot_file = "geico.html"
    risk_bias = -0.01
    loyalty_discount = 0.015

    def _compute_adjustments(self, driver_profile: Dict[str, str], base: float) -> Dict[str, float]:
        adjustments = super()._compute_adjustments(driver_profile, base)
        if driver_profile.get("defensive_driving", "no") == "yes":
            adjustments["defensive_course"] = round(-base * 0.05, 2)
        return adjustments


class StateFarmAgent(InsuranceAgent):
    company_name = "State Farm"
    snapshot_file = "statefarm.html"
    risk_bias = 0.02
    loyalty_discount = 0.025

    def _compute_adjustments(self, driver_profile: Dict[str, str], base: float) -> Dict[str, float]:
        adjustments = super()._compute_adjustments(driver_profile, base)
        if int(driver_profile.get("accidents", 0)) == 0:
            adjustments["safe_driver"] = round(-base * 0.12, 2)
        return adjustments


class AllStateAgent(InsuranceAgent):
    company_name = "Allstate"
    snapshot_file = "allstate.html"
    risk_bias = 0.06
    loyalty_discount = 0.018

    def _compute_adjustments(self, driver_profile: Dict[str, str], base: float) -> Dict[str, float]:
        adjustments = super()._compute_adjustments(driver_profile, base)
        if driver_profile.get("telematics_opt_in", "no") == "yes":
            adjustments["telematics"] = round(-base * 0.06, 2)
        return adjustments
