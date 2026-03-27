"""
Utilidades generales: formateo de moneda COP, parsing de fechas.
"""
from datetime import date


def formatear_cop(monto: float) -> str:
    """
    Formatea un número como moneda colombiana.
    Ejemplo: 1500000 → "$1.500.000"
    """
    es_negativo = monto < 0
    monto = abs(monto)
    formateado = f"{monto:,.0f}".replace(",", ".")
    signo = "-" if es_negativo else ""
    return f"{signo}${formateado}"


def nombre_mes(numero: int) -> str:
    """Retorna el nombre del mes en español."""
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }
    return meses.get(numero, "Desconocido")


def rango_mes_actual():
    """Retorna (fecha_inicio, fecha_fin) del mes actual como strings ISO."""
    hoy = date.today()
    inicio = hoy.replace(day=1).isoformat()
    if hoy.month == 12:
        fin = hoy.replace(year=hoy.year + 1, month=1, day=1).isoformat()
    else:
        fin = hoy.replace(month=hoy.month + 1, day=1).isoformat()
    return inicio, fin
