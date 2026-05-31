"""
Analizador lexico lineal para el lenguaje FISIO.
"""

from __future__ import annotations

from token_types import (
    ALFABETO_VALIDO,
    OPERADORES_MATEMATICOS,
    OPERADORES_RELACIONALES,
    PALABRAS_RESERVADAS,
    SIGNOS,
    ErrorLexico,
    TipoToken,
    Token,
)


class Lexer:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens: list[Token] = []
        self.errores: list[ErrorLexico] = []

    def analizar(self) -> tuple[list[Token], list[ErrorLexico]]:
        while not self._fin():
            actual = self._actual()

            if actual in " \t":
                self._avanzar()
                continue

            if actual in "\r\n":
                self._avanzar_linea()
                continue

            if actual.isdigit():
                self._leer_numero()
                continue

            if self._es_letra(actual):
                self._leer_identificador_o_reservada()
                continue

            if actual == "." and self._siguiente().isdigit():
                self._leer_decimal_sin_entero()
                continue

            if actual in {":", "!", "<", ">"}:
                self._leer_operador_relacional()
                continue

            if actual in OPERADORES_RELACIONALES:
                self._agregar_token_actual(OPERADORES_RELACIONALES[actual])
                self._avanzar()
                continue

            if actual in OPERADORES_MATEMATICOS:
                self._agregar_token_actual(OPERADORES_MATEMATICOS[actual])
                self._avanzar()
                continue

            if actual in SIGNOS:
                self._agregar_token_actual(SIGNOS[actual])
                self._avanzar()
                continue

            self._leer_caracter_invalido()

        return self.tokens, self.errores

    def _leer_identificador_o_reservada(self) -> None:
        linea_inicio = self.linea
        columna_inicio = self.columna
        lexema = self._consumir_mientras(
            lambda char: self._es_letra(char) or char.isdigit()
        )

        if self._hay_continuacion_mal_formada():
            lexema += self._consumir_fragmento_mal_formado()
            self._agregar_error(
                lexema,
                "Caracter fuera del alfabeto FISIO",
                linea_inicio,
                columna_inicio,
            )
            return

        if lexema in PALABRAS_RESERVADAS:
            tipo, id_tok = PALABRAS_RESERVADAS[lexema]
        else:
            tipo, id_tok = TipoToken.ID, "ID"

        self.tokens.append(Token(lexema, tipo, id_tok, linea_inicio, columna_inicio))

    def _leer_numero(self) -> None:
        linea_inicio = self.linea
        columna_inicio = self.columna
        lexema = self._consumir_mientras(str.isdigit)
        tiene_decimal = False
        mal_formado = False

        if self._actual() == ".":
            tiene_decimal = True
            lexema += self._avanzar()

            if not self._actual().isdigit():
                mal_formado = True
            else:
                lexema += self._consumir_mientras(str.isdigit)

        if self._actual() == ".":
            mal_formado = True
            lexema += self._consumir_fragmento_mal_formado()
        elif self._hay_continuacion_mal_formada(punto_es_delimitador=False):
            mal_formado = True
            lexema += self._consumir_fragmento_mal_formado()

        if (
            not mal_formado
            and not tiene_decimal
            and len(lexema) > 1
            and lexema.startswith("0")
        ):
            mal_formado = True

        if mal_formado:
            mensaje = "Numero mal formado"
            if self._contiene_caracter_fuera_alfabeto(lexema):
                mensaje = "Caracter fuera del alfabeto FISIO"

            self._agregar_error(
                lexema,
                mensaje,
                linea_inicio,
                columna_inicio,
            )
            return

        self.tokens.append(Token(lexema, TipoToken.NUM, "NUM", linea_inicio, columna_inicio))

    def _leer_decimal_sin_entero(self) -> None:
        linea_inicio = self.linea
        columna_inicio = self.columna
        lexema = self._avanzar()
        lexema += self._consumir_mientras(str.isdigit)

        if self._hay_continuacion_mal_formada(punto_es_delimitador=False):
            lexema += self._consumir_fragmento_mal_formado()

        self._agregar_error(
            lexema,
            "Numero decimal sin parte entera",
            linea_inicio,
            columna_inicio,
        )

    def _leer_operador_relacional(self) -> None:
        linea_inicio = self.linea
        columna_inicio = self.columna
        actual = self._actual()
        siguiente = self._siguiente()
        lexema_doble = actual + siguiente

        if lexema_doble in OPERADORES_RELACIONALES:
            tipo, id_tok = OPERADORES_RELACIONALES[lexema_doble]
            self.tokens.append(Token(lexema_doble, tipo, id_tok, linea_inicio, columna_inicio))
            self._avanzar()
            self._avanzar()
            return

        if actual in {"<", ">"}:
            tipo, id_tok = OPERADORES_RELACIONALES[actual]
            self.tokens.append(Token(actual, tipo, id_tok, linea_inicio, columna_inicio))
            self._avanzar()
            return

        lexema = self._avanzar()
        if self._hay_continuacion_mal_formada():
            lexema += self._consumir_fragmento_mal_formado()

        self._agregar_error(
            lexema,
            "Operador relacional incompleto o invalido",
            linea_inicio,
            columna_inicio,
        )

    def _leer_caracter_invalido(self) -> None:
        linea_inicio = self.linea
        columna_inicio = self.columna
        lexema = self._avanzar()
        lexema += self._consumir_fragmento_mal_formado()
        mensaje = "Caracter fuera del alfabeto FISIO"

        if not self._contiene_caracter_fuera_alfabeto(lexema):
            mensaje = "Caracter no reconocido en este contexto"

        self._agregar_error(lexema, mensaje, linea_inicio, columna_inicio)

    def _agregar_error(
        self,
        lexema: str,
        mensaje: str,
        linea: int,
        columna: int,
    ) -> None:
        self.errores.append(ErrorLexico(lexema, mensaje, linea, columna))
        self.tokens.append(Token(lexema, TipoToken.ERROR, "ERROR", linea, columna))

    def _consumir_fragmento_mal_formado(self) -> str:
        return self._consumir_mientras(
            lambda char: not self._es_delimitador_lexema(
                char,
                punto_es_delimitador=False,
            )
        )

    def _consumir_mientras(self, condicion) -> str:
        lexema = ""
        while not self._fin() and condicion(self._actual()):
            lexema += self._avanzar()
        return lexema

    def _agregar_token_actual(self, definicion: tuple[str, str]) -> None:
        tipo, id_tok = definicion
        self.tokens.append(Token(self._actual(), tipo, id_tok, self.linea, self.columna))

    def _contiene_caracter_fuera_alfabeto(self, lexema: str) -> bool:
        return any(char not in ALFABETO_VALIDO for char in lexema)

    def _hay_continuacion_mal_formada(
        self,
        *,
        punto_es_delimitador: bool = True,
    ) -> bool:
        return not self._es_delimitador_lexema(
            self._actual(),
            punto_es_delimitador=punto_es_delimitador,
        )

    def _es_delimitador_lexema(
        self,
        char: str,
        *,
        punto_es_delimitador: bool = True,
    ) -> bool:
        if char == "\0" or char in " \t\r\n":
            return True

        if char in OPERADORES_MATEMATICOS or char in "=<>":
            return True

        if char in ":!":
            return self._siguiente() == "="

        if char in SIGNOS:
            return punto_es_delimitador or char != "."

        return False

    def _actual(self) -> str:
        if self._fin():
            return "\0"
        return self.codigo[self.pos]

    def _siguiente(self) -> str:
        indice = self.pos + 1
        if indice >= len(self.codigo):
            return "\0"
        return self.codigo[indice]

    def _avanzar(self) -> str:
        char = self.codigo[self.pos]
        self.pos += 1
        self.columna += 1
        return char

    def _avanzar_linea(self) -> None:
        if self._actual() == "\r" and self._siguiente() == "\n":
            self.pos += 2
        else:
            self.pos += 1

        self.linea += 1
        self.columna = 1

    def _fin(self) -> bool:
        return self.pos >= len(self.codigo)

    @staticmethod
    def _es_letra(char: str) -> bool:
        return ("a" <= char <= "z") or ("A" <= char <= "Z")
