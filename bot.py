"""
Bot de Finanzas Personales — Punto de entrada principal.
Ejecutar: python bot.py
"""
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from database import init_db
from handlers import (
    cmd_start,
    cmd_ayuda,
    cmd_resumen,
    cmd_gastos,
    cmd_grafica,
    cmd_balance,
    cmd_top,
    cmd_reporte,
    procesar_texto,
    procesar_audio,
)


async def main():
    # Validar token
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Falta TELEGRAM_BOT_TOKEN en el archivo .env")
        print("Crea un archivo .env con:")
        print('  TELEGRAM_BOT_TOKEN=tu_token_aqui')
        print('  GEMINI_API_KEY=tu_api_key_aqui')
        return

    # Inicializar base de datos
    init_db()
    print("Base de datos inicializada.")

    # Crear aplicación del bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CommandHandler("help", cmd_ayuda))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("gastos", cmd_gastos))
    app.add_handler(CommandHandler("grafica", cmd_grafica))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("top", cmd_top))
    app.add_handler(CommandHandler("reporte", cmd_reporte))

    # Handler para notas de voz (debe ir antes del de texto)
    app.add_handler(MessageHandler(filters.VOICE, procesar_audio))

    # Handler para texto libre (cualquier mensaje que no sea comando)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        procesar_texto,
    ))

    print("Bot iniciado. Presiona Ctrl+C para detener.")

    # Iniciar bot manualmente (compatible con Python 3.14)
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # Mantener el bot corriendo hasta Ctrl+C
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await app.updater.stop()
            await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
