-- =========================================================
-- BASE DE DATOS: Punto de Venta - Tienda de Abarrotes
-- Motor: SQLite
-- =========================================================

PRAGMA foreign_keys = ON;

-- -----------------------------
-- Usuarios del sistema (cajeros, administrador)
-- -----------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('administrador', 'cajero')) DEFAULT 'cajero',
    activo INTEGER NOT NULL DEFAULT 1,
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- -----------------------------
-- Categorías de productos
-- -----------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

-- -----------------------------
-- Proveedores
-- -----------------------------
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    contacto TEXT,
    notas TEXT
);

-- -----------------------------
-- Productos / inventario
-- -----------------------------
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_barras TEXT UNIQUE,
    nombre TEXT NOT NULL,
    categoria_id INTEGER,
    proveedor_id INTEGER,
    precio_compra REAL NOT NULL DEFAULT 0,
    precio_venta REAL NOT NULL DEFAULT 0,
    stock REAL NOT NULL DEFAULT 0,
    stock_minimo REAL NOT NULL DEFAULT 5,
    unidad TEXT NOT NULL DEFAULT 'pieza',   -- pieza, kg, litro, paquete, etc.
    activo INTEGER NOT NULL DEFAULT 1,
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo_barras);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);

-- -----------------------------
-- Cortes de caja (apertura/cierre de turno)
-- -----------------------------
CREATE TABLE IF NOT EXISTS cortes_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_apertura TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_cierre TEXT,
    monto_inicial REAL NOT NULL DEFAULT 0,
    monto_final_sistema REAL,
    monto_final_real REAL,
    diferencia REAL,
    estado TEXT NOT NULL CHECK(estado IN ('abierto', 'cerrado')) DEFAULT 'abierto',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- -----------------------------
-- Ventas (encabezado del ticket)
-- -----------------------------
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    total REAL NOT NULL DEFAULT 0,
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo', 'tarjeta', 'transferencia')) DEFAULT 'efectivo',
    monto_recibido REAL DEFAULT 0,
    cambio REAL DEFAULT 0,
    estado TEXT NOT NULL CHECK(estado IN ('completada', 'cancelada')) DEFAULT 'completada',
    usuario_id INTEGER NOT NULL,
    corte_caja_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (corte_caja_id) REFERENCES cortes_caja(id)
);

CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);

-- -----------------------------
-- Detalle de cada venta (líneas del ticket)
-- -----------------------------
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- -----------------------------
-- Movimientos de inventario (entradas/salidas/ajustes manuales)
-- -----------------------------
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'salida', 'ajuste', 'venta')),
    cantidad REAL NOT NULL,
    motivo TEXT,
    fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    usuario_id INTEGER,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- -----------------------------
-- Lotes de producto (control de caducidad por remesa)
-- Un mismo producto puede tener varios lotes con distinta fecha de caducidad.
-- El stock total del producto siempre es la suma de sus lotes activos.
-- -----------------------------
CREATE TABLE IF NOT EXISTS lotes_producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad REAL NOT NULL DEFAULT 0,
    fecha_caducidad TEXT,          -- NULL = el lote no caduca
    fecha_ingreso TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    costo_unitario REAL,
    activo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_lotes_producto ON lotes_producto(producto_id);
CREATE INDEX IF NOT EXISTS idx_lotes_caducidad ON lotes_producto(fecha_caducidad);

-- -----------------------------
-- Recargas de tiempo aire (Telcel, AT&T, Movistar, etc.)
-- -----------------------------
CREATE TABLE IF NOT EXISTS recargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    compania TEXT NOT NULL,
    numero_telefono TEXT,
    monto REAL NOT NULL,
    comision REAL NOT NULL DEFAULT 0,
    usuario_id INTEGER NOT NULL,
    corte_caja_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (corte_caja_id) REFERENCES cortes_caja(id)
);

CREATE INDEX IF NOT EXISTS idx_recargas_fecha ON recargas(fecha);

-- -----------------------------
-- Datos iniciales (usuario administrador por defecto)
-- Usuario: admin  |  Contraseña: admin123 (cámbiala luego)
-- -----------------------------
INSERT OR IGNORE INTO usuarios (id, nombre_completo, usuario, password_hash, rol)
VALUES (1, 'Administrador', 'admin', 'PLACEHOLDER_HASH', 'administrador');

INSERT OR IGNORE INTO categorias (nombre) VALUES
('Abarrotes'), ('Bebidas'), ('Lácteos'), ('Botanas'), ('Limpieza'), ('Higiene personal'), ('Varios');
