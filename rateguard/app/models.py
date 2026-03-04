from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SubscriptionState(str, Enum):
    ACTIVE = "Active"
    PAST_DUE = "PastDue"
    GRACE = "Grace"
    SUSPENDED = "Suspended"
    CANCELED = "Canceled"


class ApplicationState(str, Enum):
    DRAFT = "Draft"
    QUOTED = "Quoted"
    APPLICATION = "Application"
    REFERRAL = "Referral"
    APPROVED = "Approved"
    BOUND = "Bound"
    ISSUED = "Issued"
    ACTIVE = "Active"
    EXPIRED = "Expired"


class ProductLine(str, Enum):
    AUTO = "auto"
    HOME = "home"
    RENTERS = "renters"
    UMBRELLA = "umbrella"


@dataclass
class User:
    user_id: str
    email: str
    household_id: str
    subscription_state: SubscriptionState = SubscriptionState.ACTIVE


@dataclass
class OnboardingRequest:
    email: str
    social_provider: str
    mfa_code: str
    household_name: str
    extraction_confidence: float

    def validate(self) -> None:
        if self.social_provider not in {"google", "apple"}:
            raise ValueError("social_provider must be google or apple")
        if len(self.mfa_code) != 6 or not self.mfa_code.isdigit():
            raise ValueError("mfa_code must be a 6-digit string")
        if not 0.0 <= self.extraction_confidence <= 1.0:
            raise ValueError("extraction_confidence must be between 0 and 1")


@dataclass
class OnboardingResponse:
    user: User
    referred_for_review: bool
    events: list[str]


@dataclass
class RiskModel:
    product_line: ProductLine
    state: str = "OH"
    limits: dict[str, Any] = field(default_factory=dict)
    deductible: int | None = None


@dataclass
class QuoteRequest:
    user_id: str
    risk: RiskModel


@dataclass
class QuoteScore:
    price: float
    coverage_quality: float
    carrier_strength: float
    weights: dict[str, float]
    final_score: float
    model_id: str


@dataclass
class Quote:
    quote_id: str
    carrier: str
    monthly_premium: float
    annual_premium: float
    coverage_summary: dict[str, Any]
    tier: str
    score: QuoteScore
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QuoteBundle:
    request_id: str
    user_id: str
    quotes: list[Quote]
    ranking_version: str


@dataclass
class BindRequest:
    user_id: str
    quote_id: str


@dataclass
class BindResponse:
    policy_id: str
    status: ApplicationState
    documents: list[str]
    events: list[str]


@dataclass
class ReferralCase:
    case_id: str
    user_id: str
    reason: str
    skill_tags: list[str]
    assigned_producer: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RenewalRecommendation:
    user_id: str
    current_policy_id: str
    suggested_action: str
    estimated_savings: float
    generated_at: datetime = field(default_factory=datetime.utcnow)
