import datetime
import time
import json
import psutil # <--- NUEVA LIBRERÍA
import os
import requests 
from flask import Flask, request, render_template_string, jsonify
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

# ==========================================
# 1. TUS CREDENCIALES
# ==========================================
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = "xtQiDZLYWisYfZU7sg37ZjC6uKHw737Ol52dobHg7xaQyLoCYAqk7Lu7NfyVmnBhWhnL6lYmHmmRMWMkDEo5wA=="
bucket = "rasp"
org = "TU_ORG_ID" 

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

# ==========================================
# 2. VARIABLES GLOBALES
# ==========================================
config_alarmas = {} 
telegram_config = { "bot_token": "", "chat_ids": [] }
ultimo_aviso = {} 
estado_sistema = { "velocidad_muestreo": 2000 }
historial_paquetes = [] 

# ==========================================
# 3. INTERFAZ GRÁFICA (HTML + JS)
# ==========================================
html_template = """
<!DOCTYPE html>
<html lang="es" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SCADA Industrial IoT</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>

    <style>
        body { background-color: #121212; font-family: 'Segoe UI', sans-serif; }
        .sidebar { height: 100vh; background: linear-gradient(180deg, #0f0c29, #302b63); border-right: 1px solid #444; padding-top: 20px; }
        .nav-link { color: #aaa; margin-bottom: 10px; cursor: pointer; transition: 0.3s; }
        .nav-link:hover, .nav-link.active { color: #00f260; background: rgba(255,255,255,0.05); border-left: 4px solid #00f260; }
        .nav-link i { margin-right: 10px; width: 20px; text-align: center; }
        .card-custom { background-color: #1e1e24; border: none; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px; }
        .card-header-custom { background: rgba(255,255,255,0.02); border-bottom: 1px solid #333; padding: 15px; font-weight: bold; color: #00f260; }
        .btn-neon { background-color: transparent; border: 1px solid #00f260; color: #00f260; transition: 0.3s; }
        .btn-neon:hover { background-color: #00f260; color: black; }
        .kpi-value { font-size: 2.5rem; font-weight: 700; color: white; }
        .terminal-table { font-family: 'Courier New', monospace; font-size: 0.85rem; }
        .json-raw { color: #ce9178; } 
        
        /* Estilos Monitor de Recursos */
        .resource-bar { height: 6px; background: #333; border-radius: 3px; margin-top: 5px; overflow: hidden; }
        .resource-fill { height: 100%; background: #00f260; transition: width 0.5s; }
        .resource-item { font-size: 0.8rem; color: #ccc; margin-bottom: 12px; }
    </style>
</head>
<body>

<div class="container-fluid">
    <div class="row">
        <div class="col-md-2 sidebar d-none d-md-block">
            <h4 class="text-center text-white mb-4"><i class="fa-solid fa-industry"></i> SCADA System</h4>
            
            <ul class="nav flex-column mb-4">
                <li class="nav-item"><a class="nav-link active" id="btn-dash" onclick="cambiarPestana('dashboard')"><i class="fa-solid fa-chart-line"></i> Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" id="btn-mon" onclick="cambiarPestana('monitoreo')"><i class="fa-solid fa-terminal"></i> Monitoreo Raw</a></li>
                <li class="nav-item"><a class="nav-link" id="btn-tele" data-bs-toggle="modal" data-bs-target="#modalTelegram"><i class="fa-brands fa-telegram"></i> Config. Telegram</a></li>
                <li class="nav-item"><a class="nav-link" id="btn-repo" onclick="descargarReporte()"><i class="fa-solid fa-file-export"></i> Reportes (CSV)</a></li>
            </ul>

            <div class="p-3 bg-dark bg-opacity-50 rounded border border-secondary mx-2">
                <h6 class="text-white border-bottom border-secondary pb-2 mb-3"><i class="fa-solid fa-server"></i> Salud Raspberry</h6>
                
                <div class="resource-item">
                    <div class="d-flex justify-content-between"><span>CPU</span> <span id="resCpu">--%</span></div>
                    <div class="resource-bar"><div id="barCpu" class="resource-fill" style="width: 0%"></div></div>
                </div>

                <div class="resource-item">
                    <div class="d-flex justify-content-between"><span>RAM</span> <span id="resRam">--%</span></div>
                    <div class="resource-bar"><div id="barRam" class="resource-fill" style="width: 0%"></div></div>
                </div>

                <div class="resource-item">
                    <div class="d-flex justify-content-between"><span>Disco</span> <span id="resDisk">--%</span></div>
                    <div class="resource-bar"><div id="barDisk" class="resource-fill" style="width: 0%"></div></div>
                </div>

                <div class="resource-item mb-0">
                    <div class="d-flex justify-content-between"><span>Temp</span> <span id="resTemp" class="text-warning">--°C</span></div>
                </div>
            </div>

        </div>

        <div class="col-md-10 p-4">
            
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-white">Panel de Supervisión</h2>
                <div class="input-group w-auto">
                    <span class="input-group-text bg-dark text-white border-secondary"><i class="fa-solid fa-robot"></i></span>
                    <select id="selectMaquinas" class="form-select w-auto bg-dark text-white border-secondary" onchange="cambiarMaquina()">
                        <option value="" disabled selected>Cargando...</option>
                    </select>
                </div>
            </div>

            <div id="view-dashboard">
                <div class="row">
                    <div class="col-lg-8">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="card card-custom p-3 text-center" style="border-bottom: 3px solid #fd7e14;">
                                    <i class="fa-solid fa-temperature-three-quarters fa-2x mb-2" style="color: #fd7e14;"></i>
                                    <div class="kpi-value" id="kpiTemp">--</div>
                                    <div class="small text-muted">TEMPERATURA (°C)</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card card-custom p-3 text-center" style="border-bottom: 3px solid #0dcaf0;">
                                    <i class="fa-solid fa-wave-square fa-2x mb-2" style="color: #0dcaf0;"></i>
                                    <div class="kpi-value" id="kpiVib">--</div>
                                    <div class="small text-muted">VIBRACIÓN (G)</div>
                                </div>
                            </div>
                        </div>
                        <div class="card card-custom">
                            <div class="card-header-custom d-flex justify-content-between align-items-center">
                                <span><i class="fa-solid fa-chart-area"></i> Tendencia</span>
                                <select class="form-select form-select-sm w-auto bg-dark text-white border-secondary" id="rangoTiempo" onchange="cargarDatos()">
                                    <option value="-1h">1 Hora</option>
                                    <option value="-6h">6 Horas</option>
                                    <option value="-24h">24 Horas</option>
                                </select>
                            </div>
                            <div class="card-body"><div id="chartGrafana" style="min-height: 350px;"></div></div>
                        </div>
                    </div>

                    <div class="col-lg-4">
                        <div class="card card-custom">
                            <div class="card-header-custom text-warning"><i class="fa-solid fa-triangle-exclamation"></i> Umbrales Alarma</div>
                            <div class="card-body">
                                <label class="form-label text-white">Max. Temp (°C)</label>
                                <input type="number" id="inputMaxTemp" class="form-control bg-dark text-white border-secondary mb-3">
                                <label class="form-label text-white">Max. Vib (G)</label>
                                <input type="number" id="inputMaxVib" class="form-control bg-dark text-white border-secondary mb-3">
                                <button onclick="guardarAlarmas()" class="btn btn-neon w-100">Guardar</button>
                                <div id="msgAlarma" class="mt-2 text-success small text-center" style="display:none;">Guardado OK</div>
                            </div>
                        </div>
                        <div class="card card-custom mt-3">
                            <div class="card-header-custom text-info"><i class="fa-solid fa-clock"></i> Frecuencia ESP32</div>
                            <div class="card-body text-center">
                                <h4 class="text-white" id="valDisplayHuman">2 seg</h4>
                                <small class="text-muted d-block mb-2" id="valDisplayRaw">(2000 ms)</small>
                                <input type="range" class="form-range" min="200" max="300000" step="100" value="{{ velocidad }}" 
                                       oninput="actualizarTextoVisual(this.value)" onchange="actualizarVelocidad(this.value)">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="view-monitoreo" style="display: none;">
                <div class="card card-custom">
                    <div class="card-header-custom text-info"><i class="fa-solid fa-network-wired"></i> Tráfico Entrante (Raw JSON)</div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-striped mb-0 terminal-table">
                                <thead><tr><th style="width:150px;">Hora</th><th style="width:100px;">ID</th><th>Payload</th></tr></thead>
                                <tbody id="tablaLogs"><tr><td colspan="3" class="text-center text-muted">Esperando...</td></tr></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</div>

<div class="modal fade" id="modalTelegram" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content bg-dark text-white border-secondary">
            <div class="modal-header border-secondary"><h5 class="modal-title">Configurar Telegram</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
            <div class="modal-body">
                <label>Bot Token</label><input type="text" id="botToken" class="form-control bg-secondary text-white mb-3">
                <label>Chat IDs</label><input type="text" id="chatIds" class="form-control bg-secondary text-white mb-3">
                <div class="d-flex gap-2">
                    <button onclick="guardarTelegram(false)" class="btn btn-primary flex-grow-1">Guardar</button>
                    <button onclick="guardarTelegram(true)" class="btn btn-outline-warning">Probar</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    var chart; var maquinaActual = ""; var currentView = 'dashboard';

    window.onload = async function() {
        actualizarTextoVisual({{ velocidad }});
        try {
            const r = await fetch('/api/maquinas'); const m = await r.json();
            const sel = document.getElementById('selectMaquinas'); sel.innerHTML = "";
            m.forEach(x => { let o = document.createElement('option'); o.value = x; o.innerText = x; sel.appendChild(o); });
            if(m.length > 0) { maquinaActual = m[0]; cargarDatos(); cargarConfigAlarma(maquinaActual); }
            else { sel.innerHTML = "<option>Sin datos...</option>"; }
        } catch(e) {}
    };

    function cambiarMaquina() { maquinaActual = document.getElementById('selectMaquinas').value; cargarDatos(); cargarConfigAlarma(maquinaActual); }

    function cambiarPestana(opcion) {
        currentView = opcion;
        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
        if(opcion === 'dashboard') document.getElementById('btn-dash').classList.add('active');
        if(opcion === 'monitoreo') document.getElementById('btn-mon').classList.add('active');
        document.getElementById('view-dashboard').style.display = (opcion === 'dashboard') ? 'block' : 'none';
        document.getElementById('view-monitoreo').style.display = (opcion === 'monitoreo') ? 'block' : 'none';
    }

    async function cargarDatos() {
        // ACTUALIZAR RECURSOS (SIEMPRE)
        const res = await fetch('/api/system-status');
        const sys = await res.json();
        document.getElementById('resCpu').innerText = sys.cpu + "%"; document.getElementById('barCpu').style.width = sys.cpu + "%";
        document.getElementById('resRam').innerText = sys.ram + "%"; document.getElementById('barRam').style.width = sys.ram + "%";
        document.getElementById('resDisk').innerText = sys.disk + "%"; document.getElementById('barDisk').style.width = sys.disk + "%";
        document.getElementById('resTemp').innerText = sys.temp + "°C";

        // VISTA MONITOREO
        if (currentView === 'monitoreo') {
            const rLog = await fetch('/api/raw-logs'); const logs = await rLog.json();
            const tbody = document.getElementById('tablaLogs'); tbody.innerHTML = "";
            logs.forEach(l => { tbody.innerHTML += `<tr><td class="text-success">${l.hora}</td><td class="fw-bold">${l.id}</td><td class="json-raw">${l.data}</td></tr>`; });
        }
        // VISTA DASHBOARD
        if (currentView === 'dashboard' && maquinaActual) {
            const rango = document.getElementById('rangoTiempo').value;
            const r = await fetch(`/api/history?id=${maquinaActual}&rango=${rango}`); const data = await r.json();
            if(data.temp.length > 0) {
                document.getElementById('kpiTemp').innerText = data.temp[data.temp.length-1].toFixed(1);
                document.getElementById('kpiVib').innerText = data.vib[data.vib.length-1].toFixed(2);
            }
            var options = {
                series: [{ name: 'Temp', data: data.temp }, { name: 'Vib', data: data.vib }],
                chart: { type: 'area', height: 350, background: 'transparent', toolbar: {show:false}, animations: {enabled:false} },
                colors: ['#fd7e14', '#0dcaf0'], stroke: { curve: 'smooth', width: 2 }, theme: { mode: 'dark' }, dataLabels: { enabled: false }, labels: data.time, 
                xaxis: { type: 'datetime', labels: { show: false }, axisBorder: { show: false } },
                yaxis: [{ title: { text: '°C', style: { color: '#fd7e14' } }, labels: { style: { colors: '#fd7e14' } } }, { opposite: true, title: { text: 'G', style: { color: '#0dcaf0' } }, labels: { style: { colors: '#0dcaf0' } } }],
                grid: { borderColor: '#333' }
            };
            if(chart) chart.updateOptions(options); else { chart = new ApexCharts(document.querySelector("#chartGrafana"), options); chart.render(); }
        }
    }
    setInterval(cargarDatos, 2000);

    function actualizarTextoVisual(ms) {
        let val = parseInt(ms);
        let texto = (val < 1000) ? val + " ms" : (val >= 60000) ? Math.floor(val/60000) + " min " + Math.floor((val%60000)/1000) + " seg" : Math.floor(val/1000) + " seg";
        document.getElementById('valDisplayHuman').innerText = texto; document.getElementById('valDisplayRaw').innerText = "(" + val + " ms)";
    }
    function actualizarVelocidad(v) { actualizarTextoVisual(v); fetch('/api/set-speed', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ ms: v }) }); }
    function descargarReporte() {
        if (!chart || chart.w.config.series[0].data.length === 0) { alert("⚠️ Sin datos."); return; }
        const t = chart.w.config.series[0].data; const v = chart.w.config.series[1].data; const l = chart.w.config.labels;
        let csv = "data:text/csv;charset=utf-8,Fecha,Temperatura,Vibracion\\n"; l.forEach((x, i) => csv += `${x},${t[i]},${v[i]}\\n`);
        const link = document.createElement("a"); link.setAttribute("href", encodeURI(csv)); link.setAttribute("download", `Reporte_${maquinaActual}.csv`);
        document.body.appendChild(link); link.click(); document.body.removeChild(link);
    }
    const myModalEl = document.getElementById('modalTelegram');
    myModalEl.addEventListener('show.bs.modal', e => { document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active')); document.getElementById('btn-tele').classList.add('active'); });
    myModalEl.addEventListener('hidden.bs.modal', e => cambiarPestana(currentView));

    async function cargarConfigAlarma(id) { const r = await fetch(`/api/alarmas?id=${id}`); const c = await r.json(); document.getElementById('inputMaxTemp').value = c.temp_max || ""; document.getElementById('inputMaxVib').value = c.vib_max || ""; }
    async function guardarAlarmas() { const t = document.getElementById('inputMaxTemp').value; const v = document.getElementById('inputMaxVib').value; await fetch('/api/alarmas', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ id: maquinaActual, temp_max: t, vib_max: v }) }); const msg = document.getElementById('msgAlarma'); msg.style.display = 'block'; setTimeout(() => msg.style.display = 'none', 3000); }
    function guardarTelegram(probar) { const t = document.getElementById('botToken').value; const i = document.getElementById('chatIds').value; fetch('/api/telegram-config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ token: t, ids: i, test: probar }) }).then(r => r.json()).then(data => alert(data.status === 'ok' ? (probar?"✅ OK":"Guardado") : "❌ Error")); }
</script>
</body>
</html>
"""

