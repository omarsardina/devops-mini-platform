import os
import socket
import psycopg2
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "platform_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASS", "secret123"),
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Mini-Platform | Live Dashboard</title>
    <style>
        :root {
            --bg: #0b1120;
            --card: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --green: #22c55e;
            --red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 24px; }
        .container { max-width: 820px; width: 100%; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 12px; }
        .title h1 { font-size: 1.6rem; color: var(--text); }
        .title p { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }
        .badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; background: rgba(34, 197, 94, 0.15); color: var(--green); border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge.error { background: rgba(239, 68, 68, 0.15); color: var(--red); border-color: rgba(239, 68, 68, 0.3); }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; box-shadow: 0 0 8px currentColor; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
        .card-label { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
        .card-value { font-size: 1.8rem; font-weight: 700; color: var(--accent); word-break: break-all; }
        .card-value.small { font-size: 1.15rem; color: var(--text); font-family: monospace; }
        .card-sub { color: var(--muted); font-size: 0.82rem; margin-top: 6px; }
        .actions { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
        button { cursor: pointer; padding: 10px 18px; border-radius: 8px; border: none; font-weight: 600; font-size: 0.9rem; transition: 0.2s; }
        .btn-primary { background: var(--accent); color: #0f172a; }
        .btn-primary:hover { opacity: 0.9; }
        .btn-secondary { background: var(--card); color: var(--text); border: 1px solid var(--border); }
        .btn-secondary:hover { border-color: var(--accent); }
        .terminal { background: #020617; border: 1px solid var(--border); border-radius: 10px; padding: 16px; font-family: monospace; font-size: 0.85rem; color: #38bdf8; display: none; }
        .terminal.active { display: block; }
        .footer { text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">
                <h1>DevOps Mini-Platform</h1>
                <p>Containerized Microservice • Kubernetes Orchestration • PostgreSQL</p>
            </div>
            <div class="badge {{ 'error' if db_error else '' }}">
                <span class="dot"></span>
                {{ 'Database Error' if db_error else 'Cluster Healthy (v2)' }}
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Total Platform Visits</div>
                <div class="card-value">{{ visits }}</div>
                <div class="card-sub">Persisted in PostgreSQL</div>
            </div>
            <div class="card">
                <div class="card-label">Served By Pod (Replica)</div>
                <div class="card-value small">{{ pod_name }}</div>
                <div class="card-sub">Refresh to test K8s load balancing</div>
            </div>
            <div class="card">
                <div class="card-label">Infrastructure Stack</div>
                <div class="card-value small">Kind + Terraform + Ansible</div>
                <div class="card-sub">Self-Healing & Probes Active</div>
            </div>
        </div>

        <div class="actions">
            <button class="btn-primary" onclick="window.location.reload()">Simulate Request (Refresh)</button>
            <button class="btn-secondary" onclick="checkHealth()">Test /health Probe</button>
        </div>

        <div id="health-output" class="terminal"></div>

        <div class="footer">
            Running on Kubernetes • Stateless Flask API + Stateful PostgreSQL
        </div>
    </div>

    <script>
        async function checkHealth() {
            const box = document.getElementById('health-output');
            box.classList.add('active');
            box.textContent = '$ curl -s http://localhost:5000/health ...';
            try {
                const res = await fetch('/health');
                const data = await res.json();
                box.textContent = '$ GET /health -> HTTP ' + res.status + '\\n' + JSON.stringify(data, null, 2);
            } catch (err) {
                box.textContent = 'Error reaching /health endpoint: ' + err;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    pod_name = socket.gethostname()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS platform_visits (
                id SERIAL PRIMARY KEY,
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("INSERT INTO platform_visits DEFAULT VALUES;")
        cur.execute("SELECT COUNT(*) FROM platform_visits;")
        visits = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return render_template_string(HTML_TEMPLATE, visits=visits, pod_name=pod_name, db_error=False)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, visits="N/A", pod_name=pod_name, db_error=True), 500

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({
            "status": "healthy",
            "version": "v2",
            "pod": socket.gethostname(),
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
