"""
=============================================================
 FISIO - Analizador Léxico  |  gui.py
 Interfaz gráfica profesional con Tkinter.
 Dark theme (Catppuccin Mocha), resaltado sintáctico,
 tabla de tokens y estadísticas.
=============================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

from lexer       import Lexer
from parser      import Parser
from token_types import (
    TipoToken,
    PALABRAS_RESERVADAS,
    OPERADORES_MATEMATICOS,
    OPERADORES_RELACIONALES,
    SIGNOS,
    COLORES_GUI,
    ALFABETO_VALIDO,
)

# ─────────────────────────────────────────────────────────────
#  EJEMPLOS PRECARGADOS
# ─────────────────────────────────────────────────────────────
EJEMPLOS = {
    "MRU completo": """\
mru(velocidad := 20, tiempo := 5);
posicion := velocidad * tiempo;
graficar(posicion);
""",
    "MRUA + caída libre": """\
mrua(aceleracion := 3, velocidad := 0, tiempo := 10);
caida(gravedad := 9.81);
altura := 150.5 - 0.5 * gravedad * tiempo ^ 2;
velocidadFinal := velocidad + aceleracion * tiempo;
simular(altura);
""",
    "Tiro parabólico": """\
parabolico(alcance := 45, altura := 12.0);
raiz(posicion);
seno(angulo);
coseno(angulo);
magnitud(velocidad);
despejar(alcance);
""",
    "Operadores y signos": """\
x := 10;
y := x + 5;
z := y - 3;
w := z * 2;
v := w / 4;
p := v ^ 2;
ok := x <= y;
nok := x != y;
lista[0];
""",
    "Errores léxicos": """\
a := .5;
b := 5.;
c := 1..5;
d := 01;
e := 12a;
f := 9.8x;
g := 5@2;
h := 3#14;
i := 5 ! 3;
1variable := 10;
""",
    "Errores de alfabeto (Reales)": """\
