import asyncio
import unittest

from rateguard.app.models import OnboardingRequest, ProductLine, QuoteRequest, RiskModel
from rateguard.app.services import (
    BindService,
    CarrierAdapter,
    EventBus,
    InMemoryStore,
    OnboardingService,
    QuoteOrchestrator,
    RenewalService,
)


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.events = EventBus(events=[])
        self.onboarding = OnboardingService(self.store, self.events)
        self.orchestrator = QuoteOrchestrator(
            self.store,
            self.events,
            [
                CarrierAdapter("A", 0.9, (0, 0)),
                CarrierAdapter("B", 0.85, (0, 0)),
                CarrierAdapter("C", 0.8, (0, 0)),
            ],
        )
        self.binding = BindService(self.store, self.events)
        self.renewal = RenewalService(self.events)

    def test_onboarding_to_quote_to_bind(self) -> None:
        onboarded = self.onboarding.onboard(
            OnboardingRequest(
                email="user@example.com",
                social_provider="google",
                mfa_code="123456",
                household_name="Smith",
                extraction_confidence=0.95,
            )
        )
        self.assertFalse(onboarded.referred_for_review)

        bundle = asyncio.run(
            self.orchestrator.generate_quotes(
                QuoteRequest(user_id=onboarded.user.user_id, risk=RiskModel(product_line=ProductLine.AUTO))
            )
        )
        self.assertGreaterEqual(len(bundle.quotes), 3)

        bound = self.binding.bind(onboarded.user.user_id, bundle.quotes[0].quote_id)
        self.assertEqual(bound.status.value, "Active")

    def test_renewal_recommendation(self) -> None:
        recommendation = self.renewal.recommend("u1", "p1", current_annual=1800, best_market_annual=1450)
        self.assertEqual(recommendation.suggested_action, "Switch")
        self.assertEqual(recommendation.estimated_savings, 350)


if __name__ == "__main__":
    unittest.main()
