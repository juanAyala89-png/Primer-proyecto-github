"""Pestaña de Reportes: ventas del día/mes, top productos, caducidad y corte de caja."""

import datetime

import customtkinter as ctk
from tkinter import messagebox, ttk

from models.venta import (
    ventas_del_dia, total_ventas_del_dia, productos_mas_vendidos,
    ventas_por_mes, anios_con_ventas,
)
from models.caja import caja_abierta, abrir_caja, cerrar_caja
from models.producto import productos_stock_bajo
from models.lote import lotes_por_caducar
from models.recarga import totales_recargas_del_dia, total_recargas_por_corte
from ui.theme import Color, Font, tarjeta, boton_primario, boton_peligro
from ui.grafica import GraficaBarras


class FrameReportes(ctk.CTkFrame):
    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.anio_seleccionado = str(datetime.date.today().year)
        self._construir_ui()
        self.refrescar()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ============ Columna izquierda ============
        col_izq = ctk.CTkScrollableFrame(self, fg_color="transparent")
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        col_izq.grid_columnconfigure(0, weight=1)

        # --- Tarjetas resumen de hoy ---
        resumen = ctk.CTkFrame(col_izq, fg_color="transparent")
        resumen.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        resumen.grid_columnconfigure((0, 1), weight=1)

        card_ventas = tarjeta(resumen)
        card_ventas.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(card_ventas, text="Ventas de hoy", font=Font.BODY, text_color=Color.TEXT_MUTED)\
            .pack(anchor="w", padx=15, pady=(15, 0))
        self.label_total_hoy = ctk.CTkLabel(card_ventas, text="$0.00", font=Font.TOTAL, text_color=Color.PRIMARY)
        self.label_total_hoy.pack(anchor="w", padx=15, pady=(0, 15))

        card_recargas = tarjeta(resumen)
        card_recargas.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(card_recargas, text="Recargas de hoy", font=Font.BODY, text_color=Color.TEXT_MUTED)\
            .pack(anchor="w", padx=15, pady=(15, 0))
        self.label_recargas_hoy = ctk.CTkLabel(card_recargas, text="$0.00", font=("Segoe UI", 28, "bold"),
                                                text_color=Color.INFO)
        self.label_recargas_hoy.pack(anchor="w", padx=15, pady=(0, 2))
        self.label_comision_hoy = ctk.CTkLabel(card_recargas, text="Comisión: $0.00", font=Font.SMALL,
                                                text_color=Color.TEXT_MUTED)
        self.label_comision_hoy.pack(anchor="w", padx=15, pady=(0, 15))

        # --- Ventas por mes (gráfica) ---
        card_grafica = tarjeta(col_izq)
        card_grafica.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        header_grafica = ctk.CTkFrame(card_grafica, fg_color="transparent")
        header_grafica.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(header_grafica, text="📊 Ventas por mes", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(side="left")

        self.combo_anio = ctk.CTkComboBox(
            header_grafica, values=[self.anio_seleccionado], width=100,
            command=self._cambiar_anio, fg_color=Color.CARD_ALT, border_color=Color.BORDER
        )
        self.combo_anio.pack(side="right")

        self.grafica = GraficaBarras(card_grafica, width=560, height=240)
        self.grafica.pack(padx=15, pady=(0, 15))

        # --- Productos más vendidos ---
        card_top = tarjeta(col_izq)
        card_top.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(card_top, text="🏆 Productos más vendidos", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(15, 10))

        tabla_frame = ctk.CTkFrame(card_top, fg_color="transparent")
        tabla_frame.pack(fill="x", padx=15, pady=(0, 15))
        columnas_top = ("producto", "cantidad", "total")
        self.tabla_top = ttk.Treeview(tabla_frame, columns=columnas_top, show="headings", height=6)
        for col, texto, ancho in [
            ("producto", "Producto", 260), ("cantidad", "Cant. vendida", 120),
            ("total", "Total generado", 130),
        ]:
            self.tabla_top.heading(col, text=texto)
            self.tabla_top.column(col, width=ancho, anchor="center" if col != "producto" else "w")
        self.tabla_top.pack(fill="x")

        # --- Ventas de hoy (detalle) ---
        card_detalle = tarjeta(col_izq)
        card_detalle.grid(row=3, column=0, sticky="ew")
        header_det = ctk.CTkFrame(card_detalle, fg_color="transparent")
        header_det.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(header_det, text="🧾 Detalle de ventas de hoy", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(side="left")
        ctk.CTkButton(header_det, text="↻ Actualizar", width=110, height=30,
                      fg_color=Color.CARD_ALT, text_color=Color.TEXT, hover_color=Color.BORDER,
                      command=self.refrescar).pack(side="right")

        tabla_frame2 = ctk.CTkFrame(card_detalle, fg_color="transparent")
        tabla_frame2.pack(fill="x", padx=15, pady=(0, 15))
        columnas = ("hora", "total", "metodo", "estado")
        self.tabla_ventas = ttk.Treeview(tabla_frame2, columns=columnas, show="headings", height=6)
        for col, texto, ancho in [
            ("hora", "Hora", 120), ("total", "Total", 100),
            ("metodo", "Método", 120), ("estado", "Estado", 100),
        ]:
            self.tabla_ventas.heading(col, text=texto)
            self.tabla_ventas.column(col, width=ancho, anchor="center")
        self.tabla_ventas.pack(fill="x")

        # ============ Columna derecha ============
        col_der = ctk.CTkScrollableFrame(self, fg_color="transparent")
        col_der.grid(row=0, column=1, sticky="nsew")
        col_der.grid_columnconfigure(0, weight=1)

        # --- Corte de caja ---
        card_caja = tarjeta(col_der)
        card_caja.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(card_caja, text="💰 Corte de caja", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(pady=(20, 8))

        self.label_estado_caja = ctk.CTkLabel(card_caja, text="", font=Font.BODY, justify="center")
        self.label_estado_caja.pack(pady=5, padx=15)

        self.entry_monto = ctk.CTkEntry(card_caja, placeholder_text="Monto ($)",
                                         fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40)
        self.entry_monto.pack(pady=10, padx=20, fill="x")

        self.boton_caja = boton_primario(card_caja, text="", command=self.accion_caja)
        self.boton_caja.pack(pady=(0, 20), padx=20, fill="x")

        # --- Productos con stock bajo ---
        card_stock = tarjeta(col_der)
        card_stock.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(card_stock, text="📦 Stock bajo", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(15, 5))
        self.frame_stock_bajo = ctk.CTkFrame(card_stock, fg_color="transparent")
        self.frame_stock_bajo.pack(fill="x", padx=15, pady=(0, 15))

        # --- Próximos a caducar ---
        card_caducidad = tarjeta(col_der)
        card_caducidad.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(card_caducidad, text="📅 Próximos a caducar", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=15, pady=(15, 5))
        self.frame_caducidad = ctk.CTkFrame(card_caducidad, fg_color="transparent")
        self.frame_caducidad.pack(fill="x", padx=15, pady=(0, 15))

    # ---------------------------------------------------------
    def _cambiar_anio(self, valor):
        self.anio_seleccionado = valor
        self._dibujar_grafica()

    def _dibujar_grafica(self):
        valores = ventas_por_mes(self.anio_seleccionado)
        self.grafica.dibujar(valores, color=Color.PRIMARY)

    def refrescar(self):
        # Años disponibles en el combo
        anios = anios_con_ventas()
        if self.anio_seleccionado not in anios:
            anios = [self.anio_seleccionado] + anios
        self.combo_anio.configure(values=anios)
        self.combo_anio.set(self.anio_seleccionado)
        self._dibujar_grafica()

        # Ventas de hoy
        ventas = ventas_del_dia()
        self.label_total_hoy.configure(text=f"${total_ventas_del_dia():.2f}")
        self.tabla_ventas.delete(*self.tabla_ventas.get_children())
        for v in ventas:
            hora = v["fecha"].split(" ")[1] if " " in v["fecha"] else v["fecha"]
            self.tabla_ventas.insert("", "end", values=(
                hora, f"${v['total']:.2f}", v["metodo_pago"], v["estado"]
            ))

        # Recargas de hoy
        monto_r, comision_r, _ = totales_recargas_del_dia()
        self.label_recargas_hoy.configure(text=f"${monto_r:.2f}")
        self.label_comision_hoy.configure(text=f"Comisión: ${comision_r:.2f}")

        # Top productos (histórico)
        self.tabla_top.delete(*self.tabla_top.get_children())
        for p in productos_mas_vendidos(10):
            self.tabla_top.insert("", "end", values=(
                p["nombre"], p["cantidad_total"], f"${p['total_vendido']:.2f}"
            ))

        # Estado de caja
        corte = caja_abierta()
        if corte:
            self.label_estado_caja.configure(
                text=f"Caja ABIERTA desde\n{corte['fecha_apertura']}\nFondo inicial: ${corte['monto_inicial']:.2f}",
                text_color=Color.PRIMARY,
            )
            self.entry_monto.configure(placeholder_text="Monto real en caja al cerrar")
            self.boton_caja.configure(text="Cerrar caja", fg_color=Color.DANGER, hover_color=Color.DANGER_HOVER)
            self._corte_actual = corte["id"]
        else:
            self.label_estado_caja.configure(text="Caja CERRADA", text_color=Color.DANGER)
            self.entry_monto.configure(placeholder_text="Fondo inicial ($)")
            self.boton_caja.configure(text="Abrir caja", fg_color=Color.PRIMARY, hover_color=Color.PRIMARY_HOVER)
            self._corte_actual = None

        # Stock bajo
        for widget in self.frame_stock_bajo.winfo_children():
            widget.destroy()
        bajos = productos_stock_bajo()
        if not bajos:
            ctk.CTkLabel(self.frame_stock_bajo, text="Todo el inventario está en buen nivel ✅",
                         text_color=Color.TEXT_MUTED, font=Font.SMALL).pack(anchor="w", pady=5)
        else:
            for p in bajos[:8]:
                ctk.CTkLabel(
                    self.frame_stock_bajo,
                    text=f"⚠️ {p['nombre']} — quedan {p['stock']:g} {p['unidad']}",
                    anchor="w", font=Font.SMALL, text_color=Color.WARNING,
                ).pack(fill="x", pady=2)

        # Próximos a caducar / vencidos
        for widget in self.frame_caducidad.winfo_children():
            widget.destroy()
        lotes = lotes_por_caducar(dias=7)
        if not lotes:
            ctk.CTkLabel(self.frame_caducidad, text="Nada por caducar en los próximos 7 días ✅",
                         text_color=Color.TEXT_MUTED, font=Font.SMALL).pack(anchor="w", pady=5)
        else:
            from datetime import date
            hoy = date.today()
            for lote in lotes[:8]:
                fecha_cad = date.fromisoformat(lote["fecha_caducidad"][:10])
                dias = (fecha_cad - hoy).days
                if dias < 0:
                    texto, color = f"🔴 {lote['producto_nombre']} — VENCIDO ({lote['cantidad']:g} {lote['unidad']})", Color.DANGER
                else:
                    texto, color = f"🟠 {lote['producto_nombre']} — caduca en {dias} días ({lote['cantidad']:g} {lote['unidad']})", Color.WARNING
                ctk.CTkLabel(self.frame_caducidad, text=texto, anchor="w", font=Font.SMALL, text_color=color)\
                    .pack(fill="x", pady=2)

    def accion_caja(self):
        try:
            monto = float(self.entry_monto.get())
        except ValueError:
            messagebox.showwarning("Monto inválido", "Escribe un monto numérico.")
            return

        if self._corte_actual:
            monto_sistema, diferencia = cerrar_caja(self._corte_actual, monto)
            total_recargas_corte = total_recargas_por_corte(self._corte_actual)
            texto = (
                f"Caja cerrada.\n\n"
                f"Monto esperado (sistema, incluye recargas): ${monto_sistema:.2f}\n"
                f"  (de las cuales ${total_recargas_corte:.2f} son de recargas)\n"
                f"Monto real contado: ${monto:.2f}\n"
                f"Diferencia: ${diferencia:.2f}"
            )
            messagebox.showinfo("Corte de caja", texto)
        else:
            abrir_caja(self.usuario["id"], monto)
            messagebox.showinfo("Caja abierta", f"Caja abierta con fondo inicial de ${monto:.2f}")

        self.entry_monto.delete(0, "end")
        self.refrescar()
