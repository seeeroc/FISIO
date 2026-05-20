"""
=============================================================
 FISIO - Analizador Léxico  |  token_types.py  v2
 Definición de tokens, IDs, alfabeto y paleta GUI.
=============================================================
"""

# ── Categorías ────────────────────────────────────────────────
class TipoToken:
    PALABRA_RESERVADA   = "PR"
    OPERADOR_MATEMATICO = "OPM"
    OPERADOR_RELACIONAL = "OPR"
    SIGNO               = "SIG"
    IDENTIFICADOR       = "ID"
    NUMERO              = "NUM"
    ERROR               = "ERROR"

# ── Palabras reservadas ───────────────────────────────────────
PALABRAS_RESERVADAS: dict[str, tuple[str, str]] = {
    "mru"         : (TipoToken.PALABRA_RESERVADA, "PR_01"),
    "mrua"        : (TipoToken.PALABRA_RESERVADA, "PR_02"),
    "caida"       : (TipoToken.PALABRA_RESERVADA, "PR_03"),
    "parabolico"  : (TipoToken.PALABRA_RESERVADA, "PR_04"),
    "despejar"    : (TipoToken.PALABRA_RESERVADA, "PR_05"),
    "graficar"    : (TipoToken.PALABRA_RESERVADA, "PR_06"),
    "simular"     : (TipoToken.PALABRA_RESERVADA, "PR_07"),
    "raiz"        : (TipoToken.PALABRA_RESERVADA, "PR_08"),
    "seno"        : (TipoToken.PALABRA_RESERVADA, "PR_09"),
    "coseno"      : (TipoToken.PALABRA_RESERVADA, "PR_10"),
    "magnitud"    : (TipoToken.PALABRA_RESERVADA, "PR_11"),
    "gravedad"    : (TipoToken.PALABRA_RESERVADA, "PR_12"),
    "posicion"    : (TipoToken.PALABRA_RESERVADA, "PR_13"),
    "velocidad"   : (TipoToken.PALABRA_RESERVADA, "PR_14"),
    "aceleracion" : (TipoToken.PALABRA_RESERVADA, "PR_15"),
    "tiempo"      : (TipoToken.PALABRA_RESERVADA, "PR_16"),
    "altura"      : (TipoToken.PALABRA_RESERVADA, "PR_17"),
    "alcance"     : (TipoToken.PALABRA_RESERVADA, "PR_18"),
}

# ── Operadores matemáticos ────────────────────────────────────
OPERADORES_MATEMATICOS: dict[str, tuple[str, str]] = {
    "+" : (TipoToken.OPERADOR_MATEMATICO, "OPM_01"),
    "-" : (TipoToken.OPERADOR_MATEMATICO, "OPM_02"),
    "*" : (TipoToken.OPERADOR_MATEMATICO, "OPM_03"),
    "/" : (TipoToken.OPERADOR_MATEMATICO, "OPM_04"),
    "^" : (TipoToken.OPERADOR_MATEMATICO, "OPM_05"),
}

# ── Operadores relacionales ───────────────────────────────────
OPERADORES_RELACIONALES: dict[str, tuple[str, str]] = {
    ":=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_01"),
    "="  : (TipoToken.OPERADOR_RELACIONAL, "OPR_02"),
    "<"  : (TipoToken.OPERADOR_RELACIONAL, "OPR_03"),
    ">"  : (TipoToken.OPERADOR_RELACIONAL, "OPR_04"),
    "<=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_05"),
    ">=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_06"),
    "!=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_07"),
}

# ── Signos ───────────────────────────────────────────────────
SIGNOS: dict[str, tuple[str, str]] = {
    "(" : (TipoToken.SIGNO, "SIG_01"),
    ")" : (TipoToken.SIGNO, "SIG_02"),
    "[" : (TipoToken.SIGNO, "SIG_03"),
    "]" : (TipoToken.SIGNO, "SIG_04"),
    "," : (TipoToken.SIGNO, "SIG_05"),
    "." : (TipoToken.SIGNO, "SIG_06"),
    ";" : (TipoToken.SIGNO, "SIG_07"),
}

# ── Alfabeto válido ───────────────────────────────────────────
ALFABETO_VALIDO: set[str] = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "+-*/^"
    ":=<>!"
    "()[],.; "
    "\t\n\r"
)

# ── Paleta de colores GUI (dark – Catppuccin Mocha) ──────────
COLORES_GUI = {
    # Fondos
    "bg_main"    : "#1e1e2e",
    "bg_editor"  : "#181825",
    "bg_panel"   : "#24273a",
    "bg_toolbar" : "#181825",
    "bg_status"  : "#11111b",
    "bg_row_alt" : "#2a2a3e",
    # Texto
    "fg_main"    : "#cdd6f4",
    "fg_dim"     : "#6c7086",
    "fg_lineno"  : "#585b70",
    # Tipos de token (tabla + editor)
    "col_PR"     : "#89b4fa",   # azul   — palabras reservadas
    "col_OPM"    : "#f38ba8",   # rojo   — operadores matemáticos
    "col_OPR"    : "#fab387",   # naranja— operadores relacionales
    "col_SIG"    : "#94e2d5",   # cyan   — signos
    "col_ID"     : "#a6e3a1",   # verde  — identificadores
    "col_NUM"    : "#f9e2af",   # amarillo — números
    "col_ERROR"  : "#f38ba8",   # rojo   — errores
    # Acento
    "accent"     : "#cba6f7",   # morado
    "accent2"    : "#89dceb",   # celeste
    "ok_green"   : "#a6e3a1",
    "err_red"    : "#f38ba8",
    # Borde / separador
    "border"     : "#313244",
}
