"""
Punto de Venta - Tienda de Abarrotes
--------------------------------------
Punto de entrada de la aplicación de escritorio.

Ejecutar con:  python main.py
"""

import customtkinter as ctk

from database.db import init_db
from ui.login import VentanaLogin
from ui.main_window import VentanaPrincipal
from ui.theme import aplicar_tema_global

aplicar_tema_global()


def iniciar_sesion_exitosa(usuario):
    ventana = VentanaPrincipal(usuario)
    ventana.mainloop()


def main():
    init_db()  # crea la base de datos y las tablas si no existen
    login = VentanaLogin(iniciar_sesion_exitosa)
    login.mainloop()


if __name__ == "__main__":
    main()
