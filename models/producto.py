"""Operaciones sobre productos, categorías e inventario."""

from database.db import get_connection
from models import lote as lote_model


# ---------- CATEGORÍAS ----------

def listar_categorias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    conn.close()
    return rows


def crear_categoria(nombre):
    conn = get_connection()
    conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()


# ---------- PRODUCTOS ----------

def listar_productos(solo_activos=True, texto_busqueda=None):
    conn = get_connection()
    query = """
        SELECT p.*, c.nombre AS categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE 1=1
    """
    params = []
    if solo_activos:
        query += " AND p.activo = 1"
    if texto_busqueda:
        query += " AND (p.nombre LIKE ? OR p.codigo_barras LIKE ?)"
        like = f"%{texto_busqueda}%"
        params.extend([like, like])
    query += " ORDER BY p.nombre"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def buscar_por_codigo(codigo_barras):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM productos WHERE codigo_barras = ? AND activo = 1",
        (codigo_barras,),
    ).fetchone()
    conn.close()
    return row


def obtener_producto(producto_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()
    conn.close()
    return row


def crear_producto(codigo_barras, nombre, categoria_id, precio_compra,
                    precio_venta, stock_inicial, stock_minimo, unidad,
                    proveedor_id=None, fecha_caducidad=None, usuario_id=None):
    """
    Crea el producto con stock en cero y, si se indicó una cantidad inicial,
    registra esa cantidad como su primer lote (con o sin caducidad).
    """
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO productos
           (codigo_barras, nombre, categoria_id, proveedor_id, precio_compra,
            precio_venta, stock, stock_minimo, unidad)
           VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
        (codigo_barras or None, nombre, categoria_id, proveedor_id,
         precio_compra, precio_venta, stock_minimo, unidad),
    )
    producto_id = cur.lastrowid
    conn.commit()
    conn.close()

    if stock_inicial and stock_inicial > 0:
        lote_model.registrar_entrada(
            producto_id, stock_inicial, fecha_caducidad=fecha_caducidad,
            costo_unitario=precio_compra, usuario_id=usuario_id,
            motivo="Stock inicial al dar de alta el producto",
        )
    return producto_id


def actualizar_producto(producto_id, **campos):
    """Actualiza cualquier subconjunto de columnas de un producto."""
    if not campos:
        return
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in campos)
    valores = list(campos.values()) + [producto_id]
    conn.execute(f"UPDATE productos SET {sets} WHERE id = ?", valores)
    conn.commit()
    conn.close()


def desactivar_producto(producto_id):
    actualizar_producto(producto_id, activo=0)


def ajustar_stock(producto_id, cantidad_delta, tipo, motivo=None, usuario_id=None):
    """
    Ajusta el stock de un producto y registra el movimiento.
    cantidad_delta: positivo para entradas, negativo para salidas/ventas.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE productos SET stock = stock + ? WHERE id = ?",
        (cantidad_delta, producto_id),
    )
    conn.execute(
        """INSERT INTO movimientos_inventario
           (producto_id, tipo, cantidad, motivo, usuario_id)
           VALUES (?, ?, ?, ?, ?)""",
        (producto_id, tipo, abs(cantidad_delta), motivo, usuario_id),
    )
    conn.commit()
    conn.close()


def productos_stock_bajo():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM productos WHERE stock <= stock_minimo AND activo = 1 ORDER BY stock ASC"
    ).fetchall()
    conn.close()
    return rows


def contar_productos_activos():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) AS n FROM productos WHERE activo = 1").fetchone()["n"]
    conn.close()
    return total
