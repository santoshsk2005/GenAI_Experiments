from __future__ import annotations

import asyncio
from dataclasses import asdict

from .models import BindRequest, OnboardingRequest, ProductLine, QuoteRequest, RiskModel
from .services import (
    BindService,
    CarrierAdapter,
    EventBus,
    InMemoryStore,
    OnboardingService,
    QuoteOrchestrator,
    ReferralService,
    RenewalService,
)


class RateGuardApplication:
    """Facade for RateGuard Phase 1 workflows.

    This keeps interfaces close to future API endpoints while staying dependency-free.
    """

    def __init__(self) -> None:
        self.store = InMemoryStore()
        self.event_bus = EventBus(events=[])
        self.onboarding = OnboardingService(self.store, self.event_bus)
        self.quote_orchestrator = QuoteOrchestrator(
            self.store,
            self.event_bus,
            adapters=[
                CarrierAdapter("Buckeye Mutual", 0.92, (0.05, 0.2)),
                CarrierAdapter("Lakefront Casualty", 0.86, (0.05, 0.2)),
                CarrierAdapter("River Valley Insurance", 0.8, (0.05, 0.2)),
            ],
        )
        self.referrals = ReferralService(self.store, self.event_bus)
        self.binding = BindService(self.store, self.event_bus)
        self.renewals = RenewalService(self.event_bus)

    async def run_demo(self) -> dict:
        onboarding = self.onboarding.onboard(
            OnboardingRequest(
                email="demo@rateguard.io",
                social_provider="google",
                mfa_code="123456",
                household_name="Doe Household",
                extraction_confidence=0.93,
            )
        )
        quotes = await self.quote_orchestrator.generate_quotes(
            QuoteRequest(
                user_id=onboarding.user.user_id,
                risk=RiskModel(product_line=ProductLine.AUTO),
            )
        )
        selected = quotes.quotes[0]
        bind = self.binding.bind(onboarding.user.user_id, selected.quote_id)
        recommendation = self.renewals.recommend(onboarding.user.user_id, bind.policy_id, 1800, selected.annual_premium)
        return {
            "onboarding": asdict(onboarding),
            "quotes": [asdict(q) for q in quotes.quotes],
            "bind": asdict(bind),
            "renewal": asdict(recommendation),
            "events": self.event_bus.events,
        }


if __name__ == "__main__":
    output = asyncio.run(RateGuardApplication().run_demo())
    print(output)
