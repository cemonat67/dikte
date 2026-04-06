
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
  bindHospitalIntakeLauncher();
  bindVisualPopupButtons();
  els.refreshBtn.onclick = loadAll;

  try {
    await loadFacilities();
    await loadAll();
  } catch (err) {
    console.warn("BOOT API SKIP:", err);
  }

  setInterval(() => {
    loadAll().catch(err => console.warn("AUTO REFRESH SKIP:", err));
  }, 15000);
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
  if(content) content.innerHTML = "";
  if(modal) modal.style.display = "none";
}

function bindHospitalIntakeLauncher(){
  const btn = document.getElementById("openHospitalIntakeBtn");
  const modal = document.getElementById("modal");
  const modalContent = document.getElementById("modalContent");
  const tpl = document.getElementById("hospitalIntakeTemplate");

  if(!btn || !modal || !modalContent || !tpl || btn.dataset.bound === "1") return;
  btn.dataset.bound = "1";

  btn.addEventListener("click", () => {
    modalContent.innerHTML = tpl.innerHTML;
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


function bindVisualPopupButtons(){
  const intakeBtn = document.getElementById("openIntakeHubBtn");
  const reportsBtn = document.getElementById("openReportsCenterBtn");

  if(intakeBtn && intakeBtn.dataset.bound !== "1"){
    intakeBtn.dataset.bound = "1";
    intakeBtn.addEventListener("click", function(e){
      e.preventDefault();
      e.stopPropagation();
      openVisualPopup("intake");
    });
  }

  if(reportsBtn && reportsBtn.dataset.bound !== "1"){
    reportsBtn.dataset.bound = "1";
    reportsBtn.addEventListener("click", function(e){
      e.preventDefault();
      e.stopPropagation();
      openVisualPopup("reports");
    });
  }
}


if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}


/* ROLE_POPUP_V1 */
(function () {
  function ensureModal() {
    if (document.getElementById("roleDetailModal")) return;

    const html = `
      <div id="roleDetailModal" style="display:none;position:fixed;inset:0;background:rgba(5,10,20,.72);z-index:99999;align-items:center;justify-content:center;padding:20px;">
        <div style="width:min(680px,96vw);background:linear-gradient(180deg,#0d1b2a 0%, #13263b 100%);border:1px solid rgba(255,255,255,.10);border-radius:18px;box-shadow:0 24px 80px rgba(0,0,0,.45);color:#fff;overflow:hidden;">
          <div style="display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid rgba(255,255,255,.08);">
            <div>
              <div id="roleDetailTitle" style="font-size:22px;font-weight:800;letter-spacing:.2px;">Role Detail</div>
              <div id="roleDetailStatus" style="margin-top:6px;font-size:13px;opacity:.82;">Status</div>
            </div>
            <button id="roleDetailClose" type="button" style="border:0;background:transparent;color:#fff;font-size:28px;line-height:1;cursor:pointer;">×</button>
          </div>

          <div style="padding:20px;">
            <div style="display:grid;grid-template-columns:1fr;gap:14px;">
              <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:14px;">
                <div style="font-size:12px;text-transform:uppercase;letter-spacing:.12em;opacity:.70;">Ne görüyorum?</div>
                <div id="roleDetailInsight" style="margin-top:8px;font-size:15px;line-height:1.55;"></div>
              </div>

              <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:14px;">
                <div style="font-size:12px;text-transform:uppercase;letter-spacing:.12em;opacity:.70;">Neden önemli?</div>
                <div id="roleDetailImpact" style="margin-top:8px;font-size:15px;line-height:1.55;"></div>
              </div>

              <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:14px;">
                <div style="font-size:12px;text-transform:uppercase;letter-spacing:.12em;opacity:.70;">Önerilen aksiyonlar</div>
                <ul id="roleDetailActions" style="margin:10px 0 0 18px;padding:0;line-height:1.8;"></ul>
              </div>
            </div>

            <div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap;">
              <button id="rolePdfBtn" type="button" style="padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#f5c451;color:#081225;font-weight:800;cursor:pointer;">PDF</button>
              <button id="roleEmailBtn" type="button" style="padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#dbeafe;color:#081225;font-weight:800;cursor:pointer;">Email</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML("beforeend", html);

    const modal = document.getElementById("roleDetailModal");
    const closeBtn = document.getElementById("roleDetailClose");

    function closeModal() {
      modal.style.display = "none";
    }

    closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeModal();
    });

    document.getElementById("rolePdfBtn").addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      setTimeout(function () {
        window.print();
      }, 20);
    }, true);

    document.getElementById("roleEmailBtn").addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();

      const title = document.getElementById("roleDetailTitle")?.textContent || "Hospital Dashboard Detail";
      const body = [
        title,
        "",
        "Durum: " + (document.getElementById("roleDetailStatus")?.textContent || ""),
        "",
        "Özet:",
        (document.getElementById("roleDetailInsight")?.textContent || ""),
        "",
        "Etki:",
        (document.getElementById("roleDetailImpact")?.textContent || "")
      ].join("\n");

      setTimeout(function () {
        window.location.href = "mailto:?subject=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(body);
      }, 20);
    }, true);
  }

  const roleData = {
    CEO: {
      title: "CEO Signal",
      status: "Kurumsal görünürlük ve genel risk özeti",
      insight: "Bu kart, üst yönetim seviyesinde operasyonel risk, sürdürülebilirlik baskısı ve genel performans sinyalini tek bakışta gösterir.",
      impact: "CEO için mesele detay değil yön duygusudur. Kırmızıya dönüyorsa bu sadece teknik bir sorun değil; itibar, yönetim odağı ve yatırımcı algısı meselesidir.",
      actions: [
        "Board-level summary aç",
        "En yüksek risk sürücülerini incele",
        "Gerekirse CFO ve OPS tarafına aksiyon devret"
      ]
    },
    CFO: {
      title: "CFO Signal",
      status: "Maliyet, kayıp ve finansal baskı görünümü",
      insight: "Bu kart, enerji, atık, verimsizlik ve CO₂ kaynaklı finansal baskının özet sinyalidir.",
      impact: "CFO için soru nettir: Bu durum bana neye patlıyor? Kartın amacı teknik veriyi maliyet hissine çevirmektir.",
      actions: [
        "PDF özet oluştur",
        "Email summary paylaş",
        "En yüksek maliyet sürücülerini aç"
      ]
    },
    OPS: {
      title: "OPS Signal",
      status: "Saha operasyonu ve anlık yürütme görünümü",
      insight: "Bu kart, günlük akış, darboğazlar, sapmalar ve saha aksiyon ihtiyacını özetler.",
      impact: "Ops tarafında küçük gecikme bile zincirleme kayıp üretir. Bu yüzden sinyal hızlı ve uygulanabilir olmalıdır.",
      actions: [
        "Operasyonel levers alanını aç",
        "Kritik darboğazı tespit et",
        "Vardiya / kaynak aksiyonu belirle"
      ]
    }
  };

  function inferRole(card) {
    const explicitRole = card.getAttribute("data-role");
    if (explicitRole) return explicitRole;

    const txt = (card.innerText || "").toUpperCase();

    if (txt.includes("CFO")) return "CFO";
    if (txt.includes("CEO")) return "CEO";
    if (txt.includes("CTO") || txt.includes("VTO")) return "OPS";
    if (txt.includes("BAŞHEKİM") || txt.includes("BASHEKIM")) return "OPS";
    if (txt.includes("HASTANE MÜDÜRÜ") || txt.includes("HASTANE MUDURU") || txt.includes("MÜDÜR") || txt.includes("MUDUR")) return "OPS";

    return null;
  }

  function seedRoleDataAttributes() {
    const cards = Array.from(document.querySelectorAll(".executive-card, .persona-card, .signal-card, .card"));
    cards.forEach(function(card) {
      const txt = (card.innerText || "").toUpperCase();
      if (card.getAttribute("data-role")) return;

      if (txt.includes("CEO")) card.setAttribute("data-role", "CEO");
      else if (txt.includes("CFO")) card.setAttribute("data-role", "CFO");
      else if (txt.includes("CTO") || txt.includes("VTO")) card.setAttribute("data-role", "OPS");
      else if (txt.includes("BAŞHEKİM") || txt.includes("BASHEKIM")) card.setAttribute("data-role", "OPS");
      else if (txt.includes("HASTANE MÜDÜRÜ") || txt.includes("HASTANE MUDURU") || txt.includes("MÜDÜR") || txt.includes("MUDUR")) card.setAttribute("data-role", "OPS");
    });
  }

  function openRoleModal(role) {
    ensureModal();
    const d = roleData[role];
    if (!d) return;

    document.getElementById("roleDetailTitle").textContent = d.title;
    document.getElementById("roleDetailStatus").textContent = d.status;
    document.getElementById("roleDetailInsight").textContent = d.insight;
    document.getElementById("roleDetailImpact").textContent = d.impact;

    /* CFO_EURO_BLOCK */
    if (role === "CFO") {
      const euroBox = document.createElement("div");
      euroBox.style.marginTop = "12px";
      euroBox.style.padding = "12px";
      euroBox.style.background = "rgba(255,255,255,.06)";
      euroBox.style.borderRadius = "12px";
      euroBox.style.fontWeight = "600";
      euroBox.innerHTML = `
        <div style="font-size:14px;">💰 CO₂ Cost Exposure: <b>€1.2M / year</b></div>
        <div style="font-size:14px;">⚡ Energy Waste: <b>€320K</b></div>
        <div style="font-size:14px;">🚀 Optimization Potential: <b>€480K</b></div>
      `;
      document.getElementById("roleDetailImpact").appendChild(euroBox);
    }

    const ul = document.getElementById("roleDetailActions");
    ul.innerHTML = "";
    d.actions.forEach(function (item) {
      const li = document.createElement("li");
      li.textContent = item;
      ul.appendChild(li);
    });

    document.getElementById("roleDetailModal").style.display = "flex";
  }

  seedRoleDataAttributes();

  document.addEventListener("click", function (e) {
    if (e.target.closest("button, a, .action-btn, [data-action], input, select, textarea")) return;
    const card = e.target.closest(".executive-card, .persona-card, .signal-card");
    if (!card) return;
    const role = card.dataset.role || inferRole(card);
    if (!role) return;
    openRoleModal(role);
  });


})();

// ===== VISUAL POPUP TEMPLATES =====
function getIntakeHubTemplate(){
  return `
    <div style="padding:16px 14px 18px 14px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
        <div>
          <div style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#8fa3bf;font-weight:700;">Data Intake Command Layer</div>
          <h2 style="margin:6px 0 6px 0;font-size:24px;line-height:1.2;color:#ffffff;">Intake Hub</h2>
          <div style="font-size:14px;color:#b8c7db;max-width:760px;">
            Sistemin veri alabileceği kaynaklar, onboarding hazırlığı ve entegrasyon olgunluğu tek merkezde gösterilir.
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="padding:8px 12px;border-radius:999px;background:rgba(38,208,124,.14);color:#7ef0ac;font-size:12px;font-weight:700;">Multi-Source Ready</span>
          <span style="padding:8px 12px;border-radius:999px;background:rgba(245,196,81,.14);color:#f5c451;font-size:12px;font-weight:700;">ERP Optional</span>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px;">
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Connected Logic</div>
          <div style="font-size:20px;font-weight:800;color:#fff;margin-top:4px;">Hybrid Intake</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">ERP + manual + mobile kaynaklar</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Priority Mode</div>
          <div style="font-size:20px;font-weight:800;color:#7ef0ac;margin-top:4px;">Fast Onboarding</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">İlk veri 1. günde alınabilir</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Operational Fit</div>
          <div style="font-size:20px;font-weight:800;color:#fff;margin-top:4px;">Field Friendly</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">WhatsApp / email / QR ile uyumlu</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Executive Outcome</div>
          <div style="font-size:20px;font-weight:800;color:#f5c451;margin-top:4px;">Visible Data</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">Karar katmanına hızlı besleme</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1.15fr .85fr;gap:14px;align-items:start;">
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:18px;padding:16px;background:rgba(9,16,30,.82);">
          <div style="font-size:13px;font-weight:800;color:#f5c451;margin-bottom:12px;">Desteklenen Veri Kaynakları</div>
          <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;">
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">SAP / ERP</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Master data, tüketim, satın alma ve operasyon kayıtları.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">Email</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Excel, PDF, sayaç özetleri ve manuel rapor akışı.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">WhatsApp</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Fotoğraf, sayaç görüntüsü, saha bildirimi ve hızlı belge paylaşımı.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">QR Code</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Atık noktası, ekipman, bölüm ve vardiya bazlı hızlı giriş.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">Manual Form</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">İlk gün devreye alınabilen düşük sürtünmeli veri toplama yapısı.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">CSV / Excel Upload</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Toplu geçmiş veri aktarımı ve hızlı demo besleme kanalı.</div>
            </div>
          </div>
        </div>

        <div style="border:1px solid rgba(143,163,191,.18);border-radius:18px;padding:16px;background:rgba(9,16,30,.82);">
          <div style="font-size:13px;font-weight:800;color:#f5c451;margin-bottom:10px;">Integration Reading</div>
          <div style="display:grid;gap:10px;">
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">Best Case</div>
              <div style="font-size:16px;font-weight:800;color:#7ef0ac;">ERP Connected</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">Fallback Mode</div>
              <div style="font-size:16px;font-weight:800;color:#fff;">Email + Form + Upload</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">Field Capture</div>
              <div style="font-size:16px;font-weight:800;color:#fff;">WhatsApp + QR</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">Board Message</div>
              <div style="font-size:13px;color:#d7e1ef;line-height:1.5;">
                “Bu platform ERP varsa entegre olur; yoksa da sahadan veri toplamayı durdurmaz.”
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function getExecutiveReportsTemplate(){
  return `
    <div style="padding:16px 14px 18px 14px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
        <div>
          <div style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#8fa3bf;font-weight:700;">Decision Intelligence Layer</div>
          <h2 style="margin:6px 0 6px 0;font-size:24px;line-height:1.2;color:#ffffff;">Executive Reports Center</h2>
          <div style="font-size:14px;color:#b8c7db;max-width:760px;">
            Yönetici seviyesinde CO₂, maliyet etkisi, operasyonel risk ve aksiyon önceliklerini tek bakışta sunan demo merkezi.
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="padding:8px 12px;border-radius:999px;background:rgba(38,208,124,.14);color:#7ef0ac;font-size:12px;font-weight:700;">Board View</span>
          <span style="padding:8px 12px;border-radius:999px;background:rgba(245,196,81,.14);color:#f5c451;font-size:12px;font-weight:700;">CFO Lens</span>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:16px;">
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">CO₂ Exposure</div>
          <div style="font-size:22px;font-weight:800;color:#fff;margin-top:4px;">1,240 tCO₂e</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">Annualized demo estimate</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Cost Exposure</div>
          <div style="font-size:22px;font-weight:800;color:#f5c451;margin-top:4px;">€1.2M</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">Utilities + waste pressure</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Optimization Potential</div>
          <div style="font-size:22px;font-weight:800;color:#7ef0ac;margin-top:4px;">€480K</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">12-month efficiency window</div>
        </div>
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:16px;padding:14px;background:rgba(10,18,35,.72);">
          <div style="font-size:12px;color:#8fa3bf;">Executive Signal</div>
          <div style="font-size:22px;font-weight:800;color:#ff8b8b;margin-top:4px;">Action</div>
          <div style="font-size:12px;color:#9fb0c8;margin-top:6px;">Waste + energy intensity</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start;">
        <div style="border:1px solid rgba(143,163,191,.18);border-radius:18px;padding:16px;background:rgba(9,16,30,.82);">
          <div style="font-size:13px;font-weight:800;color:#f5c451;margin-bottom:12px;">Recommended Report Set</div>
          <div style="display:grid;gap:10px;">
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">CEO Board Summary</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">3-slide narrative: risk, visibility, action priority.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">CFO Cost Exposure Brief</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Utilities, waste burden, savings corridor, payback logic.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">Operations Risk Pulse</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Daily operational heatmap, alert zones, intervention priority.</div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-weight:700;color:#fff;">Sustainability Positioning</div>
              <div style="font-size:13px;color:#aebed3;margin-top:4px;">Institutional visibility and future reporting readiness.</div>
            </div>
          </div>
        </div>

        <div style="border:1px solid rgba(143,163,191,.18);border-radius:18px;padding:16px;background:rgba(9,16,30,.82);">
          <div style="font-size:13px;font-weight:800;color:#f5c451;margin-bottom:12px;">Executive Reading</div>
          <div style="display:grid;gap:10px;">
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">CFO View</div>
              <div style="font-size:13px;color:#d7e1ef;line-height:1.5;margin-top:4px;">
                Enerji, su ve atık kalemleri maliyet baskısını görünür hale getiriyor; ilk odak noktası hızlı geri dönüşlü operasyonel tasarruf.
              </div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">CEO View</div>
              <div style="font-size:13px;color:#d7e1ef;line-height:1.5;margin-top:4px;">
                Bu yapı sadece çevresel raporlama değil, kurumun veriye dayalı yönetim kabiliyetini ve yatırım hikâyesini güçlendirir.
              </div>
            </div>
            <div style="border-radius:14px;padding:12px;background:rgba(255,255,255,.03);">
              <div style="font-size:12px;color:#8fa3bf;">OPS View</div>
              <div style="font-size:13px;color:#d7e1ef;line-height:1.5;margin-top:4px;">
                Müdahale alanı nettir: tüketim yoğunluğu, tıbbi atık disiplini ve proses bazlı izleme standardı.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// ===== VISUAL POPUP HANDLER =====
function openVisualPopup(type){
  const modal = document.getElementById("modal");
  const content = document.getElementById("modalContent");
  const title = document.getElementById("modalTitle");

  if(!modal || !content || !title) return;

  if(type === "intake"){
    title.innerText = "Intake Hub";
    content.innerHTML = getIntakeHubTemplate();
  } else if(type === "reports"){
    title.innerText = "Executive Reports Center";
    content.innerHTML = getExecutiveReportsTemplate();
  } else {
    return;
  }

  modal.style.display = "block";
}



