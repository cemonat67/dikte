# Zero@Trust Production Deployment Runbook

## Overview
This runbook covers the standard deployment of Zero@Trust onto a single VPS utilizing Docker Compose, PostgreSQL, an Nginx reverse proxy, and Let's Encrypt SSL via Certbot.

## 1. Initial Server Setup
Create a directory for the application on your server:
```bash
mkdir -p /opt/zerotrust
cd /opt/zerotrust
```

Copy the repository files into this directory (via `git clone` or secure copy). Ensure your DNS A record points exactly to this server's public IP.

## 2. Environment Configuration
Never commit your `.env` file. Prepare the production secrets:
```bash
cp .env.production.example .env
```
Edit the `.env` file. **CRITICAL**:
- Update `DOMAIN` to match your actual server name (e.g., `zerotrust.company.com`).
- Provide a valid `LETSENCRYPT_EMAIL`.
- Generate a new `JWT_SECRET_KEY` (e.g. `openssl rand -hex 32`).
- Generate a new `WEBHOOK_SECRET` (e.g. `openssl rand -hex 32`).
- Set a strong `ADMIN_PASSWORD`.
- Ensure `CORS_ORIGINS` points exactly to your domain `https://<DOMAIN>`. Do NOT use `*` in production.
- Update `POSTGRES_PASSWORD` and match it inside the `DATABASE_URL`.

*Note on Cloudflare:* If you are using Cloudflare, set your SSL/TLS mode to "Full" or "Full (strict)". Avoid "Flexible" mode as it causes infinite redirect loops. Restrict `CORS_ORIGINS` explicitly to `https://DOMAIN`.

## 3. Booting the Stack (Initial HTTP)
Before issuing SSL, we must boot the stack over standard HTTP to answer the ACME challenge. Open `deploy/nginx/zerotrust.conf` and ensure the `server_name` exactly matches your domain.
```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## 4. Issuing the SSL Certificate (Certbot)
Run the Certbot profile directly within Docker Compose to request your certificate using the webroot challenge:
```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    -d <YOUR_DOMAIN> \
    --email <YOUR_EMAIL> \
    --agree-tos --no-eff-email
```
*If successful, Certbot will save your keys in `deploy/certbot/conf/live/<YOUR_DOMAIN>/`.*

## 5. Switch Nginx to HTTPS
1. Open `deploy/nginx/zerotrust.conf`.
2. Modify the `location /` block inside the port `80` server to redirect to HTTPS: `return 301 https://$host$request_uri;`.
3. Uncomment the bottom `listen 443 ssl` block and replace `zerotrust.example.com` with your actual domain name.
4. Reload Nginx:
```bash
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 6. Verification & Health Check
Test HTTPS endpoints securely:
```bash
curl https://<YOUR_DOMAIN>/health
```

Test administrative access:
1. Obtain token:
```bash
curl -X POST "https://<YOUR_DOMAIN>/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "<YOUR_ADMIN_PASSWORD>"}'
```
2. Call protected endpoint (should succeed only with the valid token):
```bash
curl "https://<YOUR_DOMAIN>/api/v1/admin/environment/default/summary" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

Test public trust polling natively:
```bash
curl "https://<YOUR_DOMAIN>/api/v1/trust/state?environment_id=default"
```

## 7. Certificate Renewal Automation
Let's Encrypt certificates expire every 90 days. You can renew them and reload Nginx automatically via a cronjob:
```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Operational Security Notes
- **Admin Endpoints:** Are strictly protected by stateless expiring JWT tokens in production. The legacy `X-Admin-Key` header is intentionally ignored unless `APP_ENV=local`.
- **Database Exposure:** `docker-compose.prod.yml` intentionally does NOT map port `5432` to the host. PostgreSQL is accessible only within the Docker `internal` network.

## Backups
Enable regular PostgreSQL backups.
- **Manual Dump:**
  ```bash
  docker compose -f docker-compose.prod.yml exec postgres pg_dump -U zerotrust zerotrust > backup.sql
  ```
- **Restore:**
  ```bash
  cat backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U zerotrust zerotrust
  ```
