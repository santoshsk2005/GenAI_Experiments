from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Iterable
from uuid import uuid4

from .models import (
    ApplicationState,
    BindResponse,
    OnboardingRequest,
    OnboardingResponse,
    Quote,
    QuoteBundle,
    QuoteRequest,
    QuoteScore,
    ReferralCase,
    RenewalRecommendation,
    SubscriptionState,
    User,
)


@dataclass
class EventBus:
    events: list[str]

    def emit(self, event_name: str, **payload: str) -> None:
        self.events.append(f"{event_name}:{payload}")


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.quotes: dict[str, Quote] = {}
        self.policies: dict[str, dict] = {}
        self.referrals: dict[str, ReferralCase] = {}


class OnboardingService:
    def __init__(self, store: InMemoryStore, event_bus: EventBus, threshold: float = 0.8) -> None:
        self.store = store
        self.event_bus = event_bus
        self.threshold = threshold

    def onboard(self, request: OnboardingRequest) -> OnboardingResponse:
        request.validate()
        user_id = f"usr_{uuid4().hex[:10]}"
        user = User(
            user_id=user_id,
            email=request.email,
            household_id=f"hh_{uuid4().hex[:8]}",
            subscription_state=SubscriptionState.ACTIVE,
        )
        self.store.users[user.user_id] = user
        self.event_bus.emit("SubscriptionUpdated", user_id=user.user_id, state=user.subscription_state.value)

        referred = request.extraction_confidence < self.threshold
        if referred:
            self.event_bus.emit("ReferralTriggered", user_id=user.user_id, reason="LowExtractionConfidence")

        return OnboardingResponse(user=user, referred_for_review=referred, events=self.event_bus.events[-2:])


class CarrierAdapter:
    def __init__(self, name: str, strength: float, jitter: tuple[float, float]) -> None:
        self.name = name
        self.strength = strength
        self.jitter = jitter

    async def quote(self, annual_baseline: float) -> dict:
        await asyncio.sleep(random.uniform(*self.jitter))
        multiplier = random.uniform(0.85, 1.25)
        annual = round(annual_baseline * multiplier, 2)
        return {
            "carrier": self.name,
            "annual_premium": annual,
            "monthly_premium": round(annual / 12, 2),
            "coverage": {
                "bodily_injury": "100/300",
                "property_damage": "100",
                "comprehensive": True,
            },
            "carrier_strength": self.strength,
        }


class QuoteOrchestrator:
    def __init__(self, store: InMemoryStore, event_bus: EventBus, adapters: Iterable[CarrierAdapter]) -> None:
        self.store = store
        self.event_bus = event_bus
        self.adapters = list(adapters)
        self.score_weights = {"price": 0.5, "coverage_quality": 0.25, "carrier_strength": 0.25}
        self.scoring_model_id = "rank-v1"

    async def generate_quotes(self, request: QuoteRequest) -> QuoteBundle:
        user = self.store.users.get(request.user_id)
        if not user or user.subscription_state not in {SubscriptionState.ACTIVE, SubscriptionState.GRACE}:
            raise ValueError("Subscription is not active")
        if request.risk.state != "OH":
            raise ValueError("Phase 1 supports Ohio policies only")

        self.event_bus.emit("QuoteRequested", user_id=request.user_id, line=request.risk.product_line.value)

        baseline = 1600.0 if request.risk.product_line.value == "auto" else 1200.0
        responses = await asyncio.gather(*(adapter.quote(baseline) for adapter in self.adapters))

        raw_quotes = [self._to_quote(response) for response in responses]
        ranked = sorted(raw_quotes, key=lambda item: item.score.final_score, reverse=True)

        for quote in ranked:
            self.store.quotes[quote.quote_id] = quote

        request_id = f"qr_{uuid4().hex[:10]}"
        bundle = QuoteBundle(
            request_id=request_id,
            user_id=request.user_id,
            quotes=ranked,
            ranking_version=self.scoring_model_id,
        )
        self.event_bus.emit("QuoteGenerated", request_id=request_id, quote_count=str(len(ranked)))
        return bundle

    def _to_quote(self, carrier_data: dict) -> Quote:
        annual = carrier_data["annual_premium"]
        price_score = max(0.0, min(1.0, 1 - ((annual - 900) / 1800)))
        coverage_quality = 0.85
        carrier_strength = carrier_data["carrier_strength"]
        score = (
            self.score_weights["price"] * price_score
            + self.score_weights["coverage_quality"] * coverage_quality
            + self.score_weights["carrier_strength"] * carrier_strength
        )

        tier = "Gold" if carrier_strength >= 0.9 else "Silver" if carrier_strength >= 0.8 else "Bronze"

        return Quote(
            quote_id=f"qt_{uuid4().hex[:10]}",
            carrier=carrier_data["carrier"],
            monthly_premium=carrier_data["monthly_premium"],
            annual_premium=annual,
            coverage_summary=carrier_data["coverage"],
            tier=tier,
            score=QuoteScore(
                price=round(price_score, 4),
                coverage_quality=coverage_quality,
                carrier_strength=carrier_strength,
                weights=self.score_weights,
                final_score=round(score, 4),
                model_id=self.scoring_model_id,
            ),
        )