# ==========================================
# 4. BACKEND
# ==========================================
def get_cpu_temp():
    try:
        # Comando específico para Raspberry Pi
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except:
        return 0.0 # Si no es Rasp, devuelve 0

@app.route('/api/system-status')
def system_status():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "temp": get_cpu_temp()
    })

def enviar_mensaje_telegram(mensaje):
    token = telegram_config.get("bot_token")
    ids = telegram_config.get("chat_ids", [])
    if not token or not ids: return False
    exito = False
    for chat_id in ids:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": mensaje}, timeout=5)
            exito = True
        except: pass
    return exito

def verificar_limites(mid, datos):
    if mid in config_alarmas:
        cfg = config_alarmas[mid]
        msg = ""
        if "temp_max" in cfg and float(datos.get("temperatura", 0)) > float(cfg["temp_max"]): msg += f"🌡️ Temp Alta: {datos['temperatura']}°C\n"
        if "vib_max" in cfg and float(datos.get("vibracion", 0)) > float(cfg["vib_max"]): msg += f"⚠️ Vib Crítica: {datos['vibracion']}G\n"
        if msg:
            now = time.time()
            if now - ultimo_aviso.get(mid, 0) > 60:
                enviar_mensaje_telegram(f"🚨 ALERTA [{mid}]\n{msg}")
                ultimo_aviso[mid] = now

