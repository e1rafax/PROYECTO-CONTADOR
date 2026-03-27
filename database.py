"""
Módulo de base de datos SQLite para el bot de finanzas.
Maneja todas las operaciones CRUD de transacciones.
"""
import sqlite3
from datetime import datetime, date
from config import DATABASE_PATH


def get_connection():
    """Obtiene conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'ingreso')),
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            fecha DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insertar_transaccion(user_id: int, tipo: str, monto: float,
                         categoria: str, descripcion: str, fecha: str = None):
    """Inserta una nueva transacción."""
    if fecha is None:
        fecha = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        """INSERT INTO transacciones (user_id, tipo, monto, categoria, descripcion, fecha)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, tipo, monto, categoria, descripcion, fecha)
    )
    conn.commit()
    conn.close()


def obtener_transacciones(user_id: int, tipo: str = None,
                          fecha_inicio: str = None, fecha_fin: str = None,
                          limite: int = None):
    """Obtiene transacciones con filtros opcionales."""
    query = "SELECT * FROM transacciones WHERE user_id = ?"
    params = [user_id]

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin)

    query += " ORDER BY fecha DESC, created_at DESC"

    if limite:
        query += " LIMIT ?"
        params.append(limite)

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def obtener_gastos_por_categoria(user_id: int, fecha_inicio: str = None,
                                  fecha_fin: str = None):
    """Agrupa gastos por categoría con totales."""
    query = """
        SELECT categoria, SUM(monto) as total, COUNT(*) as cantidad
        FROM transacciones
        WHERE user_id = ? AND tipo = 'gasto'
    """
    params = [user_id]

    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin)

    query += " GROUP BY categoria ORDER BY total DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def obtener_balance(user_id: int, fecha_inicio: str = None, fecha_fin: str = None):
    """Calcula el balance: total ingresos - total gastos."""
    query = """
        SELECT tipo, SUM(monto) as total
        FROM transacciones
        WHERE user_id = ?
    """
    params = [user_id]

    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin)

    query += " GROUP BY tipo"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    resultado = {"ingresos": 0, "gastos": 0, "balance": 0}
    for row in rows:
        if row["tipo"] == "ingreso":
            resultado["ingresos"] = row["total"]
        else:
            resultado["gastos"] = row["total"]

    resultado["balance"] = resultado["ingresos"] - resultado["gastos"]
    return resultado


def obtener_resumen_mensual(user_id: int, year: int = None, month: int = None):
    """Obtiene resumen del mes: gastos, ingresos, top categorías."""
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month

    fecha_inicio = f"{year}-{month:02d}-01"
    # Calcular último día del mes
    if month == 12:
        fecha_fin = f"{year + 1}-01-01"
    else:
        fecha_fin = f"{year}-{month + 1:02d}-01"

    balance = obtener_balance(user_id, fecha_inicio, fecha_fin)
    categorias = obtener_gastos_por_categoria(user_id, fecha_inicio, fecha_fin)
    transacciones = obtener_transacciones(user_id, fecha_inicio=fecha_inicio,
                                           fecha_fin=fecha_fin)

    return {
        "balance": balance,
        "categorias": categorias,
        "total_transacciones": len(transacciones),
        "mes": month,
        "año": year,
    }
