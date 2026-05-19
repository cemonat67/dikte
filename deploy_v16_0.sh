#!/bin/bash
set -e

SERVER="root@91.98.228.234"
REMOTE_DIR="/opt/zerotrust"
DOMAIN="https://zerotrust.zeroatecosystem.com"

echo "=========================================="
echo "Zero@Trust v16.0 - Institutional Memory Deploy"
echo "=========================================="

echo "1. Creating pre-deployment backup on origin..."
ssh $SERVER "tar -czvf /root/zerotrust_backup_v16_0_pre_deploy.tar.gz -C $REMOTE_DIR ."
echo "-> Backup created at: /root/zerotrust_backup_v16_0_pre_deploy.tar.gz"

echo "2. Transferring files via rsync..."
# Only transferring backend, docs, and essential config
rsync -avz --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
    ./backend ./docs VERSION.md CHANGELOG.md requirements.txt Dockerfile \
    $SERVER:$REMOTE_DIR/

echo "3. Rebuilding zerotrust-api container (Zero-Downtime)..."
ssh $SERVER "cd $REMOTE_DIR && docker compose -f docker-compose.prod.yml up -d --build zerotrust-api"

echo "4. Waiting for API to warm up (5 seconds)..."
sleep 5

echo "5. Verifying /health endpoint..."
curl -s $DOMAIN/health | grep '"status":"ok"' && echo "Health: OK" || echo "Health: FAILED"

echo "=========================================="
echo "Deployment successful."
echo "Rollback command: ssh $SERVER 'cd $REMOTE_DIR && tar -xzvf /root/zerotrust_backup_v16_0_pre_deploy.tar.gz && docker compose -f docker-compose.prod.yml up -d --build zerotrust-api'"
echo "=========================================="
