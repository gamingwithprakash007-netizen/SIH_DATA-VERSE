// DATA VERSE - Client Application Controller
const API_BASE = '';

let currentDocument = null;
let currentSignaturePkg = null;
let latestVerificationResult = null;

// Built-in Demo Fictional Document Text
const SAMPLE_DOC_TEXT = 
  "FEDERAL CYBERSECURITY AND QUANTUM READINESS GUIDELINE v4.2\n" +
  "Author: National Infrastructure Security Council\n" +
  "Classification: UNCLASSIFIED / RESEARCH REFERENCE PROTOTYPE\n\n" +
  "1. OBJECTIVE: Enhance post-quantum resilient identity mechanisms.\n" +
  "2. SCOPE: Digital document fingerprints, Bell states, and teleportation telemetry.\n" +
  "3. DIRECTIVE: Mandate continuous audit logging and statistical threat scoring.\n" +
  "Document Verification Fingerprint Seed: 0x9F41C2E09B74A82B\n";

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadSystemStatus();
  loadHistory();
  loadSampleDocument();
});

// Tab Switcher
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      const target = document.getElementById(tabId);
      if (target) target.classList.add('active');
    });
  });
}

// System Status & Metrics
async function loadSystemStatus() {
  try {
    const res = await fetch('/system/status');
    const data = await res.json();
    document.getElementById('sys-status-badge').innerText = data.status;
  } catch (e) {
    console.warn('System status poll error:', e);
  }
}

// Load default sample document into memory
async function loadSampleDocument() {
  const blob = new Blob([SAMPLE_DOC_TEXT], { type: 'text/plain' });
  const file = new File([blob], 'Government_Digital_Guideline.pdf', { type: 'application/pdf' });
  await uploadFile(file);
}

// File Upload Handler
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const statusEl = document.getElementById('upload-status');
  if (statusEl) statusEl.innerText = 'Calculating SHA-256 and SHA3 fingerprints...';

  try {
    const res = await fetch('/documents/upload', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error(await res.text());
    currentDocument = await res.json();
    
    // Update UI elements
    document.getElementById('doc-id-display').innerText = currentDocument.document_id;
    document.getElementById('doc-filename-display').innerText = currentDocument.filename;
    document.getElementById('doc-sha256-display').innerText = currentDocument.sha256;
    document.getElementById('doc-sha3-display').innerText = currentDocument.sha3_256;
    if (statusEl) statusEl.innerText = 'Fingerprinting complete. Ready to sign.';
  } catch (err) {
    if (statusEl) statusEl.innerText = 'Upload failed: ' + err.message;
  }
}

// Handle Manual File Input
async function handleManualUpload(event) {
  const file = event.target.files[0];
  if (file) await uploadFile(file);
}

// Sign Document (Classical + Quantum Baseline)
async function signCurrentDocument() {
  if (!currentDocument) {
    alert('Please upload or select a document first.');
    return;
  }
  const statusEl = document.getElementById('sign-status');
  statusEl.innerText = 'Generating ECDSA keypair, Bell states, and QDS package...';

  try {
    const res = await fetch('/sign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_id: currentDocument.document_id,
        shots: 1024
      })
    });
    if (!res.ok) throw new Error(await res.text());
    currentSignaturePkg = await res.json();
    
    document.getElementById('sig-session-display').innerText = currentSignaturePkg.session_id;
    document.getElementById('sig-nonce-display').innerText = currentSignaturePkg.nonce;
    document.getElementById('sig-b64-display').innerText = 'SEALED IN PDF (ECDSA SECP256R1 Active)';
    statusEl.innerText = 'Document signed successfully with Quantum verification metadata.';
    
    document.getElementById('btn-verify').disabled = false;
  } catch (err) {
    statusEl.innerText = 'Signing error: ' + err.message;
  }
}

// Run Multi-Layer Verification Pipeline
async function verifyCurrentDocument() {
  if (!currentDocument || !currentSignaturePkg) {
    alert('Sign the document first before running verification.');
    return;
  }
  const statusEl = document.getElementById('verify-status');
  statusEl.innerText = 'Executing 18-step verification pipeline on Virtual Quantum Computer...';

  try {
    const res = await fetch('/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_id: currentDocument.document_id,
        signature_package: currentSignaturePkg,
        check_replay: false
      })
    });
    if (!res.ok) throw new Error(await res.text());
    latestVerificationResult = await res.json();
    renderVerificationResult(latestVerificationResult);
    loadHistory();
  } catch (err) {
    statusEl.innerText = 'Verification failed: ' + err.message;
  }
}