class ReferralService:
    def __init__(self, store: InMemoryStore, event_bus: EventBus) -> None:
        self.store = store
        self.event_bus = event_bus

    def create_referral(self, user_id: str, reason: str, skill_tags: list[str]) -> ReferralCase:
        assigned = "producer_oh_auto_senior" if "high_limit" in skill_tags else "producer_oh_general"
        case = ReferralCase(
            case_id=f"ref_{uuid4().hex[:10]}",
            user_id=user_id,
            reason=reason,
            skill_tags=skill_tags,
            assigned_producer=assigned,
        )
        self.store.referrals[case.case_id] = case
        self.event_bus.emit("ReferralTriggered", case_id=case.case_id, producer=assigned)
        return case


class BindService:
    def __init__(self, store: InMemoryStore, event_bus: EventBus) -> None:
        self.store = store
        self.event_bus = event_bus

    def bind(self, user_id: str, quote_id: str) -> BindResponse:
        user = self.store.users.get(user_id)
        quote = self.store.quotes.get(quote_id)
        if not user or not quote:
            raise ValueError("User or quote not found")
        if user.subscription_state != SubscriptionState.ACTIVE:
            raise ValueError("Subscription must be active to bind")

        self.event_bus.emit("BindRequested", user_id=user_id, quote_id=quote_id)

        policy_id = f"pl_{uuid4().hex[:12]}"
        docs = [f"{policy_id}_declaration.pdf", f"{policy_id}_id_card.pdf"]
        self.store.policies[policy_id] = {
            "user_id": user_id,
            "quote_id": quote_id,
            "status": ApplicationState.ACTIVE,
            "documents": docs,
        }

        self.event_bus.emit("BindConfirmed", user_id=user_id, policy_id=policy_id)
        self.event_bus.emit("CommissionRecorded", policy_id=policy_id, quote_id=quote_id)
        return BindResponse(policy_id=policy_id, status=ApplicationState.ACTIVE, documents=docs, events=self.event_bus.events[-3:])


class RenewalService:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def recommend(self, user_id: str, current_policy_id: str, current_annual: float, best_market_annual: float) -> RenewalRecommendation:
        savings = round(max(0.0, current_annual - best_market_annual), 2)
        action = "Switch" if savings > 100 else "Retain"
        recommendation = RenewalRecommendation(
            user_id=user_id,
            current_policy_id=current_policy_id,
            suggested_action=action,
            estimated_savings=savings,
        )
        self.event_bus.emit("RenewalRecommendationGenerated", policy_id=current_policy_id, action=action)
        return recommendation
