"""
Control de stock por lotes, para poder rastrear fechas de caducidad.

Regla de negocio: al vender o dar salida a un producto, se descuenta primero
del lote que caduca más pronto (FEFO: First-Expired, First-Out). Los lotes
sin fecha de caducidad se consumen al final.
"""

from database.db import get_connection


def registrar_entrada(producto_id, cantidad, fecha_caducidad=None,
                       costo_unitario=None, usuario_id=None, motivo="Entrada de mercancía"):
    """Crea un nuevo lote y aumenta el stock total del producto."""
    if cantidad <= 0:
        return

    conn = get_connection()
    conn.execute(
        """INSERT INTO lotes_producto (producto_id, cantidad, fecha_caducidad, costo_unitario)
           VALUES (?, ?, ?, ?)""",
        (producto_id, cantidad, fecha_caducidad or None, costo_unitario),
    )
    conn.execute(
        "UPDATE productos SET stock = stock + ? WHERE id = ?",
        (cantidad, producto_id),
    )
    conn.execute(
        """INSERT INTO movimientos_inventario
           (producto_id, tipo, cantidad, motivo, usuario_id)
           VALUES (?, 'entrada', ?, ?, ?)""",
        (producto_id, cantidad, motivo, usuario_id),
    )
    conn.commit()
    conn.close()


def registrar_salida_fefo(producto_id, cantidad, tipo="salida",
                           motivo=None, usuario_id=None):
    """
    Descuenta `cantidad` del producto, tomando primero de los lotes que
    caducan más pronto. Si no hay lotes suficientes, se descuenta el
    resto directo del stock general (para no bloquear una venta).
    """
    if cantidad <= 0:
        return

    conn = get_connection()
    lotes = conn.execute(
        """SELECT * FROM lotes_producto
           WHERE producto_id = ? AND activo = 1 AND cantidad > 0
           ORDER BY (fecha_caducidad IS NULL), fecha_caducidad ASC, fecha_ingreso ASC""",
        (producto_id,),
    ).fetchall()

    restante = cantidad
    for lote in lotes:
        if restante <= 0:
            break
        tomar = min(lote["cantidad"], restante)
        nueva_cantidad = lote["cantidad"] - tomar
        conn.execute(
            "UPDATE lotes_producto SET cantidad = ?, activo = ? WHERE id = ?",
            (nueva_cantidad, 0 if nueva_cantidad <= 0 else 1, lote["id"]),
        )
        restante -= tomar

    conn.execute(
        "UPDATE productos SET stock = MAX(0, stock - ?) WHERE id = ?",
        (cantidad, producto_id),
    )
    conn.execute(
        """INSERT INTO movimientos_inventario
           (producto_id, tipo, cantidad, motivo, usuario_id)
           VALUES (?, ?, ?, ?, ?)""",
        (producto_id, tipo, cantidad, motivo, usuario_id),
    )
    conn.commit()
    conn.close()


def listar_lotes(producto_id, solo_activos=True):
    conn = get_connection()
    query = "SELECT * FROM lotes_producto WHERE producto_id = ?"
    if solo_activos:
        query += " AND activo = 1 AND cantidad > 0"
    query += " ORDER BY (fecha_caducidad IS NULL), fecha_caducidad ASC"
    rows = conn.execute(query, (producto_id,)).fetchall()
    conn.close()
    return rows


def lotes_por_caducar(dias=7):
    """Lotes activos que caducan dentro de los próximos `dias` días (o ya caducaron)."""
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT l.*, p.nombre AS producto_nombre, p.unidad
            FROM lotes_producto l
            JOIN productos p ON l.producto_id = p.id
            WHERE l.activo = 1 AND l.cantidad > 0
              AND l.fecha_caducidad IS NOT NULL
              AND date(l.fecha_caducidad) <= date('now', 'localtime', '+{int(dias)} days')
            ORDER BY l.fecha_caducidad ASC"""
    ).fetchall()
    conn.close()
    return rows


def dar_de_baja_lote(lote_id, motivo="Merma por caducidad", usuario_id=None):
    """Da de baja un lote completo (por ejemplo, producto caducado que se tira)."""
    conn = get_connection()
    lote = conn.execute("SELECT * FROM lotes_producto WHERE id = ?", (lote_id,)).fetchone()
    if not lote or lote["cantidad"] <= 0:
        conn.close()
        return

    conn.execute(
        "UPDATE lotes_producto SET cantidad = 0, activo = 0 WHERE id = ?", (lote_id,)
    )
    conn.execute(
        "UPDATE productos SET stock = MAX(0, stock - ?) WHERE id = ?",
        (lote["cantidad"], lote["producto_id"]),
    )
    conn.execute(
        """INSERT INTO movimientos_inventario
           (producto_id, tipo, cantidad, motivo, usuario_id)
           VALUES (?, 'salida', ?, ?, ?)""",
        (lote["producto_id"], lote["cantidad"], motivo, usuario_id),
    )
    conn.commit()
    conn.close()