// Render Results to UI
function renderVerificationResult(r) {
  const threatScore = r.threat_evaluation.threat_score;
  const classification = r.final_classification;
  
  const badgeEl = document.getElementById('result-badge');
  badgeEl.className = 'badge ' + (classification === 'SAFE' ? 'badge-safe' : (classification === 'SUSPICIOUS' ? 'badge-suspicious' : 'badge-attack'));
  badgeEl.innerText = classification + ' (' + threatScore + '/100)';
  
  const meterFill = document.getElementById('threat-meter-fill');
  meterFill.style.width = threatScore + '%';
  meterFill.style.background = classification === 'SAFE' ? '#10b981' : (classification === 'SUSPICIOUS' ? '#f59e0b' : '#ef4444');
  
  const factors = r.threat_evaluation.contributing_factors;
  document.getElementById('factor-doc').innerText = factors.document_integrity;
  document.getElementById('factor-sig').innerText = factors.signature_integrity;
  document.getElementById('factor-quantum').innerText = factors.quantum_measurement;
  document.getElementById('factor-session').innerText = factors.session_integrity;
  document.getElementById('factor-replay').innerText = factors.replay_detection;
  
  const reasonsList = document.getElementById('reasons-list');
  reasonsList.innerHTML = '';
  r.threat_evaluation.reasons.forEach(item => {
    const li = document.createElement('li');
    li.innerText = item;
    reasonsList.appendChild(li);
  });
  
  const q = r.quantum_verification;
  document.getElementById('quantum-metrics-raw').innerText = 
    `Bell State: ${q.bell_state}\n` +
    `Observed Correlation: ${q.observed_correlation} (Expected: ${q.expected_correlation})\n` +
    `Teleportation Fidelity: ${q.teleportation_fidelity}\n` +
    `Pauli Correction: ${q.pauli_correction}\n` +
    `Total Variation Distance (TVD): ${q.statistical_metrics.total_variation_distance}\n` +
    `Chi-Square: ${q.statistical_metrics.chi_square_stat} (p=${q.statistical_metrics.p_value})`;

  document.getElementById('verification-card-results').style.display = 'block';
  document.getElementById('verify-status').innerText = 'Verification complete.';
}

// Attack Simulation Lab Triggers
async function triggerAttack(type) {
  if (!currentDocument || !currentSignaturePkg) {
    await loadSampleDocument();
    await signCurrentDocument();
  }
  
  const statusEl = document.getElementById('attack-status');
  statusEl.innerText = `Simulating attack: ${type}...`;

  let url = '/attacks/tamper';
  let body = { document_id: currentDocument.document_id, signature_package: currentSignaturePkg };

  if (type === 'NORMAL') {
    return verifyCurrentDocument();
  } else if (type === 'DOCUMENT_TAMPERING') {
    url = '/attacks/tamper';
    body.tamper_offset = 15;
  } else if (type === 'SIGNATURE_TAMPERING') {
    url = '/attacks/signature-tamper';
  } else if (type === 'FORGERY_SIMULATION') {
    url = '/attacks/forgery';
  } else if (type === 'REPLAY_ATTACK') {
    url = '/attacks/replay';
  } else if (type === 'QUANTUM_CHANNEL_NOISE') {
    url = '/attacks/noise';
    body.depolarizing_prob = 0.35;
  } else if (type === 'MEASUREMENT_MANIPULATION') {
    url = '/attacks/measurement-manipulation';
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    latestVerificationResult = data.verification_result;
    renderVerificationResult(latestVerificationResult);
    
    document.getElementById('attack-diff-view').innerText = JSON.stringify(data, null, 2);
    statusEl.innerText = `Attack [${type}] executed and analyzed.`;
    loadHistory();
  } catch (e) {
    statusEl.innerText = 'Attack execution error: ' + e.message;
  }
}

// Quantum Lab: Run Bell State
async function runBellState() {
  const state = document.getElementById('bell-select').value;
  const shots = parseInt(document.getElementById('bell-shots').value) || 1024;
  const out = document.getElementById('bell-output');
  out.innerText = 'Simulating Bell State on Virtual Quantum Computer...';

  try {
    const res = await fetch('/quantum/bell-state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_name: state, shots: shots })
    });
    const d = await res.json();
    out.innerText = 
      `Bell State: ${d.bell_state}\n` +
      `Observed Correlation <Z0 Z1>: ${d.observed_correlation}\n` +
      `Expected Correlation: ${d.expected_correlation}\n` +
      `Correlation Deviation: ${d.correlation_deviation}\n` +
      `Entangled: ${d.is_entangled ? 'YES (Confirmed)' : 'NO'}\n` +
      `Execution Time: ${d.execution_time_ms.toFixed(2)} ms\n\n` +
      `Measurement Histogram:\n` +
      JSON.stringify(d.counts, null, 2);
  } catch (e) {
    out.innerText = 'Error: ' + e.message;
  }
}

