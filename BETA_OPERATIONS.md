# Zero@Trust — Beta Operations & Institutional Governance

Zero@Trust is institutional infrastructure. It operates with executive stillness, relying entirely on deterministic logic, persistent memory, and isolated environments. This document governs the administrative procedures required to maintain its operational integrity.

## 1. Tenant Isolation Governance (Environment Creation)
Environments are dynamically provisioned. Injecting risk into an unknown `environment_id` automatically establishes its memory state.
- **Discipline:** Do not create environments casually. Stick to formal identifiers (e.g., `alpha-production`, `finance-eu`).
- **Isolation:** Trust states, risk severities, and continuity ticks never bleed across environments.

## 2. JWT Operational Discipline
Admin access requires a stateless JWT.
- **Login:** Execute `POST /api/v1/auth/login` to obtain an `access_token`.
- **Expiration:** Tokens expire in 60 minutes. Do not hardcode tokens in long-running scripts; always implement a refresh/re-auth loop.

## 3. Webhook Injection Procedures
Machine-to-machine intelligence is handled via `POST /api/v1/webhooks/signal`.
- **Discipline:** Always provide an `external_id` (e.g., the raw Datadog alert ID) to enforce backend idempotency and prevent duplicate risk inflation.
- **Authentication:** Must pass exactly `X-Webhook-Secret`.

## 4. Operational Freeze Procedures
During massive infrastructure maintenance, humans should not manually fight the risk engine. 
- **Procedure:** Suppress active risks using the Admin API. This enforces Governance Drag, preventing the environment from violently toggling states during maintenance windows.

## 5. Backup & Restore Procedures
Persistence relies on PostgreSQL. Database state is the absolute truth of the atmosphere.
- **Automated Backup (Cron):**
  ```bash
  docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U zerotrust zerotrust > /var/backups/zt_$(date +%F).sql
  ```
- **Restore Execution:**
  ```bash
  cat backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U zerotrust zerotrust
  ```

## 6. Container & Instance Operations
- **Graceful Restart:** `docker compose -f docker-compose.prod.yml restart zerotrust-api`
- **Health Monitoring:** Tail the logs at `INFO` level to observe the global tick. `docker compose -f docker-compose.prod.yml logs -f zerotrust-api`.

## 7. Incident Recovery & Escalation
1. **Identify:** Check Nginx logs for 502s, check API logs for Exception traces.
2. **Contain:** If the intelligence engine is poisoned with false risks, use `POST /admin/environment/{id}/resolve-risk` to drop the severity to zero.
3. **Recover:** Force temporal recovery via `POST /admin/environment/{id}/restore-continuity` if the business requires immediate visual quiet.

## 8. Optional Operational Hardening
To achieve true institutional-grade security on the VPS:
- **Fail2Ban:** Configure to ban IPs generating excessive 401/403s on `/api/v1/auth/login`.
- **UFW Baseline:** Default deny incoming. Allow 22 (SSH), 80 (HTTP), 443 (HTTPS).
- **Resource Limits:** Update `docker-compose.prod.yml` with `deploy.resources.limits` to cap memory on the FastAPI and Postgres containers.
- **Immutable Audits:** Pipe Docker stdout directly to a write-only log sink (e.g., AWS CloudWatch or Datadog) to preserve governance records immutably.

## 9. Beta Validation Matrix
Prior to formal handover, the following must be physically executed and validated:
- [ ] **SSL Renewal Simulation:** `docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run` yields Success.
- [ ] **Backup Integrity:** A manual `pg_dump` writes a non-empty SQL file.
- [ ] **Restore Integrity:** Dropping the database and applying the dump restores the exact environment states.
- [ ] **JWT Expiration:** A token older than 60 minutes explicitly returns `401 Unauthorized`.
- [ ] **Webhook Replay:** Sending the exact same webhook payload twice (identical `external_id`) results in an ignored insertion, preventing duplicate risk.
- [ ] **Nginx Restart Safety:** Reloading nginx (`nginx -s reload`) drops 0 active connections.
- [ ] **Docker Restart:** Running `docker compose down` and `up -d` results in the exact same atmospheric state loading from the database.
- [ ] **PostgreSQL Persistence:** Verify that the `postgres_data_prod` Docker volume is actively retaining `/var/lib/postgresql/data`.
