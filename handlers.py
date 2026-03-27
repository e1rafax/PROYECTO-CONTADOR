"""
Handlers de comandos y mensajes del bot de Telegram.
Cada función maneja un comando o tipo de mensaje específico.
"""
import os
from telegram import Update
from telegram.ext import ContextTypes

from ai_processor import clasificar_texto
from audio_processor import transcribir_audio, descargar_audio_telegram
from database import (
    insertar_transaccion,
    obtener_transacciones,
    obtener_gastos_por_categoria,
    obtener_balance,
    obtener_resumen_mensual,
)
from charts import generar_pie_gastos, generar_balance_chart
from reporte import generar_reporte_html
from utils import formatear_cop, nombre_mes, rango_mes_actual


# ============================================================
# /start — Bienvenida
# ============================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida con instrucciones de uso."""
    mensaje = (
        "💰 *Bot de Finanzas Personales*\n\n"
        "¡Hola! Soy tu asistente financiero. Puedo ayudarte a "
        "registrar y analizar tus gastos e ingresos.\n\n"
        "*¿Cómo usarme?*\n"
        "Simplemente escríbeme o envíame una nota de voz con tus gastos:\n"
        "• _Gasté 50 mil en comida_\n"
        "• _Pagué 120000 de arriendo_\n"
        "• _Me ingresaron 2 millones de salario_\n\n"
        "*Comandos disponibles:*\n"
        "/resumen — Resumen del mes actual\n"
        "/gastos — Últimos 10 gastos\n"
        "/grafica — Gráfico de gastos por categoría\n"
        "/balance — Ingresos vs gastos del mes\n"
        "/top — Top categorías con más gasto\n"
        "/reporte — Abre reporte HTML interactivo en tu navegador\n"
        "/ayuda — Ver este mensaje de ayuda\n"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")


# ============================================================
# /ayuda — Igual que start
# ============================================================
async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


# ============================================================
# /resumen — Resumen del mes actual
# ============================================================
async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera resumen financiero del mes actual."""
    user_id = update.effective_user.id
    resumen = obtener_resumen_mensual(user_id)

    if resumen["total_transacciones"] == 0:
        await update.message.reply_text(
            "📊 No tienes transacciones registradas este mes.\n"
            "Envíame un mensaje con tus gastos para empezar."
        )
        return

    balance = resumen["balance"]
    mes = nombre_mes(resumen["mes"])

    # Construir mensaje
    texto = f"📊 *Resumen de {mes} {resumen['año']}*\n\n"
    texto += f"📥 Ingresos: {formatear_cop(balance['ingresos'])}\n"
    texto += f"📤 Gastos: {formatear_cop(balance['gastos'])}\n"
    texto += f"💵 Balance: {formatear_cop(balance['balance'])}\n"
    texto += f"📝 Transacciones: {resumen['total_transacciones']}\n"

    # Top categorías de gasto
    if resumen["categorias"]:
        texto += "\n*Top gastos por categoría:*\n"
        for i, cat in enumerate(resumen["categorias"][:5], 1):
            texto += f"  {i}. {cat['categoria']}: {formatear_cop(cat['total'])}\n"

    await update.message.reply_text(texto, parse_mode="Markdown")


# ============================================================
# /gastos — Últimos 10 gastos
# ============================================================
async def cmd_gastos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista los últimos 10 gastos registrados."""
    user_id = update.effective_user.id
    gastos = obtener_transacciones(user_id, tipo="gasto", limite=10)

    if not gastos:
        await update.message.reply_text("📭 No tienes gastos registrados aún.")
        return

    texto = "📤 *Últimos 10 gastos:*\n\n"
    for g in gastos:
        texto += (
            f"• {g['descripcion']} — {formatear_cop(g['monto'])}\n"
            f"  📁 {g['categoria']} | 📅 {g['fecha']}\n"
        )

    await update.message.reply_text(texto, parse_mode="Markdown")


# ============================================================
# /grafica — Pie chart de gastos
# ============================================================
async def cmd_grafica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera y envía gráfico de gastos por categoría."""
    user_id = update.effective_user.id
    inicio, fin = rango_mes_actual()

    await update.message.reply_text("📊 Generando gráfico...")

    path = generar_pie_gastos(user_id, inicio, fin)
    if path is None:
        await update.message.reply_text(
            "📭 No hay gastos este mes para graficar."
        )
        return

    from datetime import date
    mes_actual = nombre_mes(date.today().month)

    with open(path, "rb") as img:
        await update.message.reply_photo(
            photo=img,
            caption=f"📊 Gastos por categoría — {mes_actual}"
        )

    # Limpiar archivo temporal
    try:
        os.remove(path)
    except OSError:
        pass


# ============================================================
# /balance — Ingresos vs Gastos
# ============================================================
async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra balance del mes y genera gráfico de barras."""
    user_id = update.effective_user.id
    inicio, fin = rango_mes_actual()

    balance = obtener_balance(user_id, inicio, fin)

    from datetime import date
    mes = nombre_mes(date.today().month)
    texto = (
        f"💵 *Balance de {mes}*\n\n"
        f"📥 Ingresos: {formatear_cop(balance['ingresos'])}\n"
        f"📤 Gastos: {formatear_cop(balance['gastos'])}\n"
        f"{'✅' if balance['balance'] >= 0 else '⚠️'} "
        f"Balance: {formatear_cop(balance['balance'])}\n"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

    # Enviar gráfico
    path = generar_balance_chart(user_id, inicio, fin)
    if path:
        with open(path, "rb") as img:
            await update.message.reply_photo(photo=img)
        try:
            os.remove(path)
        except OSError:
            pass


# ============================================================
# /top — Top categorías de gasto
# ============================================================
async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra las 5 categorías con más gasto del mes."""
    user_id = update.effective_user.id
    inicio, fin = rango_mes_actual()
    categorias = obtener_gastos_por_categoria(user_id, inicio, fin)

    if not categorias:
        await update.message.reply_text("📭 No hay gastos registrados este mes.")
        return

    texto = "🏆 *Top categorías de gasto del mes:*\n\n"
    medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, cat in enumerate(categorias[:5]):
        porcentaje = (cat["total"] / sum(c["total"] for c in categorias)) * 100
        texto += (
            f"{medallas[i]} *{cat['categoria']}*\n"
            f"   {formatear_cop(cat['total'])} ({porcentaje:.1f}%) "
            f"— {cat['cantidad']} transacciones\n"
        )

    await update.message.reply_text(texto, parse_mode="Markdown")


# ============================================================
# /reporte — Genera reporte HTML y lo abre en el navegador
# ============================================================
async def cmd_reporte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera reporte HTML interactivo y lo envía como documento."""
    user_id = update.effective_user.id

    await update.message.reply_text("📊 Generando reporte interactivo...")

    path = generar_reporte_html(user_id)
    if path is None:
        await update.message.reply_text("📭 No hay datos para generar el reporte.")
        return

    # Enviar el HTML como documento por Telegram
    with open(path, "rb") as doc:
        await update.message.reply_document(
            document=doc,
            filename="reporte_finanzas.html",
            caption="📊 Abre este archivo en tu navegador para ver el reporte interactivo con gráficas."
        )


# ============================================================
# Handler de texto libre — Procesar con IA
# ============================================================
async def procesar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe texto del usuario, lo clasifica con IA y lo registra."""
    user_id = update.effective_user.id
    texto = update.message.text

    # Ignorar si es muy corto
    if len(texto) < 3:
        return

    await update.message.reply_text("🧠 Procesando con IA local (puede tardar unos segundos)...")

    # Clasificar con Ollama
    resultado = clasificar_texto(texto)

    if resultado is None:
        await update.message.reply_text(
            "❌ No pude entender esa transacción.\n"
            "Intenta algo como: _Gasté 50 mil en comida_",
            parse_mode="Markdown",
        )
        return

    # Guardar en base de datos
    insertar_transaccion(
        user_id=user_id,
        tipo=resultado["tipo"],
        monto=resultado["monto"],
        categoria=resultado["categoria"],
        descripcion=resultado["descripcion"],
    )

    # Confirmar al usuario
    emoji = "📤" if resultado["tipo"] == "gasto" else "📥"
    tipo_texto = resultado["tipo"].capitalize()
    await update.message.reply_text(
        f"✅ *{tipo_texto} registrado*\n\n"
        f"{emoji} Monto: {formatear_cop(resultado['monto'])}\n"
        f"📁 Categoría: {resultado['categoria']}\n"
        f"📝 Descripción: {resultado['descripcion']}",
        parse_mode="Markdown",
    )


# ============================================================
# Handler de audio — Transcribir y procesar
# ============================================================
async def procesar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe nota de voz, la transcribe y la procesa como texto."""
    user_id = update.effective_user.id
    voice = update.message.voice

    await update.message.reply_text("🎤 Transcribiendo audio...")

    # Descargar audio
    file_path = await descargar_audio_telegram(voice, context.bot)
    if file_path is None:
        await update.message.reply_text("❌ No pude descargar el audio.")
        return

    # Transcribir con Gemini
    texto = await transcribir_audio(file_path)

    # Limpiar archivo temporal
    try:
        os.remove(file_path)
    except OSError:
        pass

    if texto is None:
        await update.message.reply_text("❌ No pude transcribir el audio.")
        return

    await update.message.reply_text(f"🎤 Escuché: _{texto}_", parse_mode="Markdown")

    # Procesar el texto transcrito como si fuera un mensaje de texto
    resultado = clasificar_texto(texto)

    if resultado is None:
        await update.message.reply_text(
            "❌ No pude clasificar la transacción del audio.\n"
            "Intenta ser más claro con el monto y la categoría."
        )
        return

    # Guardar en base de datos
    insertar_transaccion(
        user_id=user_id,
        tipo=resultado["tipo"],
        monto=resultado["monto"],
        categoria=resultado["categoria"],
        descripcion=resultado["descripcion"],
    )

    emoji = "📤" if resultado["tipo"] == "gasto" else "📥"
    tipo_texto = resultado["tipo"].capitalize()
    await update.message.reply_text(
        f"✅ *{tipo_texto} registrado*\n\n"
        f"{emoji} Monto: {formatear_cop(resultado['monto'])}\n"
        f"📁 Categoría: {resultado['categoria']}\n"
        f"📝 Descripción: {resultado['descripcion']}",
        parse_mode="Markdown",
    )
