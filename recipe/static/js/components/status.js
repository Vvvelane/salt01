export function statusBadge(status, label = status) {
  const safe = String(status || 'pending').replace(/[^a-z-]/g, '');
  return `<span class="badge ${safe}">${label}</span>`;
}

export function showMessage(message, status = 'pending') {
  return `<div class="message ${status}">${statusBadge(status)}<span>${message}</span></div>`;
}

