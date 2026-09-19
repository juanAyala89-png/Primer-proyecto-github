"""Pestaña de Usuarios: alta de cajeros y administradores (solo admin)."""

import customtkinter as ctk
from tkinter import messagebox, ttk

from models.usuario import listar_usuarios, crear_usuario, desactivar_usuario, cambiar_password
from ui.theme import Color, Font, tarjeta, boton_primario, boton_peligro


class FrameUsuarios(ctk.CTkFrame):
    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self._construir_ui()
        self.cargar_usuarios()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        col_izq = tarjeta(self)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        col_izq.grid_rowconfigure(1, weight=1)
        col_izq.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(col_izq, text="👥 Usuarios del sistema", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .grid(row=0, column=0, sticky="w", padx=15, pady=15)

        tabla_frame = ctk.CTkFrame(col_izq, fg_color="transparent")
        tabla_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        columnas = ("nombre", "usuario", "rol", "activo")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=14)
        for col, texto, ancho in [
            ("nombre", "Nombre completo", 220), ("usuario", "Usuario", 140),
            ("rol", "Rol", 120), ("activo", "Estado", 100),
        ]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="w" if col == "nombre" else "center")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        col_der = tarjeta(self)
        col_der.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(col_der, text="Nuevo usuario / cajero", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(20, 15))

        self.entry_nombre = self._campo(col_der, "Nombre completo")
        self.entry_usuario = self._campo(col_der, "Usuario (para iniciar sesión)")
        self.entry_password = self._campo(col_der, "Contraseña", mostrar="*")

        ctk.CTkLabel(col_der, text="Rol", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_rol = ctk.CTkComboBox(col_der, values=["cajero", "administrador"],
                                          fg_color=Color.CARD_ALT, border_color=Color.BORDER)
        self.combo_rol.set("cajero")
        self.combo_rol.pack(fill="x", padx=20, pady=(0, 20))

        boton_primario(col_der, text="Crear usuario", height=46, command=self.crear)\
            .pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(col_der, text="Usuario seleccionado", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(20, 0))
        self.entry_nueva_password = ctk.CTkEntry(
            col_der, placeholder_text="Nueva contraseña", show="*",
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40
        )
        self.entry_nueva_password.pack(fill="x", padx=20, pady=(8, 8))
        boton_primario(col_der, text="Cambiar contraseña", height=40,
                        command=self.cambiar_password_usuario).pack(fill="x", padx=20, pady=(0, 8))
        boton_peligro(col_der, text="Desactivar usuario", height=40,
                      command=self.desactivar).pack(fill="x", padx=20, pady=(0, 20))

    def _campo(self, parent, label, mostrar=None):
        ctk.CTkLabel(parent, text=label, font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(5, 0))
        kwargs = {"show": mostrar} if mostrar else {}
        entry = ctk.CTkEntry(parent, fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40, **kwargs)
        entry.pack(fill="x", padx=20, pady=(0, 5))
        return entry

    def cargar_usuarios(self):
        self.tabla.delete(*self.tabla.get_children())
        self._cache = {}
        for u in listar_usuarios():
            self.tabla.insert("", "end", iid=str(u["id"]), values=(
                u["nombre_completo"], u["usuario"], u["rol"],
                "Activo" if u["activo"] else "Inactivo"
            ))
            self._cache[str(u["id"])] = u

    def al_seleccionar(self, event=None):
        seleccion = self.tabla.selection()
        self.usuario_seleccionado_id = int(seleccion[0]) if seleccion else None

    def crear(self):
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()
        rol = self.combo_rol.get()

        if not nombre or not usuario or not password:
            messagebox.showwarning("Datos incompletos", "Completa nombre, usuario y contraseña.")
            return
        if len(password) < 4:
            messagebox.showwarning("Contraseña muy corta", "Usa al menos 4 caracteres.")
            return

        try:
            crear_usuario(nombre, usuario, password, rol)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el usuario (¿el usuario ya existe?).\n\n{e}")
            return

        messagebox.showinfo("Listo", f"Usuario '{usuario}' creado correctamente.")
        self.entry_nombre.delete(0, "end")
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.cargar_usuarios()

    def cambiar_password_usuario(self):
        if not getattr(self, "usuario_seleccionado_id", None):
            messagebox.showwarning("Sin selección", "Selecciona un usuario de la lista.")
            return
        nueva = self.entry_nueva_password.get()
        if len(nueva) < 4:
            messagebox.showwarning("Contraseña muy corta", "Usa al menos 4 caracteres.")
            return
        cambiar_password(self.usuario_seleccionado_id, nueva)
        self.entry_nueva_password.delete(0, "end")
        messagebox.showinfo("Listo", "Contraseña actualizada.")

    def desactivar(self):
        if not getattr(self, "usuario_seleccionado_id", None):
            messagebox.showwarning("Sin selección", "Selecciona un usuario de la lista.")
            return
        if self.usuario_seleccionado_id == self.usuario["id"]:
            messagebox.showwarning("No permitido", "No puedes desactivar tu propio usuario.")
            return
        if messagebox.askyesno("Confirmar", "¿Desactivar este usuario? Ya no podrá iniciar sesión."):
            desactivar_usuario(self.usuario_seleccionado_id)
            self.cargar_usuarios()
