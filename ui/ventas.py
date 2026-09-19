"""Pantalla de Punto de Venta: búsqueda, carrito en tarjetas y cobro."""

import customtkinter as ctk
from tkinter import messagebox

from models.producto import buscar_por_codigo, listar_productos
from models.venta import registrar_venta, productos_mas_vendidos
from models.caja import caja_abierta
from ui.theme import Color, Font, tarjeta, boton_primario, boton_secundario, boton_peligro


class FramePuntoDeVenta(ctk.CTkFrame):
    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.carrito = []  # cada item: producto_id, nombre, cantidad, precio_unitario, unidad

        self._construir_ui()
        self._cargar_accesos_rapidos()
        self.actualizar_totales()

    # ---------------------------------------------------------
    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ============ Columna izquierda ============
        col_izq = ctk.CTkFrame(self, fg_color="transparent")
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        col_izq.grid_rowconfigure(2, weight=1)
        col_izq.grid_columnconfigure(0, weight=1)

        # --- Buscador ---
        buscar_card = tarjeta(col_izq)
        buscar_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        buscar_card.grid_columnconfigure(0, weight=1)

        self.entry_codigo = ctk.CTkEntry(
            buscar_card, placeholder_text="🔍  Escanea el código de barras o escribe el nombre y presiona Enter",
            height=48, font=Font.BODY, corner_radius=10,
            fg_color=Color.CARD_ALT, border_color=Color.BORDER
        )
        self.entry_codigo.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        self.entry_codigo.bind("<Return>", lambda e: self.buscar_y_agregar())
        self.entry_codigo.focus()

        boton_primario(buscar_card, text="Agregar", width=110, command=self.buscar_y_agregar)\
            .grid(row=0, column=1, padx=(0, 15), pady=15)

        # --- Accesos rápidos (productos más vendidos) ---
        self.frame_accesos = ctk.CTkFrame(col_izq, fg_color="transparent")
        self.frame_accesos.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # --- Carrito (tarjetas, no tabla) ---
        carrito_card = tarjeta(col_izq)
        carrito_card.grid(row=2, column=0, sticky="nsew")
        carrito_card.grid_rowconfigure(1, weight=1)
        carrito_card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(carrito_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        ctk.CTkLabel(header, text="🛒 Carrito", font=Font.SUBTITLE, text_color=Color.TEXT).pack(side="left")
        boton_secundario(header, text="Vaciar", width=90, height=32,
                          command=self.vaciar_carrito).pack(side="right")

        self.lista_carrito = ctk.CTkScrollableFrame(carrito_card, fg_color="transparent")
        self.lista_carrito.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.lista_carrito.grid_columnconfigure(0, weight=1)

        self.label_vacio = ctk.CTkLabel(
            self.lista_carrito, text="El carrito está vacío.\nEscanea un producto para comenzar.",
            text_color=Color.TEXT_MUTED, font=Font.BODY
        )
        self.label_vacio.grid(row=0, column=0, pady=40)

        # ============ Columna derecha: resumen y cobro ============
        col_der = tarjeta(self)
        col_der.grid(row=0, column=1, sticky="nsew")
        col_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(col_der, text="Total a pagar", font=Font.BODY, text_color=Color.TEXT_MUTED)\
            .pack(pady=(30, 0))
        self.label_total = ctk.CTkLabel(col_der, text="$0.00", font=Font.TOTAL, text_color=Color.PRIMARY)
        self.label_total.pack(pady=(0, 20))

        ctk.CTkLabel(col_der, text="Método de pago", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=25)
        self.metodo_pago = ctk.CTkSegmentedButton(
            col_der, values=["efectivo", "tarjeta", "transferencia"],
            fg_color=Color.CARD_ALT, selected_color=Color.PRIMARY,
            selected_hover_color=Color.PRIMARY_HOVER, unselected_color=Color.CARD_ALT,
            command=lambda v: self.actualizar_totales()
        )
        self.metodo_pago.set("efectivo")
        self.metodo_pago.pack(pady=(8, 20), padx=25, fill="x")

        ctk.CTkLabel(col_der, text="Monto recibido", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=25)
        self.entry_recibido = ctk.CTkEntry(
            col_der, height=44, justify="center", font=Font.SUBTITLE,
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, corner_radius=10
        )
        self.entry_recibido.pack(pady=8, padx=25, fill="x")
        self.entry_recibido.bind("<KeyRelease>", lambda e: self.actualizar_totales())

        self.label_cambio = ctk.CTkLabel(col_der, text="Cambio: $0.00", font=Font.HEADING, text_color=Color.TEXT)
        self.label_cambio.pack(pady=10)

        boton_primario(
            col_der, text="COBRAR", height=58, font=("Segoe UI", 18, "bold"),
            command=self.cobrar
        ).pack(pady=(15, 25), padx=25, fill="x")

    # ---------------------------------------------------------
    def _cargar_accesos_rapidos(self):
        for w in self.frame_accesos.winfo_children():
            w.destroy()

        top = productos_mas_vendidos(limite=6)
        if not top:
            return

        ctk.CTkLabel(self.frame_accesos, text="Accesos rápidos", font=Font.SMALL,
                     text_color=Color.TEXT_MUTED).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 4))

        for i, p in enumerate(top):
            btn = ctk.CTkButton(
                self.frame_accesos, text=p["nombre"][:16], width=140, height=44,
                fg_color=Color.PRIMARY_LIGHT, text_color=Color.PRIMARY, hover_color=Color.BORDER,
                corner_radius=10, font=Font.SMALL,
                command=lambda nombre=p["nombre"]: self._agregar_por_nombre(nombre)
            )
            btn.grid(row=1, column=i, padx=4, pady=2)

    def _agregar_por_nombre(self, nombre):
        coincidencias = listar_productos(texto_busqueda=nombre)
        if coincidencias:
            producto = coincidencias[0]
            if producto["stock"] <= 0:
                messagebox.showwarning("Sin existencias", f"'{producto['nombre']}' no tiene stock disponible.")
                return
            self._agregar_al_carrito(producto)

    # ---------------------------------------------------------
    def buscar_y_agregar(self):
        texto = self.entry_codigo.get().strip()
        if not texto:
            return

        producto = buscar_por_codigo(texto)
        if not producto:
            coincidencias = listar_productos(texto_busqueda=texto)
            if len(coincidencias) == 1:
                producto = coincidencias[0]
            elif len(coincidencias) > 1:
                messagebox.showinfo(
                    "Varios resultados",
                    "Hay varios productos que coinciden. Usa el código de barras exacto "
                    "o ve a Inventario para revisar el nombre."
                )
                self.entry_codigo.select_range(0, "end")
                return

        if not producto:
            messagebox.showwarning("No encontrado", f"No se encontró ningún producto para: {texto}")
            self.entry_codigo.select_range(0, "end")
            return

        if producto["stock"] <= 0:
            messagebox.showwarning("Sin existencias", f"'{producto['nombre']}' no tiene stock disponible.")
            self.entry_codigo.select_range(0, "end")
            return

        self._agregar_al_carrito(producto)
        self.entry_codigo.delete(0, "end")

    def _agregar_al_carrito(self, producto):
        for item in self.carrito:
            if item["producto_id"] == producto["id"]:
                item["cantidad"] += 1
                self._refrescar_carrito()
                self.actualizar_totales()
                return

        self.carrito.append({
            "producto_id": producto["id"],
            "nombre": producto["nombre"],
            "cantidad": 1,
            "precio_unitario": producto["precio_venta"],
            "unidad": producto["unidad"],
        })
        self._refrescar_carrito()
        self.actualizar_totales()

    # ---------------------------------------------------------
    def _refrescar_carrito(self):
        for w in self.lista_carrito.winfo_children():
            w.destroy()

        if not self.carrito:
            self.label_vacio = ctk.CTkLabel(
                self.lista_carrito, text="El carrito está vacío.\nEscanea un producto para comenzar.",
                text_color=Color.TEXT_MUTED, font=Font.BODY
            )
            self.label_vacio.grid(row=0, column=0, pady=40)
            return

        for idx, item in enumerate(self.carrito):
            self._crear_fila_carrito(idx, item)

    def _crear_fila_carrito(self, idx, item):
        fila = ctk.CTkFrame(self.lista_carrito, fg_color=Color.CARD_ALT, corner_radius=10)
        fila.grid(row=idx, column=0, sticky="ew", pady=4, padx=2)
        fila.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(fila, fg_color="transparent")
        info.grid(row=0, column=0, sticky="w", padx=12, pady=10)
        ctk.CTkLabel(info, text=item["nombre"], font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w")
        ctk.CTkLabel(
            info, text=f"${item['precio_unitario']:.2f} / {item['unidad']}",
            font=Font.SMALL, text_color=Color.TEXT_MUTED
        ).pack(anchor="w")

        stepper = ctk.CTkFrame(fila, fg_color="transparent")
        stepper.grid(row=0, column=1, padx=8)
        ctk.CTkButton(
            stepper, text="−", width=30, height=30, corner_radius=15,
            fg_color=Color.BORDER, text_color=Color.TEXT, hover_color=Color.CARD,
            command=lambda i=idx: self._cambiar_cantidad(i, -1)
        ).pack(side="left")
        ctk.CTkLabel(stepper, text=str(item["cantidad"]), width=36, font=Font.BODY_BOLD)\
            .pack(side="left", padx=6)
        ctk.CTkButton(
            stepper, text="+", width=30, height=30, corner_radius=15,
            fg_color=Color.PRIMARY, text_color="#FFFFFF", hover_color=Color.PRIMARY_HOVER,
            command=lambda i=idx: self._cambiar_cantidad(i, 1)
        ).pack(side="left")

        subtotal = item["cantidad"] * item["precio_unitario"]
        ctk.CTkLabel(fila, text=f"${subtotal:.2f}", font=Font.BODY_BOLD, width=80, text_color=Color.PRIMARY)\
            .grid(row=0, column=2, padx=8)

        ctk.CTkButton(
            fila, text="✕", width=30, height=30, corner_radius=15,
            fg_color="transparent", text_color=Color.DANGER, hover_color=Color.DANGER_LIGHT,
            command=lambda i=idx: self._quitar_item(i)
        ).grid(row=0, column=3, padx=(0, 10))

    def _cambiar_cantidad(self, idx, delta):
        self.carrito[idx]["cantidad"] += delta
        if self.carrito[idx]["cantidad"] <= 0:
            self.carrito.pop(idx)
        self._refrescar_carrito()
        self.actualizar_totales()

    def _quitar_item(self, idx):
        self.carrito.pop(idx)
        self._refrescar_carrito()
        self.actualizar_totales()

    def vaciar_carrito(self):
        self.carrito = []
        self._refrescar_carrito()
        self.actualizar_totales()

    # ---------------------------------------------------------
    def calcular_total(self):
        return sum(item["cantidad"] * item["precio_unitario"] for item in self.carrito)

    def actualizar_totales(self):
        total = self.calcular_total()
        self.label_total.configure(text=f"${total:.2f}")

        try:
            recibido = float(self.entry_recibido.get())
        except ValueError:
            recibido = 0.0

        if self.metodo_pago.get() == "efectivo":
            cambio = recibido - total
            self.label_cambio.configure(
                text=f"Cambio: ${cambio:.2f}" if cambio >= 0 else "Cambio: --"
            )
        else:
            self.label_cambio.configure(text="")

    def cobrar(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto.")
            return

        total = self.calcular_total()
        metodo = self.metodo_pago.get()

        recibido = total
        if metodo == "efectivo":
            try:
                recibido = float(self.entry_recibido.get())
            except ValueError:
                messagebox.showwarning("Monto inválido", "Escribe el monto recibido en efectivo.")
                return
            if recibido < total:
                messagebox.showwarning("Monto insuficiente", "El monto recibido es menor al total.")
                return

        corte = caja_abierta()
        corte_id = corte["id"] if corte else None
        if not corte:
            respuesta = messagebox.askyesno(
                "Caja no abierta",
                "No hay un corte de caja abierto. ¿Deseas continuar sin asociar la venta a un corte?"
            )
            if not respuesta:
                return

        venta_id, total, cambio = registrar_venta(
            self.carrito, metodo, recibido, self.usuario["id"], corte_id
        )

        mensaje = f"Venta #{venta_id} registrada.\nTotal: ${total:.2f}"
        if metodo == "efectivo":
            mensaje += f"\nCambio: ${cambio:.2f}"
        messagebox.showinfo("Venta exitosa", mensaje)

        self.vaciar_carrito()
        self.entry_recibido.delete(0, "end")
        self.entry_codigo.focus()
        self._cargar_accesos_rapidos()
