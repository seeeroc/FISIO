"""
Definiciones de tokens para el analizador lexico del lenguaje FISIO.
"""

from __future__ import annotations

from dataclasses import dataclass
import string


class TipoToken:
    """Tipos de token usados por la GUI y el analizador lexico."""

    PR = "PR"
    OPM = "OPM"
    OPR = "OPR"
    SIG = "SIG"
    ID = "ID"
    NUM = "NUM"
    ERROR = "ERROR"


PALABRAS_RESERVADAS: dict[str, tuple[str, str]] = {
    "mru": (TipoToken.PR, "PR_01"),
    "mrua": (TipoToken.PR, "PR_02"),
    "caida": (TipoToken.PR, "PR_03"),
    "parabolico": (TipoToken.PR, "PR_04"),
    "despejar": (TipoToken.PR, "PR_05"),
    "graficar": (TipoToken.PR, "PR_06"),
    "simular": (TipoToken.PR, "PR_07"),
    "raiz": (TipoToken.PR, "PR_08"),
    "seno": (TipoToken.PR, "PR_09"),
    "coseno": (TipoToken.PR, "PR_10"),
    "magnitud": (TipoToken.PR, "PR_11"),
    "gravedad": (TipoToken.PR, "PR_12"),
    "posicion": (TipoToken.PR, "PR_13"),
    "velocidad": (TipoToken.PR, "PR_14"),
    "aceleracion": (TipoToken.PR, "PR_15"),
    "tiempo": (TipoToken.PR, "PR_16"),
    "altura": (TipoToken.PR, "PR_17"),
    "alcance": (TipoToken.PR, "PR_18"),
    "Inicio": (TipoToken.PR, "PR_19"),
    "Fin": (TipoToken.PR, "PR_20"),
}

OPERADORES_MATEMATICOS: dict[str, tuple[str, str]] = {
    "+": (TipoToken.OPM, "OPM_01"),
    "-": (TipoToken.OPM, "OPM_02"),
    "*": (TipoToken.OPM, "OPM_03"),
    "/": (TipoToken.OPM, "OPM_04"),
    "^": (TipoToken.OPM, "OPM_05"),
}

OPERADORES_RELACIONALES: dict[str, tuple[str, str]] = {
    ":=": (TipoToken.OPR, "OPR_01"),
    "=": (TipoToken.OPR, "OPR_02"),
    "<": (TipoToken.OPR, "OPR_03"),
    ">": (TipoToken.OPR, "OPR_04"),
    "<=": (TipoToken.OPR, "OPR_05"),
    ">=": (TipoToken.OPR, "OPR_06"),
    "!=": (TipoToken.OPR, "OPR_07"),
}

SIGNOS: dict[str, tuple[str, str]] = {
    "(": (TipoToken.SIG, "SIG_01"),
    ")": (TipoToken.SIG, "SIG_02"),
    "[": (TipoToken.SIG, "SIG_03"),
    "]": (TipoToken.SIG, "SIG_04"),
    ",": (TipoToken.SIG, "SIG_05"),
    ".": (TipoToken.SIG, "SIG_06"),
    ";": (TipoToken.SIG, "SIG_07"),
}

ALFABETO_VALIDO: set[str] = set(
    string.ascii_letters
    + string.digits
    + " \t\r\n"
    + "".join(OPERADORES_MATEMATICOS)
    + "".join(SIGNOS)
    + ":=!<>"
)

COLORES_GUI: dict[str, str] = {
    "bg_main": "#1e1e2e",
    "bg_editor": "#181825",
    "bg_panel": "#11111b",
    "bg_toolbar": "#313244",
    "bg_status": "#181825",
    "bg_row_alt": "#1e1e2e",
    "border": "#45475a",
    "fg_main": "#cdd6f4",
    "fg_dim": "#a6adc8",
    "fg_lineno": "#6c7086",
    "accent": "#89b4fa",
    "ok_green": "#a6e3a1",
    "col_PR": "#cba6f7",
    "col_OPM": "#f9e2af",
    "col_OPR": "#fab387",
    "col_SIG": "#89dceb",
    "col_ID": "#cdd6f4",
    "col_NUM": "#a6e3a1",
    "col_ERROR": "#f38ba8",
}


@dataclass(frozen=True, slots=True)
class Token:
    lexema: str
    tipo: str
    id_tok: str
    linea: int
    columna: int


@dataclass(frozen=True, slots=True)
class ErrorLexico:
    lexema: str
    mensaje: str
    linea: int
    columna: int
