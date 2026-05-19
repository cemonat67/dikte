document.addEventListener('DOMContentLoaded', () => {
  const clockEl = document.getElementById('clock');
  
  function updateClock() {
    const now = new Date();
    // Format: HH:MM UTC (Removed seconds to eliminate fast monitoring behavior)
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    clockEl.textContent = `${hours}:${minutes} UTC`;
  }

  // Update immediately and then every second
  updateClock();
  setInterval(updateClock, 1000);

  // v2.0 Anti-Gravity Atmosphere Engine
  const systemAtmosphere = {
    operational_pressure: 0.31,
    continuity_confidence: 0.88,
    recovery_inertia: 0.57,
    environmental_fatigue: 0.12,
    institutional_memory: 0.49,
    human_presence: 0.93,
    spatial_calm: 0.84
  };

  // v2.3 Sensory Crisis Simulation
  window.sensoryCrisis = {
    type: "network_latency",
    intensity: 0.0,
    duration: 0,
    recovery_quality: 1.0
  };

  // Development/Test Interface for User
  window.simulateCrisis = (intensity = 0.8, type = "network_latency") => {
    window.sensoryCrisis.type = type;
    window.sensoryCrisis.intensity = intensity;
    console.log(`[Zero@Trust] Sensory Crisis Activated: ${type} at ${intensity}`);
  };
  window.resolveCrisis = () => {
    window.sensoryCrisis.intensity = 0.0;
    console.log(`[Zero@Trust] Sensory Crisis Recovering.`);
  };

  // v1.7 Atmospheric Behavior Engine
  const states = {
    preserved: { 
      label: 'OPERATIONAL TRUST', 
      value: 'Preserved.', 
      context: 'Continuity Intact.', 
      human: 'Human Control.',
      atm: { 
        luminance: 0, 
        trackingVal: 0.02, 
        trackingLbl: 0.5,
        scale: 1, 
        glowWidth: 40,
        glowOpacity: 0.3,
        blurBase: 60,
        textColor: '#ffffff',
        lblColor: '#8da4be'
      }
    },
    observing: { 
      label: 'VALIDATION', 
      value: 'Monitoring.', 
      context: 'Validation Active.', 
      human: 'Human Control.',
      atm: { 
        luminance: 0.25, 
        trackingVal: -0.01, 
        trackingLbl: 0.4,
        scale: 0.99, 
        glowWidth: 30,
        glowOpacity: 0.2,
        blurBase: 40,
        textColor: '#f0f4f8',
        lblColor: '#7b92ab'
      }
    },
    review: { 
      label: 'GOVERNANCE', 
      value: 'Review.', 
      context: 'Confidence Review.', 
      human: 'Attention Requested.',
      atm: { 
        luminance: 0.6, 
        trackingVal: -0.03, 
        trackingLbl: 0.3,
        scale: 0.98, 
        glowWidth: 15,
        glowOpacity: 0.1,
        blurBase: 25,
        textColor: '#d8e2ed',
        lblColor: '#6a7f96'
      }
    },
    constrained: { 
      label: 'CONTINUITY', 
      value: 'Constrained.', 
      context: 'Service Posture Maintained.', 
      human: 'System Preserved.',
      atm: { 
        luminance: 0.15, 
        trackingVal: -0.01, 
        trackingLbl: 0.45,
        scale: 0.99, 
        glowWidth: 20,
        glowOpacity: 0.15,
        blurBase: 35,
        textColor: '#e0e6ed',
        lblColor: '#5a6f86'
      }
    }
  };

  const centerLabel = document.querySelector('.center-label');
  const centerValue = document.querySelector('.center-value');
  const rightPanelText = document.querySelector('.right-panel-content span');
  const topMetaValue = document.querySelector('.meta-item.with-dot .value');
  const humanControlValue = document.querySelector('.control-item .value');
  
  let currentState = 'preserved';
  let memoryOfTrustActive = false;
  let currentDrilldownReason = 'Continuity Intact.';

  // v5.1 Frontend Environment Handshake
  const urlParams = new URLSearchParams(window.location.search);
  const currentEnv = urlParams.get('env') || 'default';
  const localStoreKey = `zt_trust_state_${currentEnv}`;

  // v2.6.1 Preview Silence Layer
  // Detects local environment to mock API and achieve ZERO network noise in console
  const IS_PREVIEW = window.location.hostname === "127.0.0.1" || 
                     window.location.hostname === "localhost" || 
                     window.location.protocol === 'file:';

  let apiState = {
    posture: 'quiet',
    temporal_state: 'transient',
    silence_locked: false,
    atmospheric_weight: 0.0,
    frontend_phrase: 'Continuity.'
  };

  // Graceful offline fallback via localStorage isolated by tenant
  try {
    const saved = localStorage.getItem(localStoreKey);
    if (saved) apiState = JSON.parse(saved);
  } catch(e) {}

  window.globalRiskPresence = apiState.atmospheric_weight;
  window.isSilenceLocked = apiState.silence_locked;
  window.globalTemporalMultiplier = 1.0;
  currentDrilldownReason = apiState.frontend_phrase;

  // v2.1 Atmospheric Persistence Layer (Residual Trauma Engine)
  let lastIncidentTime = localStorage.getItem(`zt_last_incident_time_${currentEnv}`);
  if (lastIncidentTime) lastIncidentTime = parseInt(lastIncidentTime, 10);
  else lastIncidentTime = 0;
  
  let isIncidentActive = false;

  // v2.2 Silent Interpretation Layer (Operational Emotional Physics)
  const historyKey = `zt_incident_history_${currentEnv}`;
  const overrideKey = `zt_human_overrides_${currentEnv}`;

  let incidentHistory = [];
  try {
    const savedHistory = localStorage.getItem(historyKey);
    if (savedHistory) incidentHistory = JSON.parse(savedHistory);
  } catch(e) {}
  
  let humanOverrides = 0;
  try {
    const savedOverrides = localStorage.getItem(overrideKey);
    if (savedOverrides) humanOverrides = parseInt(savedOverrides, 10);
  } catch(e) {}

  function evaluateCognitivePhysics() {
    const now = Date.now();
    
    // 1. Recurring Instability (Recovery Hesitation)
    // Clean up history older than 7 days
    incidentHistory = incidentHistory.filter(time => (now - time) < 7 * 24 * 60 * 60 * 1000);
    localStorage.setItem(historyKey, JSON.stringify(incidentHistory));
    
    // If more than 3 incidents in 7 days, recovery hesitation rises.
    const recovery_hesitation = Math.min(1.0, incidentHistory.length * 0.15);
    
    // 2. Human Override (Human Reassurance)
    const human_reassurance = Math.min(1.0, humanOverrides * 0.1);
    
    // 3. Temporal Recurrence (Long-Term Stability -> Morning Air)
    let continuity_calm = 0;
    if (lastIncidentTime > 0) {
      const elapsedHours = (now - lastIncidentTime) / (1000 * 60 * 60);
      if (elapsedHours > 72) { // 3 days of stability
        continuity_calm = Math.min(1.0, (elapsedHours - 72) / 72); // Max calm at 6 days
      }
    } else {
       continuity_calm = 1.0; 
    }
    
    return { recovery_hesitation, human_reassurance, continuity_calm };
  }

  function calculateResidualTrauma() {
    if (isIncidentActive) return 1.0;
    if (!lastIncidentTime) return 0.0;
    
    const elapsedMs = Date.now() - lastIncidentTime;
    const hoursElapsed = elapsedMs / (1000 * 60 * 60);
    
    if (hoursElapsed > 48) return 0.0; 
    
    // Non-linear decay representing institutional memory of an incident
    if (hoursElapsed <= 2) {
      return 1.0 - (hoursElapsed / 2) * 0.2; // 1.0 -> 0.8 (First 2 hours: heavy trauma)
    } else if (hoursElapsed <= 12) {
      return 0.8 - ((hoursElapsed - 2) / 10) * 0.4; // 0.8 -> 0.4 (Next 10 hours: slow softening)
    } else {
      return 0.4 - ((hoursElapsed - 12) / 36) * 0.4; // 0.4 -> 0.0 (Up to 48 hours: returning to normal)
    }
  }

  function getDynamicAtmosphere() {
    const trauma = calculateResidualTrauma();
    const cognition = evaluateCognitivePhysics();
    
    // v2.3 & v2.4 Sensory Crisis Modifiers
    let crisisViscosity = 0;
    let crisisBreathingWeight = 0;
    let crisisLuminanceDrop = 0;
    let crisisBreathingDepth = 1.0;
    
    if (window.sensoryCrisis.intensity > 0) {
      if (window.sensoryCrisis.type === 'network_latency') {
        // Latency friction: heavy viscosity, heavy breathing, slight luminance drop
        crisisViscosity = window.sensoryCrisis.intensity * 3.0;
        crisisBreathingWeight = window.sensoryCrisis.intensity * 4.0;
        crisisLuminanceDrop = window.sensoryCrisis.intensity * 0.15;
        
        // Degrade recovery quality over time (süründürür)
        window.sensoryCrisis.recovery_quality = Math.max(0.1, window.sensoryCrisis.recovery_quality - 0.005);
      } else if (window.sensoryCrisis.type === 'api_disconnection') {
        // v2.4 Inert Continuity: Disconnection is not failure, it is conservation.
        crisisViscosity = window.sensoryCrisis.intensity * 12.0; // Extreme freeze, hover & transitions crawl
        crisisBreathingWeight = window.sensoryCrisis.intensity * 8.0; // Breathing extends drastically
        crisisBreathingDepth = 1.0 - (window.sensoryCrisis.intensity * 0.85); // Shallow breath (oxygen cut)
        crisisLuminanceDrop = window.sensoryCrisis.intensity * 0.35; // Noticeable cooling / dimming
        
        // Repeated disconnection hurts institutional trust
        window.sensoryCrisis.recovery_quality = Math.max(0.05, window.sensoryCrisis.recovery_quality - 0.02);
      } else if (window.sensoryCrisis.type === 'governance_boundary') {
        // v2.5 Governance Boundary Tension: Control perimeter tightened. Not broken, restricted.
        crisisViscosity = window.sensoryCrisis.intensity * 2.0; // Deliberate, calculated, restricted
        crisisBreathingWeight = window.sensoryCrisis.intensity * 2.0; // Slightly heavier
        crisisBreathingDepth = 1.0 - (window.sensoryCrisis.intensity * 0.4); // Narrowed breathing, but not gasping
        crisisLuminanceDrop = window.sensoryCrisis.intensity * 0.25; // Cold, stark
        
        // Institutional trust recovers faster from governance if resolved, but takes a moderate hit
        window.sensoryCrisis.recovery_quality = Math.max(0.3, window.sensoryCrisis.recovery_quality - 0.01);
      }
    } else {
       // Slowly heal recovery quality
       window.sensoryCrisis.recovery_quality = Math.min(1.0, window.sensoryCrisis.recovery_quality + 0.002);
    }
    
    // Recovery hesitation prevents trauma from fully decaying
    const effectiveTrauma = Math.max(trauma, cognition.recovery_hesitation * 0.4);
    
    // Human reassurance anchors the system, reducing pressure. Crisis adds direct friction.
    const effectivePressure = Math.max(0.1, systemAtmosphere.operational_pressure + (effectiveTrauma * 0.6) - (cognition.human_reassurance * 0.3) + (window.sensoryCrisis.intensity * 0.5));
    
    // Continuity calm forces deep, long-term rest. Crisis degrades it.
    const effectiveCalm = Math.max(0, systemAtmosphere.spatial_calm - (effectiveTrauma * 0.7) + (cognition.continuity_calm * 0.5 * window.sensoryCrisis.recovery_quality) - crisisLuminanceDrop);
    
    // Fatigue is mitigated by long-term calm, exacerbated by hesitation and crisis breathing
    const effectiveFatigue = systemAtmosphere.environmental_fatigue + (effectiveTrauma * 0.8) + (cognition.recovery_hesitation * 0.2) - (cognition.continuity_calm * 0.4) + crisisBreathingWeight;

    // Inertia is bloated heavily by sensory crisis viscosity
    const effectiveInertia = systemAtmosphere.recovery_inertia + (effectiveTrauma * 0.5) + (cognition.recovery_hesitation * 0.3) + crisisViscosity + (1.0 - window.sensoryCrisis.recovery_quality);

    return {
      pressure: effectivePressure,
      fatigue: effectiveFatigue,
      calm: Math.min(1.0, effectiveCalm),
      inertia: effectiveInertia,
      trauma: effectiveTrauma,
      cognition: cognition,
      crisisRecovery: window.sensoryCrisis.recovery_quality,
      crisisBreathingDepth: crisisBreathingDepth
    };
  }

  let currentPollingInterval = 10000;
  let pollingTimer = null;

  // v2.6 Silent Failure Architecture (Graceful API Wrapper)
  // Eliminates uncaught promises and stack trace theater
  async function silentFetch(url, options = {}) {
    return new Promise((resolve) => {
      fetch(url, options).then(res => {
        resolve(res);
      }).catch(() => {
        // Silent degradation: absorb the rejection completely
        resolve({ ok: false, status: 503, json: async () => ({}) });
      });
    });
  }

  async function syncTrustState() {
    let fetchSuccess = false;
    const fetchStart = Date.now();
    
    if (IS_PREVIEW) {
      // ZERO NETWORK NOISE: Local preview acts as a complete atmosphere without 404s
      fetchSuccess = true;
      // We do not mutate apiState here so it holds its 'preserved' fallback 
      // or whatever it currently is, preventing console errors.
    } else {
      // Silent polling targeted specifically to the active URL environment
      const baseUrl = window.location.origin;
      const res = await silentFetch(`${baseUrl}/api/v1/trust/state?environment_id=${encodeURIComponent(currentEnv)}`);
      
      if (res.ok) {
        const data = await res.json();
        if (Object.keys(data).length > 0) {
          apiState = data;
          fetchSuccess = true;
          try { localStorage.setItem(localStoreKey, JSON.stringify(apiState)); } catch(e) {}
        }
      }
    }

    if (!fetchSuccess) {
      // v2.4 Inert Continuity (API Disconnection)
      window.sensoryCrisis.type = 'api_disconnection';
      window.sensoryCrisis.intensity = Math.min(1.0, window.sensoryCrisis.intensity + 0.3); // Ramp up conservation mode
      
      // v2.6 Silent Failure Architecture: No hard fail, no panic, no forced constrained state.
      // We simply preserve the last known state (Preserved Continuity) and quietly back off to prevent retry spam.
      currentPollingInterval = Math.min(60000, currentPollingInterval + 10000); // Backoff quietly up to 60s
      window.isRecovering = false;
    } else {
      // v2.3: Real-time network latency sensor (If Chrome DevTools throttles, system feels it)
      const fetchTime = Date.now() - fetchStart;
      let latencyFriction = Math.max(0, (fetchTime - 300) / 1200); // Ramps up if >300ms
      latencyFriction = Math.min(1.0, latencyFriction);
      
      if (latencyFriction > 0 && window.sensoryCrisis.type !== 'api_disconnection') {
         window.sensoryCrisis.intensity = Math.max(window.sensoryCrisis.intensity, latencyFriction);
         window.sensoryCrisis.type = "network_latency";
      } else {
         window.sensoryCrisis.intensity = Math.max(0.0, window.sensoryCrisis.intensity - 0.05); // Smooth network/api healing
      }
      
      // v16.2 Recovery Governance: Soft reconciliation
      if (currentPollingInterval > 10000) {
        window.isRecovering = true;
        // Step down the interval slowly rather than snapping back
        currentPollingInterval = Math.max(10000, currentPollingInterval - 5000);
        
        // During recovery cooldown, keep the narrative calm
        if (currentPollingInterval > 10000) {
            apiState.frontend_phrase = 'Operational continuity recovering.';
            apiState.posture = 'constrained'; // Force constrained mode until fully settled
        }
      } else {
        window.isRecovering = false;
        currentPollingInterval = 10000; // Normal rhythm
      }
    }

    // Map Backend variables
    window.globalRiskPresence = apiState.atmospheric_weight;
    window.isSilenceLocked = apiState.silence_locked;
    currentDrilldownReason = apiState.frontend_phrase;
    
    // Deterministic Operational State Engine Integration
    const condition = apiState.dominant_condition;
    
    if (condition && !document.body.classList.contains('te-resolving')) {
        document.querySelector('.te-title').textContent = condition.title;
        document.querySelector('.te-statement').textContent = condition.statement;
        document.querySelector('.te-recommendation').textContent = condition.recommendation;
        document.querySelector('.te-cta').textContent = condition.action;
        document.querySelector('.te-state').textContent = condition.state + '.';
        
        if (!document.body.classList.contains('show-trust-event')) {
            document.body.classList.add('show-trust-event');
        }
        if (!isIncidentActive) {
            incidentHistory.push(Date.now());
            localStorage.setItem(historyKey, JSON.stringify(incidentHistory));
        }
        isIncidentActive = true;
        lastIncidentTime = Date.now();
        localStorage.setItem(`zt_last_incident_time_${currentEnv}`, lastIncidentTime.toString());
    } else if (!condition && document.body.classList.contains('show-trust-event') && !document.body.classList.contains('te-resolving')) {
        document.body.classList.remove('show-trust-event');
        if (isIncidentActive) {
          isIncidentActive = false;
          lastIncidentTime = Date.now();
          localStorage.setItem(`zt_last_incident_time_${currentEnv}`, lastIncidentTime.toString());
        }
    }

    // Map backend posture to our frozen CSS visual states
    let targetUIState = 'preserved';
    if (apiState.posture === 'withheld' || apiState.posture === 'burdened') targetUIState = 'review';
    else if (apiState.posture === 'watching') targetUIState = 'observing';
    else if (apiState.posture === 'constrained') {
      targetUIState = 'constrained';
      if (!isIncidentActive) {
          incidentHistory.push(Date.now());
          localStorage.setItem(historyKey, JSON.stringify(incidentHistory));
      }
      isIncidentActive = true;
      lastIncidentTime = Date.now();
      localStorage.setItem(`zt_last_incident_time_${currentEnv}`, lastIncidentTime.toString());
    } else {
      if (isIncidentActive && !condition) {
        isIncidentActive = false;
        lastIncidentTime = Date.now();
        localStorage.setItem(`zt_last_incident_time_${currentEnv}`, lastIncidentTime.toString());
      }
    }

    if (currentState !== targetUIState) {
      transitionTo(targetUIState);
    }
    
    applyContinuousAtmosphere();
    
    clearTimeout(pollingTimer);
    pollingTimer = setTimeout(syncTrustState, currentPollingInterval);
  }

  function applyContinuousAtmosphere() {
    const root = document.documentElement;
    const dynamicAtm = getDynamicAtmosphere();
    
    window.globalTemporalMultiplier = 1.0;
    if (apiState.temporal_state === 'enduring') window.globalTemporalMultiplier = 4.0;
    else if (apiState.temporal_state === 'persistent') window.globalTemporalMultiplier = 2.5;
    else if (apiState.temporal_state === 'stable') window.globalTemporalMultiplier = 1.5;
    else if (apiState.temporal_state === 'unavailable') window.globalTemporalMultiplier = 8.0; // Extreme slowness when constrained

    if (window.isSilenceLocked) window.globalTemporalMultiplier = Math.max(5.0, window.globalTemporalMultiplier);
    
    // Anti-Gravity Pacing Integration (Using dynamic persistence)
    const agPacing = 1.0 + (dynamicAtm.pressure * 2.0) - (systemAtmosphere.continuity_confidence * 0.5);
    window.globalTemporalMultiplier *= Math.max(0.5, agPacing);

    // 1. Transition slowness
    const riskTransitionPenalty = window.globalRiskPresence * 20;
    let matureDuration = 14 * window.globalTemporalMultiplier;
    matureDuration = Math.max(30, matureDuration + riskTransitionPenalty);
    root.style.setProperty('--atm-transition-dur', `${matureDuration}s`);

    // 2. Luminance depth (heavy burden on risk)
    const riskLuminanceMod = window.globalRiskPresence * 0.4;
    let temporalLuminanceMod = (window.globalTemporalMultiplier - 1.0) * 0.05;
    if (window.isSilenceLocked) temporalLuminanceMod = Math.min(0.15, temporalLuminanceMod);
    
    // v2.6 Living Silence + Anti-Gravity Spatial Breathing + v2.4 Inert Continuity
    // Morning Air (continuity_calm) makes breathing exceptionally slow (deep rest)
    const cycleDuration = 120000 * (1.0 + dynamicAtm.fatigue * 2.0 + dynamicAtm.cognition.continuity_calm * 3.0);
    const cyclePos = (Date.now() % cycleDuration) / cycleDuration;
    // Apply shallow breath if api_disconnection is active
    const breathing = Math.sin(cyclePos * Math.PI * 2) * (dynamicAtm.crisisBreathingDepth !== undefined ? dynamicAtm.crisisBreathingDepth : 1.0);
    
    // Always apply a subtle atmospheric breathing, governed by dynamic spatial calm
    let postLockLuminanceMod = breathing * 0.01 * dynamicAtm.calm;
    let postLockOpacityMod = breathing * 0.02 * dynamicAtm.calm;
    
    if (window.isSilenceLocked) {
      postLockLuminanceMod += breathing * 0.02;
      postLockOpacityMod += breathing * 0.05;
    }
    
    // Apply depth
    // human reassurance anchors the system, adding a slight warm weight (0.02)
    // continuity calm brings 'morning air' (reduces depth, lighter) (-0.1)
    let tensionFactor = apiState.atmospheric_weight * 0.2; 
    let agLuminanceOffset = (dynamicAtm.fatigue * 0.08) - (dynamicAtm.calm * 0.05) - (dynamicAtm.cognition.continuity_calm * 0.1) + (dynamicAtm.cognition.human_reassurance * 0.02);
    
    root.style.setProperty('--atm-confidence-luminance-mod', tensionFactor + temporalLuminanceMod + postLockLuminanceMod + riskLuminanceMod + agLuminanceOffset);
    
    // 3. Typography Opacity suppression
    // Human reassurance increases base stability
    const riskOpacitySuppress = 1.0 - (window.globalRiskPresence * 0.6);
    let temporalOpacitySuppress = 1.0 / Math.max(1.0, window.globalTemporalMultiplier * 1.5);
    
    // v2.5: In governance boundary, text remains strictly visible (authoritative), resisting temporal suppression
    if (window.sensoryCrisis && window.sensoryCrisis.type === 'governance_boundary') {
        temporalOpacitySuppress = Math.max(temporalOpacitySuppress, 0.8 * window.sensoryCrisis.intensity);
    }
    
    const baseConfidence = Math.min(1.0, (1.0 - apiState.atmospheric_weight) + (dynamicAtm.cognition.human_reassurance * 0.3));
    const finalOpacity = (baseConfidence * temporalOpacitySuppress * riskOpacitySuppress) + postLockOpacityMod;
    
    root.style.setProperty('--atm-confidence-opacity-mod', Math.max(0.01, finalOpacity));

    // Phase 19: Temporal Kinematics (Memory Binding) & Anti-Gravity Viscosity
    const mem = apiState.institutional_memory !== undefined ? apiState.institutional_memory : systemAtmosphere.institutional_memory;
    const clampedMem = Math.min(1.0, Math.max(0.0, mem + (dynamicAtm.trauma * 0.5)));
    
    // Viscosity scales transition heaviness and hover delays
    const agViscosity = 1.0 + dynamicAtm.inertia + (dynamicAtm.pressure * 0.5);
    
    // transition-base: 0.8s -> 1.8s, modified by viscosity
    root.style.setProperty('--zt-transition-base', `${(0.8 + (clampedMem * 1.0)) * agViscosity}s`);
    
    // settle-time: 1.2s -> 3.2s, modified by viscosity
    root.style.setProperty('--zt-settle-time', `${(1.2 + (clampedMem * 2.0)) * agViscosity}s`);
    
    // hover-delay / hover response
    root.style.setProperty('--zt-hover-delay', `${(clampedMem * 0.8) * agViscosity}s`);
    
    // atmospheric blur (Softness)
    // Morning air creates ultra soft contrast (more blur)
    let crisisSharpness = 0;
    if (window.sensoryCrisis && window.sensoryCrisis.type === 'governance_boundary') {
        // v2.5 Governance tension removes softness, making the UI feel harsh, stark, and authoritative.
        crisisSharpness = window.sensoryCrisis.intensity * 6.0; 
    }
    const agSoftness = Math.max(0, dynamicAtm.calm * 4.0 + (systemAtmosphere.human_presence * 2.0) + (dynamicAtm.cognition.continuity_calm * 5.0) - crisisSharpness);
    root.style.setProperty('--zt-atmospheric-blur', `${2 + (clampedMem * 2) + agSoftness}px`);
    
    // Add additional luminance drag (Visual Inertia)
    const agVisualInertia = dynamicAtm.fatigue * 0.15;
    root.style.setProperty('--zt-luminance-drag', `${(clampedMem * 0.1) + agVisualInertia}`);
  }

  function calculateSilentConfidence() {
    return apiState.frontend_phrase;
  }

  // Engage API Polling
  setTimeout(syncTrustState, 100);
  setInterval(applyContinuousAtmosphere, 1000); // 1s loop ensures sine wave animates smoothly

  function applyAtmosphere(atm, transitionSpeed = '14s') {
    const root = document.documentElement;
    root.style.setProperty('--atm-transition-dur', transitionSpeed);
    root.style.setProperty('--atm-luminance', atm.luminance);
    root.style.setProperty('--atm-tracking-val', atm.trackingVal + 'em');
    root.style.setProperty('--atm-tracking-lbl', atm.trackingLbl + 'em');
    root.style.setProperty('--atm-scale', atm.scale);
    root.style.setProperty('--atm-glow-width', atm.glowWidth + 'px');
    root.style.setProperty('--atm-glow-opacity', atm.glowOpacity);
    root.style.setProperty('--atm-glow-blur', atm.blurBase + 'px');
    root.style.setProperty('--atm-text-color', atm.textColor);
    root.style.setProperty('--atm-lbl-color', atm.lblColor);
  }

  // Initialize Base Atmosphere
  applyAtmosphere(states.preserved.atm, '0s');

  function transitionTo(stateId) {
    const prevState = currentState;
    currentState = stateId;
    document.body.setAttribute('data-state', stateId);
    
    // Memory of Trust Layer and Transition Timings
    let targetAtm = { ...states[stateId].atm };
    
    // Default fallback speed
    let baseSpeed = 10; 
    
    // Dynamic transition times based on direction
    if (prevState === 'preserved' && stateId === 'observing') baseSpeed = 9;
    else if (prevState === 'observing' && stateId === 'review') baseSpeed = 12;
    else if (prevState === 'review' && stateId === 'preserved') baseSpeed = 18;
    else if (prevState === 'observing' && stateId === 'preserved') baseSpeed = 9;
    else if (prevState === 'review' && stateId === 'observing') baseSpeed = 12;

    const dynamicAtm = getDynamicAtmosphere();
    
    // Anti-Gravity: Viscous transitions under pressure and inertia
    const agMultiplier = 1.0 + (dynamicAtm.pressure * 1.5) + (dynamicAtm.inertia * 2.0);
    let speed = `${baseSpeed * agMultiplier}s`;

    if (prevState === 'review' && stateId === 'preserved') {
      memoryOfTrustActive = true;
      targetAtm.luminance = 0.15; 
      targetAtm.trackingVal = 0.01;
      targetAtm.trackingLbl = 0.45;
    } else {
      memoryOfTrustActive = false;
    }

    applyAtmosphere(targetAtm, speed);
    
    // Slow text crossfade
    centerValue.style.opacity = '0';
    centerLabel.style.opacity = '0';
    rightPanelText.style.opacity = '0';
    topMetaValue.style.opacity = '0';
    humanControlValue.style.opacity = '0';
    
    setTimeout(() => {
      centerLabel.textContent = states[stateId].label;
      centerValue.textContent = states[stateId].value;
      rightPanelText.textContent = states[stateId].context;
      topMetaValue.textContent = states[stateId].value;
      humanControlValue.textContent = states[stateId].human;
      
      centerValue.style.opacity = '1';
      centerLabel.style.opacity = '1';
      rightPanelText.style.opacity = '1';
      topMetaValue.style.opacity = '1';
      humanControlValue.style.opacity = '1';
    }, 1800 + ((apiState.institutional_memory || 0) * 1500)); // Dynamic settle delay
  }

  // Executive Curiosity Architecture - Silent Drilldown
  const centerStage = document.querySelector('.center-stage');
  const drilldownText = document.getElementById('drilldown-text');
  let curiosityTimer;

  centerStage.addEventListener('mouseenter', () => {
    // v2.5 & v3.0 Silent Refusal Behavior & Risk suppression
    const dynamicAtm = getDynamicAtmosphere();
    const riskDelayPenalty = (typeof window.globalRiskPresence !== 'undefined' ? window.globalRiskPresence : 0) * 6000;
    const memoryDelayPenalty = (apiState.institutional_memory || systemAtmosphere.institutional_memory || 0.0) * 1500;
    
    // Anti-Gravity: Slower under pressure, calmer long exposure
    const agDelayPenalty = (dynamicAtm.pressure * 3000) + (dynamicAtm.fatigue * 4000);
    
    let dynamicDelay = (1000 * window.globalTemporalMultiplier) + riskDelayPenalty + memoryDelayPenalty + agDelayPenalty;
    
    if (typeof window.isSilenceLocked !== 'undefined' && window.isSilenceLocked) {
      dynamicDelay = Math.max(8000 + riskDelayPenalty + agDelayPenalty, dynamicDelay);
    }
    curiosityTimer = setTimeout(() => {
      document.body.classList.add('curiosity-active');
      drilldownText.textContent = currentDrilldownReason;
    }, dynamicDelay);
  });

  centerStage.addEventListener('mouseleave', () => {
    clearTimeout(curiosityTimer);
    document.body.classList.remove('curiosity-active');
  });

  const bottomBar = document.querySelector('.bottom-bar');
  const archivalTrace = document.getElementById('archival-trace');
  let evidenceRevealTimer;

  bottomBar.addEventListener('mouseenter', () => {
    // v2.5 & v3.0 Hover resistance suppresses response heavily based on risk and locks
    const dynamicAtm = getDynamicAtmosphere();
    const riskDelayPenalty = (typeof window.globalRiskPresence !== 'undefined' ? window.globalRiskPresence : 0) * 6000;
    const memoryDelayPenalty = (apiState.institutional_memory || systemAtmosphere.institutional_memory || 0.0) * 2000;
    
    // Anti-Gravity: Restrained complexity
    const agDelayPenalty = (dynamicAtm.pressure * 4000) + (dynamicAtm.fatigue * 5000);
    
    let dynamicDelay = (2500 * window.globalTemporalMultiplier) + riskDelayPenalty + memoryDelayPenalty + agDelayPenalty;
    if (typeof window.isSilenceLocked !== 'undefined' && window.isSilenceLocked) {
      dynamicDelay = Math.max(12000 + riskDelayPenalty + agDelayPenalty, dynamicDelay);
    }
    evidenceRevealTimer = setTimeout(() => {
      archivalTrace.textContent = calculateSilentConfidence();
      document.body.classList.add('evidence-reveal');
    }, dynamicDelay);
  });

  bottomBar.addEventListener('mouseleave', () => {
    clearTimeout(evidenceRevealTimer);
    document.body.classList.remove('evidence-reveal');
  });

  // Trust Event Demo Trigger
  const demoTrigger = document.getElementById('demo-trigger');
  const teCta = document.getElementById('te-cta');
  
  if (demoTrigger) {
    demoTrigger.addEventListener('dblclick', () => {
      // Deliberate pause before showing event
      incidentHistory.push(Date.now());
      localStorage.setItem(historyKey, JSON.stringify(incidentHistory));
      
      setTimeout(() => {
        transitionTo('constrained');
        document.body.classList.add('show-trust-event');
      }, 1500); // 1500ms deliberate pause
    });
  }

  if (teCta) {
    teCta.addEventListener('click', () => {
      humanOverrides++;
      localStorage.setItem(overrideKey, humanOverrides.toString());
      
      document.body.classList.add('te-resolving');
      
      // v2.6.1: Zero network noise
      if (!IS_PREVIEW) {
        // Call backend to deterministically resolve the condition silently
        const baseUrl = window.location.origin;
        silentFetch(`${baseUrl}/api/v1/trust/action/resolve`, { method: 'POST' });
      }
      
      // Keep it showing the resolution message, then fade out the event completely
      setTimeout(() => {
        document.body.classList.remove('show-trust-event');
        document.body.classList.remove('te-resolving');
        
        // Wait for fade out to finish before reverting state
        const dynamicAtm = getDynamicAtmosphere();
        const memPenalty = (apiState.institutional_memory !== undefined ? apiState.institutional_memory : systemAtmosphere.institutional_memory) * 2000;
        const agPenalty = (dynamicAtm.inertia * 3000) + (dynamicAtm.fatigue * 2000);
        const settleDelay = 2000 + memPenalty + agPenalty;
        setTimeout(() => {
          transitionTo('preserved');
        }, settleDelay);
      }, 4000); // Wait 4 seconds reading the feedback
    });
  }
});
