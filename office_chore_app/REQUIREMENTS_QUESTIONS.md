# Office Chore Planner — Clarifying Questions

Use these questions to finalize scope before backend and production rollout.

## Product requirements
1. Should chores have status values (`todo`, `in_progress`, `done`, `skipped`)?
2. Should recurring chores support end conditions (end date or occurrence count)?
3. Is assignment always one person, or can chores have multiple assignees?
4. Should users receive reminders (email, Slack, Teams, in-app notifications)?
5. Should we track audit history (who created/edited/completed chores)?

## Technical requirements
1. Is local-only browser storage acceptable, or do we need a shared backend now?
2. Do you need Microsoft 365/Outlook calendar sync?
3. Do you need SSO (Google Workspace, Entra ID, Okta)?
4. Should app data be exportable/importable (CSV, JSON)?
5. What browser/device support is required (desktop-only vs mobile)?

## Engineering principles
1. Preferred stack for long-term version (React/Vue/plain JS)?
2. Testing baseline (unit tests, e2e tests, accessibility checks)?
3. Performance target (max events displayed, acceptable load time)?
4. Accessibility target (WCAG 2.1 AA)?
5. Logging and observability requirements?

## Hard constraints
1. Required deployment target (internal server, Azure, Vercel, on-prem)?
2. Data residency or compliance constraints (SOC2, GDPR, HIPAA)?
3. Security constraints (RBAC, retention, encryption, backup)?
4. Budget/time constraints for MVP and production versions?
5. Mandatory integrations and non-negotiable deadlines?
