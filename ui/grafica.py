"""Gráfica de barras sencilla dibujada a mano sobre un tkinter Canvas.

Se evita depender de matplotlib para que el programa sea más ligero y fácil
de empaquetar como .exe.
"""

import tkinter as tk
from ui.theme import Color


MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class GraficaBarras(tk.Canvas):
    def __init__(self, master, width=560, height=260, **kwargs):
        super().__init__(master, width=width, height=height,
                          bg=Color.CARD, highlightthickness=0, **kwargs)
        self._width = width
        self._height = height

    def dibujar(self, valores, etiquetas=None, color=None):
        """valores: lista de números (ej. 12 meses). etiquetas: lista de textos cortos."""
        self.delete("all")
        etiquetas = etiquetas or MESES
        color = color or Color.PRIMARY

        margen_izq, margen_der, margen_sup, margen_inf = 55, 20, 20, 30
        area_w = self._width - margen_izq - margen_der
        area_h = self._height - margen_sup - margen_inf

        maximo = max(valores) if valores and max(valores) > 0 else 1
        n = len(valores)
        ancho_barra = area_w / n * 0.55
        paso = area_w / n

        # Líneas guía horizontales (25%, 50%, 75%, 100%)
        for frac in (0.25, 0.5, 0.75, 1.0):
            y = margen_sup + area_h * (1 - frac)
            self.create_line(
                margen_izq, y, margen_izq + area_w, y,
                fill=Color.BORDER, dash=(3, 3)
            )
            self.create_text(
                margen_izq - 10, y, text=f"${maximo * frac:,.0f}",
                anchor="e", fill=Color.TEXT_MUTED, font=("Segoe UI", 8)
            )

        # Barras
        for i, valor in enumerate(valores):
            alto = (valor / maximo) * area_h if maximo else 0
            x0 = margen_izq + i * paso + (paso - ancho_barra) / 2
            x1 = x0 + ancho_barra
            y1 = margen_sup + area_h
            y0 = y1 - alto

            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="", width=0)

            if valor > 0:
                self.create_text(
                    (x0 + x1) / 2, y0 - 10, text=f"${valor:,.0f}",
                    fill=Color.TEXT, font=("Segoe UI", 8, "bold")
                )

            etiqueta = etiquetas[i] if i < len(etiquetas) else ""
            self.create_text(
                (x0 + x1) / 2, y1 + 14, text=etiqueta,
                fill=Color.TEXT_MUTED, font=("Segoe UI", 9)
            )

        # Eje base
        self.create_line(
            margen_izq, margen_sup + area_h, margen_izq + area_w, margen_sup + area_h,
            fill=Color.BORDER
        )
