"""
Configuración central del bot de finanzas personales.
Carga variables de entorno y define constantes del sistema.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# === Tokens ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# === Ollama (LLM local) ===
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# === Base de datos ===
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "finanzas.db")

# === Categorías válidas ===
CATEGORIAS = [
    "Comida",
    "Transporte",
    "Vivienda",
    "Servicios",       # Agua, luz, gas, internet, celular
    "Salud",
    "Educación",
    "Entretenimiento",
    "Ropa",
    "Tecnología",
    "Deudas",          # Créditos, préstamos
    "Ahorro",
    "Mascotas",
    "Regalos",
    "Suscripciones",   # Netflix, Spotify, etc.
    "Otros",
]

# === Tipos de transacción ===
TIPO_GASTO = "gasto"
TIPO_INGRESO = "ingreso"

# === Moneda ===
MONEDA = "COP"
SIMBOLO_MONEDA = "$"
