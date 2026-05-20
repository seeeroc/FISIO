"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: token_types.py
 Descripción: Definición de tipos de tokens, IDs y categorías
              del lenguaje FISIO para problemas de física clásica.
 Autor: Analizador Léxico FISIO
=============================================================
"""

# ─────────────────────────────────────────────────────────────
#  CATEGORÍAS DE TOKENS
# ─────────────────────────────────────────────────────────────
class TipoToken:
    """Enumeración de categorías de tokens del lenguaje FISIO."""
    PALABRA_RESERVADA  = "PR"
    OPERADOR_MATEMATICO = "OPM"
    OPERADOR_RELACIONAL = "OPR"
    SIGNO              = "SIG"
    IDENTIFICADOR      = "ID"
    NUMERO             = "NUM"
    ERROR              = "ERROR"


# ─────────────────────────────────────────────────────────────
#  PALABRAS RESERVADAS  →  (categoría, ID)
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
#  OPERADORES MATEMÁTICOS  →  (categoría, ID)
# ─────────────────────────────────────────────────────────────
OPERADORES_MATEMATICOS: dict[str, tuple[str, str]] = {
    "+" : (TipoToken.OPERADOR_MATEMATICO, "OPM_01"),
    "-" : (TipoToken.OPERADOR_MATEMATICO, "OPM_02"),
    "*" : (TipoToken.OPERADOR_MATEMATICO, "OPM_03"),
    "/" : (TipoToken.OPERADOR_MATEMATICO, "OPM_04"),
    "^" : (TipoToken.OPERADOR_MATEMATICO, "OPM_05"),
}

# ─────────────────────────────────────────────────────────────
#  OPERADORES RELACIONALES / ASIGNACIÓN  →  (categoría, ID)
#  Nota: los operadores de 2 caracteres deben verificarse ANTES
#        que los de 1 carácter para el análisis correcto.
# ─────────────────────────────────────────────────────────────
OPERADORES_RELACIONALES: dict[str, tuple[str, str]] = {
    ":=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_01"),
    "="  : (TipoToken.OPERADOR_RELACIONAL, "OPR_02"),
    "<"  : (TipoToken.OPERADOR_RELACIONAL, "OPR_03"),
    ">"  : (TipoToken.OPERADOR_RELACIONAL, "OPR_04"),
    "<=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_05"),
    ">=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_06"),
    "!=" : (TipoToken.OPERADOR_RELACIONAL, "OPR_07"),
}

# ─────────────────────────────────────────────────────────────
#  SIGNOS DE AGRUPACIÓN Y PUNTUACIÓN  →  (categoría, ID)
# ─────────────────────────────────────────────────────────────
SIGNOS: dict[str, tuple[str, str]] = {
    "(" : (TipoToken.SIGNO, "SIG_01"),
    ")" : (TipoToken.SIGNO, "SIG_02"),
    "[" : (TipoToken.SIGNO, "SIG_03"),
    "]" : (TipoToken.SIGNO, "SIG_04"),
    "," : (TipoToken.SIGNO, "SIG_05"),
    "." : (TipoToken.SIGNO, "SIG_06"),
    ";" : (TipoToken.SIGNO, "SIG_07"),
}

# ─────────────────────────────────────────────────────────────
#  ALFABETO VÁLIDO DEL LENGUAJE FISIO
# ─────────────────────────────────────────────────────────────
ALFABETO_VALIDO: set[str] = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "+-*/^"
    ":=<>!"
    "()[],.; "
    "\t\n\r"
)
