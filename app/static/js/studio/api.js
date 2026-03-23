import { $ } from "./dom.js";

export async function request(path, opts = {}) {
  const res = await fetch(path, opts);
  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json() : await res.text();
  if (!res.ok) {
    const detail = typeof data === "string" ? data : data?.detail || JSON.stringify(data);
    throw new Error(`${res.status} ${res.statusText} • ${detail}`);
  }
  return data;
}

export function setApiStatus(ok) {
  $("apiDot").classList.toggle("bad", !ok);
  $("apiStatus").title = ok ? "API ok" : "API offline";
}

export async function ping() {
  try {
    await request("/health");
    setApiStatus(true);
  } catch {
    setApiStatus(false);
  }
}
