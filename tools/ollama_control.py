#!/usr/bin/env python3
"""
SIC Ollama Controller - Aplicación de Escritorio Linux
Controla el servicio Ollama con un switch ON/OFF visual.

Instalar atajo en escritorio:
  ~/.local/share/applications/ollama-control.desktop
"""

import tkinter as tk
from tkinter import font
import subprocess
import threading
import time
import os


# ─── Colores ───────────────────────────────────────────────────────────────
BG_DARK     = "#0d0d14"
BG_CARD     = "#13131f"
BORDER      = "#1e1e2f"
ACCENT_ON   = "#00e676"   # Verde brillante (activo)
ACCENT_OFF  = "#ff3d71"   # Rojo (apagado)
ACCENT_WAIT = "#ffd600"   # Amarillo (transición)
TEXT_PRI    = "#f0f0ff"
TEXT_SEC    = "#6b7280"
VIOLET      = "#7c3aed"


def is_ollama_active() -> bool:
    """Verifica si el servicio ollama está activo."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "ollama"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == "active"
    except Exception:
        return False


def get_ollama_memory() -> str:
    """Obtiene el consumo de RAM de Ollama."""
    try:
        result = subprocess.run(
            ["systemctl", "show", "ollama", "--property=MemoryCurrent"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if line.startswith("MemoryCurrent="):
                mem_bytes = int(line.split("=")[1])
                if mem_bytes > 0:
                    return f"{mem_bytes / (1024**3):.2f} GB"
        return "N/A"
    except Exception:
        return "N/A"


class OllamaControlApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ollama Control · SIC")
        self.root.geometry("320x420")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        self.root.attributes("-topmost", False)

        # Centrar ventana
        self.root.update_idletasks()
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = (w // 2) - 160
        y = (h // 2) - 210
        self.root.geometry(f"320x420+{x}+{y}")

        # Estado interno
        self._active = False
        self._transitioning = False
        self._blink_on = True

        self._build_ui()
        self._poll_status()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        f_title = font.Font(family="DejaVu Sans", size=10, weight="bold")
        f_label = font.Font(family="DejaVu Sans", size=9)
        f_mono  = font.Font(family="DejaVu Sans Mono", size=8)
        f_big   = font.Font(family="DejaVu Sans", size=13, weight="bold")

        # Header
        header = tk.Frame(self.root, bg=BG_CARD, height=52, bd=0)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="⚡  Ollama Controller", font=f_title,
            bg=BG_CARD, fg=TEXT_PRI, anchor="w", padx=16
        ).pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            header, text="SIC", font=f_mono,
            bg=BG_CARD, fg=VIOLET, anchor="e", padx=14
        ).pack(side=tk.RIGHT, fill=tk.Y)

        # Separator
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # Status card
        card = tk.Frame(self.root, bg=BG_CARD, padx=20, pady=20, bd=0)
        card.pack(fill=tk.X, padx=16, pady=(16, 8))

        # Dot indicator + estado
        dot_row = tk.Frame(card, bg=BG_CARD)
        dot_row.pack(fill=tk.X)

        self._dot = tk.Label(dot_row, text="●", font=font.Font(size=14),
                              bg=BG_CARD, fg=ACCENT_OFF)
        self._dot.pack(side=tk.LEFT)

        self._status_label = tk.Label(
            dot_row, text="Verificando...", font=f_big,
            bg=BG_CARD, fg=TEXT_PRI, padx=8
        )
        self._status_label.pack(side=tk.LEFT)

        # Detalles
        self._memory_label = tk.Label(
            card, text="RAM: —", font=f_mono,
            bg=BG_CARD, fg=TEXT_SEC, anchor="w"
        )
        self._memory_label.pack(fill=tk.X, pady=(6, 0))

        self._pid_label = tk.Label(
            card, text="PID: —", font=f_mono,
            bg=BG_CARD, fg=TEXT_SEC, anchor="w"
        )
        self._pid_label.pack(fill=tk.X)

        # ── SWITCH ─────────────────────────────────────────────────────────
        switch_frame = tk.Frame(self.root, bg=BG_DARK, pady=8)
        switch_frame.pack(fill=tk.X, padx=16)

        tk.Label(
            switch_frame, text="ESTADO DEL SERVICIO", font=f_mono,
            bg=BG_DARK, fg=TEXT_SEC
        ).pack(pady=(0, 8))

        # Canvas switch toggle
        self._switch_canvas = tk.Canvas(
            switch_frame, width=120, height=52,
            bg=BG_DARK, highlightthickness=0, cursor="hand2"
        )
        self._switch_canvas.pack()
        self._switch_canvas.bind("<Button-1>", self._on_switch_click)
        self._draw_switch(False)

        # Botones Inicio / Parar
        btn_row = tk.Frame(self.root, bg=BG_DARK)
        btn_row.pack(fill=tk.X, padx=16, pady=(8, 0))

        self._btn_start = tk.Button(
            btn_row, text="▶  ENCENDER", font=f_label,
            bg="#16a34a", fg="white", activebackground="#15803d",
            activeforeground="white", relief="flat", bd=0,
            padx=14, pady=10, cursor="hand2",
            command=self._start_ollama
        )
        self._btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self._btn_stop = tk.Button(
            btn_row, text="■  APAGAR", font=f_label,
            bg="#dc2626", fg="white", activebackground="#b91c1c",
            activeforeground="white", relief="flat", bd=0,
            padx=14, pady=10, cursor="hand2",
            command=self._stop_ollama
        )
        self._btn_stop.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(4, 0))

        # Log mini
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, padx=16, pady=(12, 6))
        self._log_label = tk.Label(
            self.root, text="→ Sistema listo.", font=f_mono,
            bg=BG_DARK, fg=TEXT_SEC, anchor="w", padx=16, wraplength=290
        )
        self._log_label.pack(fill=tk.X)

    def _draw_switch(self, active: bool):
        c = self._switch_canvas
        c.delete("all")
        w, h = 120, 52
        r = 22
        color_track = ACCENT_ON if active else "#2d2d3f"
        knob_border = "#aaaaaa" if active else "#555555"

        # Track (rounded rect via oval trick)
        c.create_oval(4, 4, 4 + h - 8, h - 4, fill=color_track, outline=color_track)
        c.create_oval(w - (h - 4), 4, w - 4, h - 4, fill=color_track, outline=color_track)
        c.create_rectangle(4 + (h - 8) // 2, 4, w - 4 - (h - 8) // 2, h - 4,
                            fill=color_track, outline=color_track)

        # Knob
        knob_x = w - 8 - r if active else 8 + r
        c.create_oval(knob_x - r, h // 2 - r, knob_x + r, h // 2 + r,
                      fill="white", outline=knob_border)
        c.create_text(knob_x, h // 2, text="I" if active else "O",
                      fill=color_track, font=("DejaVu Sans", 11, "bold"))

    # ── Acciones ───────────────────────────────────────────────────────────

    def _on_switch_click(self, event):
        if self._transitioning:
            return
        if self._active:
            self._stop_ollama()
        else:
            self._start_ollama()

    def _start_ollama(self):
        self._set_transitioning(True, "🟡 Iniciando Ollama...")
        threading.Thread(target=self._exec_start, daemon=True).start()

    def _stop_ollama(self):
        self._set_transitioning(True, "🟡 Deteniendo Ollama...")
        threading.Thread(target=self._exec_stop, daemon=True).start()

    def _exec_start(self):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", "ollama"],
                capture_output=True, text=True, timeout=15
            )
            time.sleep(1.5)
            self.root.after(0, lambda: self._set_transitioning(False, "✅ Ollama encendido."))
        except Exception as e:
            self.root.after(0, lambda: self._set_transitioning(False, f"❌ Error: {e}"))

    def _exec_stop(self):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", "ollama"],
                capture_output=True, text=True, timeout=15
            )
            time.sleep(1.0)
            self.root.after(0, lambda: self._set_transitioning(False, "🔴 Ollama apagado."))
        except Exception as e:
            self.root.after(0, lambda: self._set_transitioning(False, f"❌ Error: {e}"))

    def _set_transitioning(self, val: bool, msg: str = ""):
        self._transitioning = val
        if msg:
            self._log_label.config(text=f"→ {msg}")
        self._update_buttons()

    def _update_buttons(self):
        disabled = self._transitioning
        self._btn_start.config(state="disabled" if disabled or self._active else "normal")
        self._btn_stop.config(state="disabled" if disabled or not self._active else "normal")

    # ── Polling de estado ──────────────────────────────────────────────────

    def _poll_status(self):
        threading.Thread(target=self._fetch_and_update, daemon=True).start()

    def _fetch_and_update(self):
        active = is_ollama_active()
        mem = get_ollama_memory() if active else "—"

        pid = "—"
        if active:
            try:
                r = subprocess.run(
                    ["systemctl", "show", "ollama", "--property=MainPID"],
                    capture_output=True, text=True, timeout=3
                )
                for line in r.stdout.splitlines():
                    if line.startswith("MainPID="):
                        pid = line.split("=")[1]
            except Exception:
                pass

        self.root.after(0, lambda: self._apply_status(active, mem, pid))
        # Siguiente poll en 5 segundos
        self.root.after(5000, self._poll_status)

    def _apply_status(self, active: bool, mem: str, pid: str):
        self._active = active
        color = ACCENT_ON if active else ACCENT_OFF
        label = "ACTIVO" if active else "INACTIVO"

        self._dot.config(fg=color)
        self._status_label.config(text=label, fg=color)
        self._memory_label.config(text=f"RAM: {mem}")
        self._pid_label.config(text=f"PID: {pid}")
        self._draw_switch(active)

        if not self._transitioning:
            self._update_buttons()


def main():
    root = tk.Tk()
    app = OllamaControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
