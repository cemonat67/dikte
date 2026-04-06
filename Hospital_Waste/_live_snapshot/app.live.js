
async function loadFacilities(){
  const res = await fetch('/api/facilities');
  const data = await res.json();

  const sel = document.getElementById('facilitySelect');
  sel.innerHTML = '<option value="">Tüm Tesisler</option>';

  data.forEach(f=>{
    const opt = document.createElement('option');
    opt.value = f.facility_code;
    opt.textContent = f.facility_name;
    sel.appendChild(opt);
  });

  sel.addEventListener('change', ()=>{
    loadAll(sel.value);
  });
}

const els = {
  refreshBtn: document.getElementById("refreshBtn"),
  latestKpis: document.getElementById("latestKpis"),
  dailyTableBody: document.querySelector("#dailyTable tbody"),

  personaCeo: document.getElementById("personaCeoValue"),
  personaCfo: document.getElementById("personaCfoValue"),
  personaCto: document.getElementById("personaCtoValue"),
  personaChief: document.getElementById("personaChiefValue"),
  personaManager: document.getElementById("personaManagerValue"),

  trendChart: document.getElementById("trendChart"),
  impactChart: document.getElementById("impactChart"),
};

function fmt(v){
  return v==null ? "—" : Number(v).toLocaleString("tr-TR");
}

async function safeFetch(url){
  try{
    const r = await fetch(url);
    if(!r.ok) throw new Error();
    return await r.json();
  }catch{
    console.warn("API FAIL:", url);
    return null;
  }
}

function renderPersonas(ai, latest){
  if(!latest) return;

  const statusMap = {
    STABLE: "Stabil",
    RISK: "Risk",
    LOW_CONFIDENCE: "Düşük Güven"
  };

  const statusText = statusMap[ai?.overall_status] || "Stabil";
  const energyText = `${fmt(latest.energy_kwh)} kWh`;
  const prodText = `${fmt(latest.production_kg)} kg`;

  let ctoText = "Normal";
  if (ai?.energy_trend === "increasing") ctoText = "Enerji Artışı";
  else if (ai?.energy_trend === "decreasing") ctoText = "Enerji Düşüşü";

  let chiefText = "Rutin izleme";
  if (ai?.recommended_action === "Continue monitoring.") chiefText = "İzlemeye devam";
  else if (ai?.recommended_action === "Investigate missing data sources.") chiefText = "Veri kaynağını kontrol et";
  else if (ai?.recommended_action === "Review operational efficiency and recent changes.") chiefText = "Operasyonu gözden geçir";
  else if (ai?.recommended_action) chiefText = ai.recommended_action;

  let cfoText = energyText;
  if (latest.energy_kwh && latest.co2_kg) {
    cfoText = `${fmt(latest.energy_kwh)} kWh / ${fmt(latest.co2_kg)} kg CO₂`;
  }

  els.personaCeo.textContent = statusText;
  els.personaCfo.textContent = cfoText;
  els.personaCto.textContent = ctoText;
  els.personaChief.textContent = chiefText;
  els.personaManager.textContent = prodText;
}

