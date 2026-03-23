import { $ } from "./dom.js";

/** @type {File[]} */
let stagedFiles = [];

function syncStagedFilesToInput() {
  const input = /** @type {HTMLInputElement} */ ($("agentFiles"));
  const dt = new DataTransfer();
  stagedFiles.forEach((f) => dt.items.add(f));
  input.files = dt.files;
}

function renderFileList() {
  const wrap = $("fileList");
  wrap.innerHTML = "";
  if (!stagedFiles.length) {
    wrap.hidden = true;
    return;
  }
  wrap.hidden = false;
  stagedFiles.forEach((file, idx) => {
    const row = document.createElement("div");
    row.className = "fileChip";
    const nameEl = document.createElement("span");
    nameEl.className = "name";
    nameEl.title = file.name;
    nameEl.textContent = file.name;
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    const rm = document.createElement("button");
    rm.type = "button";
    rm.textContent = "Remover";
    rm.addEventListener("click", (e) => {
      e.stopPropagation();
      stagedFiles = stagedFiles.filter((_, i) => i !== idx);
      syncStagedFilesToInput();
      renderFileList();
    });
    row.appendChild(nameEl);
    row.appendChild(meta);
    row.appendChild(rm);
    wrap.appendChild(row);
  });
}

function addStagedFiles(fileList) {
  const allowed = [".pdf", ".txt"];
  for (const f of fileList) {
    const lower = f.name.toLowerCase();
    const ok = allowed.some((ext) => lower.endsWith(ext));
    if (!ok) continue;
    const dup = stagedFiles.some((x) => x.name === f.name && x.size === f.size);
    if (!dup) stagedFiles.push(f);
  }
  syncStagedFilesToInput();
  renderFileList();
}

export function wireFileDropzone() {
  const dz = $("fileDropzone");
  const input = /** @type {HTMLInputElement} */ ($("agentFiles"));
  dz.addEventListener("click", () => input.click());
  dz.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      input.click();
    }
  });
  input.addEventListener("change", () => {
    if (input.files?.length) addStagedFiles(input.files);
  });
  ["dragenter", "dragover"].forEach((ev) => {
    dz.addEventListener(ev, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dz.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach((ev) => {
    dz.addEventListener(ev, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dz.classList.remove("dragover");
    });
  });
  dz.addEventListener("drop", (e) => {
    const fl = e.dataTransfer?.files;
    if (fl?.length) addStagedFiles(fl);
  });
}

export function resetStagedFiles() {
  stagedFiles = [];
  syncStagedFilesToInput();
  renderFileList();
}

export function getAgentFileInput() {
  return /** @type {HTMLInputElement} */ ($("agentFiles"));
}
