# LUDO LEGENDS - Engineering Master Brief v1.1 (Confidential)

CONFIDENTIAL - Internal development use only.

## Objective
Build a scalable Ludo tournament platform with:
- Flutter app
- FastAPI backend
- PostgreSQL
- React Admin
- AI-ready architecture
- Configuration-driven rules

## Core Principles
- No hardcoded business rules
- Server-authoritative wallet
- Modular architecture
- Event-driven automation
- AI integration from day one

## Stack
Flutter, FastAPI, PostgreSQL, Redis, Firebase Cloud Messaging, React, Docker, GitHub Actions.

## Repository
/mobile-app
/backend-api
/admin-dashboard
/ai-services
/shared
/docs
/infrastructure

## Modules
Authentication, Profiles, Wallet, Tournament Engine, Results, Referrals, Rewards, Giveaways, Notifications, Leaderboard, Admin Dashboard, Analytics, AI.

## Security
OTP, JWT, RBAC, Audit Logs, Rate Limiting, Validation.
Do not claim control over third-party game dice. Focus on fair tournament workflows.

## Event Architecture
Events:
- TournamentCreated
- TournamentFull
- TournamentStarted
- TournamentCompleted
- WinnerConfirmed
- GiveawayDayStarted
- WithdrawalRequested

## AI Services
Marketing Agent
Operations Agent
Reward Agent
Business Intelligence Agent
Fraud Detection Agent
Admin Copilot

## AI Rule Engine
Rules editable by admin.
AI drafts, recommends and schedules.
Admin approval required for withdrawals, bans, manual wallet changes and disputes.

## Development
Sprint1: Scaffold, Auth, DB, Config
Sprint2: Tournament, Wallet, Notifications
Sprint3: Referral, Rewards, Giveaway
Sprint4: AI, Analytics, Automation

## Deliverables
ERD
Database migrations
OpenAPI
CI/CD
Docker
Unit tests
AI extension points
