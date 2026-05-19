document.addEventListener('DOMContentLoaded', () => {
  const surface = document.querySelector('.surface');
  const body = document.body;
  const layerActive = document.getElementById('layer-active');
  const layerFade = document.getElementById('layer-fade');
  const bgLayers = {
    stable: document.querySelector('.bg-layer.state-stable'),
    observing: document.querySelector('.bg-layer.state-observing'),
    review: document.querySelector('.bg-layer.state-review')
  };
  
  const states = {
    stable: {
      id: 'stable',
      primary: 'Stable',
      secondary: 'Human in Control',
      condition: 'Operational continuity preserved',
      context: [
        { label: 'Continuity', value: 'High' },
        { label: 'Validation Pressure', value: 'Low' },
        { label: 'Silent Signals', value: '184' },
        { label: 'Human Review Required', value: '0', resting: true }
      ]
    },
    observing: {
      id: 'observing',
      primary: 'Observing',
      secondary: 'Quiet Attention Active',
      condition: 'Quiet validation in progress',
      context: [
        { label: 'Continuity', value: 'High' },
        { label: 'Validation Pressure', value: 'Moderate' },
        { label: 'Silent Signals', value: '193' },
        { label: 'Human Review Required', value: '0', resting: true }
      ]
    },
    review: {
      id: 'review',
      primary: 'Review',
      secondary: 'Human Review Suggested',
      condition: 'Human judgment may improve confidence',
      context: [
        { label: 'Continuity', value: 'Preserved' },
        { label: 'Validation Pressure', value: 'Elevated' },
        { label: 'Silent Signals', value: '211' },
        { label: 'Human Review Suggested', value: '1', alert: true }
      ]
    }
  };

  let currentStateId = 'stable';
  let currentLayer = layerActive;
  let hiddenLayer = layerFade;

  function renderStateContent(stateData) {
    const contextHtml = stateData.context.map(item => `
      <div class="context-node ${item.resting ? 'resting' : ''} ${item.alert ? 'alert-node' : ''}">
        <span class="context-label">${item.label}</span>
        <span class="context-value">${item.value}</span>
      </div>
    `).join('');

    return `
      <div class="core-focus">
        <h1 class="status-primary">${stateData.primary}</h1>
        <div class="status-divider"></div>
        <h2 class="status-secondary">${stateData.secondary}</h2>
        <div class="condition-phrase">${stateData.condition}</div>
      </div>
      <footer class="micro-context">
        ${contextHtml}
      </footer>
    `;
  }

  // Initial render
  currentLayer.innerHTML = renderStateContent(states.stable);
  currentLayer.classList.add('active');

  // Soft Emergence
  // Allow the screen to be fully black/silent for a moment before the 6s fade begins
  setTimeout(() => {
    surface.style.opacity = '1';
  }, 800);

  // Invisible Keyboard Interaction
  // Keys 1, 2, 3 silently transition the states without UI buttons
  document.addEventListener('keydown', (e) => {
    if (e.key === '1' && currentStateId !== 'stable') transitionTo(states.stable);
    if (e.key === '2' && currentStateId !== 'observing') transitionTo(states.observing);
    if (e.key === '3' && currentStateId !== 'review') transitionTo(states.review);
  });

  function transitionTo(targetState) {
    currentStateId = targetState.id;
    
    // Update structural body data for CSS hooks (lights, shadows, colors)
    body.setAttribute('data-state', targetState.id);

    // Crossfade Backgrounds for deep environmental shift
    Object.values(bgLayers).forEach(layer => layer.classList.remove('active'));
    bgLayers[targetState.id].classList.add('active');

    // Crossfade Content Layers for smooth typographic morphing
    hiddenLayer.innerHTML = renderStateContent(targetState);
    hiddenLayer.classList.add('active');
    currentLayer.classList.remove('active');

    // Swap layer pointers
    const temp = currentLayer;
    currentLayer = hiddenLayer;
    hiddenLayer = temp;
  }

  // Atmospheric Breathing (Psychological Drift)
  // Movement must be almost undetectable consciously, only felt.
  let currentElapsed = 0;
  let lastTimestamp = performance.now();

  function atmosphericDrift(timestamp) {
    const deltaTime = timestamp - lastTimestamp;
    lastTimestamp = timestamp;

    // Temporal Calm: Motion resembles slow environmental passage, not UI movement.
    let speedMultiplier = 0.4; // Extremely slow baseline
    if (currentStateId === 'observing') speedMultiplier = 0.3; // Measured attention
    if (currentStateId === 'review') speedMultiplier = 0.15; // Historically grounded, almost still

    currentElapsed += deltaTime * speedMultiplier;
    
    // Imperceptible scaling (1.000 to 1.001 over ~20 seconds)
    const scale = 1 + (Math.sin(currentElapsed * 0.00005) * 0.001);

    // Applying scale uniformly to the entire surface prevents layout jumps
    surface.style.transform = `scale(${scale})`;

    requestAnimationFrame(atmosphericDrift);
  }

  // Start the subtle drift
  requestAnimationFrame(atmosphericDrift);
});