@app.route('/')
def index(): return render_template_string(html_template, velocidad=estado_sistema["velocidad_muestreo"])

@app.route('/api/raw-logs')
def get_logs(): return jsonify(historial_paquetes)

@app.route('/api/maquinas')
def get_maquinas():
    try:
        q = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "{bucket}", tag: "maquina")'
        return jsonify([r.get_value() for t in query_api.query(q) for r in t.records])
    except: return jsonify([])

@app.route('/api/history')
def get_history():
    mid = request.args.get('id', 'MAQ_1')
    rango = request.args.get('rango', '-1h')
    q = f"""from(bucket:"{bucket}") |> range(start:{rango}) 
    |> filter(fn:(r)=>r["_measurement"]=="telemetria_industrial" and r["maquina"]=="{mid}")
    |> filter(fn:(r)=>r["_field"]=="temperatura" or r["_field"]=="vibracion")
    |> aggregateWindow(every:1m, fn:mean, createEmpty:false)
    |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")"""
    try:
        tables = query_api.query(q)
        d = {"time":[], "temp":[], "vib":[]}
        for t in tables:
            for r in t.records:
                d["time"].append(r.get_time().isoformat())
                d["temp"].append(r.values.get("temperatura", 0))
                d["vib"].append(r.values.get("vibracion", 0))
        return jsonify(d)
    except: return jsonify({"time":[],"temp":[],"vib":[]})

