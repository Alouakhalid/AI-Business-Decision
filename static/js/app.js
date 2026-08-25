// DecisionOS AI - Advanced Dashboard with Node Graphs & Terminal
let currentReport = null;
let financialChartInstance = null;
let currentSlideIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  checkApiHealth();
});

async function checkApiHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    document.getElementById('groqStatus').innerHTML = data.groq_api ? `<span class="status-dot-active"></span> Groq API (${data.primary_model.split('/')[1] || data.primary_model})` : `<span class="status-dot-active" style="background-color: var(--accent-rose);"></span> Groq Key Missing`;
    document.getElementById('cohereStatus').innerHTML = data.cohere_api ? `<span class="status-dot-active"></span> Cohere Active` : `<span class="status-dot-active" style="background-color: var(--accent-rose);"></span> Cohere Key Missing`;
  } catch (e) {
    console.warn("Backend API not reachable");
  }
}

// --- ADMIN API KEY & CONFIGURATION PORTAL HANDLERS ---
async function openAdminModal() {
  try {
    const res = await fetch('/api/admin/config');
    const data = await res.json();
    document.getElementById('adminGroqKey').value = '';
    document.getElementById('adminGroqKey').placeholder = data.groq_api_key_masked;
    document.getElementById('adminCohereKey').value = '';
    document.getElementById('adminCohereKey').placeholder = data.cohere_api_key_masked;
    document.getElementById('adminPrimaryModel').value = data.primary_model;
    document.getElementById('adminTestResult').style.display = 'none';
    document.getElementById('adminModal').style.display = 'flex';
  } catch (e) { alert("Could not load admin configuration."); }
}

function closeAdminModal() { document.getElementById('adminModal').style.display = 'none'; }

