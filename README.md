# Digital Public Safety Intelligence Platform

AI-powered platform for fraud prevention, counterfeit currency screening,
digital-arrest scam detection, fraud-network analysis, geospatial intelligence,
case management, and citizen protection.

## What's included

- **Backend** — FastAPI + MongoDB (Motor/Beanie), JWT auth, RBAC
- **Frontend** — Next.js command-center UI with live scam assessment
- **AI modules** — Digital arrest scam NLP, counterfeit note CV, fraud network graph
- **APIs** — Reports, evidence upload, analytics, geospatial hotspots, assistant chat

## Prerequisites (Windows)

1. **Python 3.12+** — [python.org](https://www.python.org/downloads/)
2. **Node.js 20+** — [nodejs.org](https://nodejs.org/)
3. **MongoDB Community Server** — [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

No Docker or PostgreSQL required.

### Install MongoDB on Windows

1. Download and run the MongoDB Community MSI installer.
2. Choose **Complete** setup and install **MongoDB as a Service**.
3. Verify the service is running:

```powershell
Get-Service MongoDB
```

Default connection: `mongodb://localhost:27017`

## Quick start

### 1. Backend

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Or use the helper script from the repo root:

```powershell
.\scripts\start-backend.ps1
```

On startup the app connects to MongoDB, creates indexes, and seeds the admin user plus sample reports.

- API docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health

**Default admin:** `admin@suraksha.gov.in` / `Admin@12345`

### 2. Frontend

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
npm run dev
```

Or:

```powershell
.\scripts\start-frontend.ps1
```

Open http://localhost:3000

### 3. Run tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Tests use an in-memory MongoDB mock — no live MongoDB needed for pytest.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `digital_public_safety` | Database name |
| `SECRET_KEY` | (dev default) | JWT signing key — change in production |
| `ADMIN_EMAIL` | `admin@suraksha.gov.in` | Bootstrap admin email |
| `ADMIN_PASSWORD` | `Admin@12345` | Bootstrap admin password |

## Repository layout

```
digital-public-safety/
├── backend/          FastAPI app (MongoDB, auth, APIs, ML)
├── frontend/         Next.js web application
├── ai-models/        Training and inference modules
├── scripts/          Windows startup scripts
├── docs/             Architecture and deployment guides
└── tests/            Integration tests
```

## API highlights

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | JWT login |
| `POST /api/v1/scam/analyse` | Digital arrest scam detection |
| `POST /api/v1/counterfeit/analyse` | Counterfeit currency screening |
| `POST /api/v1/reports` | Submit fraud report |
| `GET /api/v1/geo/hotspots` | District crime hotspots |
| `GET /api/v1/analytics/summary` | Fraud analytics |
| `POST /api/v1/graph/analyse` | Fraud network analysis |
| `POST /api/v1/assistant/chat` | Citizen safety assistant |

## Security notes

- Change `SECRET_KEY` and `ADMIN_PASSWORD` before any public deployment.
- Set `APP_ENV=production` — startup validation rejects insecure defaults.
- Officers and admins cannot self-register; they must be provisioned by an admin.

## Documentation

- [Architecture](docs/01-ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)
