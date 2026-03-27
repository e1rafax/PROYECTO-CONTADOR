"""
Generador de reporte HTML interactivo con Chart.js.
Crea un archivo HTML con gráficas bonitas de finanzas personales.
"""
import os
import json
import webbrowser
from datetime import date
from database import (
    obtener_transacciones,
    obtener_gastos_por_categoria,
    obtener_balance,
)
from utils import formatear_cop, nombre_mes, rango_mes_actual

REPORTE_PATH = os.path.join(os.path.dirname(__file__), "reporte.html")

# Colores para las categorías
COLORES = [
    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
    "#FF9F40", "#E7E9ED", "#7BC8A4", "#F67280", "#C06C84",
    "#6C5B7B", "#355C7D", "#F8B500", "#FC5185", "#3FC1C9",
]


def generar_reporte_html(user_id: int) -> str:
    """
    Genera un reporte HTML completo con gráficas interactivas.

    Returns:
        Ruta al archivo HTML generado
    """
    inicio, fin = rango_mes_actual()
    hoy = date.today()
    mes = nombre_mes(hoy.month)
    año = hoy.year

    # Datos
    balance = obtener_balance(user_id, inicio, fin)
    categorias = obtener_gastos_por_categoria(user_id, inicio, fin)
    gastos = obtener_transacciones(user_id, tipo="gasto", fecha_inicio=inicio, fecha_fin=fin)
    ingresos = obtener_transacciones(user_id, tipo="ingreso", fecha_inicio=inicio, fecha_fin=fin)
    todas = obtener_transacciones(user_id, fecha_inicio=inicio, fecha_fin=fin)

    # Preparar datos para Chart.js
    cat_labels = json.dumps([c["categoria"] for c in categorias], ensure_ascii=False)
    cat_valores = json.dumps([c["total"] for c in categorias])
    cat_colores = json.dumps(COLORES[:len(categorias)])

    # Gastos por día del mes
    gastos_por_dia = {}
    for t in gastos:
        dia = t["fecha"]
        gastos_por_dia[dia] = gastos_por_dia.get(dia, 0) + t["monto"]

    dias_labels = json.dumps(sorted(gastos_por_dia.keys()))
    dias_valores = json.dumps([gastos_por_dia[d] for d in sorted(gastos_por_dia.keys())])

    # Tabla de transacciones
    filas_html = ""
    for t in todas[:50]:
        emoji = "📤" if t["tipo"] == "gasto" else "📥"
        clase = "gasto" if t["tipo"] == "gasto" else "ingreso"
        filas_html += f"""
            <tr class="{clase}">
                <td>{t['fecha']}</td>
                <td>{emoji} {t['tipo'].capitalize()}</td>
                <td class="monto">{formatear_cop(t['monto'])}</td>
                <td>{t['categoria']}</td>
                <td>{t['descripcion']}</td>
            </tr>"""

    # Top categoría
    top_cat = categorias[0]["categoria"] if categorias else "N/A"
    top_cat_monto = formatear_cop(categorias[0]["total"]) if categorias else "$0"

    # Porcentaje de ahorro
    if balance["ingresos"] > 0:
        pct_ahorro = (balance["balance"] / balance["ingresos"]) * 100
    else:
        pct_ahorro = 0

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Financiero - {mes} {año}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            text-align: center;
            font-size: 2.2em;
            margin-bottom: 10px;
            background: linear-gradient(to right, #00d2ff, #928dab);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-4px); }}
        .card .emoji {{ font-size: 2em; margin-bottom: 8px; }}
        .card .label {{ color: #aaa; font-size: 0.9em; margin-bottom: 4px; }}
        .card .valor {{ font-size: 1.6em; font-weight: bold; }}
        .card.ingresos .valor {{ color: #2ecc71; }}
        .card.gastos .valor {{ color: #e74c3c; }}
        .card.balance .valor {{ color: {"#2ecc71" if balance["balance"] >= 0 else "#e74c3c"}; }}
        .card.ahorro .valor {{ color: #3498db; }}

        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }}
        .chart-box {{
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .chart-box h3 {{
            margin-bottom: 16px;
            color: #ccc;
            font-size: 1.1em;
        }}

        .tabla-section {{
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .tabla-section h3 {{ color: #ccc; margin-bottom: 16px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: rgba(255,255,255,0.1);
            padding: 12px;
            text-align: left;
            font-size: 0.9em;
            color: #aaa;
        }}
        td {{ padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        tr.gasto .monto {{ color: #e74c3c; }}
        tr.ingreso .monto {{ color: #2ecc71; }}
        tr:hover {{ background: rgba(255,255,255,0.04); }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #555;
            font-size: 0.85em;
        }}

        @media (max-width: 600px) {{
            .charts {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Reporte Financiero</h1>
        <p class="subtitle">{mes} {año} &mdash; Generado el {hoy.strftime('%d/%m/%Y')}</p>

        <!-- Tarjetas de resumen -->
        <div class="cards">
            <div class="card ingresos">
                <div class="emoji">📥</div>
                <div class="label">Ingresos</div>
                <div class="valor">{formatear_cop(balance['ingresos'])}</div>
            </div>
            <div class="card gastos">
                <div class="emoji">📤</div>
                <div class="label">Gastos</div>
                <div class="valor">{formatear_cop(balance['gastos'])}</div>
            </div>
            <div class="card balance">
                <div class="emoji">{'✅' if balance['balance'] >= 0 else '⚠️'}</div>
                <div class="label">Balance</div>
                <div class="valor">{formatear_cop(balance['balance'])}</div>
            </div>
            <div class="card ahorro">
                <div class="emoji">💡</div>
                <div class="label">Mayor gasto: {top_cat}</div>
                <div class="valor">{top_cat_monto}</div>
            </div>
        </div>

        <!-- Gráficas -->
        <div class="charts">
            <div class="chart-box">
                <h3>Gastos por Categoría</h3>
                <canvas id="pieChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Gastos Diarios del Mes</h3>
                <canvas id="lineChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Ingresos vs Gastos</h3>
                <canvas id="barChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Distribución por Categoría</h3>
                <canvas id="doughnutChart"></canvas>
            </div>
        </div>

        <!-- Tabla de transacciones -->
        <div class="tabla-section">
            <h3>Últimas Transacciones</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Tipo</th>
                        <th>Monto</th>
                        <th>Categoría</th>
                        <th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>

        <p class="footer">Bot de Finanzas Personales &mdash; Reporte generado autom&aacute;ticamente</p>
    </div>

    <script>
        // Pie Chart - Gastos por categoría
        new Chart(document.getElementById('pieChart'), {{
            type: 'pie',
            data: {{
                labels: {cat_labels},
                datasets: [{{
                    data: {cat_valores},
                    backgroundColor: {cat_colores},
                    borderWidth: 0,
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#ccc', padding: 12 }} }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                let v = ctx.parsed;
                                let total = ctx.dataset.data.reduce((a,b)=>a+b,0);
                                let pct = ((v/total)*100).toFixed(1);
                                return ctx.label + ': $' + v.toLocaleString('es-CO') + ' (' + pct + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Line Chart - Gastos diarios
        new Chart(document.getElementById('lineChart'), {{
            type: 'line',
            data: {{
                labels: {dias_labels},
                datasets: [{{
                    label: 'Gastos',
                    data: {dias_valores},
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231,76,60,0.15)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#e74c3c',
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }},
                scales: {{
                    x: {{ ticks: {{ color: '#888' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    y: {{
                        ticks: {{
                            color: '#888',
                            callback: function(v) {{ return '$' + (v/1000) + 'K'; }}
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}
                    }}
                }}
            }}
        }});

        // Bar Chart - Ingresos vs Gastos
        new Chart(document.getElementById('barChart'), {{
            type: 'bar',
            data: {{
                labels: ['Ingresos', 'Gastos', 'Balance'],
                datasets: [{{
                    data: [{balance['ingresos']}, {balance['gastos']}, {balance['balance']}],
                    backgroundColor: ['#2ecc71', '#e74c3c', '{"#3498db" if balance["balance"] >= 0 else "#e67e22"}'],
                    borderRadius: 8,
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{ return '$' + ctx.parsed.y.toLocaleString('es-CO'); }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#ccc' }}, grid: {{ display: false }} }},
                    y: {{
                        ticks: {{
                            color: '#888',
                            callback: function(v) {{ return '$' + (v/1000000).toFixed(1) + 'M'; }}
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}
                    }}
                }}
            }}
        }});

        // Doughnut Chart
        new Chart(document.getElementById('doughnutChart'), {{
            type: 'doughnut',
            data: {{
                labels: {cat_labels},
                datasets: [{{
                    data: {cat_valores},
                    backgroundColor: {cat_colores},
                    borderWidth: 0,
                    hoverOffset: 10,
                }}]
            }},
            options: {{
                responsive: true,
                cutout: '60%',
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#ccc', padding: 12 }} }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return ctx.label + ': $' + ctx.parsed.toLocaleString('es-CO');
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(REPORTE_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    return REPORTE_PATH


def abrir_reporte(user_id: int):
    """Genera el reporte y lo abre en el navegador."""
    path = generar_reporte_html(user_id)
    if path:
        webbrowser.open(f"file:///{path.replace(os.sep, '/')}")
    return path
