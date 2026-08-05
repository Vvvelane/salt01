export function renderTable(rows, columns, empty = 'No data') {
  if (!rows?.length) return `<p class="muted">${empty}</p>`;
  return `<div class="table-wrap"><table><thead><tr>${columns.map(([key, label]) => `<th scope="col">${label}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${columns.map(([key]) => `<td>${row[key] ?? '—'}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

