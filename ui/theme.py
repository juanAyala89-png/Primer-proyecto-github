"""
Tema visual centralizado de la aplicación.
Cambiar los valores aquí actualiza el look de toda la app.
"""

import customtkinter as ctk
from tkinter import ttk


class Color:
    # Verde principal (marca / botones primarios)
    PRIMARY = "#1F7A54"
    PRIMARY_HOVER = "#175E41"
    PRIMARY_LIGHT = "#E6F4EE"

    # Acento para caducidad / advertencias
    WARNING = "#E08A2B"
    WARNING_LIGHT = "#FCEEDD"

    # Peligro (eliminar, vencido, cancelar)
    DANGER = "#D64545"
    DANGER_HOVER = "#B93636"
    DANGER_LIGHT = "#FBE7E7"

    # Info / recargas
    INFO = "#2E6FDB"
    INFO_HOVER = "#2559B0"
    INFO_LIGHT = "#E8EFFC"

    # Neutros
    BG = "#F3F5F2"
    CARD = "#FFFFFF"
    CARD_ALT = "#F8FAF8"
    BORDER = "#E2E5E1"
    TEXT = "#1F2A22"
    TEXT_MUTED = "#6B7568"
    SIDEBAR = "#16281F"
    SIDEBAR_TEXT = "#EAF2ED"
    SIDEBAR_HOVER = "#1F3B2C"
    SIDEBAR_ACTIVE = "#1F7A54"


class Font:
    TITLE = ("Segoe UI", 24, "bold")
    SUBTITLE = ("Segoe UI", 16, "bold")
    HEADING = ("Segoe UI", 14, "bold")
    BODY = ("Segoe UI", 13)
    BODY_BOLD = ("Segoe UI", 13, "bold")
    SMALL = ("Segoe UI", 11)
    TOTAL = ("Segoe UI", 40, "bold")


def aplicar_tema_global():
    """Configura la apariencia base de CustomTkinter (llamar antes de crear cualquier ventana)."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")


def configurar_estilo_ttk():
    """
    Configura el estilo de las tablas (ttk.Treeview). Debe llamarse DESPUÉS
    de que ya exista una ventana Tk/CTk creada, o lanzará un error.
    """
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Treeview",
        background=Color.CARD,
        fieldbackground=Color.CARD,
        foreground=Color.TEXT,
        rowheight=34,
        borderwidth=0,
        font=Font.BODY,
    )
    style.configure(
        "Treeview.Heading",
        background=Color.PRIMARY_LIGHT,
        foreground=Color.PRIMARY,
        font=Font.BODY_BOLD,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", Color.PRIMARY)],
        foreground=[("selected", "#FFFFFF")],
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])


def tarjeta(master, **kwargs):
    """Crea un CTkFrame con look de tarjeta (fondo blanco, esquinas redondeadas)."""
    defaults = dict(fg_color=Color.CARD, corner_radius=14, border_width=1, border_color=Color.BORDER)
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)


def boton_primario(master, **kwargs):
    defaults = dict(fg_color=Color.PRIMARY, hover_color=Color.PRIMARY_HOVER,
                     text_color="#FFFFFF", corner_radius=10, font=Font.BODY_BOLD, height=42)
    defaults.update(kwargs)
    return ctk.CTkButton(master, **defaults)


def boton_peligro(master, **kwargs):
    defaults = dict(fg_color=Color.DANGER, hover_color=Color.DANGER_HOVER,
                     text_color="#FFFFFF", corner_radius=10, font=Font.BODY_BOLD, height=42)
    defaults.update(kwargs)
    return ctk.CTkButton(master, **defaults)


def boton_secundario(master, **kwargs):
    defaults = dict(fg_color="transparent", hover_color=Color.CARD_ALT,
                     text_color=Color.TEXT, border_width=1, border_color=Color.BORDER,
                     corner_radius=10, font=Font.BODY_BOLD, height=42)
    defaults.update(kwargs)
    return ctk.CTkButton(master, **defaults)


def etiqueta_pill(master, texto, color_fondo, color_texto):
    return ctk.CTkLabel(
        master, text=texto, fg_color=color_fondo, text_color=color_texto,
        corner_radius=20, font=Font.SMALL, padx=10, pady=4,
    )
