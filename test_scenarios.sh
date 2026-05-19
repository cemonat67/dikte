#!/bin/bash

DOMAIN="https://zerotrust.zeroatecosystem.com/api/v1"

echo "=== ZERO@TRUST V15.2 PRODUCTION SCENARIO TESTS ==="

echo "0. Resolving any existing state..."
curl -X POST $DOMAIN/trust/action/resolve
sleep 1

echo -e "\n\n1. TRIGGER: Supplier Approval Drift"
curl -X POST $DOMAIN/simulate/trust_event/supplier_approval_drift
echo "Wait for hysteresis (2 ticks, ~2 seconds)..."
sleep 2
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*}' || echo "Not surfaced yet"

echo -e "\n\n2. RESOLVE"
curl -X POST $DOMAIN/trust/action/resolve
sleep 1

echo -e "\n\n3. TRIGGER: Midnight Executive Login (Staged)"
curl -X POST $DOMAIN/simulate/trust_event/midnight_executive_login
echo "Wait for phase 1 (Observation)..."
sleep 2
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*}'
echo "Wait for phase 2 (Constrained)..."
sleep 2
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*}'

echo -e "\n\n4. TRIGGER: Payment Verification Mismatch (Degraded Dominance)"
curl -X POST $DOMAIN/simulate/trust_event/payment_verification_mismatch
echo "Wait for hysteresis..."
sleep 2
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*}'

echo -e "\n\n5. FINAL RESOLVE"
curl -X POST $DOMAIN/trust/action/resolve
sleep 1
curl -s $DOMAIN/trust/state | grep '"dominant_condition":null' && echo "State clean."