; Todos estos símbolos están fuera del alfabeto FISIO
x := 5 @ 2;
y := 3 # 14;
precio := 100$;
porcentaje := 50%;
y_comercial := a & b;
mi_variable := 25;
conjunto := { 1, 2, 3 };
mensaje := "hola";
operador_invalido := a \\ b | c;
pregunta := ¿test?;
info := ¡alerta!;
""",
}


# ─────────────────────────────────────────────────────────────
#  WIDGET: EDITOR CON NÚMEROS DE LÍNEA
# ─────────────────────────────────────────────────────────────
class EditorCodigo(tk.Frame):
    """Editor de código con numeración de líneas y resaltado sintáctico."""

    def __init__(self, parent, colores: dict, **kwargs):
        super().__init__(parent, bg=colores["bg_editor"], **kwargs)
        self.colores = colores
        self._construir()
        self._configurar_tags()
        self._bind_eventos()

    def _construir(self):
        C = self.colores
        mono = ("Consolas", 12) if sys.platform == "win32" else ("Courier New", 12)

        # Números de línea
        self.numeros = tk.Text(
            self, width=4, state="disabled",
            bg=C["bg_editor"], fg=C["fg_lineno"],
            font=mono, bd=0, padx=4, pady=6,
            cursor="arrow", takefocus=False,
            relief="flat", wrap="none",
        )
        self.numeros.pack(side="left", fill="y")

        # Separador vertical
        tk.Frame(self, width=1, bg=C["border"]).pack(side="left", fill="y")

        # Scrollbar
        self.scroll_y = ttk.Scrollbar(self, orient="vertical")
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal")
        self.scroll_x.pack(side="bottom", fill="x")

        # Texto principal
        self.texto = tk.Text(
            self, wrap="none",
            bg=C["bg_editor"], fg=C["fg_main"],
            insertbackground=C["accent"],
            selectbackground=C["border"],
            font=mono, bd=0, padx=8, pady=6,
            undo=True, maxundo=200,
            yscrollcommand=self._sync_scroll_y,
            xscrollcommand=self.scroll_x.set,
            relief="flat",
        )
        self.texto.pack(side="left", fill="both", expand=True)
        self.scroll_y.config(command=self._scroll_ambos)
        self.scroll_x.config(command=self.texto.xview)

    def _sync_scroll_y(self, *args):
        self.scroll_y.set(*args)
        self._actualizar_numeros()

    def _scroll_ambos(self, *args):
        self.texto.yview(*args)
        self.numeros.yview(*args)

    def _configurar_tags(self):
        C = self.colores
        tags = {
            "PR"   : {"foreground": C["col_PR"],  "font": ("Consolas", 12, "bold")},
            "OPM"  : {"foreground": C["col_OPM"]},
            "OPR"  : {"foreground": C["col_OPR"]},
            "SIG"  : {"foreground": C["col_SIG"]},
            "ID"   : {"foreground": C["col_ID"]},
            "NUM"  : {"foreground": C["col_NUM"]},
            "ERROR": {"foreground": C["col_ERROR"],
                      "underline": True,
                      "font": ("Consolas", 12, "italic")},
            "linea_error": {"background": "#2d1b1b"},
        }
        for nombre, opts in tags.items():
            self.texto.tag_configure(nombre, **opts)

    def _bind_eventos(self):
        self.texto.bind("<KeyRelease>",     self._on_cambio)
        self.texto.bind("<ButtonRelease>",  self._on_cambio)
        self.texto.bind("<MouseWheel>",     self._on_scroll_mouse)

    def _on_cambio(self, _event=None):
        self._actualizar_numeros()

    def _on_scroll_mouse(self, event):
        self.numeros.yview_scroll(int(-1*(event.delta/120)), "units")

    def _actualizar_numeros(self):
        contenido = self.texto.get("1.0", "end-1c")
        n_lineas  = contenido.count("\n") + 1
        nums      = "\n".join(str(i) for i in range(1, n_lineas + 1))

        self.numeros.config(state="normal")
        self.numeros.delete("1.0", "end")
        self.numeros.insert("1.0", nums)
        self.numeros.config(state="disabled")
        self.numeros.yview_moveto(self.texto.yview()[0])

    def resaltar(self, tokens: list, errores: list):
        """Aplica tags de color al editor según los tokens y errores encontrados."""
        for tag in ("PR", "OPM", "OPR", "SIG", "ID", "NUM", "ERROR", "linea_error"):
            self.texto.tag_remove(tag, "1.0", "end")

        # Marcar líneas con error de fondo
        lineas_error = {e.linea for e in errores}
        for l in lineas_error:
            self.texto.tag_add("linea_error", f"{l}.0", f"{l}.end")

        # Colorear tokens
        for tok in tokens:
            ini = f"{tok.linea}.{tok.columna - 1}"
            fin = f"{tok.linea}.{tok.columna - 1 + len(tok.lexema)}"
            self.texto.tag_add(tok.tipo, ini, fin)

        # Subrayar lexemas de error
        for err in errores:
            lexema = getattr(err, "lexema", None)
            if lexema is None and hasattr(err, "token"):
                lexema = err.token.lexema
            if not lexema:
                continue
            ini = f"{err.linea}.{err.columna - 1}"
            fin = f"{err.linea}.{err.columna - 1 + len(lexema)}"
            self.texto.tag_add("ERROR", ini, fin)

    def get_codigo(self) -> str:
        return self.texto.get("1.0", "end-1c")

    def set_codigo(self, texto: str):
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self._actualizar_numeros()

    def limpiar(self):
        self.texto.delete("1.0", "end")
        self._actualizar_numeros()


# ─────────────────────────────────────────────────────────────
#  WIDGET: TABLA DE TOKENS
# ─────────────────────────────────────────────────────────────
class TablaTokens(tk.Frame):
    """Treeview con tokens, coloreados por tipo."""

    COLUMNAS = ("lexema", "tipo", "id_token", "linea", "columna")
    CABECERAS = ("Lexema", "Tipo", "ID Token", "Línea", "Columna")
    ANCHOS    = (180, 90, 90, 60, 70)

    def __init__(self, parent, colores: dict, **kwargs):
        super().__init__(parent, bg=colores["bg_panel"], **kwargs)
        self.colores = colores
        self._construir()

    def _construir(self):
        C = self.colores
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Tokens.Treeview",
            background      = C["bg_panel"],
            foreground      = C["fg_main"],
            fieldbackground = C["bg_panel"],
            rowheight       = 24,
            font            = ("Consolas", 11),
            borderwidth     = 0,
        )
        style.configure("Tokens.Treeview.Heading",
            background  = C["bg_toolbar"],
            foreground  = C["accent"],
            font        = ("Segoe UI", 10, "bold"),
            relief      = "flat",
            borderwidth = 0,
        )
        style.map("Tokens.Treeview",
            background = [("selected", C["border"])],
            foreground = [("selected", C["fg_main"])],
        )
        style.configure("Vertical.TScrollbar",
            background  = C["bg_toolbar"],
            troughcolor = C["bg_panel"],
            arrowcolor  = C["fg_dim"],
        )

        frame = tk.Frame(self, bg=C["bg_panel"])
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            frame, columns=self.COLUMNAS, show="headings",
            style="Tokens.Treeview", selectmode="browse",
        )
        for col, cab, ancho in zip(self.COLUMNAS, self.CABECERAS, self.ANCHOS):
            self.tree.heading(col, text=cab)
            self.tree.column(col, width=ancho, minwidth=40, anchor="center")
        self.tree.column("lexema", anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        sbx = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=sbx.set)
        sbx.pack(side="bottom", fill="x")

        self.tree.pack(fill="both", expand=True)

        for tipo, color in [
            ("PR", "col_PR"), ("OPM", "col_OPM"), ("OPR", "col_OPR"),
            ("SIG", "col_SIG"), ("ID", "col_ID"), ("NUM", "col_NUM"),
            ("ERROR", "col_ERROR"),
        ]:
            self.tree.tag_configure(tipo, foreground=C[color])
        self.tree.tag_configure("par",   background=C["bg_row_alt"])
        self.tree.tag_configure("impar", background=C["bg_panel"])

    def poblar(self, tokens: list):
        self.tree.delete(*self.tree.get_children())
        for i, tok in enumerate(tokens):
            par = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end",
                values=(tok.lexema, tok.tipo, tok.id_tok,
                        tok.linea, tok.columna),
                tags=(tok.tipo, par),
            )

    def limpiar(self):
        self.tree.delete(*self.tree.get_children())


# ─────────────────────────────────────────────────────────────
#  WIDGET: PANEL RESUMEN / ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────
class PanelResumen(tk.Frame):
    """Muestra estadísticas del análisis con barras de progreso visuales."""

    TIPOS = [
        ("PR",  "Palabras Reservadas", "col_PR"),
        ("OPM", "Op. Matemáticos",     "col_OPM"),
        ("OPR", "Op. Relacionales",    "col_OPR"),
        ("SIG", "Signos",              "col_SIG"),
        ("ID",  "Identificadores",     "col_ID"),
        ("NUM", "Números",             "col_NUM"),
    ]

    def __init__(self, parent, colores: dict, **kwargs):
        super().__init__(parent, bg=colores["bg_panel"], **kwargs)
        self.colores = colores
        self._construir()

    def _construir(self):
        C = self.colores

        sb = ttk.Scrollbar(self, orient="vertical")
        sb.pack(side="right", fill="y")

        self.canvas = tk.Canvas(
            self, bg=C["bg_panel"], bd=0, highlightthickness=0,
            yscrollcommand=sb.set,
        )
        self.canvas.pack(fill="both", expand=True)
        sb.config(command=self.canvas.yview)

        self.inner = tk.Frame(self.canvas, bg=C["bg_panel"])
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.inner.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_configure(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self._win, width=event.width)

    def poblar(self, tokens: list, errores: list):
        C = self.colores

        for w in self.inner.winfo_children():
            w.destroy()

        total   = len(tokens)
        n_err   = len(errores)
        conteos = {}
        for tok in tokens:
            conteos[tok.tipo] = conteos.get(tok.tipo, 0) + 1

        # ── Encabezado ────────────────────────────────────────
        tk.Label(self.inner, text="RESUMEN DEL ANÁLISIS",
                 bg=C["bg_panel"], fg=C["accent"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(16, 2))

        tk.Frame(self.inner, height=1, bg=C["border"]).pack(fill="x", padx=20, pady=4)

        # ── Totales ───────────────────────────────────────────
        color_err = C["ok_green"] if n_err == 0 else C["col_ERROR"]
        estado_txt = "ANÁLISIS EXITOSO  ✔" if n_err == 0 else f"CON ERRORES  ✖ ({n_err})"
        estado_col = C["ok_green"] if n_err == 0 else C["col_ERROR"]

        def stat_row(lbl, val, color):
            f = tk.Frame(self.inner, bg=C["bg_panel"])
            f.pack(fill="x", padx=20, pady=2)
            tk.Label(f, text=lbl, bg=C["bg_panel"],
                     fg=C["fg_dim"], font=("Segoe UI", 11),
                     width=22, anchor="w").pack(side="left")
            tk.Label(f, text=str(val), bg=C["bg_panel"],
                     fg=color, font=("Consolas", 12, "bold")).pack(side="left")

        stat_row("Total tokens:",  total,      C["col_NUM"])
        stat_row("Total errores:", n_err,      color_err)
        stat_row("Estado:",        estado_txt, estado_col)

        tk.Frame(self.inner, height=1, bg=C["border"]).pack(fill="x", padx=20, pady=8)

        # ── Distribución por tipo ─────────────────────────────
        tk.Label(self.inner, text="Distribución por tipo:",
                 bg=C["bg_panel"], fg=C["fg_main"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=20, pady=(0, 6))

        max_val = max(conteos.values()) if conteos else 1

        for tipo, nombre, col_key in self.TIPOS:
            cnt   = conteos.get(tipo, 0)
            color = C[col_key]
            pct   = cnt / max_val if max_val > 0 else 0

            row = tk.Frame(self.inner, bg=C["bg_panel"])
            row.pack(fill="x", padx=20, pady=3)

            tk.Label(row, text=f"{tipo:<5}", bg=C["bg_panel"],
                     fg=color, font=("Consolas", 11, "bold"),
                     width=6, anchor="w").pack(side="left")
            tk.Label(row, text=nombre, bg=C["bg_panel"],
                     fg=C["fg_dim"], font=("Segoe UI", 10),
                     width=20, anchor="w").pack(side="left")

            bar_frame = tk.Frame(row, bg=C["bg_toolbar"], height=14, width=200)
            bar_frame.pack(side="left", padx=(4, 8))
            bar_frame.pack_propagate(False)

            fill_w = max(int(200 * pct), 2) if cnt > 0 else 0
            if fill_w > 0:
                tk.Frame(bar_frame, bg=color, width=fill_w, height=14).place(x=0, y=0)

            tk.Label(row, text=str(cnt), bg=C["bg_panel"],
                     fg=color, font=("Consolas", 11, "bold"),
                     width=4, anchor="e").pack(side="left")

        # ── Resumen de errores ────────────────────────────────
        if errores:
            tk.Frame(self.inner, height=1, bg=C["border"]).pack(
                fill="x", padx=20, pady=8)
            tk.Label(self.inner, text="Errores detectados:",
                     bg=C["bg_panel"], fg=C["col_ERROR"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=20, pady=(0, 4))

            for err in errores:
                f = tk.Frame(self.inner, bg=C["bg_panel"])
                f.pack(fill="x", padx=24, pady=1)
                tk.Label(f, text=f"Línea {err.linea:>3}, Col {err.columna:>3} │",
                         bg=C["bg_panel"], fg=C["fg_dim"],
                         font=("Consolas", 10)).pack(side="left")
                tk.Label(f, text=f" '{err.lexema}'",
                         bg=C["bg_panel"], fg=C["col_OPR"],
                         font=("Consolas", 10, "bold")).pack(side="left")
                tk.Label(f, text=f"  {err.mensaje}",
                         bg=C["bg_panel"], fg=C["col_ERROR"],
                         font=("Segoe UI", 9)).pack(side="left")

        self.inner.update_idletasks()
        self._on_configure()
        self._bind_mousewheel(self.inner)

    def limpiar(self):
        for w in self.inner.winfo_children():
            w.destroy()


# ─────────────────────────────────────────────────────────────
#  WIDGET: PANEL ALFABETO / ESPECIFICACIÓN
# ─────────────────────────────────────────────────────────────
class PanelSintactico(tk.Frame):
    """Muestra el resultado del parser y una vista textual del AST."""

    def __init__(self, parent, colores: dict, **kwargs):
        super().__init__(parent, bg=colores["bg_panel"], **kwargs)
        self.colores = colores
        self._construir()

    def _construir(self):
        C = self.colores

        frame = tk.Frame(self, bg=C["bg_panel"])
        frame.pack(fill="both", expand=True)

        self.texto = tk.Text(
            frame,
            wrap="none",
            bg=C["bg_panel"],
            fg=C["fg_main"],
            insertbackground=C["accent"],
            selectbackground=C["border"],
            font=("Consolas", 10),
            bd=0,
            padx=14,
            pady=12,
            relief="flat",
            state="disabled",
        )
        sb_y = ttk.Scrollbar(frame, orient="vertical", command=self.texto.yview)
        sb_x = ttk.Scrollbar(frame, orient="horizontal", command=self.texto.xview)
        self.texto.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.texto.pack(side="left", fill="both", expand=True)

        self.texto.tag_configure("titulo", foreground=C["accent"], font=("Consolas", 11, "bold"))
        self.texto.tag_configure("ok", foreground=C["ok_green"], font=("Consolas", 10, "bold"))
        self.texto.tag_configure("error", foreground=C["col_ERROR"])
        self.texto.tag_configure("dim", foreground=C["fg_dim"])

    def poblar(self, ast, errores: list):
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")

        self.texto.insert("end", "ANALISIS SINTACTICO\n", "titulo")
        self.texto.insert("end", "\n")

        if errores:
            self.texto.insert("end", f"CON ERRORES ({len(errores)})\n\n", "error")
            self.texto.insert("end", "Errores detectados:\n", "titulo")
            for err in errores:
                lexema = self._lexema_error(err)
                self.texto.insert(
                    "end",
                    f"  Linea {err.linea:>3}, Col {err.columna:>3} | '{lexema}' | {err.mensaje}\n",
                    "error",
                )
            self.texto.insert("end", "\nAST parcial:\n", "titulo")
        else:
            self.texto.insert("end", "ANALISIS EXITOSO\n\n", "ok")
            self.texto.insert("end", "AST:\n", "titulo")

        for linea in self._formatear_ast(ast):
            self.texto.insert("end", f"{linea}\n", "dim")

        self.texto.config(state="disabled")

    def limpiar(self):
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.config(state="disabled")

    def _formatear_ast(self, nodo, nivel: int = 0) -> list[str]:
        if nodo is None:
            return ["<sin AST>"]

        indent = "  " * nivel
        nombre = nodo.__class__.__name__
        detalles: list[str] = []

        for attr in ("nombre", "identificador", "variable", "operador", "token", "indice"):
            token = getattr(nodo, attr, None)
            if token is not None:
                detalles.append(f"{attr}='{token.lexema}'")

        encabezado = f"{indent}{nombre}"
        if detalles:
            encabezado += " (" + ", ".join(detalles) + ")"

        lineas = [encabezado]
        for attr in ("sentencias", "argumentos"):
            valores = getattr(nodo, attr, None)
            if valores:
                lineas.append(f"{indent}  {attr}:")
                for valor in valores:
                    lineas.extend(self._formatear_ast(valor, nivel + 2))

        for attr in ("lugar", "expresion", "izquierda", "derecha"):
            valor = getattr(nodo, attr, None)
            if valor is not None:
                lineas.append(f"{indent}  {attr}:")
                lineas.extend(self._formatear_ast(valor, nivel + 2))

        return lineas

    @staticmethod
    def _lexema_error(err) -> str:
        lexema = getattr(err, "lexema", None)
        if lexema is None and hasattr(err, "token"):
            lexema = err.token.lexema
        return lexema or "EOF"


class PanelAlfabeto(tk.Frame):
    """Muestra la especificación del alfabeto y tokens del lenguaje FISIO."""

    def __init__(self, parent, colores: dict, **kwargs):
        super().__init__(parent, bg=colores["bg_panel"], **kwargs)
        self.colores = colores
        self._construir()

    def _construir(self):
        C = self.colores

        sb = ttk.Scrollbar(self, orient="vertical")
        sb.pack(side="right", fill="y")

        self.canvas = tk.Canvas(
            self, bg=C["bg_panel"], bd=0, highlightthickness=0,
            yscrollcommand=sb.set,
        )
        self.canvas.pack(fill="both", expand=True)
        sb.config(command=self.canvas.yview)

        self.inner = tk.Frame(self.canvas, bg=C["bg_panel"])
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.inner.bind("<MouseWheel>", self._on_mousewheel)

        self._poblar_informacion()
        self._bind_mousewheel(self.inner)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_configure(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self._win, width=event.width)

    def _poblar_informacion(self):
        C = self.colores

        def titulo(texto):
            tk.Label(
                self.inner,
                text=texto,
                bg=C["bg_panel"],
                fg=C["accent"],
                font=("Segoe UI", 12, "bold")
            ).pack(anchor="w", padx=20, pady=(16, 4))

        def separador():
            tk.Frame(
                self.inner,
                height=1,
                bg=C["border"]
            ).pack(fill="x", padx=20, pady=6)

        def item(lexema, tipo, token_id, color):
            fila = tk.Frame(self.inner, bg=C["bg_panel"])
            fila.pack(fill="x", padx=20, pady=2)

            tk.Label(
                fila,
                text=lexema,
                width=18,
                anchor="w",
                bg=C["bg_panel"],
                fg=color,
                font=("Consolas", 10, "bold")
            ).pack(side="left", padx=(10, 4), pady=2)

            tk.Label(
                fila,
                text=tipo,
                width=10,
                anchor="center",
                bg=C["bg_panel"],
                fg=C["fg_main"],
                font=("Consolas", 9)
            ).pack(side="left")

            tk.Label(
                fila,
                text=token_id,
                width=12,
                anchor="center",
                bg=C["bg_panel"],
                fg=C["fg_dim"],
                font=("Consolas", 9)
            ).pack(side="left")

        # ── Encabezado ──
        tk.Label(self.inner, text="ESPECIFICACIÓN LÉXICA FISIO",
                 bg=C["bg_panel"], fg=C["accent"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(16, 2))

        separador()

        # ── Información General ──
        info = (
            "FISIO es un lenguaje orientado a simulaciones y cálculos "
            "de física clásica.\n"
            "El analizador léxico identifica palabras reservadas, "
            "operadores, signos, identificadores y números."
        )
        tk.Label(
            self.inner,
            text=info,
            justify="left",
            bg=C["bg_panel"],
            fg=C["fg_main"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=20, pady=(0, 6))

        separador()

        # ── Alfabeto Permitido ──
        titulo("🔤 Alfabeto Permitido")
        alfabeto_texto = (
            "• Letras: a-z A-Z\n"
            "• Dígitos: 0-9\n"
            "• Operadores matemáticos: + - * / ^\n"
            "• Operadores relacionales: := = < > <= >= !=\n"
            "• Signos: ( ) [ ] , . ;\n"
            "• Espacios válidos: espacio, tabulación y salto de línea"
        )
        tk.Label(
            self.inner,
            text=alfabeto_texto,
            justify="left",
            bg=C["bg_panel"],
            fg=C["fg_main"],
            font=("Consolas", 10)
        ).pack(anchor="w", padx=30, pady=(0, 6))

        separador()

        # ── Palabras Reservadas ──
        titulo("📚 Palabras Reservadas")
        for lexema, (tipo, token_id) in PALABRAS_RESERVADAS.items():
            item(lexema, tipo, token_id, C["col_PR"])

        separador()

        # ── Operadores Matemáticos ──
        titulo("➕ Operadores Matemáticos")
        for lexema, (tipo, token_id) in OPERADORES_MATEMATICOS.items():
            item(lexema, tipo, token_id, C["col_OPM"])

        separador()

        # ── Operadores Relacionales ──
        titulo("🔀 Operadores Relacionales")
        for lexema, (tipo, token_id) in OPERADORES_RELACIONALES.items():
            item(lexema, tipo, token_id, C["col_OPR"])

        separador()

        # ── Signos ──
        titulo("🔣 Signos")
        for lexema, (tipo, token_id) in SIGNOS.items():
            item(lexema, tipo, token_id, C["col_SIG"])

        separador()

        # ── Tipos de Token ──
        titulo("🧩 Tipos de Token")
        tipos = [
            ("PR", "Palabra Reservada", C["col_PR"]),
            ("OPM", "Operador Matemático", C["col_OPM"]),
            ("OPR", "Operador Relacional", C["col_OPR"]),
            ("SIG", "Signo", C["col_SIG"]),
            ("ID", "Identificador", C["col_ID"]),
            ("NUM", "Número", C["col_NUM"]),
            ("ERROR", "Token inválido", "#ff5555"),
        ]
        for sigla, desc, color in tipos:
            fila = tk.Frame(self.inner, bg=C["bg_panel"])
            fila.pack(fill="x", padx=20, pady=2)

            tk.Label(
                fila,
                text=sigla,
                width=10,
                bg=C["bg_panel"],
                fg=color,
                font=("Consolas", 10, "bold")
            ).pack(side="left", padx=(10, 4), pady=2)

            tk.Label(
                fila,
                text=desc,
                bg=C["bg_panel"],
                fg=C["fg_main"],
                font=("Segoe UI", 9)
            ).pack(side="left")


# ─────────────────────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
class AplicacionFISIO(tk.Tk):
    """Ventana principal del Analizador Léxico FISIO."""

    def __init__(self):
        super().__init__()
        self.C = COLORES_GUI
        self._archivo_actual: str | None = None
        self._tokens  = []
        self._errores = []
        self._ast = None
        self._errores_sintacticos = []
        self._lexico_realizado = False
        self._codigo_analizado_lexico: str | None = None
        self._btn_sintactico: tk.Button | None = None
        self._configurar_ventana()
        self._construir_ui()
        self._cargar_ejemplo("MRU completo")

    # ── Configuración de la ventana ───────────────────────────
    def _configurar_ventana(self):
        self.title("FISIO — Analizador Léxico y Sintáctico")
        self.geometry("1280x780")
        self.minsize(900, 600)
        self.configure(bg=self.C["bg_main"])
        try:
            self.iconbitmap(default="")
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", self._salir)

    # ── Construcción de la UI ─────────────────────────────────
    def _construir_ui(self):
        self._construir_toolbar()
        self._construir_cuerpo()
        self._construir_statusbar()
        self.bind("<F5>", lambda _event: self._analizar_lexico())
        self.bind("<F6>", lambda _event: self._analizar_sintactico())

    def _set_sintactico_disponible(self, disponible: bool):
        if self._btn_sintactico is None:
            return

        estado = "normal" if disponible else "disabled"
        self._btn_sintactico.config(state=estado, disabledforeground=self.C["fg_dim"])

    # ── Toolbar ───────────────────────────────────────────────
    def _construir_toolbar(self):
        C = self.C
        bar = tk.Frame(self, bg=C["bg_toolbar"], height=46)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", side="top")

        def btn(parent, texto, cmd, color_fg=None, color_bg=None, emoji=""):
            fg = color_fg or C["fg_main"]
            bg = color_bg or C["bg_toolbar"]
            b = tk.Button(
                parent, text=f"  {emoji} {texto}  ",
                command=cmd, fg=fg, bg=bg,
                activeforeground=C["accent"],
                activebackground=C["border"],
                relief="flat", bd=0, padx=6, pady=4,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            b.pack(side="left", padx=2, pady=6)
            b.bind("<Enter>", lambda _: b.config(bg=C["border"]))
            b.bind("<Leave>", lambda _: b.config(bg=bg))
            return b

        btn(bar, "Abrir",           self._abrir_archivo,  emoji="📂")
        btn(bar, "Guardar",         self._guardar_archivo, emoji="💾")
        btn(bar, "Alfabeto FISIO",  self._mostrar_alfabeto_tab, emoji="ℹ")

        tk.Frame(bar, width=1, bg=C["border"], height=28).pack(side="left", padx=6, pady=8)

        btn(bar, "Léxico  [F5]", self._analizar_lexico,
            color_fg=C["bg_main"], color_bg=C["accent"], emoji="▶")
        self._btn_sintactico = btn(bar, "Sintáctico  [F6]", self._analizar_sintactico,
            color_fg=C["fg_main"], color_bg=C["bg_toolbar"], emoji="✓")
        self._set_sintactico_disponible(False)

        tk.Frame(bar, width=1, bg=C["border"], height=28).pack(side="left", padx=6, pady=8)

        btn(bar, "Limpiar", self._limpiar_todo, emoji="✕")

        self._ejemplo_var = tk.StringVar(value="Ejemplos…")
        ejm = tk.OptionMenu(bar, self._ejemplo_var, *EJEMPLOS.keys(),
                            command=self._cargar_ejemplo)
        ejm.config(
            fg=C["fg_main"], bg=C["bg_toolbar"],
            activeforeground=C["accent"],
            activebackground=C["border"],
            relief="flat", bd=0, highlightthickness=0,
            font=("Segoe UI", 10), cursor="hand2",
        )
        ejm["menu"].config(
            bg=C["bg_toolbar"], fg=C["fg_main"],
            activebackground=C["border"],
            activeforeground=C["accent"],
        )
        ejm.pack(side="left", padx=4)

        tk.Label(bar, text="FISIO  Analizador Léxico y Sintáctico",
                 bg=C["bg_toolbar"], fg=C["accent"],
                 font=("Segoe UI", 12, "bold")).pack(side="right", padx=16)

    # ── Cuerpo principal ──────────────────────────────────────
    def _construir_cuerpo(self):
        C = self.C

        paned = tk.PanedWindow(
            self, orient="horizontal",
            bg=C["border"], sashwidth=4,
            sashrelief="flat", handlesize=0,
        )
        paned.pack(fill="both", expand=True)

        # Panel izquierdo: editor
        izq = tk.Frame(paned, bg=C["bg_editor"])
        paned.add(izq, minsize=340, width=560)

        tk.Label(izq, text="  CÓDIGO FUENTE",
                 bg=C["bg_toolbar"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x")
        tk.Frame(izq, height=1, bg=C["border"]).pack(fill="x")

        self.editor = EditorCodigo(izq, C)
        self.editor.pack(fill="both", expand=True)
        self.editor.texto.bind("<KeyRelease>", self._on_codigo_modificado, add="+")

        # Panel derecho: Notebook
        der = tk.Frame(paned, bg=C["bg_panel"])
        paned.add(der, minsize=340)

        style = ttk.Style()
        style.configure("Fisio.TNotebook",
            background=C["bg_panel"],
            tabmargins=[0, 0, 0, 0],
        )
        style.configure("Fisio.TNotebook.Tab",
            background = C["bg_toolbar"],
            foreground = C["fg_dim"],
            padding    = [14, 6],
            font       = ("Segoe UI", 10, "bold"),
        )
        style.map("Fisio.TNotebook.Tab",
            background = [("selected", C["bg_panel"])],
            foreground = [("selected", C["accent"])],
        )

        self.notebook = ttk.Notebook(der, style="Fisio.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Pestaña Tokens
        frame_tok = tk.Frame(self.notebook, bg=C["bg_panel"])
        self.notebook.add(frame_tok, text="  🔑  Tokens  ")
        self.tabla_tokens = TablaTokens(frame_tok, C)
        self.tabla_tokens.pack(fill="both", expand=True)

        # Pestaña Resumen
        frame_res = tk.Frame(self.notebook, bg=C["bg_panel"])
        self.notebook.add(frame_res, text="  📊  Resumen  ")
        self.panel_resumen = PanelResumen(frame_res, C)
        self.panel_resumen.pack(fill="both", expand=True)

        # Pestaña Sintaxis
        frame_sin = tk.Frame(self.notebook, bg=C["bg_panel"])
        self.notebook.add(frame_sin, text="  Sintaxis  ")
        self.panel_sintactico = PanelSintactico(frame_sin, C)
        self.panel_sintactico.pack(fill="both", expand=True)

        # Pestaña Alfabeto
        frame_alf = tk.Frame(self.notebook, bg=C["bg_panel"])
        self.notebook.add(frame_alf, text="  📘  Alfabeto  ")
        self.panel_alfabeto = PanelAlfabeto(frame_alf, C)
        self.panel_alfabeto.pack(fill="both", expand=True)

    # ── Barra de estado ───────────────────────────────────────
    def _construir_statusbar(self):
        C = self.C
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", side="bottom")
        bar = tk.Frame(self, bg=C["bg_status"], height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._sv_archivo = tk.StringVar(value="Sin archivo")
        self._sv_tokens  = tk.StringVar(value="Tokens: —")
        self._sv_errores = tk.StringVar(value="Errores: —")
        self._sv_sintaxis = tk.StringVar(value="Sintaxis: —")
        self._sv_estado  = tk.StringVar(value="Listo")

        def lbl(parent, var, fg=None, side="left", padx=8):
            tk.Label(parent, textvariable=var,
                     bg=C["bg_status"],
                     fg=fg or C["fg_dim"],
                     font=("Segoe UI", 9)).pack(side=side, padx=padx)

        lbl(bar, self._sv_archivo, fg=C["fg_dim"])
        tk.Frame(bar, width=1, bg=C["border"]).pack(side="left", fill="y", pady=4)
        lbl(bar, self._sv_tokens, fg=C["col_NUM"])
        tk.Frame(bar, width=1, bg=C["border"]).pack(side="left", fill="y", pady=4)
        lbl(bar, self._sv_errores, fg=C["col_ERROR"])
        tk.Frame(bar, width=1, bg=C["border"]).pack(side="left", fill="y", pady=4)
        lbl(bar, self._sv_sintaxis, fg=C["accent"])
        lbl(bar, self._sv_estado, fg=C["accent"], side="right", padx=12)

    # ── Acciones ──────────────────────────────────────────────
    def _on_codigo_modificado(self, _event=None):
        if self._lexico_realizado:
            self._invalidar_analisis_por_cambio()

    def _invalidar_analisis_por_cambio(self):
        self._tokens = []
        self._errores = []
        self._ast = None
        self._errores_sintacticos = []
        self._lexico_realizado = False
        self._codigo_analizado_lexico = None

        self.tabla_tokens.limpiar()
        self.panel_resumen.limpiar()
        self.panel_sintactico.limpiar()
        self.editor.resaltar([], [])
        self._set_sintactico_disponible(False)

        if hasattr(self, "_sv_tokens"):
            self._sv_tokens.set("Tokens: —")
            self._sv_errores.set("Errores: —")
            self._sv_sintaxis.set("Sintaxis: —")
            self._sv_estado.set("Codigo modificado; ejecuta analisis lexico")

    def _mostrar_alfabeto_tab(self):
        """Muestra la pestaña con la especificación del alfabeto."""
        self.notebook.select(3)

    def _analizar(self):
        self._analizar_lexico()

    def _analizar_lexico(self):
        codigo = self.editor.get_codigo()
        if not codigo.strip():
            messagebox.showwarning(
                "Sin código",
                "El editor está vacío.\nEscribe o carga código FISIO para analizar."
            )
            return

        lex = Lexer(codigo)
        self._tokens, self._errores = lex.analizar()
        self._ast = None
        self._errores_sintacticos = []
        self._lexico_realizado = True
        self._codigo_analizado_lexico = codigo
        self.panel_sintactico.limpiar()

        self.tabla_tokens.poblar(self._tokens)
        self.panel_resumen.poblar(self._tokens, self._errores)
        self.editor.resaltar(self._tokens, self._errores)

        n_tok = len(self._tokens)
        n_err = len(self._errores)
        self._sv_tokens.set(f"Tokens: {n_tok}")
        self._sv_errores.set(f"Errores: {n_err}")
        self._sv_sintaxis.set("Sintaxis: —")
        self._set_sintactico_disponible(n_err == 0)

        if n_err == 0:
            self._sv_estado.set("✓ Analisis lexico exitoso")
            self.notebook.select(0)
        else:
            self._sv_estado.set(f"✕ {n_err} error(es) lexicos")
            self.notebook.select(1)

    def _analizar_sintactico(self):
        codigo_actual = self.editor.get_codigo()

        if not self._lexico_realizado:
            messagebox.showwarning(
                "Analisis lexico requerido",
                "Primero ejecuta el analisis lexico antes del analisis sintactico."
            )
            return

        if self._codigo_analizado_lexico != codigo_actual:
            self._invalidar_analisis_por_cambio()
            messagebox.showwarning(
                "Codigo modificado",
                "El codigo cambio despues del analisis lexico. Ejecuta de nuevo el analisis lexico."
            )
            return

        if self._errores:
            messagebox.showwarning(
                "Errores lexicos",
                "Corrige los errores lexicos antes de ejecutar el analisis sintactico."
            )
            self._set_sintactico_disponible(False)
            return

        parser = Parser(self._tokens)
        self._ast, self._errores_sintacticos = parser.parse()

        self.panel_sintactico.poblar(self._ast, self._errores_sintacticos)
        self.editor.resaltar(self._tokens, self._errores_sintacticos)

        n_err = len(self._errores_sintacticos)
        self._sv_sintaxis.set(f"Sintaxis: {n_err} error(es)")

        if n_err == 0:
            self._sv_estado.set("✓ Analisis sintactico exitoso")
        else:
            self._sv_estado.set(f"✕ {n_err} error(es) sintacticos")

        self.notebook.select(2)

    def _abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo FISIO",
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Archivos FISIO", "*.fisio"),
                       ("Todos", "*.*")],
        )
        if not ruta:
            return
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = f.read()
        except UnicodeDecodeError:
            with open(ruta, encoding="latin-1") as f:
                contenido = f.read()

        self.editor.set_codigo(contenido)
        self._archivo_actual = ruta
        self._sv_archivo.set(f"📄 {os.path.basename(ruta)}")
        self.title(f"FISIO — {os.path.basename(ruta)}")
        self._limpiar_resultados()

    def _guardar_archivo(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar código FISIO",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"),
                       ("Archivo FISIO", "*.fisio")],
        )
        if not ruta:
            return
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.editor.get_codigo())
        self._archivo_actual = ruta
        self._sv_archivo.set(f"📄 {os.path.basename(ruta)}")
        messagebox.showinfo("Guardado", f"Archivo guardado:\n{ruta}")

    def _cargar_ejemplo(self, nombre: str):
        codigo = EJEMPLOS.get(nombre, "")
        self.editor.set_codigo(codigo)
        self._ejemplo_var.set("Ejemplos…")
        self._sv_archivo.set(f"📝 Ejemplo: {nombre}")
        self.title(f"FISIO — Ejemplo: {nombre}")
        self._limpiar_resultados()

    def _limpiar_todo(self):
        self.editor.limpiar()
        self._limpiar_resultados()
        self._sv_archivo.set("Sin archivo")
        self._sv_tokens.set("Tokens: —")
        self._sv_errores.set("Errores: —")
        self._sv_sintaxis.set("Sintaxis: —")
        self._sv_estado.set("Listo")
        self.title("FISIO — Analizador Léxico y Sintáctico")

    def _limpiar_resultados(self):
        self._tokens = []
        self._errores = []
        self._ast = None
        self._errores_sintacticos = []
        self._lexico_realizado = False
        self._codigo_analizado_lexico = None
        self.tabla_tokens.limpiar()
        self.panel_resumen.limpiar()
        self.panel_sintactico.limpiar()
        self.editor.resaltar([], [])
        self._set_sintactico_disponible(False)
        self._sv_tokens.set("Tokens: —")
        self._sv_errores.set("Errores: —")
        self._sv_sintaxis.set("Sintaxis: —")
        self._sv_estado.set("Listo")

    def _acerca_de(self):
        C = self.C
        win = tk.Toplevel(self)
        win.title("Acerca de FISIO")
        win.configure(bg=C["bg_main"])
        win.geometry("480x340")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="FISIO",
                 bg=C["bg_main"], fg=C["accent"],
                 font=("Segoe UI", 28, "bold")).pack(pady=(24, 4))
        tk.Label(win,
                 text="Analizador Léxico para Física Clásica",
                 bg=C["bg_main"], fg=C["fg_main"],
                 font=("Segoe UI", 12)).pack()
        tk.Frame(win, height=1, bg=C["border"]).pack(fill="x", padx=40, pady=16)

        info = [
            ("Versión",   "2.0 — GUI"),
            ("Lenguaje",  "Python 3.11+ / Tkinter"),
            ("Módulos",   "MRU · MRUA · Caída Libre · Parabólico"),
            ("Tokens PR", "18 palabras reservadas"),
        ]
        for lbl_txt, val in info:
            f = tk.Frame(win, bg=C["bg_main"])
            f.pack(anchor="center", pady=2)
            tk.Label(f, text=f"{lbl_txt}:", bg=C["bg_main"],
                     fg=C["fg_dim"], font=("Segoe UI", 10),
                     width=12, anchor="e").pack(side="left")
            tk.Label(f, text=val, bg=C["bg_main"],
                     fg=C["fg_main"], font=("Segoe UI", 10, "bold")).pack(side="left")

        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg=C["accent"], fg=C["bg_main"],
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", bd=0, padx=20, pady=6,
                  cursor="hand2").pack(pady=20)

    def _salir(self):
        if messagebox.askokcancel("Salir", "¿Cerrar el analizador FISIO?"):
            self.destroy()


# ─────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
def main():
    app = AplicacionFISIO()
    app.mainloop()


if __name__ == "__main__":
    main()
