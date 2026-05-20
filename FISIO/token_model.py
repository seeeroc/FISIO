"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: token_model.py
 Descripción: Clase Token — unidad fundamental del análisis léxico.
              Encapsula lexema, tipo, ID, línea y columna.
=============================================================
"""


class Token:
    """
    Representa un token reconocido durante el análisis léxico.

    Atributos
    ---------
    lexema  : str   — secuencia de caracteres reconocida
    tipo    : str   — categoría del token (PR, OPM, OPR, SIG, ID, NUM, ERROR)
    id_tok  : str   — identificador único del token (p.e. PR_01, OPM_03...)
    linea   : int   — número de línea donde aparece (1-indexado)
    columna : int   — número de columna donde inicia (1-indexado)
    mensaje : str   — mensaje adicional (usado solo en tokens de error)
    """

    def __init__(
        self,
        lexema:  str,
        tipo:    str,
        id_tok:  str,
        linea:   int,
        columna: int,
        mensaje: str = "",
    ) -> None:
        self.lexema  = lexema
        self.tipo    = tipo
        self.id_tok  = id_tok
        self.linea   = linea
        self.columna = columna
        self.mensaje = mensaje

    # ── Representación para depuración ──────────────────────
    def __repr__(self) -> str:
        return (
            f"Token(lexema={self.lexema!r}, tipo={self.tipo!r}, "
            f"id={self.id_tok!r}, línea={self.linea}, col={self.columna})"
        )

    # ── Serialización a diccionario ──────────────────────────
    def to_dict(self) -> dict:
        return {
            "lexema" : self.lexema,
            "tipo"   : self.tipo,
            "id"     : self.id_tok,
            "linea"  : self.linea,
            "columna": self.columna,
        }
