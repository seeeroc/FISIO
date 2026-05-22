"""
=============================================================
 FISIO - Analizador Léxico  |  lexer.py  v2
 Clase Lexer — AFD principal re-validado completamente.
=============================================================
"""

import re
from token_model import Token
from token_types import (
    TipoToken, PALABRAS_RESERVADAS, OPERADORES_MATEMATICOS,
    OPERADORES_RELACIONALES, SIGNOS, ALFABETO_VALIDO,
)
from validador import Validador


class Lexer:
    """Analizador léxico del lenguaje FISIO (v2 — re-validado)."""

    def __init__(self, fuente: str) -> None:
        self.fuente  = fuente
        self.pos     = 0
        self.linea   = 1
        self.columna = 1
        self.tokens : list[Token] = []
        self.errores: list[Token] = []

    # ── Punto de entrada ─────────────────────────────────────
    def analizar(self) -> tuple[list[Token], list[Token]]:
        self.pos = self.linea = 0
        self.columna = 1
        self.linea   = 1
        self.tokens  = []
        self.errores = []

        while not self._fin():
            car = self._actual()

            # Blancos
            if car in (' ', '\t', '\r'):
                self._avanzar(); continue
            if car == '\n':
                self._avanzar(); self.linea += 1; self.columna = 1; continue

            # Fuera del alfabeto
            if car not in ALFABETO_VALIDO:
                self._registrar_error(
                    car,
                    f"Símbolo no reconocido '{car}': "
                    "fuera del alfabeto del lenguaje FISIO."
                )
                self._avanzar(); continue

            if car.isalpha():
                self._leer_palabra(); continue
            if car.isdigit():
                self._leer_numero(); continue
            if car == '.':
                self._manejar_punto_inicial(); continue
            if car in (':', '<', '>', '!'):
                self._leer_operador_compuesto(car); continue
            if car == '=':
                self._agregar_token_en(car, *OPERADORES_RELACIONALES['='],
                                       self.linea, self.columna)
                self._avanzar(); continue
            if car in OPERADORES_MATEMATICOS:
                self._agregar_token_en(car, *OPERADORES_MATEMATICOS[car],
                                       self.linea, self.columna)
                self._avanzar(); continue
            if car in SIGNOS:
                self._agregar_token_en(car, *SIGNOS[car],
                                       self.linea, self.columna)
                self._avanzar(); continue

            # Cualquier otro
            self._registrar_error(car, f"Carácter inesperado '{car}'.")
            self._avanzar()

        return self.tokens, self.errores

    # ── Leer palabra (PR / ID) ────────────────────────────────
    def _leer_palabra(self) -> None:
        col_ini, lin_ini = self.columna, self.linea
        buf = ""
        while not self._fin() and self._actual().isalnum():
            buf += self._actual(); self._avanzar()

        # Carácter inválido pegado (ej: abc@)
        if not self._fin() and self._actual() not in ALFABETO_VALIDO:
            inv = self._actual()
            buf += inv; self._avanzar()
            self._registrar_error_en(
                buf, lin_ini, col_ini,
                f"Identificador inválido '{buf}': "
                f"contiene carácter no permitido '{inv}'."
            )
            return

        if buf in PALABRAS_RESERVADAS:
            tipo, id_tok = PALABRAS_RESERVADAS[buf]
            self._agregar_token_en(buf, tipo, id_tok, lin_ini, col_ini)
        else:
            valido, msg = Validador.validar_identificador(buf)
            if valido:
                self._agregar_token_en(buf, TipoToken.IDENTIFICADOR, "ID",
                                       lin_ini, col_ini)
            else:
                self._registrar_error_en(buf, lin_ini, col_ini, msg)

    # ── Leer número ───────────────────────────────────────────
    def _leer_numero(self) -> None:
        """
        AFD simplificado para literales numéricos.
        Agrupa caracteres alfanuméricos y puntos en una única secuencia,
        para luego delegar la validación y errores específicos al Validador.
        """
        col_ini, lin_ini = self.columna, self.linea
        buf = ""
        while not self._fin() and (self._actual().isalnum() or self._actual() == '.'):
            buf += self._actual()
            self._avanzar()

        valido, msg = Validador.validar_numero(buf)
        if valido:
            self._agregar_token_en(buf, TipoToken.NUMERO, "NUM", lin_ini, col_ini)
        else:
            self._registrar_error_en(buf, lin_ini, col_ini, msg)

    # ── Punto inicial (.5) ────────────────────────────────────
    def _manejar_punto_inicial(self) -> None:
        """
        Maneja literales que inician con punto.
        Si va seguido de un dígito, se lee como un literal numérico (inválido por no tener parte entera).
        De lo contrario, se trata como el signo punto '.'.
        """
        col_ini, lin_ini = self.columna, self.linea
        sig_pos = self.pos + 1
        if sig_pos < len(self.fuente) and self.fuente[sig_pos].isdigit():
            buf = "."
            self._avanzar()
            while not self._fin() and (self._actual().isalnum() or self._actual() == '.'):
                buf += self._actual()
                self._avanzar()
            self._agregar_token_en(
                buf, TipoToken.NUMERO, "NUM", lin_ini, col_ini
            )
        else:
            self._agregar_token_en(".", *SIGNOS["."], lin_ini, col_ini)
            self._avanzar()

    # ── Operador compuesto (:=, <=, >=, !=) ──────────────────
    def _leer_operador_compuesto(self, primer: str) -> None:
        col_ini, lin_ini = self.columna, self.linea
        self._avanzar()
        seg = self._actual() if not self._fin() else ""
        doble = primer + seg

        if doble in OPERADORES_RELACIONALES:
            self._agregar_token_en(doble, *OPERADORES_RELACIONALES[doble],
                                   lin_ini, col_ini)
            self._avanzar()
        elif primer in OPERADORES_RELACIONALES:
            self._agregar_token_en(primer, *OPERADORES_RELACIONALES[primer],
                                   lin_ini, col_ini)
        else:
            self._agregar_token_en(primer, TipoToken.SIGNO, "SIG_OP", lin_ini, col_ini)

    # ── Navegación ────────────────────────────────────────────
    def _actual(self) -> str:        return self.fuente[self.pos]
    def _avanzar(self) -> None:      self.pos += 1; self.columna += 1
    def _fin(self) -> bool:          return self.pos >= len(self.fuente)

    # ── Registro ─────────────────────────────────────────────
    def _agregar_token_en(self, lex, tipo, id_tok, lin, col):
        self.tokens.append(Token(lex, tipo, id_tok, lin, col))

    def _registrar_error(self, lex, msg):
        self.errores.append(
            Token(lex, TipoToken.ERROR, "ERROR", self.linea, self.columna, msg)
        )

    def _registrar_error_en(self, lex, lin, col, msg):
        self.errores.append(Token(lex, TipoToken.ERROR, "ERROR", lin, col, msg))
