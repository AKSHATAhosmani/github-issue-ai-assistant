const analyzeBtn = document.getElementById('analyzeBtn');
const repoInput = document.getElementById('repoUrl');
const issueInput = document.getElementById('issueNumber');
const resultSection = document.getElementById('result');
const jsonOutput = document.getElementById('jsonOutput');
const copyBtn = document.getElementById('copyBtn');
const statusEl = document.getElementById('status');

analyzeBtn.addEventListener('click', async () => {
  const repoUrl = repoInput.value.trim();
  const issueNumber = Number(issueInput.value);

  if (!repoUrl || !issueNumber) {
    statusEl.textContent = 'Please enter both repository URL and issue number.';
    return;
  }

  statusEl.textContent = 'Analyzing issue...';
  analyzeBtn.disabled = true;

  try {
    const resp = await fetch('http://localhost:8000/analyze_issue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        repo_url: repoUrl,
        issue_number: issueNumber
      })
    });

    if (!resp.ok) {
      let err;
      try {
        err = await resp.json();
      } catch {
        err = { detail: 'Unknown error from backend' };
      }
      statusEl.textContent = 'Error: ' + (err.detail || JSON.stringify(err));
      alert(statusEl.textContent);

      analyzeBtn.disabled = false;
      return;
    }

    const data = await resp.json();
    jsonOutput.textContent = JSON.stringify(data, null, 2);
    resultSection.classList.remove('hidden');
    statusEl.textContent = 'Done. Review the analysis below.';
  } catch (e) {
    statusEl.textContent = 'Network error: ' + e.message;
    alert(statusEl.textContent);

  }

  analyzeBtn.disabled = false;
});

copyBtn.addEventListener('click', () => {
  if (!jsonOutput.textContent.trim()) {
    statusEl.textContent = 'Nothing to copy.';
    return;
  }
  navigator.clipboard.writeText(jsonOutput.textContent);
  statusEl.textContent = 'JSON copied to clipboard.';
});
