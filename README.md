# Fleet Maintenance + Spares Automation

Production-oriented MVP for UAV fleet maintenance planning, spare parts traceability, and auto-indent recommendations.

## Stack
- Backend: FastAPI + SQLModel + Alembic + APScheduler
- Database: PostgreSQL
- Frontend: React + Vite + MUI
- Auth: JWT with role-based access (Admin, Maintainer, Storekeeper, Viewer)
- Local dev: Docker Compose

## Features
1. Asset registry for UAVs
2. Usage log ingestion (manual + API)
3. Maintenance programs with hour/day intervals
4. Auto work-order generation for due-soon or overdue programs
5. Parts catalog + instances with install/remove traceability
6. Inventory by location with on_hand/reserved/min/reorder_point/lead_time
7. Scheduled + on-demand indent recommendation
8. Dashboard metrics for due maintenance, low stock, stockout risk proxies
9. Audit logs on all write actions

## Repo Structure
- `backend/app` API, models, services, scheduler
- `backend/alembic` DB migrations
- `backend/tests` unit tests for due/reorder logic
- `frontend/src` dashboard UI
- `docker-compose.yml` full local stack

## Run locally
```bash
docker compose up --build
```

## API Docs
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Dev commands
```bash
cd backend
pip install -r requirements.txt
pytest
```
