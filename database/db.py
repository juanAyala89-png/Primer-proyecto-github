"""
Módulo de conexión a la base de datos SQLite.
Maneja la conexión única, inicialización del esquema y utilidades
de hash de contraseñas.
"""

import sqlite3
import os
import hashlib
import secrets

# Ruta del archivo de base de datos (se crea junto al programa)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pos_abarrotes.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def hash_password(password: str, salt: str = None) -> str:
    """Genera un hash seguro de contraseña con salt (PBKDF2-SHA256)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"{salt}${hash_bytes.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica una contraseña contra el hash guardado."""
    try:
        salt, _ = stored_hash.split("$")
    except ValueError:
        return False
    return hash_password(password, salt) == stored_hash


def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos con foreign keys activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen y asegura el usuario administrador inicial."""
    is_new = not os.path.exists(DB_PATH)

    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        script = f.read()
    conn.executescript(script)
    conn.commit()

    # Si el admin quedó con el hash de plantilla, generamos uno real
    cur = conn.execute(
        "SELECT id, password_hash FROM usuarios WHERE usuario = 'admin'"
    )
    row = cur.fetchone()
    if row and row["password_hash"] == "PLACEHOLDER_HASH":
        real_hash = hash_password("admin123")
        conn.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?",
            (real_hash, row["id"]),
        )
        conn.commit()

    conn.close()
    return is_new
