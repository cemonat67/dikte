#!/bin/bash

DOMAIN="https://zerotrust.zeroatecosystem.com/api/v1"

echo "=== ZERO@TRUST V16.0 INSTITUTIONAL MEMORY TESTS ==="

echo "0. Resolving any existing state..."
curl -s -X POST $DOMAIN/trust/action/resolve >/dev/null
sleep 1
echo "- Baseline Check:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":[a-z]*' || echo "No dominant condition"
curl -s $DOMAIN/trust/state | grep -o '"institutional_memory":[0-9.]*'

echo -e "\n\n1. TRIGGER & RESOLVE: Supplier Approval Drift"
curl -s -X POST $DOMAIN/simulate/trust_event/supplier_approval_drift >/dev/null
sleep 3
echo "- State BEFORE resolve:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*' | cut -c 1-100
curl -s -X POST $DOMAIN/trust/action/resolve >/dev/null
sleep 1
echo "- State AFTER resolve:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":[a-z]*'
curl -s $DOMAIN/trust/state | grep -o '"institutional_memory":[0-9.]*'

echo -e "\n\n2. TRIGGER & RESOLVE: Payment Verification Mismatch (Tier 1)"
curl -s -X POST $DOMAIN/simulate/trust_event/payment_verification_mismatch >/dev/null
sleep 3
echo "- State BEFORE resolve:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*' | cut -c 1-100
curl -s -X POST $DOMAIN/trust/action/resolve >/dev/null
sleep 1
echo "- State AFTER resolve:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":[a-z]*'
curl -s $DOMAIN/trust/state | grep -o '"institutional_memory":[0-9.]*'
echo "-> Expected: Memory should be significantly higher now."

echo -e "\n\n3. ACTIVE DOMINANCE TEST: Document Integrity Degradation"
curl -s -X POST $DOMAIN/simulate/trust_event/document_integrity_degradation >/dev/null
sleep 3
echo "- Dominant Condition Status:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":{[^}]*' | cut -c 1-100
echo "-> Expected: Even with high memory, active event takes over."

echo -e "\n\n4. FINAL RESOLVE"
curl -s -X POST $DOMAIN/trust/action/resolve >/dev/null
sleep 1
echo "- Final State:"
curl -s $DOMAIN/trust/state | grep -o '"dominant_condition":[a-z]*'
curl -s $DOMAIN/trust/state | grep -o '"institutional_memory":[0-9.]*'
echo "-> Expected: Dominant condition is null, but institutional memory remains > 0 (Atmospheric persistence)."