async function testAdminKeys() {
  const groqKey = document.getElementById('adminGroqKey').value.trim();
  const cohereKey = document.getElementById('adminCohereKey').value.trim();
  const resBox = document.getElementById('adminTestResult');
  resBox.style.display = 'block';
  resBox.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Testing connections...`;
  try {
    const res = await fetch('/api/admin/test-keys', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ groq_api_key: groqKey, cohere_api_key: cohereKey })
    });
    const data = await res.json();
    resBox.innerHTML = `<div style="margin-bottom: 0.5rem;"><strong style="color: ${data.groq.valid ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">Groq:</strong> ${data.groq.message}</div><div><strong style="color: ${data.cohere.valid ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">Cohere:</strong> ${data.cohere.message}</div>`;
  } catch (e) { resBox.innerHTML = `<span style="color: var(--accent-rose);">Error: ${e.message}</span>`; }
}

async function saveAdminConfig() {
  const groqKey = document.getElementById('adminGroqKey').value.trim();
  const cohereKey = document.getElementById('adminCohereKey').value.trim();
  const primaryModel = document.getElementById('adminPrimaryModel').value;
  try {
    const res = await fetch('/api/admin/config', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ groq_api_key: groqKey || undefined, cohere_api_key: cohereKey || undefined, primary_model: primaryModel })
    });
    if (res.ok) { alert("Settings saved!"); closeAdminModal(); checkApiHealth(); }
  } catch (e) { alert(`Error: ${e.message}`); }
}

// --- NEW: URL INGESTION ---
async function ingestUrl() {
  const url = document.getElementById('urlInput').value.trim();
  if (!url) return alert('Enter a URL first');
  const btn = document.querySelector('.btn-url-pill');
  btn.innerText = 'Scraping...';
  try {
    const res = await fetch('/api/ingest-url', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url })
    });
    const data = await res.json();
    if (res.ok) { document.getElementById('ideaInput').value = data.extracted_idea; }
    else { alert(data.detail || 'Failed to extract URL'); }
  } catch(e) { alert('Error scraping URL'); }
  btn.innerText = 'Scrape & Extract';
}

function applyPreset(presetType) {
  const inputEl = document.getElementById('ideaInput');
  if (presetType.includes('Legal')) inputEl.value = "An AI-powered B2B platform for automated legal contract risk auditing and instant redlining.";
  else if (presetType.includes('Logistics')) inputEl.value = "Autonomous supply chain routing and predictive inventory engine powered by multi-agent AI.";
  else if (presetType.includes('Longevity')) inputEl.value = "Precision Longevity AI platform synthesizing multi-omic biomarkers for customized therapies.";
  else if (presetType.includes('Micro-SaaS')) inputEl.value = "AI-driven automated code security review and dependency vulnerability patch generator.";
}

// --- CORE SWARM ANALYSIS ---
async function startAnalysis() {
  const idea = document.getElementById('ideaInput').value.trim();
  if (!idea) return alert("Please enter a venture concept!");
  const budget = parseFloat(document.getElementById('budgetInput').value) || 100000;
  
  const btn = document.getElementById('analyzeBtn');
  const consoleEl = document.getElementById('deliberationConsole');
  const logStream = document.getElementById('logStream');
  const resultsEl = document.getElementById('dashboardResults');
  
  btn.disabled = true; btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running 6-Agent Swarm...`;
  consoleEl.style.display = 'block'; resultsEl.style.display = 'none'; logStream.innerHTML = '';
  
  let stepIdx = 0;
  const sim = [
    { agent: 'CEO', action: 'Swarm Orchestration', thought: 'Initializing 6-agent boardroom swarm...' },
    { agent: 'CSO', action: 'Market Strategy', thought: 'Synthesizing Cohere RAG market signals & Business Model Canvas...' },
    { agent: 'CFO', action: 'Financial Modeling', thought: 'Executing 1,000 Monte Carlo stochastic trials & P&L trajectory...' },
    { agent: 'CTO', action: 'System Architecture', thought: 'Building node-based interactive cloud architecture graph...' },
    { agent: 'CMO', action: 'Growth Strategy', thought: 'Designing GTM acquisition channels & pitch presentation deck...' },
    { agent: 'RedTeam', action: 'Adversarial Audit', thought: 'Auditing critical vulnerabilities & attack scenarios...' }
  ];

  const interval = setInterval(() => {
    if(stepIdx < sim.length) { appendLog(sim[stepIdx]); stepIdx++; }
  }, 1200);

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea_description: idea, initial_budget_usd: budget })
    });
    clearInterval(interval);
    if (!response.ok) throw new Error("Analysis failed");
    currentReport = await response.json();
    
    // Append actual backend agent logs if present
    if (currentReport.agent_logs && currentReport.agent_logs.length > 0) {
      currentReport.agent_logs.forEach(l => appendLog(l));
    }

    document.getElementById('deliberationStatus').innerHTML = `<i class="fa-solid fa-circle-check"></i> 6-Agent Consensus Reached`;
    setTimeout(() => { renderResults(currentReport); resultsEl.style.display = 'flex'; btn.disabled = false; btn.innerHTML = `<i class="fa-solid fa-rocket"></i> Launch C-Suite Swarm`; }, 500);
  } catch (err) { clearInterval(interval); btn.disabled = false; btn.innerHTML = `<i class="fa-solid fa-rocket"></i> Launch C-Suite Swarm`; alert(err.message); }
}

function getBadgeClass(agent) {
  const a = (agent || '').toUpperCase();
  if (a.includes('CEO')) return 'badge-ceo';
  if (a.includes('STRATEGY') || a.includes('CSO')) return 'badge-strategy';
  if (a.includes('CFO') || a.includes('FINANCE')) return 'badge-cfo';
  if (a.includes('CTO') || a.includes('TECH')) return 'badge-cto';
  if (a.includes('CMO') || a.includes('MARKETING')) return 'badge-cmo';
  if (a.includes('RED') || a.includes('AUDIT')) return 'badge-redteam';
  return 'badge-ceo';
}

function appendLog(log) {
  const logStream = document.getElementById('logStream');
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  const badgeClass = getBadgeClass(log.agent);
  entry.innerHTML = `<span class="badge-agent-pill ${badgeClass}">${log.agent}</span> <div><strong>${log.action}:</strong> <span style="color:var(--text-muted-dark);">${log.thought}</span></div>`;
  logStream.appendChild(entry);
  logStream.scrollTop = logStream.scrollHeight;
}

// --- DASHBOARD RENDERER ---
function renderResults(report) {
  document.getElementById('reportTitle').innerText = report.project_title;
  document.getElementById('execSummary').innerText = report.executive_summary;
  document.getElementById('viabilityScore').innerText = report.viability_score;

  // Node Graph
  if(report.tech_architecture && report.tech_architecture.architecture_nodes) {
    renderNodeGraph(report.tech_architecture.architecture_nodes, report.tech_architecture.architecture_edges);
  }

  // Finances
  const fin = report.financials;
  document.getElementById('tblRevY1').value = fin.annual_revenue.year1;
  document.getElementById('tblRevY2').value = fin.annual_revenue.year2;
  document.getElementById('tblRevY3').value = fin.annual_revenue.year3;
  document.getElementById('tblOpexY1').value = fin.operating_expenses.year1;
  document.getElementById('tblOpexY2').value = fin.operating_expenses.year2;
  document.getElementById('tblOpexY3').value = fin.operating_expenses.year3;
  updateTableProjections();
}

