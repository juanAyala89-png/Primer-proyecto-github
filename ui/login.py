"""Ventana de inicio de sesión."""

import customtkinter as ctk
from tkinter import messagebox
from models.usuario import autenticar
from ui.theme import Color, Font, tarjeta, boton_primario


class VentanaLogin(ctk.CTk):
    def __init__(self, on_login_exitoso):
        super().__init__()
        self.on_login_exitoso = on_login_exitoso

        self.title("Punto de Venta - Iniciar sesión")
        self.geometry("440x560")
        self.resizable(False, False)
        self.configure(fg_color=Color.BG)

        frame = tarjeta(self, corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        circulo = ctk.CTkFrame(frame, width=80, height=80, corner_radius=40, fg_color=Color.PRIMARY_LIGHT)
        circulo.pack(pady=(40, 0))
        circulo.pack_propagate(False)
        ctk.CTkLabel(circulo, text="🛒", font=("Segoe UI", 34)).pack(expand=True)

        ctk.CTkLabel(
            frame, text="Tienda de Abarrotes", font=Font.TITLE, text_color=Color.TEXT
        ).pack(pady=(15, 0))
        ctk.CTkLabel(
            frame, text="Punto de Venta", font=Font.BODY, text_color=Color.TEXT_MUTED
        ).pack(pady=(0, 25))

        self.entry_usuario = ctk.CTkEntry(
            frame, placeholder_text="Usuario", width=280, height=44,
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, corner_radius=10
        )
        self.entry_usuario.pack(pady=8)
        self.entry_usuario.insert(0, "admin")

        self.entry_password = ctk.CTkEntry(
            frame, placeholder_text="Contraseña", show="*", width=280, height=44,
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, corner_radius=10
        )
        self.entry_password.pack(pady=8)
        self.entry_password.bind("<Return>", lambda e: self.intentar_login())

        boton_primario(frame, text="Iniciar sesión", width=280, height=46,
                        command=self.intentar_login).pack(pady=(20, 5))

        self.label_error = ctk.CTkLabel(frame, text="", text_color=Color.DANGER, font=Font.SMALL)
        self.label_error.pack(pady=(5, 0))

        ctk.CTkLabel(
            frame, text="Usuario inicial: admin / admin123",
            font=Font.SMALL, text_color=Color.TEXT_MUTED
        ).pack(side="bottom", pady=15)

        self.entry_usuario.focus()

    def intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            self.label_error.configure(text="Ingresa usuario y contraseña")
            return

        row = autenticar(usuario, password)
        if row:
            self.destroy()
            self.on_login_exitoso(row)
        else:
            self.label_error.configure(text="Usuario o contraseña incorrectos")
            self.entry_password.delete(0, "end")
