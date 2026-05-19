document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = '/api/v1';

    const statusEl = document.getElementById('status-message');
    const stateOutputEl = document.getElementById('state-output');

    const showStatus = (msg) => {
        statusEl.classList.remove('visible');
        
        // Wait 1.5s in the void, then show new message slowly
        setTimeout(() => {
            statusEl.textContent = msg;
            statusEl.classList.add('visible');
            
            // Wait 5s, then fade out
            setTimeout(() => {
                if (statusEl.textContent === msg) {
                    statusEl.classList.remove('visible');
                    // Clear text after fade finishes
                    setTimeout(() => {
                        if (!statusEl.classList.contains('visible')) {
                            statusEl.textContent = '';
                        }
                    }, 4000);
                }
            }, 5000);
        }, 1500);
    };

    const clearStateOutput = () => {
        stateOutputEl.classList.add('hidden');
        stateOutputEl.textContent = '';
    };

    const postAction = async (endpoint, successMsg) => {
        clearStateOutput();
        statusEl.classList.remove('visible');
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (res.ok) {
                showStatus(successMsg);
            } else {
                showStatus('Action unconfirmed.');
            }
        } catch (err) {
            showStatus('Communication error.');
        }
    };

    document.getElementById('btn-resolve').addEventListener('click', () => {
        postAction('/trust/action/resolve', 'Baseline restored.');
    });

    document.getElementById('btn-supplier').addEventListener('click', () => {
        postAction('/simulate/trust_event/supplier_approval_drift', 'Supplier drift introduced.');
    });

    document.getElementById('btn-identity').addEventListener('click', () => {
        postAction('/simulate/trust_event/midnight_executive_login', 'Identity uncertainty introduced.');
    });

    document.getElementById('btn-payment').addEventListener('click', () => {
        postAction('/simulate/trust_event/payment_verification_mismatch', 'Routing inconsistency introduced.');
    });

    document.getElementById('btn-state').addEventListener('click', async () => {
        statusEl.classList.remove('visible');
        try {
            const res = await fetch(`${API_BASE}/trust/state`);
            if (res.ok) {
                const data = await res.json();
                stateOutputEl.textContent = JSON.stringify(data, null, 2);
                stateOutputEl.classList.remove('hidden');
                showStatus('Posture read complete.');
            } else {
                showStatus('Unable to read posture.');
            }
        } catch (err) {
            showStatus('Communication error.');
        }
    });
});
