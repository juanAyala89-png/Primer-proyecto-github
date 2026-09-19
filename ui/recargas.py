"""Pestaña de Recargas de tiempo aire."""

import customtkinter as ctk
from tkinter import messagebox

from models.recarga import registrar_recarga, recargas_del_dia, totales_recargas_del_dia, COMPANIAS
from models.caja import caja_abierta
from ui.theme import Color, Font, tarjeta, boton_primario


DENOMINACIONES = [20, 30, 50, 100, 150, 200, 300, 500]


class FrameRecargas(ctk.CTkFrame):
    def __init__(self, master, usuario):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.compania_seleccionada = COMPANIAS[0]
        self.monto_seleccionado = None

        self._construir_ui()
        self.refrescar()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ============ Columna izquierda: formulario de registro ============
        col_izq = tarjeta(self)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(col_izq, text="📱 Registrar recarga", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(20, 15))

        ctk.CTkLabel(col_izq, text="Compañía", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20)
        self.segment_compania = ctk.CTkSegmentedButton(
            col_izq, values=COMPANIAS, fg_color=Color.CARD_ALT,
            selected_color=Color.INFO, selected_hover_color=Color.INFO_HOVER,
            command=self._set_compania
        )
        self.segment_compania.set(COMPANIAS[0])
        self.segment_compania.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkLabel(col_izq, text="Monto de la recarga", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20)
        grid_montos = ctk.CTkFrame(col_izq, fg_color="transparent")
        grid_montos.pack(fill="x", padx=20, pady=(5, 10))
        self.botones_monto = {}
        for i, monto in enumerate(DENOMINACIONES):
            btn = ctk.CTkButton(
                grid_montos, text=f"${monto}", width=90, height=44,
                fg_color=Color.CARD_ALT, text_color=Color.TEXT, hover_color=Color.INFO_LIGHT,
                font=Font.BODY_BOLD, corner_radius=10,
                command=lambda m=monto: self._set_monto(m)
            )
            btn.grid(row=i // 4, column=i % 4, padx=4, pady=4)
            self.botones_monto[monto] = btn

        self.entry_monto_manual = ctk.CTkEntry(
            col_izq, placeholder_text="Otro monto ($)",
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40
        )
        self.entry_monto_manual.pack(fill="x", padx=20, pady=(5, 20))
        self.entry_monto_manual.bind("<KeyRelease>", lambda e: self._set_monto(None))

        ctk.CTkLabel(col_izq, text="Comisión que gana la tienda ($)", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20)
        self.entry_comision = ctk.CTkEntry(
            col_izq, placeholder_text="Ej. 5.00",
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40
        )
        self.entry_comision.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkLabel(col_izq, text="Número de teléfono (opcional)", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20)
        self.entry_telefono = ctk.CTkEntry(
            col_izq, placeholder_text="10 dígitos",
            fg_color=Color.CARD_ALT, border_color=Color.BORDER, height=40
        )
        self.entry_telefono.pack(fill="x", padx=20, pady=(5, 20))

        boton_primario(col_izq, text="Registrar recarga", height=50,
                        command=self.registrar).pack(fill="x", padx=20, pady=(0, 20))

        # ============ Columna derecha: resumen del día ============
        col_der = tarjeta(self)
        col_der.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(col_der, text="Resumen de hoy", font=Font.SUBTITLE, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20, pady=(20, 10))

        self.label_total = ctk.CTkLabel(col_der, text="$0.00", font=Font.TOTAL, text_color=Color.INFO)
        self.label_total.pack(anchor="w", padx=20)
        self.label_comision_total = ctk.CTkLabel(col_der, text="Comisión ganada: $0.00", font=Font.BODY,
                                                  text_color=Color.TEXT_MUTED)
        self.label_comision_total.pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(col_der, text="Recargas registradas hoy", font=Font.BODY_BOLD, text_color=Color.TEXT)\
            .pack(anchor="w", padx=20)
        self.lista_recargas = ctk.CTkScrollableFrame(col_der, fg_color="transparent")
        self.lista_recargas.pack(fill="both", expand=True, padx=15, pady=10)

    def _set_compania(self, valor):
        self.compania_seleccionada = valor

    def _set_monto(self, monto):
        for m, btn in self.botones_monto.items():
            btn.configure(fg_color=Color.INFO if m == monto else Color.CARD_ALT,
                          text_color="#FFFFFF" if m == monto else Color.TEXT)
        self.monto_seleccionado = monto
        if monto is not None:
            self.entry_monto_manual.delete(0, "end")

    def registrar(self):
        monto = self.monto_seleccionado
        if monto is None:
            try:
                monto = float(self.entry_monto_manual.get())
            except ValueError:
                messagebox.showwarning("Monto inválido", "Selecciona un monto o escribe uno válido.")
                return

        try:
            comision = float(self.entry_comision.get() or 0)
        except ValueError:
            messagebox.showwarning("Comisión inválida", "La comisión debe ser un número.")
            return

        corte = caja_abierta()
        corte_id = corte["id"] if corte else None

        registrar_recarga(
            self.compania_seleccionada, monto, comision, self.usuario["id"],
            corte_id=corte_id, numero_telefono=self.entry_telefono.get().strip() or None,
        )

        messagebox.showinfo("Listo", f"Recarga de ${monto:.2f} ({self.compania_seleccionada}) registrada.")

        self.entry_monto_manual.delete(0, "end")
        self.entry_comision.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self._set_monto(None)
        self.refrescar()

    def refrescar(self):
        monto_total, comision_total, _ = totales_recargas_del_dia()
        self.label_total.configure(text=f"${monto_total:.2f}")
        self.label_comision_total.configure(text=f"Comisión ganada: ${comision_total:.2f}")

        for w in self.lista_recargas.winfo_children():
            w.destroy()

        recargas = recargas_del_dia()
        if not recargas:
            ctk.CTkLabel(self.lista_recargas, text="Aún no hay recargas hoy.",
                         text_color=Color.TEXT_MUTED, font=Font.BODY).pack(pady=20)
            return

        for r in recargas:
            fila = ctk.CTkFrame(self.lista_recargas, fg_color=Color.CARD_ALT, corner_radius=8)
            fila.pack(fill="x", pady=3)
            hora = r["fecha"].split(" ")[1] if " " in r["fecha"] else r["fecha"]
            ctk.CTkLabel(fila, text=f"{r['compania']}  ·  ${r['monto']:.2f}", font=Font.BODY_BOLD,
                         text_color=Color.TEXT).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(fila, text=f"{hora}   |   comisión ${r['comision']:.2f}", font=Font.SMALL,
                         text_color=Color.TEXT_MUTED).pack(anchor="w", padx=12, pady=(0, 8))
