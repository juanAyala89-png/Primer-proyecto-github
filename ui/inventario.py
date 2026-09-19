"""Pestaña de Inventario: alta, edición, precios y caducidad de productos."""

import customtkinter as ctk
from tkinter import messagebox, ttk

from models.producto import (
    listar_productos, crear_producto, actualizar_producto,
    desactivar_producto, listar_categorias, crear_categoria,
)
from models.lote import listar_lotes, registrar_entrada, dar_de_baja_lote
from ui.theme import Color, Font, tarjeta, boton_primario, boton_secundario, boton_peligro


class FrameInventario(ctk.CTkFrame):
    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.producto_seleccionado_id = None

        self._construir_ui()
        self.cargar_productos()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------- Columna izquierda: lista de productos ----------
        col_izq = tarjeta(self)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        col_izq.grid_rowconfigure(1, weight=1)
        col_izq.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(col_izq, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        top.grid_columnconfigure(0, weight=1)

        self.entry_buscar = ctk.CTkEntry(
            top, placeholder_text="🔍  Buscar producto por nombre o código...",
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=38
        )
        self.entry_buscar.grid(row=0, column=0, sticky="ew")
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.cargar_productos())

        boton_primario(top, text="+ Nuevo", width=110, height=38, command=self.limpiar_formulario)\
            .grid(row=0, column=1, padx=(10, 0))

        tabla_frame = ctk.CTkFrame(col_izq, fg_color="transparent")
        tabla_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "categoria", "precio", "stock")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=16)
        for col, texto, ancho in [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 210),
            ("categoria", "Categoría", 110),
            ("precio", "Precio", 90),
            ("stock", "Stock", 70),
        ]:
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="w" if col == "nombre" else "center")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # ---------- Columna derecha: formulario + caducidad ----------
        col_der = ctk.CTkScrollableFrame(self, corner_radius=14, label_text="Datos del producto",
                                          fg_color=Color.CARD, label_text_color=Color.TEXT)
        col_der.grid(row=0, column=1, sticky="nsew")

        self.entry_nombre = self._campo(col_der, "Nombre*")
        self.entry_codigo = self._campo(col_der, "Código de barras")

        ctk.CTkLabel(col_der, text="Categoría", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(10, 0))
        self.categorias_map = {c["nombre"]: c["id"] for c in listar_categorias()}
        self.combo_categoria = ctk.CTkComboBox(col_der, values=list(self.categorias_map.keys()),
                                                fg_color=Color.CARD_ALT, border_color=Color.BORDER)
        self.combo_categoria.pack(fill="x", padx=15, pady=(0, 5))

        self.entry_precio_compra = self._campo(col_der, "Precio de compra")
        self.entry_precio_venta = self._campo(col_der, "Precio de venta*")
        self.entry_stock_minimo = self._campo(col_der, "Stock mínimo (alerta)")
        self.entry_unidad = self._campo(col_der, "Unidad (pieza, kg, litro...)")
        self.entry_unidad.insert(0, "pieza")

        # --- Solo visible al crear un producto nuevo ---
        self.frame_stock_inicial = ctk.CTkFrame(col_der, fg_color=Color.PRIMARY_LIGHT, corner_radius=10)
        ctk.CTkLabel(self.frame_stock_inicial, text="Stock inicial (solo al crear)",
                     font=Font.BODY_BOLD, text_color=Color.PRIMARY).pack(anchor="w", padx=12, pady=(10, 0))
        self.entry_stock_inicial = ctk.CTkEntry(self.frame_stock_inicial, placeholder_text="Cantidad",
                                                 fg_color=Color.CARD, border_color=Color.BORDER)
        self.entry_stock_inicial.pack(fill="x", padx=12, pady=6)
        self.entry_caducidad_inicial = ctk.CTkEntry(
            self.frame_stock_inicial, placeholder_text="Fecha de caducidad (AAAA-MM-DD, opcional)",
            fg_color=Color.CARD, border_color=Color.BORDER
        )
        self.entry_caducidad_inicial.pack(fill="x", padx=12, pady=(0, 12))
        self.frame_stock_inicial.pack(fill="x", padx=15, pady=10)

        botones = ctk.CTkFrame(col_der, fg_color="transparent")
        self.botones_frame = botones
        botones.pack(fill="x", padx=15, pady=20)
        boton_primario(botones, text="Guardar", command=self.guardar).pack(side="left", expand=True, fill="x", padx=(0, 5))
        boton_peligro(botones, text="Desactivar", command=self.desactivar).pack(side="left", expand=True, fill="x", padx=(5, 0))

        # --- Sección de caducidad / lotes (solo al editar) ---
        self.frame_lotes = ctk.CTkFrame(col_der, fg_color="transparent")
        ctk.CTkLabel(self.frame_lotes, text="📅 Lotes y caducidad", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(10, 5))

        self.lista_lotes = ctk.CTkFrame(self.frame_lotes, fg_color="transparent")
        self.lista_lotes.pack(fill="x", padx=15)

        entrada_card = ctk.CTkFrame(self.frame_lotes, fg_color=Color.CARD_ALT, corner_radius=10)
        entrada_card.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(entrada_card, text="Registrar nueva entrada de mercancía",
                     font=Font.BODY_BOLD, text_color=Color.TEXT).pack(anchor="w", padx=12, pady=(10, 5))

        fila1 = ctk.CTkFrame(entrada_card, fg_color="transparent")
        fila1.pack(fill="x", padx=12)
        self.entry_nueva_cantidad = ctk.CTkEntry(fila1, placeholder_text="Cantidad",
                                                  fg_color=Color.CARD, border_color=Color.BORDER)
        self.entry_nueva_cantidad.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.entry_nueva_caducidad = ctk.CTkEntry(fila1, placeholder_text="Caducidad AAAA-MM-DD (opcional)",
                                                   fg_color=Color.CARD, border_color=Color.BORDER)
        self.entry_nueva_caducidad.pack(side="left", expand=True, fill="x", padx=(5, 0))

        boton_primario(entrada_card, text="Agregar lote al inventario", height=36,
                        command=self.registrar_nuevo_lote).pack(fill="x", padx=12, pady=12)

    def _campo(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(10, 0))
        entry = ctk.CTkEntry(parent, fg_color=Color.CARD_ALT, border_color=Color.BORDER)
        entry.pack(fill="x", padx=15, pady=(0, 5))
        return entry

    # ---------------------------------------------------------
    def cargar_productos(self):
        texto = self.entry_buscar.get().strip() or None
        self.tabla.delete(*self.tabla.get_children())
        self._productos_cache = {}
        for p in listar_productos(texto_busqueda=texto):
            self.tabla.insert("", "end", iid=str(p["id"]), values=(
                p["codigo_barras"] or "-", p["nombre"], p["categoria_nombre"] or "-",
                f"${p['precio_venta']:.2f}", p["stock"]
            ))
            self._productos_cache[str(p["id"])] = p

    def al_seleccionar(self, event=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        p = self._productos_cache[seleccion[0]]
        self.producto_seleccionado_id = p["id"]

        self.entry_nombre.delete(0, "end"); self.entry_nombre.insert(0, p["nombre"])
        self.entry_codigo.delete(0, "end"); self.entry_codigo.insert(0, p["codigo_barras"] or "")
        self.combo_categoria.set(p["categoria_nombre"] or "")
        self.entry_precio_compra.delete(0, "end"); self.entry_precio_compra.insert(0, str(p["precio_compra"]))
        self.entry_precio_venta.delete(0, "end"); self.entry_precio_venta.insert(0, str(p["precio_venta"]))
        self.entry_stock_minimo.delete(0, "end"); self.entry_stock_minimo.insert(0, str(p["stock_minimo"]))
        self.entry_unidad.delete(0, "end"); self.entry_unidad.insert(0, p["unidad"])

        self.frame_stock_inicial.pack_forget()
        self.frame_lotes.pack(fill="both", expand=True, after=self.botones_frame)
        self._cargar_lotes(p["id"])

    def _cargar_lotes(self, producto_id):
        for w in self.lista_lotes.winfo_children():
            w.destroy()

        lotes = listar_lotes(producto_id)
        if not lotes:
            ctk.CTkLabel(self.lista_lotes, text="Sin lotes registrados todavía.",
                         text_color=Color.TEXT_MUTED, font=Font.SMALL).pack(anchor="w", pady=5)
            return

        from datetime import date
        hoy = date.today()

        for lote in lotes:
            fila = ctk.CTkFrame(self.lista_lotes, fg_color=Color.CARD_ALT, corner_radius=8)
            fila.pack(fill="x", pady=3)

            if lote["fecha_caducidad"]:
                fecha_cad = date.fromisoformat(lote["fecha_caducidad"][:10])
                dias = (fecha_cad - hoy).days
                if dias < 0:
                    color, texto_estado = Color.DANGER, "VENCIDO"
                elif dias <= 7:
                    color, texto_estado = Color.WARNING, f"Caduca en {dias} días"
                else:
                    color, texto_estado = Color.TEXT_MUTED, lote["fecha_caducidad"][:10]
            else:
                color, texto_estado = Color.TEXT_MUTED, "Sin caducidad"

            ctk.CTkLabel(
                fila, text=f"{lote['cantidad']:g} unidades", font=Font.BODY_BOLD, text_color=Color.TEXT
            ).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(fila, text=texto_estado, font=Font.SMALL, text_color=color)\
                .pack(side="left", padx=10)
            ctk.CTkButton(
                fila, text="Dar de baja", width=90, height=26, font=Font.SMALL,
                fg_color="transparent", text_color=Color.DANGER, hover_color=Color.DANGER_LIGHT,
                command=lambda lid=lote["id"]: self._dar_de_baja(lid)
            ).pack(side="right", padx=8)

    def _dar_de_baja(self, lote_id):
        if messagebox.askyesno("Confirmar", "¿Dar de baja este lote completo? (por ejemplo, por caducidad)"):
            dar_de_baja_lote(lote_id, motivo="Baja manual desde inventario", usuario_id=self.usuario["id"])
            self._cargar_lotes(self.producto_seleccionado_id)
            self.cargar_productos()

    def registrar_nuevo_lote(self):
        if not self.producto_seleccionado_id:
            return
        try:
            cantidad = float(self.entry_nueva_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Escribe una cantidad numérica mayor a cero.")
            return

        fecha_cad = self.entry_nueva_caducidad.get().strip() or None
        if fecha_cad:
            try:
                from datetime import date
                date.fromisoformat(fecha_cad)
            except ValueError:
                messagebox.showwarning("Fecha inválida", "Usa el formato AAAA-MM-DD, por ejemplo 2026-12-31.")
                return

        registrar_entrada(
            self.producto_seleccionado_id, cantidad, fecha_caducidad=fecha_cad,
            usuario_id=self.usuario["id"], motivo="Entrada manual desde inventario",
        )
        self.entry_nueva_cantidad.delete(0, "end")
        self.entry_nueva_caducidad.delete(0, "end")
        self._cargar_lotes(self.producto_seleccionado_id)
        self.cargar_productos()
        messagebox.showinfo("Listo", "Se agregó el nuevo lote al inventario.")

    def limpiar_formulario(self):
        self.producto_seleccionado_id = None
        for entry in [self.entry_nombre, self.entry_codigo, self.entry_precio_compra,
                      self.entry_precio_venta, self.entry_stock_minimo]:
            entry.delete(0, "end")
        self.entry_unidad.delete(0, "end")
        self.entry_unidad.insert(0, "pieza")
        self.combo_categoria.set("")
        self.entry_stock_inicial.delete(0, "end")
        self.entry_caducidad_inicial.delete(0, "end")
        self.tabla.selection_remove(self.tabla.selection())

        self.frame_lotes.pack_forget()
        self.frame_stock_inicial.pack(fill="x", padx=15, pady=10, before=self.botones_frame)

    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        precio_venta_txt = self.entry_precio_venta.get().strip()

        if not nombre or not precio_venta_txt:
            messagebox.showwarning("Datos incompletos", "Nombre y precio de venta son obligatorios.")
            return

        try:
            precio_compra = float(self.entry_precio_compra.get() or 0)
            precio_venta = float(precio_venta_txt)
            stock_minimo = float(self.entry_stock_minimo.get() or 5)
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Precios y cantidades deben ser numéricos.")
            return

        categoria_nombre = self.combo_categoria.get().strip()
        categoria_id = self.categorias_map.get(categoria_nombre)
        if categoria_nombre and not categoria_id:
            crear_categoria(categoria_nombre)
            self.categorias_map = {c["nombre"]: c["id"] for c in listar_categorias()}
            self.combo_categoria.configure(values=list(self.categorias_map.keys()))
            categoria_id = self.categorias_map.get(categoria_nombre)

        codigo = self.entry_codigo.get().strip() or None
        unidad = self.entry_unidad.get().strip() or "pieza"

        try:
            if self.producto_seleccionado_id:
                actualizar_producto(
                    self.producto_seleccionado_id,
                    nombre=nombre, codigo_barras=codigo, categoria_id=categoria_id,
                    precio_compra=precio_compra, precio_venta=precio_venta,
                    stock_minimo=stock_minimo, unidad=unidad,
                )
            else:
                stock_inicial = float(self.entry_stock_inicial.get() or 0)
                fecha_cad = self.entry_caducidad_inicial.get().strip() or None
                if fecha_cad:
                    from datetime import date
                    date.fromisoformat(fecha_cad)  # valida formato, lanza ValueError si es incorrecto
                crear_producto(
                    codigo, nombre, categoria_id, precio_compra,
                    precio_venta, stock_inicial, stock_minimo, unidad,
                    fecha_caducidad=fecha_cad, usuario_id=self.usuario["id"],
                )
        except ValueError:
            messagebox.showwarning("Fecha inválida", "Usa el formato AAAA-MM-DD para la caducidad.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto.\n\nDetalle: {e}")
            return

        messagebox.showinfo("Listo", "Producto guardado correctamente.")
        self.limpiar_formulario()
        self.cargar_productos()

    def desactivar(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la lista primero.")
            return
        if messagebox.askyesno("Confirmar", "¿Desactivar este producto? Ya no aparecerá en el punto de venta."):
            desactivar_producto(self.producto_seleccionado_id)
            self.limpiar_formulario()
            self.cargar_productos()
