"""Operaciones sobre usuarios y autenticación."""

from database.db import get_connection, hash_password, verify_password


def autenticar(usuario, password):
    """Devuelve el registro del usuario si las credenciales son válidas, o None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE usuario = ? AND activo = 1", (usuario,)
    ).fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return row
    return None


def listar_usuarios():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nombre_completo, usuario, rol, activo FROM usuarios ORDER BY nombre_completo"
    ).fetchall()
    conn.close()
    return rows


def crear_usuario(nombre_completo, usuario, password, rol="cajero"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO usuarios (nombre_completo, usuario, password_hash, rol)
           VALUES (?, ?, ?, ?)""",
        (nombre_completo, usuario, hash_password(password), rol),
    )
    conn.commit()
    conn.close()


def cambiar_password(usuario_id, nueva_password):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET password_hash = ? WHERE id = ?",
        (hash_password(nueva_password), usuario_id),
    )
    conn.commit()
    conn.close()


def desactivar_usuario(usuario_id):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()