@app.route('/api/alarmas', methods=['GET', 'POST'])
def manage_alarmas():
    if request.method == 'POST':
        d = request.json
        config_alarmas[d.get('id')] = {'temp_max': d.get('temp_max'), 'vib_max': d.get('vib_max')}
        return jsonify({"status": "ok"})
    return jsonify(config_alarmas.get(request.args.get('id'), {}))

@app.route('/api/telegram-config', methods=['POST'])
def config_telegram():
    d = request.json
    telegram_config["bot_token"] = d.get("token")
    telegram_config["chat_ids"] = [x.strip() for x in d.get("ids").split(',') if x.strip()]
    if d.get("test"): return jsonify({"status": "ok" if enviar_mensaje_telegram("✅ PRUEBA OK") else "error"})
    return jsonify({"status": "ok"})

@app.route('/api/set-speed', methods=['POST'])
def set_speed():
    estado_sistema["velocidad_muestreo"] = int(request.json['ms'])
    return jsonify({"status": "ok"})

@app.route('/api/telemetria', methods=['POST'])
def receive():
    try:
        payload = request.json
        if not isinstance(payload, list): payload = [payload]
        pts = []
        for d in payload:
            mid = d.get("id", "unknown")
            log_entry = { "hora": datetime.datetime.now().strftime("%H:%M:%S"), "id": mid, "data": json.dumps(d) }
            historial_paquetes.insert(0, log_entry)
            if len(historial_paquetes) > 20: historial_paquetes.pop()
            verificar_limites(mid, d) 
            p = Point("telemetria_industrial").time(datetime.datetime.utcnow())
            if "id" in d: p.tag("maquina", d["id"])
            for k,v in d.items():
                if k!="id": p.field(k, float(v) if isinstance(v,(int,float)) else str(v))
            pts.append(p)
        if pts: write_api.write(bucket=bucket, org=org, record=pts)
        return jsonify({"status":"ok", "nuevo_intervalo": estado_sistema["velocidad_muestreo"]})
    except Exception as e: return jsonify({"error":str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)