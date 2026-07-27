# Ludo Legends

Tournament Platform — Flutter PWA + FastAPI Backend + React Admin

## Quick Start

### Backend (Docker)
```bash
cd backend-api
docker compose up -d --build
```
Backend runs at `http://localhost:8000` (API docs at `/docs`)

### Development OTP
When `ENVIRONMENT=development`, use OTP: **123456** for any phone number.

### Demo Accounts
| Role | Phone | OTP |
|------|-------|-----|
| Super Admin | +910000000000 | 123456 |
| Player | +919876543210 | 123456 |

### Flutter Web (PWA)
```bash
cd mobile-app
flutter pub get
flutter build web
```

### Flutter APK
```bash
flutter build apk --debug
```

## Tech Stack
- **Mobile/Web**: Flutter 3.44 (Riverpod, GoRouter, Dio)
- **Backend**: FastAPI + SQLAlchemy + asyncpg
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Migrations**: Alembic
- **Admin**: React + Vite
- **Deployment**: Docker, Vercel, GCP
