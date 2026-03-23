import { $ } from "./dom.js";
import { request } from "./api.js";
import { getAgentFileInput, resetStagedFiles } from "./files.js";

export function setResult(el, value, isError = false) {
  el.textContent = value ?? "";
  el.classList.toggle("error", Boolean(isError));
}

function clearPlaygroundInference() {
  /** @type {HTMLInputElement} */ ($("pgTemp")).value = "0.7";
  /** @type {HTMLInputElement} */ ($("pgTopP")).value = "1";
  /** @type {HTMLInputElement} */ ($("pgMaxTok")).value = "";
  /** @type {HTMLInputElement} */ ($("pgRagK")).value = "5";
}

export async function refreshAgents(selectAgentId = null) {
  const select = /** @type {HTMLSelectElement} */ ($("agentsSelect"));
  select.innerHTML = "";

  const agents = await request("/agents");
  if (!Array.isArray(agents) || agents.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "Nenhum agente encontrado";
    select.appendChild(opt);
    /** @type {HTMLInputElement} */ ($("selectedSlug")).value = "";
    /** @type {HTMLInputElement} */ ($("selectedKey")).value = "";
    /** @type {HTMLInputElement} */ ($("selectedModel")).value = "";
    /** @type {HTMLInputElement} */ ($("selectedName")).value = "";
    clearPlaygroundInference();
    return;
  }

  for (const a of agents) {
    const opt = document.createElement("option");
    opt.value = String(a.id);
    opt.textContent = `#${a.id} • ${a.name} • ${a.slug} • ${a.model || "?"}`;
    opt.dataset.slug = a.slug;
    opt.dataset.key = a.api_key;
    opt.dataset.model = a.model || "";
    opt.dataset.name = a.name || "";
    opt.dataset.temperature = String(a.temperature ?? 0.7);
    opt.dataset.topP = String(a.top_p ?? 1);
    opt.dataset.ragTopK = String(a.rag_top_k ?? 5);
    opt.dataset.maxTokens = a.max_tokens != null && a.max_tokens !== undefined ? String(a.max_tokens) : "";
    select.appendChild(opt);
  }

  if (selectAgentId) {
    const idx = agents.findIndex((x) => String(x.id) === String(selectAgentId));
    if (idx >= 0) select.selectedIndex = idx;
  }

  applySelectedAgent();
}

export function applySelectedAgent() {
  const select = /** @type {HTMLSelectElement} */ ($("agentsSelect"));
  const opt = select.selectedOptions?.[0];
  if (!opt?.dataset?.slug) {
    clearPlaygroundInference();
    return;
  }
  /** @type {HTMLInputElement} */ ($("selectedSlug")).value = opt.dataset.slug || "";
  /** @type {HTMLInputElement} */ ($("selectedKey")).value = opt.dataset.key || "";
  /** @type {HTMLInputElement} */ ($("selectedModel")).value = opt.dataset.model || "";
  /** @type {HTMLInputElement} */ ($("selectedName")).value = opt.dataset.name || "";
  /** @type {HTMLInputElement} */ ($("pgTemp")).value = opt.dataset.temperature || "0.7";
  /** @type {HTMLInputElement} */ ($("pgTopP")).value = opt.dataset.topP || "1";
  /** @type {HTMLInputElement} */ ($("pgRagK")).value = opt.dataset.ragTopK || "5";
  /** @type {HTMLInputElement} */ ($("pgMaxTok")).value = opt.dataset.maxTokens || "";
}

