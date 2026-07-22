# API and demonstration guide

## Demo flow

1. Sign in using the administrator values configured in `backend/.env`.
2. Paste a digital-arrest message into Live Scam Assessment.
3. Review risk score, detected manipulation signals, and citizen actions.
4. Use Swagger to create a citizen report and move it through investigation.
5. Upload an evidence file and note its immutable SHA-256 digest.
6. Analyse a currency image and inspect per-feature scores and heatmap.
7. Submit linked phones, UPI IDs, devices, and accounts to graph analysis.
8. View analytics summary and district hotspot endpoints.

## Principal endpoints

- `POST /api/v1/auth/register`, `/auth/login`, `/auth/refresh`
- `POST /api/v1/scam/analyse`
- `POST /api/v1/counterfeit/analyse`
- `POST|GET /api/v1/reports`, `PATCH /api/v1/reports/{id}`
- `POST /api/v1/evidence/{report_id}`
- `POST /api/v1/graph/analyse`
- `GET /api/v1/geo/hotspots`, `/analytics/summary`
- `POST /api/v1/assistant/chat`

Every operational endpoint requires a bearer access token. Officer, analyst,
and administrator operations additionally enforce role-based access.