// Quantum Lab: Run Teleportation
async function runTeleportation() {
  const out = document.getElementById('teleport-output');
  out.innerText = 'Simulating 3-Qubit Teleportation & Pauli Correction...';

  try {
    const res = await fetch('/quantum/teleport', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alpha: 0.70710678, beta: 0.70710678 })
    });
    const d = await res.json();
    out.innerText = 
      `Input Qubit: |+> (α=0.7071, β=0.7071)\n` +
      `Alice Bell Measurement Bits: m0=${d.bell_measurement_bits.m0}, m1=${d.bell_measurement_bits.m1} (Outcome: ${d.bell_measurement_bits.bitstring})\n` +
      `Bob Pauli Correction Applied: ${d.pauli_correction_applied}\n` +
      `Reconstructed Qubit: α=${d.reconstructed_state.alpha}, β=${d.reconstructed_state.beta}\n` +
      `Quantum State Fidelity: ${d.quantum_fidelity} (1.0 = Exact Match)\n` +
      `Teleportation Status: ${d.teleportation_successful ? 'SUCCESS' : 'FAILURE'}\n` +
      `Execution Time: ${d.execution_time_ms.toFixed(2)} ms`;
  } catch (e) {
    out.innerText = 'Error: ' + e.message;
  }
}

// History Loader
async function loadHistory() {
  try {
    const res = await fetch('/history?limit=15');
    const items = await res.json();
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    let safeCount = 0, suspCount = 0, attackCount = 0;

    items.forEach(row => {
      if (row.classification === 'SAFE') safeCount++;
      else if (row.classification === 'SUSPICIOUS') suspCount++;
      else if (row.classification === 'ATTACK') attackCount++;

      const tr = document.createElement('tr');
      const clsBadge = `<span class="badge badge-${row.classification.toLowerCase()}">${row.classification}</span>`;
      tr.innerHTML = `
        <td><code>${row.verification_id}</code></td>
        <td>${row.timestamp.substring(11, 19)}</td>
        <td>${row.threat_score}</td>
        <td>${clsBadge}</td>
        <td>${row.attack_type}</td>
        <td>
          <a href="/reports/${row.verification_id}/pdf" target="_blank" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">PDF</a>
        </td>
      `;
      tbody.appendChild(tr);
    });

    if (document.getElementById('stat-total-verified')) {
      document.getElementById('stat-total-verified').innerText = items.length;
      document.getElementById('stat-safe').innerText = safeCount;
      document.getElementById('stat-suspicious').innerText = suspCount;
      document.getElementById('stat-attack').innerText = attackCount;
    }
  } catch (e) {
    console.warn('History load error:', e);
  }
}


// Download the generated QDS Signature Package as a .qds.json file
function downloadSignaturePackage() {
  if (!currentSignaturePkg) {
    alert('Please sign a document first before downloading the signature package.');
    return;
  }
  const filename = (currentSignaturePkg.filename || 'document') + '.qds.json';
  const blob = new Blob([JSON.stringify(currentSignaturePkg, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Independent Verifier (Bob Mode): Uploads document + signature package file
async function verifyIndependentFiles() {
  const docInput = document.getElementById('independent-doc-file');
  const statusEl = document.getElementById('independent-verify-status');

  if (!docInput.files[0]) {
    alert('Please select the signed PDF file to verify.');
    return;
  }

  statusEl.innerText = 'Extracting embedded Quantum Signature from PDF and running 18-step verification...';

  const formData = new FormData();
  formData.append('document', docInput.files[0]);

  try {
    const res = await fetch('/verify/independent', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const errText = await res.text();
      let msg = errText;
      try {
        const j = JSON.parse(errText);
        msg = j.detail || errText;
      } catch(e) {}
      throw new Error(msg);
    }
    latestVerificationResult = await res.json();
    renderVerificationResult(latestVerificationResult);
    loadHistory();
    statusEl.innerText = 'Single-file PDF verification complete (' + latestVerificationResult.final_classification + ').';
  } catch (err) {
    statusEl.innerText = 'Verification failed: ' + err.message;
    alert('Verification Error: ' + err.message);
  }
}


// Download the document as a clean PDF without any visible signature text
async function downloadCleanDocumentPdf() {
  if (!currentDocument || !currentDocument.document_id) {
    alert('Please upload or select a document first.');
    return;
  }
  const statusEl = document.getElementById('sign-status');
  if (statusEl) statusEl.innerText = 'Downloading clean document PDF...';

  try {
    const url = '/documents/' + currentDocument.document_id + '/pdf';
    const res = await fetch(url);
    if (!res.ok) {
      const errDetail = await res.text();
      throw new Error(`Server status ${res.status}: ${errDetail}`);
    }
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    const baseName = currentDocument.filename ? currentDocument.filename.replace(/\.[^/.]+$/, "") : "document";
    a.download = baseName + ".pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
    if (statusEl) statusEl.innerText = 'Document PDF downloaded successfully.';
  } catch (err) {
    console.error('Download error:', err);
    if (statusEl) statusEl.innerText = 'Download error: ' + err.message;
    alert('PDF Download Error: ' + err.message);
  }
}
