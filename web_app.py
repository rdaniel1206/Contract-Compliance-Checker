"""Zero-dependency Web UI and REST API for Contract Compliance Checker."""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main_agent import MainAgent
from core.observability import get_event_logs

agent = MainAgent()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Contract Compliance & Risk Auditor</title>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        header h1 { font-size: 2.2rem; font-weight: 700; color: #60a5fa; margin-bottom: 8px; }
        header p { color: var(--text-secondary); font-size: 1.1rem; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .card h2 { font-size: 1.3rem; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
        textarea {
            width: 100%;
            height: 280px;
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            padding: 12px;
            font-family: monospace;
            font-size: 0.95rem;
            resize: vertical;
        }
        .btn-group { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
        button, select {
            background: var(--accent-blue);
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        select { background: #334155; }
        button:hover { opacity: 0.9; }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: bold;
            font-size: 0.85rem;
        }
        .badge-low { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; }
        .badge-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #d97706; }
        .badge-high { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; }
        .badge-critical { background: rgba(220, 38, 38, 0.3); color: #fca5a5; border: 1px solid #b91c1c; }
        .metric-box {
            display: flex;
            justify-content: space-around;
            background: #0b1120;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            text-align: center;
        }
        .metric-item .val { font-size: 1.6rem; font-weight: bold; }
        .metric-item .lbl { font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; }
        .clause-card {
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .clause-card .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .clause-title { font-weight: 600; font-size: 1.05rem; }
        .red-flags { margin-top: 8px; padding-left: 20px; color: #f87171; font-size: 0.9rem; }
        .recommendation { margin-top: 6px; font-size: 0.88rem; color: #93c5fd; }
        pre { background: #000; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; color: #a5f3fc; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Contract Compliance & Risk Auditor</h1>
            <p>Autonomous Multi-Agent Legal Analysis (Planner - Worker - Evaluator)</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>Contract Ingestion</h2>
                <div style="margin-bottom: 12px; display: flex; gap: 8px; align-items: center;">
                    <label style="color: var(--text-secondary);">Load Sample:</label>
                    <select id="sampleSelect" onchange="loadSelectedSample()">
                        <option value="">-- Select Sample Contract --</option>
                        <option value="sample_nda_standard.txt">Standard NDA (Low/Medium Risk)</option>
                        <option value="sample_vendor_msa_risky.txt">High-Risk Vendor MSA (Critical Risk)</option>
                        <option value="sample_dpa_standard.txt">GDPR DPA Agreement</option>
                        <option value="sample_employment_agreement.txt">Employment Agreement</option>
                    </select>
                </div>
                <textarea id="contractText" placeholder="Paste contract terms or load a sample contract..."></textarea>
                <div class="btn-group">
                    <button onclick="analyzeContract()" id="btnAnalyze">Analyze Compliance</button>
                    <button onclick="document.getElementById('contractText').value=''" style="background:#475569;">Clear</button>
                </div>
            </div>

            <div class="card">
                <h2>Audit & Risk Results</h2>
                <div id="resultsPlaceholder" style="text-align:center; padding: 60px 20px; color: var(--text-secondary);">
                    Run an analysis to inspect contract type, risk scores, red flags, and recommendations.
                </div>
                <div id="resultsContent" style="display:none;">
                    <div class="metric-box">
                        <div class="metric-item">
                            <div class="val" id="metricType">-</div>
                            <div class="lbl">Contract Type</div>
                        </div>
                        <div class="metric-item">
                            <div class="val" id="metricRisk">-</div>
                            <div class="lbl">Risk Rating</div>
                        </div>
                        <div class="metric-item">
                            <div class="val" id="metricScore">-</div>
                            <div class="lbl">Risk Score</div>
                        </div>
                        <div class="metric-item">
                            <div class="val" id="metricFlags">-</div>
                            <div class="lbl">Red Flags</div>
                        </div>
                    </div>
                    <div id="clausesList" style="max-height: 480px; overflow-y: auto;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function loadSelectedSample() {
            const select = document.getElementById('sampleSelect');
            const file = select.value;
            if (!file) return;
            try {
                const res = await fetch('/api/samples?file=' + encodeURIComponent(file));
                const data = await res.json();
                if (data.content) {
                    document.getElementById('contractText').value = data.content;
                }
            } catch(e) {
                alert('Failed to load sample: ' + e);
            }
        }

        async function analyzeContract() {
            const text = document.getElementById('contractText').value.trim();
            if (!text) {
                alert('Please enter or paste contract text.');
                return;
            }
            const btn = document.getElementById('btnAnalyze');
            btn.innerText = 'Analyzing...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ contract_text: text })
                });
                const data = await res.json();
                renderResults(data);
            } catch(e) {
                alert('Analysis failed: ' + e);
            } finally {
                btn.innerText = 'Analyze Compliance';
                btn.disabled = false;
            }
        }

        function renderResults(data) {
            document.getElementById('resultsPlaceholder').style.display = 'none';
            const container = document.getElementById('resultsContent');
            container.style.display = 'block';

            document.getElementById('metricType').innerText = data.contract_type || 'GENERIC';
            const lvl = data.meta?.level || 'LOW';
            const score = data.meta?.score || 0;
            const flags = data.meta?.red_flags?.length || 0;

            const badgeClass = lvl === 'LOW' ? 'badge-low' : (lvl === 'MEDIUM' ? 'badge-medium' : (lvl === 'CRITICAL' ? 'badge-critical' : 'badge-high'));
            document.getElementById('metricRisk').innerHTML = `<span class="badge ${badgeClass}">${lvl}</span>`;
            document.getElementById('metricScore').innerText = `${score} / 1.0`;
            document.getElementById('metricFlags').innerText = flags;

            const clauses = data.report_data?.clauses || [];
            const listEl = document.getElementById('clausesList');
            listEl.innerHTML = '';

            clauses.forEach(c => {
                const cLvl = c.risk_level || 'LOW';
                const cBadge = cLvl === 'LOW' ? 'badge-low' : (cLvl === 'MEDIUM' ? 'badge-medium' : 'badge-high');
                const title = c.clause_type.replace(/_/g, ' ').toUpperCase();
                
                let flagsHtml = '';
                if (c.red_flags && c.red_flags.length > 0) {
                    flagsHtml = `<ul class="red-flags">` + c.red_flags.map(f => `<li>⚠️ ${f}</li>`).join('') + `</ul>`;
                }

                const card = document.createElement('div');
                card.className = 'clause-card';
                card.innerHTML = `
                    <div class="header">
                        <span class="clause-title">${title}</span>
                        <span class="badge ${cBadge}">${cLvl}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8;">${c.reason || ''}</div>
                    ${flagsHtml}
                    <div class="recommendation">💡 <b>Advice:</b> ${c.recommendation || 'Standard clause.'}</div>
                `;
                listEl.appendChild(card);
            });
        }
    </script>
</body>
</html>
"""

class ComplianceRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif parsed.path == '/api/samples':
            params = urllib.parse.parse_qs(parsed.query)
            file_name = params.get('file', [''])[0]
            samples_dir = os.path.join(BASE_DIR, 'sample_contracts')
            target = os.path.join(samples_dir, os.path.basename(file_name))
            if os.path.exists(target):
                with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self._send_json(200, {'file': file_name, 'content': content})
            else:
                self._send_json(404, {'error': 'Sample file not found'})
        elif parsed.path == '/api/logs':
            logs = get_event_logs()
            self._send_json(200, {'logs': logs})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/analyze':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            try:
                req_data = json.loads(body)
                contract_text = req_data.get('contract_text', '')
                file_path = req_data.get('file_path')

                if file_path:
                    result = agent.analyze_file(file_path)
                else:
                    result = agent.handle_message(contract_text)

                self._send_json(200, result)
            except Exception as e:
                self._send_json(500, {'error': str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

def run_server(port=8080):
    server = HTTPServer(('127.0.0.1', port), ComplianceRequestHandler)
    print(f'Server running at http://127.0.0.1:{port}/')
    server.serve_forever()

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