function readCreateInferencePayload() {
  const temperature = Number(/** @type {HTMLInputElement} */ ($("createTemp")).value);
  const top_p = Number(/** @type {HTMLInputElement} */ ($("createTopP")).value);
  const rag_top_k = Number(/** @type {HTMLInputElement} */ ($("createRagK")).value);
  const mt = /** @type {HTMLInputElement} */ ($("createMaxTok")).value.trim();
  const max_tokens = mt === "" ? null : Number(mt);
  if (Number.isNaN(temperature) || Number.isNaN(top_p) || Number.isNaN(rag_top_k)) {
    throw new Error("Temperature, Top P e Chunks RAG precisam ser números válidos");
  }
  if (mt !== "" && Number.isNaN(max_tokens)) {
    throw new Error("Max tokens inválido");
  }
  return { temperature, top_p, rag_top_k, max_tokens };
}

export function readPlaygroundInferenceBody() {
  const temperature = Number(/** @type {HTMLInputElement} */ ($("pgTemp")).value);
  const top_p = Number(/** @type {HTMLInputElement} */ ($("pgTopP")).value);
  const rag_top_k = Number(/** @type {HTMLInputElement} */ ($("pgRagK")).value);
  const mt = /** @type {HTMLInputElement} */ ($("pgMaxTok")).value.trim();
  const max_tokens = mt === "" ? null : Number(mt);
  if (Number.isNaN(temperature) || Number.isNaN(top_p) || Number.isNaN(rag_top_k)) {
    throw new Error("Temperature, Top P e Chunks RAG precisam ser números válidos");
  }
  if (mt !== "" && Number.isNaN(max_tokens)) {
    throw new Error("Max tokens inválido");
  }
  return { temperature, top_p, rag_top_k, max_tokens };
}

export async function createAgent() {
  const name = /** @type {HTMLInputElement} */ ($("agentName")).value.trim();
  const prompt = /** @type {HTMLTextAreaElement} */ ($("agentPrompt")).value.trim();
  const slug = /** @type {HTMLInputElement} */ ($("agentSlug")).value.trim();
  const model = /** @type {HTMLSelectElement} */ ($("agentModel")).value;
  const inf = readCreateInferencePayload();

  if (!name) throw new Error("Nome do agente é obrigatório");

  const payload = {
    name,
    slug: slug || null,
    model: model || null,
    prompt: prompt || null,
    user_id: null,
    ...inf,
  };

  const agent = await request("/agents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const files = getAgentFileInput().files;
  if (files && files.length) {
    for (const f of files) {
      const form = new FormData();
      form.append("file", f, f.name);
      await request(`/agents/${agent.id}/documents`, { method: "POST", body: form });
    }
  }

  resetStagedFiles();
  await refreshAgents(agent.id);
  return agent;
}

export async function saveAgentConfig() {
  const select = /** @type {HTMLSelectElement} */ ($("agentsSelect"));
  const id = select.value;
  if (!id) throw new Error("Selecione um agente para salvar");

  const inf = readPlaygroundInferenceBody();
  const agent = await request(`/agents/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inf),
  });

  const opt = select.selectedOptions?.[0];
  if (opt) {
    opt.dataset.temperature = String(agent.temperature);
    opt.dataset.topP = String(agent.top_p);
    opt.dataset.ragTopK = String(agent.rag_top_k);
    opt.dataset.maxTokens = agent.max_tokens != null ? String(agent.max_tokens) : "";
  }
  applySelectedAgent();
  return agent;
}

export async function ask() {
  const slug = /** @type {HTMLInputElement} */ ($("selectedSlug")).value.trim();
  const key = /** @type {HTMLInputElement} */ ($("selectedKey")).value.trim();
  const question = /** @type {HTMLInputElement} */ ($("question")).value.trim();
  const inf = readPlaygroundInferenceBody();

  if (!slug) throw new Error("Selecione um agente");
  if (!key) throw new Error("X-API-Key não encontrado (crie/seleciona um agente)");
  if (!question) throw new Error("Escreva uma pergunta");

  const out = await request(`/public/agent/${encodeURIComponent(slug)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": key },
    body: JSON.stringify({ question, ...inf }),
  });

  setResult($("answer"), out.answer || "");
  setResult($("sources"), Array.isArray(out.sources) ? out.sources.join("\n") : "");
}
