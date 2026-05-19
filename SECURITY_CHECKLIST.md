# Zero@Trust Security Checklist

Before assigning real DNS traffic to the production environment, the following conditions must be explicitly verified by the deployment engineer.

### 1. Credentials & Secrets
- [ ] Rotate `ADMIN_PASSWORD` to a highly secure passphrase.
- [ ] Rotate `JWT_SECRET_KEY` (use `openssl rand -hex 32`).
- [ ] Rotate `WEBHOOK_SECRET` (use `openssl rand -hex 32`).
- [ ] Ensure `.env` is listed in `.gitignore` and has not been committed to the repository.

### 2. Networking & Edge
- [ ] Confirm `CORS_ORIGINS` is set to exactly the required domains (e.g., `https://zerotrust.company.com`).
- [ ] Confirm wildcard `*` is entirely absent from `CORS_ORIGINS` in production.
- [ ] Verify SSL/TLS is active via Certbot or Cloudflare (Full Strict mode).
- [ ] Confirm port `5432` (PostgreSQL) is NOT mapped or exposed to the public host.

### 3. Application State
- [ ] Confirm `APP_ENV=production`.
- [ ] Confirm `DATABASE_URL` points to a PostgreSQL instance (SQLite is blocked from production).
- [ ] Verify that navigating to `/api/v1/admin/environment/default/summary` natively without a JWT returns a `401 Unauthorized`.
- [ ] Verify that `POST /api/v1/webhooks/signal` natively without `X-Webhook-Secret` returns a `401 Unauthorized`.

### 4. Operations
- [ ] Confirm the database backup strategy (pg_dump or Managed RDS snapshots) is active.
- [ ] (Optional) Restrict `/api/v1/admin` blocks in Nginx to specific corporate VPN IP addresses for defense-in-depth.
