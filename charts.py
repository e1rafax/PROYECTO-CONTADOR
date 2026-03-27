"""
Generador de gráficos para reportes financieros.
Usa matplotlib para crear visualizaciones y exportar como PNG.
"""
import os
import tempfile
import matplotlib
matplotlib.use("Agg")  # Backend sin GUI para servidores
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from database import obtener_gastos_por_categoria, obtener_balance


def _formatear_cop(valor, _pos=None):
    """Formatea un número como moneda COP: $1.234.567"""
    if valor >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"
    elif valor >= 1_000:
        return f"${valor / 1_000:.0f}K"
    return f"${valor:,.0f}"


def generar_pie_gastos(user_id: int, fecha_inicio: str = None,
                        fecha_fin: str = None) -> str:
    """
    Genera un pie chart de gastos por categoría.

    Returns:
        Ruta al archivo PNG generado
    """
    datos = obtener_gastos_por_categoria(user_id, fecha_inicio, fecha_fin)

    if not datos:
        return None

    categorias = [d["categoria"] for d in datos]
    totales = [d["total"] for d in datos]

    # Colores para las categorías
    colores = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
        "#F8C471", "#82E0AA", "#F1948A", "#AED6F1", "#D5DBDB",
    ]

    fig, ax = plt.subplots(figsize=(10, 7))

    # Crear pie chart con porcentajes y valores
    def make_label(pct, allvals):
        absoluto = int(round(pct / 100.0 * sum(allvals)))
        return f"{pct:.1f}%\n({_formatear_cop(absoluto)})"

    wedges, texts, autotexts = ax.pie(
        totales,
        labels=categorias,
        autopct=lambda pct: make_label(pct, totales),
        colors=colores[:len(categorias)],
        startangle=140,
        textprops={"fontsize": 9},
    )

    # Estilo de los textos
    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_fontweight("bold")

    ax.set_title("Gastos por Categoría", fontsize=14, fontweight="bold", pad=20)

    total_general = sum(totales)
    fig.text(0.5, 0.02, f"Total: {_formatear_cop(total_general)}",
             ha="center", fontsize=11, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0"))

    plt.tight_layout()

    # Guardar como imagen temporal
    path = os.path.join(tempfile.gettempdir(), f"pie_gastos_{user_id}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return path


def generar_balance_chart(user_id: int, fecha_inicio: str = None,
                           fecha_fin: str = None) -> str:
    """
    Genera gráfico de barras: Ingresos vs Gastos.

    Returns:
        Ruta al archivo PNG generado
    """
    balance = obtener_balance(user_id, fecha_inicio, fecha_fin)

    if balance["ingresos"] == 0 and balance["gastos"] == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))

    categorias_bar = ["Ingresos", "Gastos", "Balance"]
    valores = [balance["ingresos"], balance["gastos"], balance["balance"]]
    colores = ["#2ecc71", "#e74c3c",
               "#3498db" if balance["balance"] >= 0 else "#e67e22"]

    bars = ax.bar(categorias_bar, valores, color=colores, width=0.5, edgecolor="white")

    # Agregar valores encima de las barras
    for bar, valor in zip(bars, valores):
        y_pos = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., y_pos,
                _formatear_cop(abs(valor)),
                ha="center", va="bottom", fontweight="bold", fontsize=11)

    ax.set_title("Ingresos vs Gastos", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_formatear_cop))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(y=0, color="gray", linewidth=0.5)

    plt.tight_layout()

    path = os.path.join(tempfile.gettempdir(), f"balance_{user_id}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return path
