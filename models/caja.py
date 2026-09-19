"""Operaciones sobre apertura y cierre de caja (turnos)."""

from database.db import get_connection
from models.recarga import total_recargas_por_corte


def caja_abierta(usuario_id=None):
    """Devuelve el corte de caja abierto actual (o de un usuario), o None."""
    conn = get_connection()
    if usuario_id:
        row = conn.execute(
            "SELECT * FROM cortes_caja WHERE estado = 'abierto' AND usuario_id = ?",
            (usuario_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM cortes_caja WHERE estado = 'abierto' LIMIT 1"
        ).fetchone()
    conn.close()
    return row


def abrir_caja(usuario_id, monto_inicial):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO cortes_caja (usuario_id, monto_inicial)
           VALUES (?, ?)""",
        (usuario_id, monto_inicial),
    )
    conn.commit()
    corte_id = cur.lastrowid
    conn.close()
    return corte_id


def cerrar_caja(corte_id, monto_final_real):
    conn = get_connection()
    corte = conn.execute(
        "SELECT * FROM cortes_caja WHERE id = ?", (corte_id,)
    ).fetchone()

    ventas_efectivo = conn.execute(
        """SELECT COALESCE(SUM(total), 0) AS total FROM ventas
           WHERE corte_caja_id = ? AND metodo_pago = 'efectivo' AND estado = 'completada'""",
        (corte_id,),
    ).fetchone()["total"]

    total_recargas = total_recargas_por_corte(corte_id)
    monto_final_sistema = corte["monto_inicial"] + ventas_efectivo + total_recargas
    diferencia = round(monto_final_real - monto_final_sistema, 2)

    conn.execute(
        """UPDATE cortes_caja
           SET fecha_cierre = datetime('now', 'localtime'),
               monto_final_sistema = ?,
               monto_final_real = ?,
               diferencia = ?,
               estado = 'cerrado'
           WHERE id = ?""",
        (monto_final_sistema, monto_final_real, diferencia, corte_id),
    )
    conn.commit()
    conn.close()
    return monto_final_sistema, diferencia


def resumen_corte(corte_id):
    conn = get_connection()
    resumen = conn.execute(
        """SELECT metodo_pago, COUNT(*) AS num_ventas, COALESCE(SUM(total), 0) AS total
           FROM ventas
           WHERE corte_caja_id = ? AND estado = 'completada'
           GROUP BY metodo_pago""",
        (corte_id,),
    ).fetchall()
    conn.close()
    return resumen