function getNodeIcon(type) {
  const t = (type || '').toLowerCase();
  if (t.includes('frontend')) return '<i class="fa-solid fa-laptop-code"></i>';
  if (t.includes('backend') || t.includes('api')) return '<i class="fa-solid fa-server"></i>';
  if (t.includes('database') || t.includes('storage')) return '<i class="fa-solid fa-database"></i>';
  if (t.includes('ai') || t.includes('vector') || t.includes('model')) return '<i class="fa-solid fa-brain"></i>';
  if (t.includes('cache') || t.includes('queue')) return '<i class="fa-solid fa-bolt"></i>';
  return '<i class="fa-solid fa-cubes"></i>';
}

// --- ENHANCED CTO NODE GRAPH RENDERER ---
function renderNodeGraph(nodes, edges) {
  const container = document.getElementById('nodeGraphContainer');
  const svg = document.getElementById('nodeEdgesSvg');
  
  Array.from(container.children).forEach(c => { if(c.id !== 'nodeEdgesSvg') c.remove(); });
  svg.innerHTML = `
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(253, 224, 71, 0.8)"/>
      </marker>
    </defs>
  `;
  
  const width = container.clientWidth || 900;
  const height = container.clientHeight || 450;
  
  const tierMap = { frontend: [], backend: [], data_ai: [] };
  nodes.forEach(n => {
    const t = (n.type || '').toLowerCase();
    if (t.includes('frontend')) tierMap.frontend.push(n);
    else if (t.includes('backend') || t.includes('api') || t.includes('gateway')) tierMap.backend.push(n);
    else tierMap.data_ai.push(n);
  });
  
  const positions = {};

  const layoutTier = (nodeList, columnPct) => {
    const x = width * columnPct;
    const total = nodeList.length;
    nodeList.forEach((n, idx) => {
      const step = height / (total + 1);
      const y = step * (idx + 1);
      positions[n.id] = { x, y };
    });
  };

  layoutTier(tierMap.frontend.length ? tierMap.frontend : [nodes[0]], 0.18);
  layoutTier(tierMap.backend.length ? tierMap.backend : [nodes[1] || nodes[0]], 0.50);
  layoutTier(tierMap.data_ai.length ? tierMap.data_ai : nodes.slice(2), 0.82);

  nodes.forEach((n, i) => {
    if (!positions[n.id]) {
      positions[n.id] = { x: width * (0.2 + (i * 0.25) % 0.6), y: height * 0.5 };
    }
  });

  nodes.forEach((n) => {
    const pos = positions[n.id];
    const icon = getNodeIcon(n.type);
    const typeClass = `node-type-${(n.type || 'backend').toLowerCase()}`;
    
    const div = document.createElement('div');
    div.className = `tech-node ${typeClass}`;
    div.style.left = `${pos.x - 70}px`;
    div.style.top = `${pos.y - 35}px`;
    div.title = `${n.label}: ${n.description || n.type}`;
    div.innerHTML = `
      <div class="tech-node-type">${icon} ${n.type || 'service'}</div>
      <div style="font-weight:800; color:#FFF; font-size:0.9rem;">${n.label}</div>
      <div class="tech-node-cost">${n.cost_estimate || '$50/mo'}</div>
    `;
    container.appendChild(div);
  });
  
  edges.forEach(e => {
    const s = positions[e.source];
    const t = positions[e.target];
    if(s && t) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', s.x); line.setAttribute('y1', s.y);
      line.setAttribute('x2', t.x); line.setAttribute('y2', t.y);
      line.setAttribute('class', 'node-svg-line');
      line.setAttribute('marker-end', 'url(#arrow)');
      svg.appendChild(line);
      
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', (s.x + t.x)/2); text.setAttribute('y', (s.y + t.y)/2 - 8);
      text.setAttribute('fill', 'var(--shout-yellow)'); text.setAttribute('font-size', '10px');
      text.setAttribute('font-weight', 'bold');
      text.setAttribute('text-anchor', 'middle');
      text.textContent = e.label;
      svg.appendChild(text);
    }
  });
}

