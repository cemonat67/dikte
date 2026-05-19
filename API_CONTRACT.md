# Zero@Trust API Contract

## Public Routes
*No authentication required. Returns strictly non-sensitive atmospheric data or accepts isolated input.*

- **GET `/health`**: Returns system boot status and version.
- **GET `/api/v1/trust/state?environment_id=...`**: Returns the rendered atmospheric posture for the requested environment.
- **POST `/api/v1/risk/evaluate`**: Public risk ingestion (legacy/unauthenticated path).
- **POST `/api/v1/evidence/record`**: Public evidence ingestion (legacy/unauthenticated path).

## Webhook Routes
*Requires `X-Webhook-Secret` header.*

- **POST `/api/v1/webhooks/signal`**: Primary intake for machine-to-machine intelligence (AWS, Datadog, Stripe). Validates standard JSON payloads and deduplicates based on `external_id`.

## Authentication Routes
*No authentication required.*

- **POST `/api/v1/auth/login`**: Accepts `username` and `password`. Returns a standard `Bearer` JWT `access_token`.

## Admin Governance Routes
*Requires `Authorization: Bearer <TOKEN>` header.*

- **GET `/api/v1/admin/environment/{environment_id}/summary`**: Returns precise telemetry (weighted scores, risk counts, governance delays) for the environment.
- **POST `/api/v1/admin/environment/{environment_id}/resolve-risk`**: Drops all active risk severity to zero for the given environment.
- **POST `/api/v1/admin/environment/{environment_id}/suppress-risk`**: Suppresses active risks, reducing their atmospheric impact to 25%.
- **POST `/api/v1/admin/environment/{environment_id}/restore-continuity`**: Instantly forces the environment back to a `persistent` temporal state.
- **POST `/api/v1/admin/environment/{environment_id}/record-review`**: Appends an immutable manual governance note to the environment's audit log.
