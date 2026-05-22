"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: salida.py
 Descripción: Formateador de salida profesional.
              Genera tablas de tokens, reportes de errores
              y resúmenes estadísticos del análisis léxico.
=============================================================
"""

from token_model import Token


# ─────────────────────────────────────────────────────────────
#  PALETA DE COLORES ANSI (para terminales compatibles)
# ─────────────────────────────────────────────────────────────
class Color:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    CYAN     = "\033[96m"
    GREEN    = "\033[92m"
    YELLOW   = "\033[93m"
    RED      = "\033[91m"
    MAGENTA  = "\033[95m"
    BLUE     = "\033[94m"
    WHITE    = "\033[97m"
    DIM      = "\033[2m"

    @staticmethod
    def aplicar(texto: str, *codigos: str) -> str:
        """Aplica uno o más códigos de color ANSI a un texto."""
        return "".join(codigos) + texto + Color.RESET


# ─────────────────────────────────────────────────────────────
#  CLASE FORMATEADOR DE SALIDA
# ─────────────────────────────────────────────────────────────
class FormateadorSalida:
    """
    Genera salida profesional para el analizador léxico FISIO.

    Uso
    ---
        fmt = FormateadorSalida(tokens, errores, usar_color=True)
        fmt.imprimir_todo()
    """

    # Anchos de columna de la tabla principal
    _ANC_LEXEMA  = 18
    _ANC_TIPO    = 14
    _ANC_ID      = 10
    _ANC_LINEA   =  7
    _ANC_COLUMNA =  9

    def __init__(
        self,
        tokens:     list[Token],
        errores:    list[Token],
        usar_color: bool = True,
    ) -> None:
        self.tokens     = tokens
        self.errores    = errores
        self.usar_color = usar_color

    # ── API pública ──────────────────────────────────────────
    def imprimir_todo(self) -> None:
        """Imprime el encabezado, tabla de tokens, errores y resumen."""
        self._imprimir_encabezado()
        self._imprimir_tabla_tokens()
        self._imprimir_errores()
        self._imprimir_resumen()

    def imprimir_tabla_tokens(self) -> None:
        """Imprime solo la tabla de tokens."""
        self._imprimir_tabla_tokens()

    def imprimir_errores(self) -> None:
        """Imprime solo los errores."""
        self._imprimir_errores()

    # ── Encabezado ───────────────────────────────────────────
    def _imprimir_encabezado(self) -> None:
        linea = "=" * 70
        print()
        print(self._c(linea, Color.CYAN, Color.BOLD))
        print(self._c(
            "  FISIO — ANALIZADOR LÉXICO".center(70),
            Color.CYAN, Color.BOLD
        ))
        print(self._c(
            "  Lenguaje para Física Clásica (MRU, MRUA, Caída Libre, Parabólico)".center(70),
            Color.DIM
        ))
        print(self._c(linea, Color.CYAN, Color.BOLD))
        print()

    # ── Tabla de tokens ──────────────────────────────────────
    def _imprimir_tabla_tokens(self) -> None:
        a = self._ANC_LEXEMA
        b = self._ANC_TIPO
        c = self._ANC_ID
        d = self._ANC_LINEA
        e = self._ANC_COLUMNA

        separador = (
            "+" + "-"*(a+2) + "+" + "-"*(b+2) + "+"
            + "-"*(c+2) + "+" + "-"*(d+2) + "+" + "-"*(e+2) + "+"
        )

        encabezado = (
            f"| {'LEXEMA':<{a}} | {'TIPO':<{b}} | {'ID TOKEN':<{c}} "
            f"| {'LÍNEA':<{d}} | {'COLUMNA':<{e}} |"
        )

        print(self._c("  TABLA DE TOKENS RECONOCIDOS", Color.GREEN, Color.BOLD))
        print(self._c(separador, Color.DIM))
        print(self._c(encabezado, Color.WHITE, Color.BOLD))
        print(self._c(separador, Color.DIM))

        if not self.tokens:
            vacio = f"| {'(ningún token reconocido)':<{a+b+c+d+e+13}} |"
            print(self._c(vacio, Color.YELLOW))
        else:
            for tok in self.tokens:
                color_tipo = self._color_por_tipo(tok.tipo)
                lex_txt  = self._truncar(tok.lexema,  a)
                tipo_txt = self._truncar(tok.tipo,    b)
                id_txt   = self._truncar(tok.id_tok,  c)
                fila = (
                    f"| {lex_txt:<{a}} | "
                    f"{tipo_txt:<{b}} | "
                    f"{id_txt:<{c}} | "
                    f"{tok.linea:<{d}} | "
                    f"{tok.columna:<{e}} |"
                )
                print(self._c(fila, color_tipo))

        print(self._c(separador, Color.DIM))
        print()

    # ── Reporte de errores ───────────────────────────────────
    def _imprimir_errores(self) -> None:
        if not self.errores:
            msg = "  ✔  Sin errores léxicos detectados."
            print(self._c(msg, Color.GREEN, Color.BOLD))
            print()
            return

        titulo = f"  ERRORES LÉXICOS DETECTADOS ({len(self.errores)})"
        print(self._c(titulo, Color.RED, Color.BOLD))
        print(self._c("  " + "─" * 66, Color.RED))

        for i, err in enumerate(self.errores, 1):
            num   = self._c(f"  [{i}]", Color.YELLOW, Color.BOLD)
            label = self._c("  ERROR LÉXICO:", Color.RED, Color.BOLD)
            print(f"\n{num} {label}")
            print(self._c(f"      {err.mensaje}", Color.WHITE))
            print(
                self._c(f"      Lexema  : ", Color.DIM) +
                self._c(f"'{err.lexema}'", Color.MAGENTA, Color.BOLD)
            )
            print(
                self._c(f"      Línea   : ", Color.DIM) +
                self._c(str(err.linea),   Color.YELLOW)
            )
            print(
                self._c(f"      Columna : ", Color.DIM) +
                self._c(str(err.columna), Color.YELLOW)
            )

        print()
        print(self._c("  " + "─" * 66, Color.RED))
        print()

    # ── Resumen estadístico ──────────────────────────────────
    def _imprimir_resumen(self) -> None:
        conteos: dict[str, int] = {}
        for tok in self.tokens:
            conteos[tok.tipo] = conteos.get(tok.tipo, 0) + 1

        total_tok = len(self.tokens)
        total_err = len(self.errores)

        print(self._c("  RESUMEN DEL ANÁLISIS", Color.CYAN, Color.BOLD))
        print(self._c("  " + "─" * 40, Color.CYAN))
        print(
            self._c("  Total de tokens   : ", Color.DIM) +
            self._c(str(total_tok), Color.GREEN, Color.BOLD)
        )
        print(
            self._c("  Total de errores  : ", Color.DIM) +
            self._c(str(total_err), Color.RED if total_err else Color.GREEN, Color.BOLD)
        )
        print()

        if conteos:
            print(self._c("  Distribución por tipo:", Color.WHITE, Color.BOLD))
            for tipo, cantidad in sorted(conteos.items()):
                barra  = "█" * cantidad
                linea  = f"    {tipo:<6} │ {barra:<30} {cantidad}"
                print(self._c(linea, self._color_por_tipo(tipo)))

        print()
        linea_final = "=" * 70
        estado = (
            self._c("  RESULTADO: ", Color.BOLD) +
            (
                self._c("ANÁLISIS EXITOSO — sin errores léxicos ✔", Color.GREEN, Color.BOLD)
                if total_err == 0 else
                self._c(f"ANÁLISIS COMPLETADO — {total_err} error(es) encontrado(s) ✖", Color.RED, Color.BOLD)
            )
        )
        print(self._c(linea_final, Color.CYAN, Color.BOLD))
        print(estado)
        print(self._c(linea_final, Color.CYAN, Color.BOLD))
        print()

    # ── Utilidades internas ──────────────────────────────────
    def _c(self, texto: str, *codigos: str) -> str:
        """Aplica color si está habilitado, de lo contrario retorna el texto."""
        if self.usar_color:
            return Color.aplicar(texto, *codigos)
        return texto

    @staticmethod
    def _truncar(texto: str, ancho: int) -> str:
        """Trunca el texto si supera el ancho máximo de columna."""
        if len(texto) > ancho:
            return texto[:ancho - 1] + "…"
        return texto

    @staticmethod
    def _color_por_tipo(tipo: str) -> str:
        """Retorna el código de color ANSI según el tipo de token."""
        mapa = {
            "PR"    : Color.BLUE,
            "OPM"   : Color.MAGENTA,
            "OPR"   : Color.YELLOW,
            "SIG"   : Color.CYAN,
            "ID"    : Color.GREEN,
            "NUM"   : Color.WHITE,
            "ERROR" : Color.RED,
        }
        return mapa.get(tipo, Color.RESET)
