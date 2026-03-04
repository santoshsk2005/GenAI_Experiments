# RateGuard Phase 1 (Software Blueprint + Working Backend Skeleton)

This folder contains a production-oriented starter implementation of **RateGuard** aligned to the provided requirements:

- Single-tenant platform model
- Ohio-first personal lines focus
- STP-first workflows with referral escalation
- Event-driven core behaviors
- Subscription-gated quoting and binding
- Transparent ranking output with weighted component scores

## Implemented Modules

### 1) Identity + Onboarding
- Social-provider constrained onboarding payload
- MFA code validation shape
- User + household creation placeholder
- Extraction confidence check with automatic referral trigger

### 2) Quote Orchestration
- Subscription-state validation
- Ohio-only validation for Phase 1
- Parallel simulated carrier rating calls
- Quote normalization to canonical model
- Weighted ranking engine with versioned model ID
- QuoteGenerated event emission

### 3) Referral Engine (Skill-Based Routing)
- Referral case creation with skill tags
- Producer assignment based on skills
- Immutable event emission and case persistence

### 4) STP Bind Flow
- BindRequested and BindConfirmed events
- Policy activation and issued document references
- Commission ledger event emission

### 5) Renewal Recommendation
- Current vs market premium comparison
- Switch/retain recommendation
- Savings estimate and event emission

## Code Structure

- `app/models.py`: domain entities and request/response models
- `app/services.py`: workflow services and orchestration logic
- `app/main.py`: app façade and end-to-end demo execution
- `tests/test_workflows.py`: regression tests for core workflow paths

## Run Locally

```bash
python -m unittest discover -s rateguard/tests -v
python -m rateguard.app.main
```

## Notes for Next Iteration

- Replace in-memory store with PostgreSQL + object storage.
- Add message queue and dead-letter queue for carrier timeouts.
- Add OAuth2/JWT and role-based auth middleware.
- Integrate real carrier adapters + vendor integrations.
- Add feature flag controls by state/product/carrier.
