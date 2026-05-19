document.addEventListener('DOMContentLoaded', () => {
  const clockEl = document.getElementById('clock');
  
  function updateClock() {
    const now = new Date();
    // Format: HH:MM:SS UTC
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    const seconds = String(now.getUTCSeconds()).padStart(2, '0');
    clockEl.textContent = `${hours}:${minutes}:${seconds} UTC`;
  }

  // Update immediately and then every second
  updateClock();
  setInterval(updateClock, 1000);

  // Atmospheric State Management (Anti-Gravity)
  const states = {
    stable: { label: 'OPERATIONAL TRUST', value: 'Stable', context: 'All systems nominal' },
    observing: { label: 'QUIET VALIDATION', value: 'Observing', context: 'Sensing posture active' },
    review: { label: 'HUMAN GOVERNANCE', value: 'Review', context: 'Confidence degradation' }
  };

  const centerLabel = document.querySelector('.center-label');
  const centerValue = document.querySelector('.center-value');
  const rightPanelText = document.querySelector('.right-panel-content span');
  
  let currentState = 'stable';

  document.addEventListener('keydown', (e) => {
    if (e.key === '1' && currentState !== 'stable') transitionTo('stable');
    if (e.key === '2' && currentState !== 'observing') transitionTo('observing');
    if (e.key === '3' && currentState !== 'review') transitionTo('review');
  });

  function transitionTo(stateId) {
    currentState = stateId;
    document.body.setAttribute('data-state', stateId);
    
    // Slow text crossfade
    centerValue.style.opacity = '0';
    centerLabel.style.opacity = '0';
    rightPanelText.style.opacity = '0';
    
    setTimeout(() => {
      centerLabel.textContent = states[stateId].label;
      centerValue.textContent = states[stateId].value;
      rightPanelText.textContent = states[stateId].context;
      
      centerValue.style.opacity = '1';
      centerLabel.style.opacity = '1';
      rightPanelText.style.opacity = '1';
    }, 1200); // Delay word swapping until the atmosphere starts squeezing
  }
});
