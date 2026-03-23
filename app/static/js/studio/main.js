import { $ } from "./dom.js";
import { ping } from "./api.js";
import { wireFileDropzone } from "./files.js";
import {
  applySelectedAgent,
  ask,
  createAgent,
  refreshAgents,
  saveAgentConfig,
  setResult,
} from "./agents.js";

function init() {
  $("baseUrl").textContent = window.location.origin;

  $("btnOpenDocs").addEventListener("click", () => {
    window.open("/docs", "_blank", "noopener,noreferrer");
  });

  $("btnRefreshAgents").addEventListener("click", async () => {
    try {
      await refreshAgents();
    } catch (e) {
      alert(String(e.message || e));
    }
  });

  $("agentsSelect").addEventListener("change", applySelectedAgent);

  $("btnCopyAgentKey").addEventListener("click", async () => {
    const k = /** @type {HTMLInputElement} */ ($("selectedKey")).value.trim();
    if (!k) {
      alert("Selecione um agente para copiar a X-API-Key.");
      return;
    }
    try {
      await navigator.clipboard.writeText(k);
      const btn = /** @type {HTMLButtonElement} */ ($("btnCopyAgentKey"));
      const prev = btn.textContent;
      btn.textContent = "Copiado!";
      setTimeout(() => {
        btn.textContent = prev;
      }, 1500);
    } catch (e) {
      alert(String(e.message || e));
    }
  });

  $("btnCreate").addEventListener("click", async () => {
    try {
      const agent = await createAgent();
      alert(`Agente criado!\n\nid=${agent.id}\nslug=${agent.slug}\napi_key=${agent.api_key}`);
    } catch (e) {
      alert(String(e.message || e));
    }
  });

  $("btnSaveAgentConfig").addEventListener("click", async () => {
    try {
      await saveAgentConfig();
      alert("Configuração do agente salva.");
    } catch (e) {
      alert(String(e.message || e));
    }
  });

  $("btnAsk").addEventListener("click", async () => {
    try {
      setResult($("answer"), "Carregando...");
      setResult($("sources"), "");
      await ask();
    } catch (e) {
      setResult($("answer"), String(e.message || e), true);
      setResult($("sources"), "", false);
    }
  });

  wireFileDropzone();
}

init();

(async () => {
  await ping();
  try {
    await refreshAgents();
  } catch {
    // ignore
  }
})();
