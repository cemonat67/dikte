(function () {
  function $(sel) {
    return document.querySelector(sel);
  }

  function findFileInput() {
    return document.querySelector('input[type="file"]');
  }

  function findPrepareButton() {
    return Array.from(document.querySelectorAll('button')).find(
      btn => /prepare upload/i.test(btn.textContent || "")
    );
  }

  function ensureStatusBox() {
    let box = document.getElementById("uploadStatusBox");
    if (!box) {
      box = document.createElement("div");
      box.id = "uploadStatusBox";
      box.style.marginTop = "12px";
      box.style.fontSize = "14px";
      box.style.color = "#cfd8ea";
      const wrap =
        findPrepareButton()?.parentElement ||
        document.querySelector(".card") ||
        document.body;
      wrap.appendChild(box);
    }
    return box;
  }

  function setStatus(msg, isError) {
    const box = ensureStatusBox();
    box.textContent = msg;
    box.style.color = isError ? "#ff8a8a" : "#cfd8ea";
    console.log("[upload-binding]", msg);
  }

  async function handlePrepareUpload() {
    const btn = findPrepareButton();
    if (btn) btn.disabled = true;

    try {
      const input = findFileInput();
      if (!input) {
        setStatus("File input bulunamadı.", true);
        return;
      }

      if (!input.files || !input.files.length) {
        setStatus("Önce bir CSV dosyası seç.", true);
        return;
      }

      const file = input.files[0];
      setStatus(`Seçilen dosya hazır: ${file.name}`);

      if (!window.ZeroIntakeConfig || !window.ZeroIntakeConfig.preflightUrl || !window.ZeroIntakeConfig.commitUrl) {
        setStatus("Upload config bulunamadı.", true);
        return;
      }

      const preflightUrl = window.ZeroIntakeConfig.preflightUrl();
      const commitUrl = window.ZeroIntakeConfig.commitUrl();

      const formData = new FormData();
      formData.append("file", file);

      setStatus(`Preflight kontrolü yapılıyor: ${file.name}`);

      const preflight = await fetch(preflightUrl, {
        method: "POST",
        body: formData
      });

      const preflightData = await preflight.json();

      if (!preflight.ok) {
        setStatus(`Preflight hata döndürdü (${preflight.status}).`, true);
        console.warn("[upload-binding] preflight error:", preflightData);
        return;
      }

      console.log("[upload-binding] preflight:", preflightData);

      setStatus(`Commit gönderiliyor: ${file.name}`);

      const commitForm = new FormData();
      commitForm.append("file", file);
      commitForm.append("zero_fill_missing", "true");

      const commit = await fetch(commitUrl, {
        method: "POST",
        body: commitForm
      });

      const commitData = await commit.json();

      if (!commit.ok) {
        setStatus(`Commit hata döndürdü (${commit.status}).`, true);
        console.warn("[upload-binding] commit error:", commitData);
        return;
      }

      console.log("[upload-binding] commit:", commitData);

      const inserted = Number(commitData.inserted || 0);
      const duplicate = Number(commitData.duplicate || 0);
      const rejected = Number(commitData.rejected || 0);

      if (inserted > 0 && duplicate === 0) {
        setStatus(`Upload başarılı — inserted=${inserted}, duplicate=${duplicate}, rejected=${rejected}`);
      } else if (inserted > 0 && duplicate > 0) {
        setStatus(`Upload tamamlandı — inserted=${inserted}, duplicate skipped=${duplicate}, rejected=${rejected}`);
      } else if (inserted === 0 && duplicate > 0) {
        setStatus(`Upload tamamlandı — yeni kayıt yok, duplicate skipped=${duplicate}, rejected=${rejected}`);
      } else {
        setStatus(`Upload tamamlandı — inserted=${inserted}, duplicate=${duplicate}, rejected=${rejected}`);
      }

      if (typeof window.loadOpsFromApi === "function") {
        try {
          await window.loadOpsFromApi();
          console.log("[upload-binding] dashboard refreshed");
        } catch (e) {
          console.warn("[upload-binding] loadOpsFromApi rerun failed", e);
        }
      }
    } catch (err) {
      setStatus("Upload binding aktif, ama backend upload endpoint henüz bağlı değil.", true);
      console.warn("[upload-binding] fetch failed", err);
    } finally {
      const btn = findPrepareButton();
      if (btn) btn.disabled = false;
    }
  }

  function init() {
    const btn = findPrepareButton();
    if (!btn) {
      console.warn("[upload-binding] Prepare Upload button not found");
      return;
    }

    btn.addEventListener("click", handlePrepareUpload);
    console.log("[upload-binding] active");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
