"""Registro de recargas de tiempo aire (Telcel, AT&T, Movistar, etc.)."""

from database.db import get_connection

COMPANIAS = ["Telcel", "AT&T", "Movistar", "Unefon", "Otro"]


def registrar_recarga(compania, monto, comision, usuario_id,
                       corte_caja_id=None, numero_telefono=None):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO recargas
           (compania, numero_telefono, monto, comision, usuario_id, corte_caja_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (compania, numero_telefono or None, monto, comision, usuario_id, corte_caja_id),
    )
    conn.commit()
    recarga_id = cur.lastrowid
    conn.close()
    return recarga_id


def recargas_del_dia(fecha=None):
    conn = get_connection()
    if fecha:
        rows = conn.execute(
            "SELECT * FROM recargas WHERE date(fecha) = ? ORDER BY fecha DESC", (fecha,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM recargas WHERE date(fecha) = date('now', 'localtime') ORDER BY fecha DESC"
        ).fetchall()
    conn.close()
    return rows


def totales_recargas_del_dia(fecha=None):
    recargas = recargas_del_dia(fecha)
    total_monto = sum(r["monto"] for r in recargas)
    total_comision = sum(r["comision"] for r in recargas)
    return total_monto, total_comision, len(recargas)


def total_recargas_por_corte(corte_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(monto), 0) AS total FROM recargas WHERE corte_caja_id = ?",
        (corte_id,),
    ).fetchone()
    conn.close()
    return row["total"]


def recargas_por_mes(anio):
    conn = get_connection()
    rows = conn.execute(
        """SELECT strftime('%m', fecha) AS mes, COALESCE(SUM(monto), 0) AS total,
                  COALESCE(SUM(comision), 0) AS comision
           FROM recargas
           WHERE strftime('%Y', fecha) = ?
           GROUP BY mes""",
        (str(anio),),
    ).fetchall()
    conn.close()

    totales = {f"{i:02d}": 0.0 for i in range(1, 13)}
    comisiones = {f"{i:02d}": 0.0 for i in range(1, 13)}
    for r in rows:
        totales[r["mes"]] = r["total"]
        comisiones[r["mes"]] = r["comision"]
    return (
        [totales[f"{i:02d}"] for i in range(1, 13)],
        [comisiones[f"{i:02d}"] for i in range(1, 13)],
    )
