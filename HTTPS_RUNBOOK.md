# Zero@Trust — HTTPS & Edge Governance Runbook

This document defines the strict procedures for maintaining the cryptographic integrity, edge routing, and proxy alignment of the Zero@Trust operational environment. 

## 1. Cloudflare SSL Mode Alignment
When routing traffic through Cloudflare, the SSL/TLS encryption mode must exclusively be set to **Full (Strict)**. 
- **Flexible** will cause infinite 301 redirect loops due to Nginx enforcing HTTPS at the origin.
- **Full** is acceptable if using self-signed origin certs, but **Full (Strict)** with a Let's Encrypt origin certificate is the mandated institutional standard.

## 2. DNS Proxy Guidance
- The main domain `A` record must point to the VPS public IP.
- Cloudflare proxy status (the orange cloud) should be **Proxied**.
- Avoid exposing the raw VPS IP in any subdomains not protected by Cloudflare.

## 3. SSL Verification Workflow
To verify the active edge certificate:
```bash
curl -vI https://<DOMAIN>
```
Look for `SSL connection using TLSv1.3` and the correct issuer (Let's Encrypt or Cloudflare).

## 4. Certbot Renewal Procedures
Certificates expire every 90 days. Renewal is performed via the dedicated Docker profile.
```bash
# Dry run simulation
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Live execution
docker compose -f docker-compose.prod.yml run --rm certbot renew

# Reload Nginx to apply
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 5. Nginx Lifecycle Procedures
```bash
# Test configuration syntax before reloading
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Graceful reload (zero downtime)
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Hard restart
docker compose -f docker-compose.prod.yml restart nginx
```

## 6. HTTPS Validation Commands
```bash
# Verify API Health over HTTPS
curl -s https://<DOMAIN>/health | jq .

# Verify strict redirect from HTTP
curl -I http://<DOMAIN>/
# Expected: HTTP/1.1 301 Moved Permanently -> Location: https://<DOMAIN>/
```

## 7. ACME Challenge Recovery
If Certbot fails to renew due to challenge failures:
1. Ensure the `/.well-known/acme-challenge/` block is active in the port 80 server block.
2. If Cloudflare is blocking the challenge, ensure "Always Use HTTPS" is temporarily bypassed for `.well-known` via Page Rules, or simply let Nginx handle the port 80 challenge before redirecting.

## 8. Troubleshooting Edge Errors
- **Error 521 (Web Server Is Down):**
  Cloudflare cannot reach the VPS. Verify Nginx container is running: `docker compose -f docker-compose.prod.yml ps`. Verify UFW allows ports 80/443.
- **Error 502 (Bad Gateway):**
  Nginx cannot reach FastAPI. Verify `zerotrust-api` is running and bound to port 8000 on the internal network. Check API logs: `docker compose -f docker-compose.prod.yml logs --tail 50 zerotrust-api`.

## 9. Websocket & Polling Guidance
Zero@Trust relies on standard HTTP polling for its atmospheric frontend.
- Cloudflare caches standard GETs by default. Ensure Cache Rules bypass `/api/v1/trust/state` to prevent stale atmospheric data.
- If websockets are enabled later, Nginx `proxy_set_header Upgrade $http_upgrade;` must remain intact.

## 10. Mixed-Content Troubleshooting
If the atmospheric UI fails to load due to `Blocked: mixed-content`, ensure:
- FastAPI's `CORS_ORIGINS` strictly matches `https://<DOMAIN>`.
- Nginx is passing `X-Forwarded-Proto $scheme`.

## 11. Rollback & Emergency Recovery Flow
If Nginx configuration corruption breaks production routing:
```bash
# Revert config changes
git checkout deploy/nginx/zerotrust.conf

# Restart the proxy layer
docker compose -f docker-compose.prod.yml restart nginx
```
If Let's Encrypt limits are hit and the origin certificate is destroyed, generate a 15-year Cloudflare Origin Certificate, mount it into `deploy/certbot/conf/live/<DOMAIN>/`, and reload Nginx.
