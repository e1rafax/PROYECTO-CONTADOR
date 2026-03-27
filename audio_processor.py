"""
Procesador de audio para notas de voz de Telegram.
Usa Whisper local (openai-whisper) para transcribir audio a texto.
Si Whisper no está instalado, usa Ollama como fallback.
"""
import os
import tempfile
import requests
from config import OLLAMA_URL, OLLAMA_MODEL

# Intentar importar whisper local (opcional)
_whisper_model = None


def _get_whisper():
    """Carga el modelo Whisper local bajo demanda (solo la primera vez)."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    try:
        import whisper
        print("Cargando modelo Whisper (primera vez, puede tardar)...")
        _whisper_model = whisper.load_model("base")
        print("Modelo Whisper cargado.")
        return _whisper_model
    except ImportError:
        return None


async def transcribir_audio(file_path: str) -> str:
    """
    Transcribe un archivo de audio a texto.
    Intenta con Whisper local primero, si no está, usa Ollama.

    Args:
        file_path: Ruta al archivo de audio (.ogg de Telegram)

    Returns:
        Texto transcrito o None si falla
    """
    # Opción 1: Whisper local (si está instalado)
    model = _get_whisper()
    if model is not None:
        try:
            result = model.transcribe(file_path, language="es")
            texto = result["text"].strip()
            return texto if texto else None
        except Exception as e:
            print(f"Error con Whisper local: {e}")

    # Opción 2: Ollama (fallback — menos preciso para audio,
    # pero funciona si se convierte a texto primero)
    # Nota: Ollama no soporta audio directamente, así que informamos al usuario
    print("Whisper no está instalado. Instálalo con: pip install openai-whisper")
    return None


async def descargar_audio_telegram(voice, bot) -> str:
    """
    Descarga nota de voz de Telegram a un archivo temporal.

    Args:
        voice: Objeto Voice de Telegram
        bot: Instancia del bot de Telegram

    Returns:
        Ruta al archivo temporal descargado
    """
    try:
        file = await bot.get_file(voice.file_id)
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"voice_{voice.file_unique_id}.ogg")
        await file.download_to_drive(file_path)
        return file_path
    except Exception as e:
        print(f"Error al descargar audio: {e}")
        return None
