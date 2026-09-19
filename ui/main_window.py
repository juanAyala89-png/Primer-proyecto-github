"""Ventana principal de la aplicación, con barra lateral de navegación."""

import customtkinter as ctk

from ui.ventas import FramePuntoDeVenta
from ui.inventario import FrameInventario
from ui.reportes import FrameReportes
from ui.recargas import FrameRecargas
from ui.usuarios import FrameUsuarios
from ui.theme import Color, Font, configurar_estilo_ttk


class VentanaPrincipal(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        configurar_estilo_ttk()
        self.usuario = usuario
        self.configure(fg_color=Color.BG)

        self.title(f"Punto de Venta - Tienda de Abarrotes  |  Sesión: {usuario['nombre_completo']}")
        self.geometry("1280x760")
        self.minsize(1050, 680)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_contenedor()

        self.mostrar_frame("ventas")

    def _construir_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=Color.SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="🛒 Abarrotes", font=("Segoe UI", 20, "bold"), text_color=Color.SIDEBAR_TEXT
        ).pack(pady=(30, 5))
        ctk.CTkLabel(
            sidebar, text=self.usuario["nombre_completo"],
            font=Font.SMALL, text_color="#9FB3A6"
        ).pack(pady=(0, 5))
        ctk.CTkLabel(
            sidebar, text=self.usuario["rol"].capitalize(),
            font=("Segoe UI", 10), text_color=Color.PRIMARY, fg_color="#0F1D15",
            corner_radius=10, padx=10, pady=2
        ).pack(pady=(0, 25))

        self.botones_nav = {}
        opciones = [
            ("ventas", "🧾  Punto de venta"),
            ("inventario", "📦  Inventario"),
            ("recargas", "📱  Recargas"),
            ("reportes", "📊  Reportes y caja"),
        ]
        if self.usuario["rol"] == "administrador":
            opciones.append(("usuarios", "👥  Usuarios"))

        for clave, texto in opciones:
            btn = ctk.CTkButton(
                sidebar, text=texto, anchor="w", height=44,
                fg_color="transparent", text_color=Color.SIDEBAR_TEXT,
                hover_color=Color.SIDEBAR_HOVER, corner_radius=10,
                font=Font.BODY_BOLD,
                command=lambda k=clave: self.mostrar_frame(k)
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.botones_nav[clave] = btn

        ctk.CTkButton(
            sidebar, text="Cerrar sesión", fg_color="transparent", border_width=1,
            border_color="#3A5346", text_color=Color.SIDEBAR_TEXT, hover_color=Color.SIDEBAR_HOVER,
            corner_radius=10, command=self.cerrar_sesion
        ).pack(side="bottom", fill="x", padx=15, pady=20)

    def _construir_contenedor(self):
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}

    def mostrar_frame(self, clave):
        for k, btn in self.botones_nav.items():
            btn.configure(fg_color=Color.SIDEBAR_ACTIVE if k == clave else "transparent")

        for f in self.frames.values():
            f.grid_forget()

        if clave not in self.frames:
            if clave == "ventas":
                self.frames[clave] = FramePuntoDeVenta(self.contenedor, self.usuario)
            elif clave == "inventario":
                self.frames[clave] = FrameInventario(self.contenedor, self.usuario)
            elif clave == "recargas":
                self.frames[clave] = FrameRecargas(self.contenedor, self.usuario)
            elif clave == "reportes":
                self.frames[clave] = FrameReportes(self.contenedor, self.usuario)
            elif clave == "usuarios":
                self.frames[clave] = FrameUsuarios(self.contenedor, self.usuario)

        self.frames[clave].grid(row=0, column=0, sticky="nsew")

        # Refrescar datos que pueden haber cambiado en otra pestaña
        if clave == "reportes":
            self.frames[clave].refrescar()
        elif clave == "inventario":
            self.frames[clave].cargar_productos()
        elif clave == "recargas":
            self.frames[clave].refrescar()
        elif clave == "usuarios":
            self.frames[clave].cargar_usuarios()
        elif clave == "ventas":
            self.frames[clave]._cargar_accesos_rapidos()

    def cerrar_sesion(self):
        self.destroy()
        from ui.login import VentanaLogin

        def al_iniciar(usuario):
            ventana = VentanaPrincipal(usuario)
            ventana.mainloop()

        login = VentanaLogin(al_iniciar)
        login.mainloop()
