"""Operaciones sobre ventas: registrar tickets, consultar historial y reportes."""

import datetime

from database.db import get_connection
from models.lote import registrar_salida_fefo, registrar_entrada


def registrar_venta(carrito, metodo_pago, monto_recibido, usuario_id, corte_caja_id=None):
    """
    carrito: lista de dicts con {producto_id, cantidad, precio_unitario}
    Devuelve el id de la venta creada.
    """
    total = sum(item["cantidad"] * item["precio_unitario"] for item in carrito)
    cambio = round(monto_recibido - total, 2) if metodo_pago == "efectivo" else 0

    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO ventas
           (total, metodo_pago, monto_recibido, cambio, usuario_id, corte_caja_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (total, metodo_pago, monto_recibido, cambio, usuario_id, corte_caja_id),
    )
    venta_id = cur.lastrowid

    for item in carrito:
        subtotal = round(item["cantidad"] * item["precio_unitario"], 2)
        conn.execute(
            """INSERT INTO detalle_ventas
               (venta_id, producto_id, cantidad, precio_unitario, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (venta_id, item["producto_id"], item["cantidad"],
             item["precio_unitario"], subtotal),
        )

    conn.commit()
    conn.close()

    # Descontar inventario: primero de los lotes que caducan más pronto (FEFO)
    for item in carrito:
        registrar_salida_fefo(
            item["producto_id"], item["cantidad"], tipo="venta",
            motivo=f"Venta #{venta_id}", usuario_id=usuario_id,
        )

    return venta_id, total, cambio


def cancelar_venta(venta_id, usuario_id):
    """Marca una venta como cancelada y regresa el stock vendido."""
    conn = get_connection()
    detalle = conn.execute(
        "SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id = ?",
        (venta_id,),
    ).fetchall()
    conn.execute("UPDATE ventas SET estado = 'cancelada' WHERE id = ?", (venta_id,))
    conn.commit()
    conn.close()

    for row in detalle:
        registrar_entrada(
            row["producto_id"], row["cantidad"], fecha_caducidad=None,
            usuario_id=usuario_id, motivo=f"Cancelación venta #{venta_id}",
        )


def detalle_de_venta(venta_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT dv.*, p.nombre AS producto_nombre
           FROM detalle_ventas dv
           JOIN productos p ON dv.producto_id = p.id
           WHERE dv.venta_id = ?""",
        (venta_id,),
    ).fetchall()
    conn.close()
    return rows


def ventas_del_dia(fecha=None):
    """fecha en formato 'YYYY-MM-DD'; si es None, usa hoy (hora local)."""
    conn = get_connection()
    if fecha:
        rows = conn.execute(
            """SELECT * FROM ventas
               WHERE date(fecha) = ? AND estado = 'completada'
               ORDER BY fecha DESC""",
            (fecha,),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM ventas
               WHERE date(fecha) = date('now', 'localtime') AND estado = 'completada'
               ORDER BY fecha DESC"""
        ).fetchall()
    conn.close()
    return rows


def total_ventas_del_dia(fecha=None):
    ventas = ventas_del_dia(fecha)
    return sum(v["total"] for v in ventas)


def productos_mas_vendidos(limite=10, desde=None, hasta=None):
    """
    Top de productos por cantidad vendida.
    desde/hasta: fechas 'YYYY-MM-DD' opcionales para acotar el rango.
    """
    conn = get_connection()
    query = """SELECT p.nombre, SUM(dv.cantidad) AS cantidad_total,
                      SUM(dv.subtotal) AS total_vendido
               FROM detalle_ventas dv
               JOIN productos p ON dv.producto_id = p.id
               JOIN ventas v ON dv.venta_id = v.id
               WHERE v.estado = 'completada'"""
    params = []
    if desde:
        query += " AND date(v.fecha) >= ?"
        params.append(desde)
    if hasta:
        query += " AND date(v.fecha) <= ?"
        params.append(hasta)
    query += " GROUP BY p.id ORDER BY cantidad_total DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def ventas_por_mes(anio):
    """Devuelve una lista de 12 posiciones con el total vendido por mes del año dado."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT strftime('%m', fecha) AS mes, COALESCE(SUM(total), 0) AS total
           FROM ventas
           WHERE strftime('%Y', fecha) = ? AND estado = 'completada'
           GROUP BY mes""",
        (str(anio),),
    ).fetchall()
    conn.close()

    totales = {f"{i:02d}": 0.0 for i in range(1, 13)}
    for r in rows:
        totales[r["mes"]] = r["total"]
    return [totales[f"{i:02d}"] for i in range(1, 13)]


def anios_con_ventas():
    """Lista de años (como texto) en los que hay al menos una venta registrada."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT strftime('%Y', fecha) AS anio FROM ventas ORDER BY anio DESC"
    ).fetchall()
    conn.close()
    anios = [r["anio"] for r in rows if r["anio"]]
    return anios or [str(datetime.date.today().year)]
