# Zero@Trust Production Handover

## System Purpose
Zero@Trust is an operational intelligence engine designed to process continuous risk and evidence signals from diverse enterprise systems. Its core mandate is to translate raw telemetry into a deterministic, high-level "atmospheric trust posture." This posture is rendered strictly visually via a headless frontend, ensuring that end-users experience the physical weight of risk without being exposed to raw intelligence logs or performative dashboards.

## Architecture Summary
- **Backend**: FastAPI (Python 3) driving an asynchronous intelligence loop.
- **Persistence**: PostgreSQL (production) or SQLite (local fallback) storing continuous temporal memory and risk history.
- **Frontend**: Subtractive HTML/CSS/JS served directly by FastAPI. Zero business logic resides in the browser.
- **Deployment**: Docker Compose orchestrated across isolated networks, sitting behind an Nginx reverse proxy capable of ACME/Certbot SSL provisioning.

## Service Map
- `zerotrust-api`: The core FastAPI application (Port 8000 internal).
- `postgres`: The persistent data store (Port 5432 internal, strictly isolated).
- `nginx`: The edge reverse proxy routing HTTP/HTTPS traffic.
- `certbot`: Ephemeral Docker profile for SSL issuance.

## Environment Variables
See `.env.production.example` for the required footprint. Key constraints:
- `APP_ENV`: Must be `production`.
- `CORS_ORIGINS`: Must be explicitly set to the deployment domain (no `*`).
- `DATABASE_URL`: Must connect to the internal `postgres` container or a managed DB.

## Deployment Flow
Refer to `DEPLOYMENT.md` for the exact Docker and Nginx sequence.

## Admin Login Flow
Admin APIs are stateless. 
1. `POST /api/v1/auth/login` with `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
2. Extract `access_token`.
3. Pass as `Authorization: Bearer <TOKEN>` to all `/api/v1/admin/*` endpoints.

## Webhook Intake Flow
External systems (Datadog, AWS, ERPs) push JSON to `POST /api/v1/webhooks/signal`.
Authentication is handled via the `X-Webhook-Secret` header natively.

## Rollback Notes
If a catastrophic logic error occurs, the production stack supports rolling back to a previous `git` commit and triggering `docker compose up -d --build`. Database migrations are currently handled via SQLAlchemy `create_all`; future iterations should implement Alembic for complex schema transitions.

## Known Exclusions
- No role-based access control (RBAC). A single `ADMIN` identity manages the system.
- No public telemetry API.
- No interactive dashboards.
- No internal task queues (e.g. Celery). The trust tick is handled by a background AsyncIO task.