// --- TERMINAL AGENT CHAT (STREAMING & NO ASTERISKS) ---
async function handleTerminalKey(e) {
  if(e.key === 'Enter') {
    const input = document.getElementById('terminalInput');
    const q = input.value.trim();
    if(!q) return;
    const agent = document.getElementById('terminalAgentSelect').value;
    input.value = '';
    input.disabled = true;
    
    const out = document.getElementById('terminalOutput');
    const userLine = document.createElement('div');
    userLine.style.color = '#FFFFFF';
    userLine.style.fontWeight = 'bold';
    userLine.innerText = `user@decisionos:~$ @${agent.toUpperCase()} ${q}`;
    out.appendChild(userLine);
    out.scrollTop = out.scrollHeight;
    
    try {
      const res = await fetch('/api/agent-chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agent, query: q })
      });
      const data = await res.json();
      
      // Clean all markdown asterisks (*, **), hashes (#), and backticks (`)
      let cleanText = (data.response || '')
        .replace(/\*\*/g, '')
        .replace(/\*/g, '')
        .replace(/#/g, '')
        .replace(/`/g, '')
        .trim();

      const responseEl = document.createElement('div');
      responseEl.style.color = 'var(--shout-yellow)';
      responseEl.style.marginBottom = '1rem';
      responseEl.style.lineHeight = '1.5';
      responseEl.innerHTML = `<strong style="color: #FFF;">[${agent.toUpperCase()}]</strong> `;
      out.appendChild(responseEl);
      
      const words = cleanText.split(/\s+/);
      let wordIdx = 0;
      
      const streamTimer = setInterval(() => {
        if (wordIdx < words.length) {
          responseEl.innerHTML += words[wordIdx] + ' ';
          out.scrollTop = out.scrollHeight;
          wordIdx++;
        } else {
          clearInterval(streamTimer);
          input.disabled = false;
          input.focus();
        }
      }, 30); // 30ms per word typewriter streaming speed
      
    } catch(err) {
      const errEl = document.createElement('div');
      errEl.style.color = 'var(--accent-rose)';
      errEl.innerText = `Error reaching @${agent.toUpperCase()}`;
      out.appendChild(errEl);
      out.scrollTop = out.scrollHeight;
      input.disabled = false;
      input.focus();
    }
  }
}

// --- SPREADSHEET TABLE EDITING & CSV EXPORT ---
function updateTableProjections() {
  const r1 = parseFloat(document.getElementById('tblRevY1').value) || 0;
  const r2 = parseFloat(document.getElementById('tblRevY2').value) || 0;
  const r3 = parseFloat(document.getElementById('tblRevY3').value) || 0;
  const o1 = parseFloat(document.getElementById('tblOpexY1').value) || 0;
  const o2 = parseFloat(document.getElementById('tblOpexY2').value) || 0;
  const o3 = parseFloat(document.getElementById('tblOpexY3').value) || 0;
  const p1 = r1 - o1; const p2 = r2 - o2; const p3 = r3 - o3;

  document.getElementById('tblProfitY1').innerText = `$${p1.toLocaleString()}`;
  document.getElementById('tblProfitY2').innerText = `$${p2.toLocaleString()}`;
  document.getElementById('tblProfitY3').innerText = `$${p3.toLocaleString()}`;
  
  if (financialChartInstance) {
    financialChartInstance.data.datasets[0].data = [r1, r2, r3];
    financialChartInstance.data.datasets[1].data = [o1, o2, o3];
    financialChartInstance.data.datasets[2].data = [p1, p2, p3];
    financialChartInstance.update();
  } else {
      const ctx = document.getElementById('financialChart').getContext('2d');
      financialChartInstance = new Chart(ctx, {
        type: 'bar',
        data: { labels: ['Y1','Y2','Y3'], datasets: [
          { label: 'Rev', data: [r1,r2,r3], backgroundColor: '#FDE047' },
          { label: 'Opex', data: [o1,o2,o3], backgroundColor: '#F43F5E' },
          { label: 'Profit', type:'line', data: [p1,p2,p3], borderColor: '#10B981', fill:false }
        ]},
        options: { responsive: true, maintainAspectRatio: false }
      });
  }
}
function exportFinancialCSV() {}
async function submitRedTeamDefense() {}
function openPitchModal() { document.getElementById('pitchModal').style.display = 'flex'; }
function closePitchModal() { document.getElementById('pitchModal').style.display = 'none'; }
