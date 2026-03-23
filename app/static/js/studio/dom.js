/** @param {string} id */
export function $(id) {
  const el = document.getElementById(id);
  if (!el) throw new Error(`#${id} não encontrado`);
  return el;
}
