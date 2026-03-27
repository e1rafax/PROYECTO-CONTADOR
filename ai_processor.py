"""
Procesador de texto con Ollama (LLM local).
Clasifica mensajes de texto en transacciones financieras estructuradas.
"""
import json
import requests
from config import OLLAMA_MODEL, OLLAMA_URL, CATEGORIAS

# Prompt compacto para respuestas más rápidas
SYSTEM_PROMPT = f"""Extrae datos financieros del texto. Responde SOLO con JSON puro.
Montos en COP: "50 mil"=50000, "50k"=50000, "1 millón"=1000000, "200 lucas"=200000, "un palo"=1000000.
Categorías válidas: {json.dumps(CATEGORIAS, ensure_ascii=False)}
pagar/gastar/comprar=gasto. recibir/cobrar/salario=ingreso. Si no sabes la categoría usa "Otros".
Formato: {{"tipo":"gasto","monto":50000,"categoria":"Comida","descripcion":"Almuerzo"}}"""


def clasificar_texto(texto: str) -> dict:
    """
    Envía texto a Ollama y retorna la transacción clasificada.

    Returns:
        dict con keys: tipo, monto, categoria, descripcion
        None si no se pudo clasificar
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": texto},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100,
                },
            },
            timeout=120,
        )
        response.raise_for_status()

        contenido = response.json()["message"]["content"].strip()
        print(f"Respuesta Ollama: {contenido}")  # Debug

        # Limpiar posibles backticks de markdown
        if contenido.startswith("```"):
            contenido = contenido.split("\n", 1)[1]
            contenido = contenido.rsplit("```", 1)[0]
            contenido = contenido.strip()

        # Buscar el JSON dentro de la respuesta si hay texto extra
        inicio_json = contenido.find("{")
        fin_json = contenido.rfind("}") + 1
        if inicio_json != -1 and fin_json > inicio_json:
            contenido = contenido[inicio_json:fin_json]

        resultado = json.loads(contenido)

        # Validar campos obligatorios
        campos_requeridos = ["tipo", "monto", "categoria", "descripcion"]
        if not all(campo in resultado for campo in campos_requeridos):
            return None

        if resultado["tipo"] not in ("gasto", "ingreso"):
            return None

        resultado["monto"] = abs(float(resultado["monto"]))

        if resultado["categoria"] not in CATEGORIAS:
            resultado["categoria"] = "Otros"

        return resultado

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error al procesar respuesta de Ollama: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Ollama no está corriendo. Ejecuta 'ollama serve' primero.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Ollama tardó demasiado en responder (timeout 120s).")
        return None
    except Exception as e:
        print(f"Error de conexión con Ollama: {e}")
        return None
