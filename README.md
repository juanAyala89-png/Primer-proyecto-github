# Punto de Venta – Tienda de Abarrotes

Sistema de punto de venta de escritorio, 100% offline, hecho en Python. Este proyecto esta bonito good

## ⚠️ Si ya tenías una versión anterior instalada

Esta versión reorganiza el proyecto en 3 carpetas: `database/`, `models/` y `ui/`.
**No copies estos archivos sueltos dentro de una sola carpeta** (por ejemplo,
todo dentro de `models/`) — eso es lo que causa errores como
`Import "database.py" could not be resolved`.

**La forma correcta de actualizar:**
1. Borra por completo tu carpeta `pos_abarrotes` anterior en VS Code (o el proyecto viejo).
2. Descomprime este ZIP tal cual, respetando las carpetas.
3. Ábrelo de nuevo en VS Code como carpeta raíz del proyecto.

La estructura correcta debe verse así en el Explorador de VS Code:

```
pos_abarrotes/          <- carpeta raíz que abres en VS Code
├── main.py
├── database/
│   ├── db.py
│   └── schema.sql
├── models/
│   ├── producto.py
│   ├── lote.py
│   ├── usuario.py
│   ├── venta.py
│   ├── caja.py
│   └── recarga.py
└── ui/
    ├── theme.py
    ├── grafica.py
    ├── login.py
    ├── main_window.py
    ├── ventas.py
    ├── inventario.py
    ├── reportes.py
    ├── recargas.py
    └── usuarios.py
```

Si `database.py`, `Producto.py`, etc. aparecen **todos en el mismo nivel** dentro
de una sola carpeta `models`, ese es el error: hay que separarlos en sus 3
carpetas correspondientes tal como se muestra arriba.

## ¿Qué incluye esta versión?

- **Punto de venta rediseñado**: ya no es una tabla tipo "caja registradora".
  Ahora el carrito se ve como tarjetas modernas con botones +/− para la
  cantidad, y hay accesos rápidos con los productos más vendidos.
- **Caducidad por lotes**: un mismo producto puede tener varias remesas con
  fechas de caducidad distintas. Al vender, el sistema descuenta primero del
  lote que caduca más pronto (FEFO). Hay alertas de productos por caducar o
  ya vencidos.
- **Recargas de tiempo aire**: pantalla dedicada para registrar recargas
  (Telcel, AT&T, Movistar, Unefon, Otro), con botones de montos comunes y
  registro de la comisión que gana la tienda. Se suman automáticamente al
  corte de caja.
- **Reportes ampliados**: ventas por mes con gráfica de barras, productos más
  vendidos, ventas del día, stock bajo y próximos a caducar, todo en una sola
  pantalla.
- **Usuarios en la misma PC**: cada cajero tiene su propio usuario y
  contraseña. El administrador tiene una pantalla exclusiva (pestaña
  "Usuarios") para crear cajeros, cambiar contraseñas y desactivar usuarios.
- **Diseño renovado**: paleta de colores consistente, tarjetas con esquinas
  redondeadas, y tablas restilizadas — en vez del look gris genérico de
  Tkinter clásico.

## Requisitos

- Python 3.10 o superior instalado ([python.org](https://www.python.org/downloads/)).
  Al instalar en Windows, marca la casilla **"Add Python to PATH"**.

## Instalación (primera vez)

Abre una terminal (CMD o PowerShell) dentro de la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

## Ejecutar el programa

```bash
python main.py
```

### Usuario inicial

| Usuario | Contraseña |
|---------|-----------|
| admin   | admin123  |

**Importante:** cambia esta contraseña en cuanto lo instales en la tienda —
ve a la pestaña **Usuarios**, selecciona `admin` en la tabla y usa
"Cambiar contraseña".

## Primeros pasos recomendados

1. Inicia sesión con `admin`.
2. Ve a **Inventario** y da de alta tus productos. Si el producto tiene
   caducidad (lácteos, embutidos, etc.), captura la fecha al crearlo.
   Para reabastecer un producto que ya existe, selecciónalo en la lista y usa
   "Registrar nueva entrada de mercancía" (ahí puedes poner una fecha de
   caducidad distinta a la del lote anterior).
3. Ve a **Usuarios** y da de alta a tus cajeros con su propio usuario y
   contraseña (así cada quien inicia sesión con su cuenta en la misma PC).
4. Ve a **Reportes y caja** y abre la caja con el fondo inicial del día.
5. Ve a **Punto de venta** y comienza a cobrar, o a **Recargas** para
   registrar tiempo aire.
6. Al final del día, ve a **Reportes y caja** y cierra la caja contando el
   efectivo real (el sistema ya incluye las recargas en efectivo esperado).

## Convertirlo en un .exe (para no depender de tener Python instalado)

Una vez que todo funcione con `python main.py`:

```bash
pyinstaller --name "PuntoDeVenta" --windowed --onefile ^
    --add-data "database/schema.sql;database" main.py
```

(En Mac/Linux usa `:` en vez de `;` en `--add-data`).

El ejecutable quedará en la carpeta `dist/`.

## Estructura del proyecto

```
pos_abarrotes/
├── main.py                    # Punto de entrada
├── database/
│   ├── schema.sql               # Definición de todas las tablas
│   └── db.py                     # Conexión y utilidades (hash de contraseñas, etc.)
├── models/                      # Lógica de negocio (sin interfaz)
│   ├── producto.py                # Productos y categorías
│   ├── lote.py                     # Control de stock por lote y caducidad (FEFO)
│   ├── usuario.py                   # Usuarios y autenticación
│   ├── venta.py                      # Registro de ventas y reportes
│   ├── caja.py                        # Apertura/cierre de caja
│   └── recarga.py                      # Recargas de tiempo aire
└── ui/                          # Interfaz gráfica (CustomTkinter)
    ├── theme.py                   # Colores, fuentes y estilos compartidos
    ├── grafica.py                   # Gráfica de barras (ventas por mes)
    ├── login.py
    ├── main_window.py
    ├── ventas.py
    ├── inventario.py
    ├── recargas.py
    ├── reportes.py
    └── usuarios.py
```

## Ideas para siguientes mejoras

- Impresión de tickets (impresora térmica ESC/POS).
- Compras a proveedores (ya está la tabla `proveedores` en la base de datos).
- Respaldo automático de la base de datos (copiar `pos_abarrotes.db` a una USB
  o a la nube periódicamente).
- Exportar reportes a Excel/PDF.
