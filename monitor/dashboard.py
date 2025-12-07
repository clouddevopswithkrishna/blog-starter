from flask import Flask, jsonify, render_template_string, request, Response
import json
import os
import requests
import threading
import time
import random

app = Flask(__name__)
LOG_FILE = "/var/log/container_stats.json"
BACKEND_URL = "http://backend:4000/api"

# Global state for load generation
load_state = {
    "targets": {
        "frontend": {"users": 0, "active": False},
        "backend": {"users": 0, "active": False},
        "db": {"users": 0, "active": False}
    },
    "total_requests": 0,
    "errors": 0
}

# Thread management
load_threads = {
    "frontend": [],
    "backend": [],
    "db": []
}

def user_worker(target_type, worker_id):
    # Mapping targets to URLs
    urls = {
        "frontend": "http://frontend:80", 
        "backend": f"{BACKEND_URL}/posts",
        "db": f"{BACKEND_URL}/database-intensive"
    }
    
    url = urls.get(target_type)
    if not url: return

    while True:
        # Check if we should stop
        current_target_users = load_state["targets"][target_type]["users"]
        if worker_id > current_target_users:
            break
            
        try:
            # Different behavior per type
            if target_type == 'db':
                requests.get(url, timeout=5)
            else:
                requests.get(url, timeout=2)
                
            load_state["total_requests"] += 1
        except:
            load_state["errors"] += 1
        
        # User think time
        if target_type != 'db':
            time.sleep(random.uniform(0.5, 2.0))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>High-Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px; background: #f3f4f6; color: #1f2937; }
        .dark-mode { background: #111827; color: #f3f4f6; }
        
        h1 { font-size: 2rem; font-weight: 300; margin-bottom: 2rem; color: #3b82f6; }
        h2 { font-size: 1.2rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.5rem; }
        .dark-mode h2 { border-color: #374151; }

        /* Helpers */
        .card { background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); border: 1px solid #e5e7eb; }
        .dark-mode .card { background: #1f2937; border-color: #374151; }
        
        /* Stats Row */
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
        .stat-card-label { font-size: 0.875rem; color: #6b7280; font-weight: 600; text-transform: uppercase; }
        .stat-card-value { font-size: 2rem; font-weight: 800; margin-top: 0.5rem; }
        
        /* Charts Row */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }
        .chart-container { position: relative; height: 300px; width: 100%; }

        /* Alerts */
        .alert-item { padding: 10px; border-left: 4px solid #ef4444; background: #fee2e2; margin-bottom: 8px; border-radius: 4px; color: #b91c1c; font-size: 0.9rem; }
        .dark-mode .alert-item { background: #450a0a; color: #fca5a5; }

        /* Controls */
        .btn { padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer; color: white; transition: 0.2s; font-weight: 600; margin-right: 5px; margin-bottom: 5px; }
        .btn-green { background: #10b981; } .btn-green:hover { background: #059669; }
        .btn-red { background: #ef4444; } .btn-red:hover { background: #dc2626; }
        .btn-blue { background: #3b82f6; } .btn-blue:hover { background: #2563eb; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .dark-mode th, .dark-mode td { border-bottom-color: #374151; }
    </style>
</head>
<body class="dark-mode">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>🚀 Antigravity Blog Monitor</h1>
        <button class="btn btn-blue" onclick="document.body.classList.toggle('dark-mode')">Toggle Theme</button>
    </div>

    <!-- Row 1: Top Metrics -->
    <div class="grid-4">
        <div class="card">
            <div class="stat-card-label">Container Status</div>
            <div class="stat-card-value" style="color: #10b981;">● Running</div>
        </div>
        <div class="card">
            <div class="stat-card-label">Avg CPU Usage</div>
            <div class="stat-card-value" id="val-cpu">0%</div>
            <div style="background: #e5e7eb; height: 6px; border-radius: 3px; margin-top: 5px;"><div id="bar-cpu" style="width: 0%; height: 100%; background: #3b82f6; border-radius: 3px;"></div></div>
        </div>
        <div class="card">
            <div class="stat-card-label">Total Memory</div>
            <div class="stat-card-value" id="val-mem">0MB</div>
             <div style="background: #e5e7eb; height: 6px; border-radius: 3px; margin-top: 5px;"><div id="bar-mem" style="width: 0%; height: 100%; background: #8b5cf6; border-radius: 3px;"></div></div>
        </div>
        <div class="card">
            <div class="stat-card-label">Response Time</div>
            <div class="stat-card-value" id="val-latency">0 ms</div>
        </div>
    </div>

    <!-- Row 2: Charts -->
    <div class="grid-2">
        <div class="card">
            <div class="stat-card-label">Latency (ms)</div>
            <div class="chart-container"><canvas id="chartLatency"></canvas></div>
        </div>
        <div class="card">
            <div class="stat-card-label">Load & Status</div>
             <div class="chart-container"><canvas id="chartUptime"></canvas></div>
        </div>
    </div>

    <!-- Row 3: Resources & Alerts -->
    <div class="grid-2">
        <div class="card">
            <div class="stat-card-label">Resource Metrics</div>
            <div class="chart-container"><canvas id="chartResources"></canvas></div>
        </div>
        <div class="card">
            <div class="stat-card-label">Recent Alerts</div>
            <div id="alerts-box" style="height: 300px; overflow-y: auto; margin-top: 15px;">
                <div class="alert-item">[System] Dashboard initialized. Monitoring active.</div>
            </div>
        </div>
    </div>

    <!-- Container Table -->
    <div class="card" style="margin-bottom: 2rem;">
        <div class="stat-card-label">Detailed Container Health</div>
        <table id="container-table">
            <thead><tr><th>Container</th><th>CPU %</th><th>Mem Usage</th></tr></thead>
            <tbody id="container-body"></tbody>
        </table>
    </div>

    <!-- Controls Section -->
    <h2>🎛️ Load Controls & Logs</h2>
    <div class="grid-2">
         <!-- Load Controls -->
         <div class="card">
            <div class="stat-card-label">Traffic Generator</div>
            <div style="margin-top: 15px; display: grid; gap: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>Frontend Users: <b id="count-frontend">0</b></span>
                    <div>
                        <button class="btn btn-green" onclick="adjustLoad('frontend', 5)">+5</button>
                        <button class="btn btn-red" onclick="adjustLoad('frontend', -5)">-5</button>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Backend Users: <b id="count-backend">0</b></span>
                    <div>
                        <button class="btn btn-green" onclick="adjustLoad('backend', 5)">+5</button>
                        <button class="btn btn-red" onclick="adjustLoad('backend', -5)">-5</button>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>DB Queries: <b id="count-db">0</b></span>
                    <div>
                        <button class="btn btn-green" onclick="adjustLoad('db', 1)">+1</button>
                        <button class="btn btn-red" onclick="adjustLoad('db', -1)">-1</button>
                    </div>
                </div>
                <hr style="border: 0; border-top: 1px solid #374151; margin: 10px 0;">
                 <button class="btn btn-blue" onclick="triggerEffect('cpu')">Trigger CPU Spike</button>
                 <button class="btn btn-blue" onclick="triggerEffect('memory')">Trigger Memory Leak</button>
            </div>
         </div>
         
         <!-- Logs -->
         <div class="card">
            <div class="stat-card-label">Live Logs</div>
            <div style="margin-top: 10px; margin-bottom: 10px;">
                <button class="btn btn-blue" onclick="selectLog('backend')">Backend</button>
                <button class="btn btn-blue" onclick="selectLog('frontend')">Frontend</button>
                <button class="btn btn-blue" onclick="selectLog('db')">DB</button>
                <button class="btn btn-blue" onclick="selectLog('monitor')">Monitor</button>
            </div>
            <div id="log-container" style="background: #111827; padding: 10px; border-radius: 4px; height: 150px; overflow-y: auto; font-family: monospace; font-size: 0.8em; color: #d1d5db;">Select a service...</div>
         </div>
    </div>

    <script>
        // Charts Init
        const MAX_POINTS = 30;
        const labels = Array(MAX_POINTS).fill('');
        
        const chartLatency = new Chart(document.getElementById('chartLatency'), {
            type: 'line',
            data: { 
                labels: labels, 
                datasets: [
                    { label: 'Frontend', data: Array(MAX_POINTS).fill(0), borderColor: '#10b981', tension: 0.4 },
                    { label: 'Backend', data: Array(MAX_POINTS).fill(0), borderColor: '#3b82f6', tension: 0.4 },
                    { label: 'DB', data: Array(MAX_POINTS).fill(0), borderColor: '#ef4444', tension: 0.4 }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false } } }
        });

        const chartUptime = new Chart(document.getElementById('chartUptime'), {
            type: 'line',
            data: { 
                labels: labels, 
                datasets: [
                    { label: 'Frontend', data: Array(MAX_POINTS).fill(0), borderColor: '#10b981', tension: 0.4 },
                    { label: 'Backend', data: Array(MAX_POINTS).fill(0), borderColor: '#3b82f6', tension: 0.4 },
                    { label: 'DB', data: Array(MAX_POINTS).fill(0), borderColor: '#ef4444', tension: 0.4 }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false } } }
        });

        const chartResources = new Chart(document.getElementById('chartResources'), {
            type: 'line',
            data: { 
                labels: labels, 
                datasets: [
                    { label: 'CPU %', data: Array(MAX_POINTS).fill(0), borderColor: '#3b82f6', tension: 0.4 },
                    { label: 'Mem %', data: Array(MAX_POINTS).fill(0), borderColor: '#ef4444', tension: 0.4 }
                ] 
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false }, y: { min: 0, max: 100 } } }
        });

        function addData(chart, dataPoint, datasetIndex=0) {
            const data = chart.data.datasets[datasetIndex].data;
            data.push(dataPoint);
            if (data.length > MAX_POINTS) data.shift();
            chart.update('none'); // Perf opt
        }

        // Logic
        function updateStats() {
            fetch('/data')
                .then(r => r.json())
                .then(data => {
                    // 1. Latency & Response Time
                    const lat = data.latencies || { frontend: 0, backend: 0, db: 0 };
                    document.getElementById('val-latency').innerText = (lat.backend || 0) + ' ms';
                    
                    addData(chartLatency, lat.frontend, 0);
                    addData(chartLatency, lat.backend, 1);
                    addData(chartLatency, lat.db, 2);
                    
                    // 2. Load
                    if(data.load_stats.targets) {
                         document.getElementById('count-frontend').innerText = data.load_stats.targets.frontend.users;
                         document.getElementById('count-backend').innerText = data.load_stats.targets.backend.users;
                         document.getElementById('count-db').innerText = data.load_stats.targets.db.users;
                         
                         addData(chartUptime, data.load_stats.targets.frontend.users, 0);
                         addData(chartUptime, data.load_stats.targets.backend.users, 1);
                         addData(chartUptime, data.load_stats.targets.db.users, 2);
                    }

                    // 3. Docker Stats Aggregation
                    let totalCpu = 0;
                    let totalMemVal = 0; // MB
                    let maxMem = 1000; // Guess 1GB per container roughly? Or just sum %
                    
                    const tbody = document.getElementById('container-body');
                    tbody.innerHTML = '';
                    
                    if (data.docker_stats && data.docker_stats.length > 0) {
                        data.docker_stats.forEach( row => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `<td>${row.name}</td><td>${row.cpu}</td><td>${row.mem}</td>`;
                            tbody.appendChild(tr);
                            
                            // Parse
                            let cpu = parseFloat(row.cpu.replace('%','')) || 0;
                            totalCpu += cpu;
                            
                            // Parse Mem (e.g. "45MiB / 1GiB")
                            if(row.mem.includes('MiB')) {
                                totalMemVal += parseFloat(row.mem);
                            } else if (row.mem.includes('GiB')) {
                                totalMemVal += parseFloat(row.mem) * 1024;
                            }
                        });
                    }
                    
                    document.getElementById('val-cpu').innerText = totalCpu.toFixed(1) + '%';
                    document.getElementById('bar-cpu').style.width = Math.min(totalCpu, 100) + '%';
                    
                    document.getElementById('val-mem').innerText = totalMemVal.toFixed(0) + ' MB';
                    // Arbitrary resource scaling for chart
                    addData(chartResources, totalCpu, 0);
                    addData(chartResources, Math.min(totalMemVal / 20, 100), 1); 

                    // 4. Alerts
                    if(totalCpu > 80) addAlert("High CPU Usage Detected: " + totalCpu.toFixed(1) + "%");
                    if(data.load_stats.errors > 0) addAlert("System Errors Detected in Load Generator");
                });
        }
        
        // Alert Helper to avoid spam
        let lastAlert = "";
        let lastAlertTime = 0;
        function addAlert(msg) {
            const now = Date.now();
            if(msg === lastAlert && (now - lastAlertTime) < 5000) return; // Debounce
            lastAlert = msg;
            lastAlertTime = now;
            
            const box = document.getElementById('alerts-box');
            const d = new Date().toLocaleTimeString();
            const div = document.createElement('div');
            div.className = 'alert-item';
            div.innerText = `[${d}] ALERT: ${msg}`;
            box.insertBefore(div, box.firstChild);
        }

        function adjustLoad(type, amount) { fetch(`/load/adjust?type=${type}&amount=${amount}`, { method: 'POST' }); }
        function triggerEffect(type) { fetch('/trigger/' + type); }
        
        let currentLogContainer = null;
        let logInterval = null;
        function selectLog(container) {
            currentLogContainer = container;
            fetchLogs();
            if (logInterval) clearInterval(logInterval);
            logInterval = setInterval(fetchLogs, 2000); 
        }
        function fetchLogs() {
            if (!currentLogContainer) return;
            fetch('/logs/' + currentLogContainer).then(r => r.text()).then(text => {
                 const el = document.getElementById('log-container');
                 el.innerText = text;
                 el.scrollTop = el.scrollHeight; 
            });
        }

        setInterval(updateStats, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    latencies = {"frontend": 0, "backend": 0, "db": 0}
    
    # 1. Frontend Latency
    try:
        s = time.time()
        requests.get("http://frontend:80", timeout=0.5)
        latencies["frontend"] = int((time.time() - s) * 1000)
    except: pass
    
    # 2. Backend Latency (lightweight)
    try:
        s = time.time()
        requests.get(f"{BACKEND_URL}/../health", timeout=0.5)
        latencies["backend"] = int((time.time() - s) * 1000)
    except:
        try:
             s = time.time()
             requests.get(f"http://backend:4000/health", timeout=0.5)
             latencies["backend"] = int((time.time() - s) * 1000)
        except: pass
        
    # 3. DB Latency (using new db-ping)
    try:
        s = time.time()
        requests.get(f"{BACKEND_URL}/db-ping", timeout=0.5)
        latencies["db"] = int((time.time() - s) * 1000)
    except: pass

    # App Stats (Cache/Records)
    app_stats = {}
    try: 
        r = requests.get(f"{BACKEND_URL}/stats", timeout=0.5)
        if r.status_code == 200: app_stats = r.json()
    except: pass

    # Docker Stats
    docker_stats = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    for line in content.splitlines():
                        parts = line.split('|')
                        if len(parts) >= 3:
                            docker_stats.append({
                                "name": parts[0].strip(),
                                "cpu": parts[1].strip(),
                                "mem": parts[2].strip()
                            })
    except: pass

    return jsonify({
        "latencies": latencies,
        "app_stats": app_stats,
        "load_stats": load_state,
        "docker_stats": docker_stats
    })

@app.route('/load/adjust', methods=['POST'])
def adjust_load():
    type = request.args.get('type')
    amount = int(request.args.get('amount', 0))
    
    if type not in load_state["targets"]:
        return jsonify({"error": "Invalid type"}), 400

    target_config = load_state["targets"][type]
    threads_list = load_threads[type]
    
    new_count = target_config["users"] + amount
    if new_count < 0: new_count = 0
    if new_count > 500: new_count = 500
    
    target_config["users"] = new_count
    current_count = len(threads_list)
    
    if new_count > current_count:
        for i in range(current_count, new_count):
            t = threading.Thread(target=user_worker, args=(type, i+1), daemon=True)
            threads_list.append(t)
            t.start()
    elif new_count < current_count:
        del threads_list[new_count:]
        
    return jsonify({"success": True, "users": new_count})

@app.route('/logs/<container>')
def get_logs(container):
    import subprocess
    try:
        cmd = "docker ps --format '{{.Names}}'"
        containers = subprocess.check_output(cmd, shell=True).decode().splitlines()
        target_name = None
        for name in containers:
            if container in name:
                target_name = name
                break
        if not target_name: return "Container not found", 404
        logs = subprocess.check_output(['docker', 'logs', '--tail', '100', target_name], stderr=subprocess.STDOUT)
        return logs.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Error fetching logs: {str(e)}"
        
@app.route('/trigger/<path:test_type>')
def trigger(test_type):
    # Support 'cpu', 'memory' etc AND 'stress/memory/grow'
    endpoints = { 
        'cpu': 'cpu-intensive', 
        'memory': 'memory-intensive', 
        'database': 'database-intensive' 
    }
    target_path = endpoints.get(test_type, test_type)
    try:
        r = requests.get(f"{BACKEND_URL}/{target_path}", timeout=1)
        return jsonify(r.json())
    except Exception as e:
         return jsonify({"message": f"Triggered {test_type} (async/timeout)", "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, threaded=True)