function drawTrend(canvas,data){
  if(!canvas || !data?.length) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const padTop = 22;
  const padBottom = 28;
  const plotH = h - padTop - padBottom;

  ctx.clearRect(0,0,w,h);

  const values = data.map(d=>d.energy_kwh||0).reverse();
  const max = Math.max(...values);
  const min = Math.min(...values);
  const span = Math.max(max - min, 1);

  // grid
  ctx.strokeStyle = "rgba(255,255,255,0.05)";
  ctx.lineWidth = 1;
  for(let i=0;i<5;i++){
    const y = padTop + (plotH/4)*i;
    ctx.beginPath();
    ctx.moveTo(0,y);
    ctx.lineTo(w,y);
    ctx.stroke();
  }

  // area
  ctx.beginPath();
  values.forEach((v,i)=>{
    const x = (i/(values.length-1))*w;
    const y = padTop + (1 - ((v - min)/span)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.lineTo(w, h - padBottom);
  ctx.lineTo(0, h - padBottom);
  ctx.closePath();
  ctx.fillStyle = "rgba(249,186,0,0.10)";
  ctx.fill();

  // line
  ctx.beginPath();
  values.forEach((v,i)=>{
    const x = (i/(values.length-1))*w;
    const y = padTop + (1 - ((v - min)/span)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.strokeStyle = "#f9ba00";
  ctx.lineWidth = 2.5;
  ctx.stroke();
}

function drawImpact(canvas,data){
  if(!canvas || !data?.length) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const padTop = 22;
  const padBottom = 28;
  const plotH = h - padTop - padBottom;

  ctx.clearRect(0,0,w,h);

  const co2Values = data.map(d => d.co2_kg || 0).reverse();
  const prodValues = data.map(d => d.production_kg || 0).reverse();

  const maxCo2 = Math.max(...co2Values);
  const minCo2 = Math.min(...co2Values);
  const spanCo2 = Math.max(maxCo2 - minCo2, 1);

  const maxProd = Math.max(...prodValues);
  const minProd = Math.min(...prodValues);
  const spanProd = Math.max(maxProd - minProd, 1);

  // grid
  ctx.strokeStyle = "rgba(255,255,255,0.05)";
  ctx.lineWidth = 1;
  for(let i=0;i<5;i++){
    const y = padTop + (plotH/4)*i;
    ctx.beginPath();
    ctx.moveTo(0,y);
    ctx.lineTo(w,y);
    ctx.stroke();
  }

  // CO2 fill
  ctx.beginPath();
  co2Values.forEach((v,i)=>{
    const x = (i/(co2Values.length-1))*w;
    const y = padTop + (1 - ((v - minCo2)/spanCo2)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.lineTo(w, h - padBottom);
  ctx.lineTo(0, h - padBottom);
  ctx.closePath();
  ctx.fillStyle = "rgba(239,68,68,0.08)";
  ctx.fill();

  // CO2 line
  ctx.beginPath();
  co2Values.forEach((v,i)=>{
    const x = (i/(co2Values.length-1))*w;
    const y = padTop + (1 - ((v - minCo2)/spanCo2)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.strokeStyle = "#ef4444";
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Production fill
  ctx.beginPath();
  prodValues.forEach((v,i)=>{
    const x = (i/(prodValues.length-1))*w;
    const y = padTop + (1 - ((v - minProd)/spanProd)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.lineTo(w, h - padBottom);
  ctx.lineTo(0, h - padBottom);
  ctx.closePath();
  ctx.fillStyle = "rgba(34,197,94,0.08)";
  ctx.fill();

  // Production line
  ctx.beginPath();
  prodValues.forEach((v,i)=>{
    const x = (i/(prodValues.length-1))*w;
    const y = padTop + (1 - ((v - minProd)/spanProd)) * plotH;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  });
  ctx.strokeStyle = "#22c55e";
  ctx.lineWidth = 2.5;
  ctx.stroke();
}

async function loadAll(){

  const ai = await safeFetch('/api/ai/summary?days=14');
  const latestRows = await safeFetch('/api/dashboard/latest');
  const daily = await safeFetch('/api/dashboard/daily?days=14');

  if(!latestRows || !daily){
    console.error("DATA FAIL");
    return;
  }

  const latest = latestRows[0];

  renderPersonas(ai, latest);
  drawTrend(els.trendChart, daily);
  drawImpact(els.impactChart, daily);

  els.latestKpis.innerHTML = `
    <div class="card"><div class="card-title">Enerji</div><div class="card-value">${fmt(latest.energy_kwh)} kWh</div></div>
    <div class="card"><div class="card-title">Su</div><div class="card-value">${fmt(latest.water_m3)} m³</div></div>
    <div class="card"><div class="card-title">CO₂</div><div class="card-value">${fmt(latest.co2_kg)} kg</div></div>
  `;

  els.dailyTableBody.innerHTML = "";

  daily.forEach(r=>{
    const tr=document.createElement("tr");
    tr.innerHTML=`
      <td>${r.reading_date}</td>
      <td>${r.facility}</td>
      <td>${fmt(r.production_kg)}</td>
      <td>${fmt(r.energy_kwh)}</td>
      <td>${fmt(r.water_m3)}</td>
      <td>${fmt(r.co2_kg)}</td>
      <td style="color:#22c55e;font-weight:bold">LIVE ●</td>
    `;
    els.dailyTableBody.appendChild(tr);
  });

  await loadClinicDashboard();
}

async function boot(){
  await loadFacilities(); loadAll();
  els.refreshBtn.onclick=loadAll;
  bindHospitalIntakeLauncher();
  setInterval(loadAll,15000);
}


async function openClinicModal(facility){
  const res = await fetch(`/api/clinics?facility_code=${facility}`);
  const data = await res.json();

  const el = document.getElementById('modalContent');
  el.innerHTML = data.map(c => `
    <div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
      <b>${c.clinic_name}</b> — ${Math.round(c.co2_kg)} kg CO₂
    </div>
  `).join('');

  document.getElementById('modal').style.display = 'block';
}


function closeModal(){
  const modal = document.getElementById("modal");
  const content = document.getElementById("modalContent");
  const title = document.getElementById("modalTitle");
  const modalBox = modal ? modal.querySelector(":scope > div") : null;
  const legacyClose = modal ? modal.querySelector(":scope > div > button:not(.intake-modal-close)") : null;

  if(content) content.innerHTML = "";
  if(title) title.style.display = "";
  if(legacyClose) legacyClose.style.display = "";
  if(modalBox){
    modalBox.style.maxWidth = "800px";
    modalBox.style.width = "";
    modalBox.style.margin = "80px auto";
    modalBox.style.background = "#0b1220";
    modalBox.style.padding = "24px";
    modalBox.style.borderRadius = "16px";
    modalBox.style.maxHeight = "";
    modalBox.style.overflow = "";
  }
  if(modal){
    modal.style.display = "none";
    modal.style.background = "rgba(0,0,0,0.6)";
    modal.style.zIndex = "999";
  }
}

function closeIntake(){
  closeModal();
}

function bindHospitalIntakeLauncher(){
  const btn = document.getElementById("openHospitalIntakeBtn");
  const modal = document.getElementById("modal");
  const modalContent = document.getElementById("modalContent");
  const tpl = document.getElementById("hospitalIntakeTemplate");
  const modalTitle = document.getElementById("modalTitle");
  const modalBox = modal ? modal.querySelector(":scope > div") : null;
  const legacyClose = modal ? modal.querySelector(":scope > div > button:not(.intake-modal-close)") : null;

  if(!btn || !modal || !modalContent || !tpl || btn.dataset.bound === "1") return;
  btn.dataset.bound = "1";

  btn.addEventListener("click", () => {
    modalContent.innerHTML = tpl.innerHTML;

    const intakeShell = modalContent.querySelector(".intake-modal-shell");
    if(intakeShell){
      intakeShell.style.display = "block";
      intakeShell.style.position = "static";
      intakeShell.style.inset = "auto";
      intakeShell.style.background = "transparent";
      intakeShell.style.zIndex = "auto";
    }

    if(modalTitle) modalTitle.style.display = "none";
    if(legacyClose) legacyClose.style.display = "none";

    if(modalBox){
      modalBox.style.maxWidth = "1100px";
      modalBox.style.width = "92vw";
      modalBox.style.margin = "40px auto";
      modalBox.style.background = "#081225";
      modalBox.style.padding = "32px";
      modalBox.style.borderRadius = "24px";
      modalBox.style.maxHeight = "90vh";
      modalBox.style.overflow = "auto";
    }

    modal.style.background = "rgba(2,6,23,0.82)";
    modal.style.zIndex = "9999";
    modal.style.display = "block";

    bindHospitalIntakeForm();
  });

  modal.addEventListener("click", (e) => {
    if(e.target === modal) closeModal();
  });
}

document.getElementById('personaCeoCard')?.addEventListener('click', ()=>{
  const sel = document.getElementById('facilitySelect');
  openClinicModal(sel.value);
});

async function loadClinicDashboard(){
  const highlights = await safeFetch(`/api/dashboard/clinic-highlights?facility_code=bazekol`);
  const daily = await safeFetch(`/api/dashboard/clinic-daily?facility_code=bazekol&days=14`);

  if(!highlights || !daily) return;

  const hlDiv = document.getElementById("clinicHighlights");
  const miniChartDiv = document.getElementById("clinicDailyMiniChart");
  const wasteDiv = document.getElementById("clinicWaste");

  if(!hlDiv || !wasteDiv || !miniChartDiv) return;

  const normalizedHighlights = Array.from(
    highlights.reduce((acc, item) => {
      const prev = acc.get(item.clinic);
      if (!prev || Number(item.risk_score || 0) > Number(prev.risk_score || 0)) {
        acc.set(item.clinic, item);
      }
      return acc;
    }, new Map()).values()
  ).sort((a, b) => {
    const rankDiff = Number(a.rank || 999999) - Number(b.rank || 999999);
    if (rankDiff !== 0) return rankDiff;
    return Number(b.risk_score || 0) - Number(a.risk_score || 0);
  });

  hlDiv.innerHTML = normalizedHighlights.map(h => {
    const riskClass =
      h.risk_level === "kirmizi" ? "risk-bad" :
      h.risk_level === "sari" ? "risk-warn" :
      "risk-ok";

    return `
      <div class="card clinic-highlight-card ${riskClass}">
        <div class="clinic-card-head">
          <div class="card-title">${h.clinic}</div>
          <div class="clinic-rank-badge">#${h.rank}</div>
        </div>
        <div class="clinic-risk-value">${String(h.risk_level || "").toUpperCase()}</div>
        <div class="clinic-risk-meta">Risk Skoru: ${Math.round(Number(h.risk_score || 0))}</div>
      </div>
    `;
  }).join("");

  const maxWaste = Math.max(...daily.map(d => Number(d.total_waste_kg || 0)), 1);
  const topClinic = daily.find(d => Number(d.total_waste_kg || 0) === maxWaste);

  miniChartDiv.innerHTML = `
    <div class="clinic-mini-chart-head">
      <div class="clinic-mini-chart-title">Klinik Atık Yoğunluğu — 14 Günlük Karşılaştırma</div>
      <div class="clinic-mini-chart-subtitle">Toplam atık bazında klinikler arası hızlı görünüm</div>
    </div>
    <div class="clinic-mini-chart-bars">
      ${daily.map(d => {
        const totalWaste = Number(d.total_waste_kg || 0);
        const width = Math.max(6, Math.round((totalWaste / maxWaste) * 100));
        const isLeader = topClinic && d.clinic === topClinic.clinic;
        return `
          <div class="clinic-mini-chart-row ${isLeader ? "is-leader" : ""}">
            <div class="clinic-mini-chart-label">
              ${d.clinic}
              ${isLeader ? '<span class="clinic-leader-badge">#1 Yük</span>' : ''}
            </div>
            <div class="clinic-mini-chart-track">
              <div class="clinic-mini-chart-fill ${isLeader ? "is-leader" : ""}" style="width:${width}%"></div>
            </div>
            <div class="clinic-mini-chart-value ${isLeader ? "is-leader" : ""}">${fmt(totalWaste)} kg</div>
          </div>
        `;
      }).join("")}
    </div>
  `;

  wasteDiv.innerHTML = daily.map(d => `
    <div class="card clinic-waste-card">
      <div class="clinic-card-head">
        <div class="card-title">${d.clinic}</div>
        <div class="clinic-mini-badge">14 Gün</div>
      </div>
      <div class="clinic-metric-row"><span>Su</span><strong>${fmt(d.water_m3)} m³</strong></div>
      <div class="clinic-metric-row"><span>Karbon Ayak İzi</span><strong>${fmt(d.co2_kg)} kg CO₂</strong></div>
      <div class="clinic-metric-row"><span>Tıbbi Atık</span><strong>${fmt(d.medical_waste_kg)} kg</strong></div>
      <div class="clinic-metric-row"><span>Patolojik Atık</span><strong>${fmt(d.pathological_waste_kg)} kg</strong></div>
      <div class="clinic-total-row"><span>Toplam Atık</span><strong>${fmt(d.total_waste_kg)} kg</strong></div>
    </div>
  `).join("");
}

function bindHospitalIntakeForm(){
  const form = document.getElementById("hospitalIntakeForm");
  const statusEl = document.getElementById("intakeFormStatus");
  if(!form || !statusEl || form.dataset.bound === "1") return;

  form.dataset.bound = "1";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fd = new FormData(form);
    const requestedModules = String(fd.get("requested_modules") || "")
      .split(",")
      .map(x => x.trim())
      .filter(Boolean);

    const toInt = (v) => {
      const x = String(v || "").trim();
      if(!x) return null;
      const n = Number(x);
      return Number.isFinite(n) ? n : null;
    };

    const payload = {
      facility_code: "bazekol",
      hospital_name: String(fd.get("hospital_name") || "").trim(),
      contact_name: String(fd.get("contact_name") || "").trim() || null,
      contact_title: String(fd.get("contact_title") || "").trim() || null,
      contact_email: String(fd.get("contact_email") || "").trim() || null,
      contact_phone: String(fd.get("contact_phone") || "").trim() || null,
      facility_type: String(fd.get("facility_type") || "").trim() || null,
      bed_count: toInt(fd.get("bed_count")),
      employee_count: toInt(fd.get("employee_count")),
      daily_patient_count: toInt(fd.get("daily_patient_count")),
      requested_modules: requestedModules,
      current_systems: String(fd.get("current_systems") || "").trim() || null,
      priority_level: String(fd.get("priority_level") || "normal").trim() || "normal",
      notes: String(fd.get("notes") || "").trim() || null,
      source_channel: "dashboard"
    };

    if(!payload.hospital_name){
      statusEl.textContent = "Hastane adı zorunlu.";
      statusEl.className = "intake-status error";
      return;
    }

    statusEl.textContent = "Kaydediliyor...";
    statusEl.className = "intake-status pending";

    try {
      const res = await fetch("/api/intake", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if(!res.ok || data.status !== "ok"){
        throw new Error(data.detail || "Intake kaydı başarısız");
      }

      statusEl.textContent = `Kaydedildi: ${data.intake.hospital_name}`;
      statusEl.className = "intake-status success";
      form.reset();
      form.querySelector('input[name="hospital_name"]').value = "Demo Hospital";
      form.querySelector('select[name="priority_level"]').value = "normal";
      setTimeout(() => closeModal(), 900);
    } catch (err) {
      statusEl.textContent = `Hata: ${err.message}`;
      statusEl.className = "intake-status error";
    }
  });
}

boot();


// === Intake modal override ===
window.openIntake = function(html) {
  const modal = document.getElementById("intakeModal");
  const content = document.getElementById("intakeContent");

  if (!modal || !content) {
    console.error("Intake modal container missing");
    return;
  }

  content.innerHTML = html;
  modal.classList.add("active");
};

window.closeIntake = function() {
  document.getElementById("intakeModal")?.classList.remove("active");

  const legacyModal = document.getElementById("modal");
  const legacyContent = document.getElementById("modalContent");
  const legacyTitle = document.getElementById("modalTitle");

  if (legacyContent) legacyContent.innerHTML = "";
  if (legacyTitle) legacyTitle.style.display = "";
  if (legacyModal) legacyModal.style.display = "none";
};

// ESC ile kapatma
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeIntake();
});


function openVisualPopup(kind){
  const modal = document.getElementById("modal");
  const content = document.getElementById("modalContent");

  const tpl = document.getElementById(
    kind === "reports" ? "reportsCenterTemplate" : "intakeHubTemplate"
  );

  if(!modal || !content || !tpl) return;

  content.innerHTML = tpl.innerHTML;
  modal.style.display = "block";
}

