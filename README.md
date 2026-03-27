# 💰 Bot de Finanzas Personales — Telegram

Bot de Telegram que te permite registrar gastos e ingresos usando texto o notas de voz, los clasifica automáticamente con IA local (Ollama) y genera reportes interactivos con gráficas.

**100% local, 100% gratis, sin enviar datos a la nube.**

---

## ✨ Funcionalidades

- **Registro por texto**: Escribe "Gasté 50 mil en comida" y el bot entiende monto, categoría y tipo
- **Registro por voz**: Envía notas de voz y se transcriben automáticamente (requiere Whisper)
- **IA local con Ollama**: Clasifica transacciones sin depender de APIs de pago
- **Reportes interactivos**: Genera un HTML con gráficas Chart.js que abres en tu navegador
- **Gráficas por Telegram**: Pie charts y barras directamente en el chat
- **Moneda COP**: Entiende "50 mil", "200 lucas", "un palo", "1.5M"
- **Inicio automático**: Se puede configurar para arrancar con Windows

---

## 📁 Estructura del Proyecto

```
PROYECTO CONTADOR/
├── .env                    ← Tus tokens (NO compartir)
├── requirements.txt        ← Dependencias Python
├── bot.py                  ← Punto de entrada principal
├── config.py               ← Configuración y constantes
├── database.py             ← Operaciones SQLite
├── ai_processor.py         ← Clasificación con Ollama
├── audio_processor.py      ← Transcripción de voz (Whisper)
├── charts.py               ← Gráficos matplotlib
├── reporte.py              ← Generador de reporte HTML interactivo
├── handlers.py             ← Comandos del bot
├── utils.py                ← Utilidades (formateo COP, fechas)
├── iniciar_bot.bat         ← Script para ejecutar el bot
├── crear_acceso_inicio.bat ← Configura inicio automático en Windows
└── finanzas.db             ← Base de datos SQLite (se crea sola)
```

---

## 🚀 Instalación Paso a Paso

### 1. Requisitos previos

