# Deployment and operations (Windows + MongoDB)

## Prerequisites

- Python 3.12+
- Node.js 20+
- MongoDB Community Server 7+ (Windows service)
- Ports 3000 and 8000 available

No Docker or PostgreSQL required.

## First launch

### 1. MongoDB

Install MongoDB Community from https://www.mongodb.com/try/download/community

Verify the service:

```powershell
Get-Service MongoDB
```

Default URI: `mongodb://localhost:27017`

### 2. Backend

```powershell
cd backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On startup the backend:
- Connects to MongoDB via Motor/Beanie
- Creates collection indexes
- Seeds admin user and sample fraud reports

### 3. Frontend

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
npm run dev
```

Open http://localhost:3000

### Helper scripts (from repo root)

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
.\scripts\seed-database.ps1
```

## Production checklist

1. Set `APP_ENV=production` in `backend/.env`
2. Generate `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
3. Change `ADMIN_PASSWORD`
4. Use MongoDB authentication and TLS in `MONGODB_URI`
5. Place backend behind HTTPS reverse proxy
6. Restrict CORS to your frontend origin

## Operations

```powershell
# View MongoDB databases
mongosh --eval "show dbs"

# Backup
mongodump --db digital_public_safety --out .\backup

# Restore
mongorestore --db digital_public_safety .\backup\digital_public_safety

# Run tests (no live MongoDB needed)
cd backend
pytest
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection |
| `MONGODB_DB_NAME` | `digital_public_safety` | Database name |
| `SECRET_KEY` | dev default | JWT signing key |
| `ADMIN_EMAIL` | `admin@suraksha.gov.in` | Bootstrap admin |
| `ADMIN_PASSWORD` | `Admin@12345` | Bootstrap password |
