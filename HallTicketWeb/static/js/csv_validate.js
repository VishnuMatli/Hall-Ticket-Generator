async function validateCsv(inputEl, type, resultElId) {
  const file = inputEl.files[0];
  const resultEl = document.getElementById(resultElId);
  if (!file) {
    if (resultEl) resultEl.innerHTML = '';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', type);

  resultEl.innerHTML = '<div class="small text-info">Validating...</div>';

  try {
    const res = await fetch('/validate-csv', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.error) {
      resultEl.innerHTML = '<div class="small text-danger">' + data.error + '</div>';
      return;
    }

    if (data.has_errors) {
      const firstErrors = data.errors.slice(0, 3)
        .map(e => 'Row ' + e.row + ': ' + e.errors.join(', '))
        .join('<br>');
      const more = data.errors.length > 3 ? '<br>...' : '';
      resultEl.innerHTML = '<div class="small text-danger">Found ' + data.errors.length + ' issue rows.<br>' + firstErrors + more + '</div>';
    } else {
      resultEl.innerHTML = '<div class="small text-success">All ' + data.total_rows + ' rows look valid.</div>';
    }
  } catch (err) {
    console.error(err);
    resultEl.innerHTML = '<div class="small text-danger">Validation failed.</div>';
  }
}