- **Python 3.10+** → [Descargar](https://www.python.org/downloads/) (marcar "Add to PATH" al instalar)
- **Ollama** → [Descargar](https://ollama.com/download) (se instala como cualquier programa)
- **Git** (opcional) → Para clonar el repositorio

### 2. Crear tu bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Elige un nombre (ej: "Mi Contador Personal")
4. Elige un username (ej: `mi_contador_bot`)
5. BotFather te dará un **token** como `123456:ABC-xyz...` → guárdalo

### 3. Descargar el modelo de IA

Abre una terminal y ejecuta:

```bash
ollama pull gemma3:4b
```

Esto descarga el modelo (~3GB, solo la primera vez).

### 4. Instalar dependencias de Python

```bash
cd "ruta/a/PROYECTO CONTADOR"
pip install -r requirements.txt
```

### 5. Configurar el archivo `.env`

Abre el archivo `.env` y reemplaza los valores:

```env
# Tu token de BotFather (paso 2)
TELEGRAM_BOT_TOKEN=PEGA_TU_TOKEN_AQUI

# Ollama (no cambiar a menos que uses otro puerto o modelo)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

### 6. Ejecutar el bot

```bash
python bot.py
```

Deberías ver:

```
Base de datos inicializada.
Bot iniciado. Presiona Ctrl+C para detener.
```

Ahora ve a Telegram, busca tu bot y envía `/start`.

---

## 📱 Comandos Disponibles

| Comando | Qué hace |
|---------|----------|
| `/start` | Muestra bienvenida e instrucciones |
| `/resumen` | Resumen financiero del mes actual |
| `/gastos` | Lista los últimos 10 gastos |
| `/grafica` | Envía pie chart de gastos por categoría |
| `/balance` | Muestra ingresos vs gastos + gráfico de barras |
| `/top` | Top 5 categorías donde más gastas |
| `/reporte` | Genera reporte HTML interactivo con todas las gráficas |
| `/ayuda` | Muestra los comandos disponibles |

### Registrar transacciones

Solo escribe de forma natural:

```
Gasté 50 mil en comida
Pagué 120000 de arriendo
Me ingresaron 2 millones de salario
Uber 15k
Netflix 30 mil
200 lucas en mercado
```

El bot entiende expresiones informales colombianas como "lucas", "un palo", "50k", "1.5M".

---

## ⚙️ Qué Personalizar

### Cambiar el modelo de IA

En `.env`, cambia `OLLAMA_MODEL` por otro modelo de Ollama:

```env
# Más ligero y rápido (~2GB)
OLLAMA_MODEL=gemma3:1b

# Más preciso pero más pesado (~5GB)
OLLAMA_MODEL=gemma3:12b

# Otro modelo que soporte español
OLLAMA_MODEL=llama3.1:8b
```

Recuerda descargar el modelo primero: `ollama pull nombre_del_modelo`

### Cambiar las categorías

En `config.py`, edita la lista `CATEGORIAS`:

```python
CATEGORIAS = [
    "Comida",
    "Transporte",
    "Vivienda",
    # ... agrega o quita las que necesites
    "Gimnasio",
    "Café",
]
```

### Usar con otra moneda

En `config.py`, cambia:

```python
MONEDA = "USD"
SIMBOLO_MONEDA = "$"
```

Y ajusta el prompt en `ai_processor.py` para que interprete montos en tu moneda.

### Usar una API de IA en la nube (OpenAI, Gemini)

Si prefieres usar GPT o Gemini en vez de Ollama:

1. Instala la librería: `pip install openai` o `pip install google-genai`
2. Modifica `ai_processor.py` para usar el cliente correspondiente
3. Agrega tu API key al `.env`

---

## 🖥️ Inicio Automático con Windows

Para que el bot arranque cada vez que enciendas el PC:

1. Haz doble clic en `crear_acceso_inicio.bat`
2. Listo. El bot se ejecutará en segundo plano al iniciar Windows

**Para desactivarlo**, elimina el archivo:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\iniciar_bot_finanzas.vbs
```

O presiona `Win + R`, escribe `shell:startup` y borra el archivo desde ahí.

---

## 🎤 Notas de Voz (Opcional)

Para transcribir notas de voz necesitas instalar Whisper:

```bash
pip install openai-whisper
```

También necesitas **ffmpeg**:
- Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html)
- O instala con: `winget install ffmpeg`

---

## 🔒 Seguridad

- **No compartas tu archivo `.env`** — contiene el token de tu bot
- **No subas `.env` a GitHub** — agrega `.env` a tu `.gitignore`
- Todos los datos se guardan localmente en `finanzas.db`
- La IA corre 100% local con Ollama, tus datos financieros no salen de tu PC

---

## 📊 Sobre el Reporte HTML

El comando `/reporte` genera un archivo HTML interactivo que incluye:

- **Tarjetas resumen**: Ingresos, gastos, balance y mayor categoría de gasto
- **Pie chart**: Distribución de gastos por categoría
- **Gráfica de línea**: Gastos diarios del mes
- **Barras**: Comparación ingresos vs gastos
- **Doughnut chart**: Otra vista de distribución
- **Tabla completa**: Todas las transacciones del mes

Se abre en cualquier navegador. Usa Chart.js para gráficas interactivas con tooltips.

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.10+ |
| Bot | python-telegram-bot v21 |
| IA (clasificación) | Ollama + gemma3:4b |
| IA (voz) | OpenAI Whisper (local) |
| Base de datos | SQLite |
| Gráficos (Telegram) | matplotlib |
| Gráficos (reporte) | Chart.js |
| Moneda | COP (pesos colombianos) |

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| `pip` no se reconoce | Usa `python -m pip install ...` |
| Ollama no responde | Verifica que esté corriendo: `ollama list` |
| Bot no responde en Telegram | Revisa que el token en `.env` sea correcto |
| IA tarda mucho la primera vez | Normal — está cargando el modelo en RAM. Las siguientes serán rápidas |
| Error de asyncio en Python 3.14 | Ya está corregido en `bot.py` con `asyncio.run()` |
| No transcribe audio | Instala Whisper: `pip install openai-whisper` y ffmpeg |

---

## 📝 Licencia

Proyecto personal de código abierto. Úsalo, modifícalo y compártelo libremente.
