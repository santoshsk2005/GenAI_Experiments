"""Orchestrator that coordinates the insurance quoting agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from .agents import (
    AllStateAgent,
    GeicoAgent,
    NationwideAgent,
    StateFarmAgent,
)


@dataclass
class QuoteResult:
    """Container for the result returned by an agent."""

    company: str
    estimated_premium: float
    base_premium: float
    adjustments: Dict[str, float]

    @property
    def total_adjustment(self) -> float:
        return sum(self.adjustments.values())


class RateOrchestrator:
    """Coordinates the execution of the individual insurance agents."""

    def __init__(self) -> None:
        self._agents = self._build_agents()

    @staticmethod
    def _build_agents() -> Sequence:
        return (
            NationwideAgent(),
            GeicoAgent(),
            StateFarmAgent(),
            AllStateAgent(),
        )

    def collect_quotes(self, driver_profile: Dict[str, str]) -> List[QuoteResult]:
        results: List[QuoteResult] = []
        for agent in self._agents:
            agent_result = agent.get_quote(driver_profile)
            results.append(
                QuoteResult(
                    company=agent.company_name,
                    estimated_premium=agent_result["total"],
                    base_premium=agent_result["base"],
                    adjustments=agent_result["adjustments"],
                )
            )
        return results
