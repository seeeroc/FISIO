"""
Parser descendente recursivo para el lenguaje FISIO.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional

from token_types import TipoToken, Token


@dataclass(frozen=True, slots=True)
class NodoAST:
    """Clase base para todos los nodos del AST."""

    linea: int
    columna: int


@dataclass(frozen=True, slots=True)
class NodoPrograma(NodoAST):
    sentencias: list[NodoAST]


@dataclass(frozen=True, slots=True)
class NodoAsignacion(NodoAST):
    lugar: NodoAST
    expresion: NodoAST


@dataclass(frozen=True, slots=True)
class NodoComando(NodoAST):
    nombre: Token
    argumentos: list[NodoAST]


@dataclass(frozen=True, slots=True)
class NodoCalculo(NodoAST):
    nombre: Token
    expresion: NodoAST


@dataclass(frozen=True, slots=True)
class NodoParametro(NodoAST):
    variable: Token
    expresion: NodoAST


@dataclass(frozen=True, slots=True)
class NodoOperacion(NodoAST):
    operador: Token
    izquierda: NodoAST
    derecha: NodoAST


@dataclass(frozen=True, slots=True)
class NodoOperacionRelacional(NodoAST):
    operador: Token
    izquierda: NodoAST
    derecha: NodoAST


@dataclass(frozen=True, slots=True)
class NodoAgrupacion(NodoAST):
    expresion: NodoAST


@dataclass(frozen=True, slots=True)
class NodoNumero(NodoAST):
    token: Token


@dataclass(frozen=True, slots=True)
class NodoIdentificador(NodoAST):
    token: Token


@dataclass(frozen=True, slots=True)
class NodoAccesoArreglo(NodoAST):
    identificador: Token
    indice: Token


@dataclass(frozen=True, slots=True)
class NodoVariableFisica(NodoAST):
    token: Token


@dataclass(frozen=True, slots=True)
class ErrorSintactico:
    token: Token
    mensaje: str
    linea: int
    columna: int


class Parser:
    VAR_FISICAS: ClassVar[frozenset[str]] = frozenset(
        {
            "gravedad",
            "posicion",
            "velocidad",
            "aceleracion",
            "tiempo",
            "altura",
            "alcance",
        }
    )
    CMD_MOVIMIENTO: ClassVar[frozenset[str]] = frozenset(
        {"mru", "mrua", "caida", "parabolico"}
    )
    CMD_FUNCION: ClassVar[frozenset[str]] = frozenset(
        {"despejar", "graficar", "simular"}
    )
    CALCULOS: ClassVar[frozenset[str]] = frozenset(
        {"raiz", "seno", "coseno", "magnitud"}
    )
    OP_RELACIONALES: ClassVar[frozenset[str]] = frozenset(
        {"=", "<", ">", "<=", ">=", "!="}
    )
    SINCRONIZACION: ClassVar[frozenset[str]] = frozenset({";", "Fin"})

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errores: list[ErrorSintactico] = []
        self.eof = self._crear_eof()

    def parse(self) -> tuple[NodoAST, list[ErrorSintactico]]:
        sentencias: list[NodoAST] = []
        tiene_inicio = self._coincidir_lexema("Inicio")

        while not self._fin():
            if self._check_lexema("Fin"):
                break

            if self._check_lexema("Inicio"):
                self._error_actual("Token 'Inicio' inesperado dentro del programa")
                self._sincronizar()
                continue

            sentencia = self.parse_sentencia()
            if sentencia is not None:
                sentencias.append(sentencia)

        if self._check_lexema("Fin"):
            self._avanzar()
        elif tiene_inicio:
            self._error_actual("Se esperaba 'Fin' para cerrar el programa")

        if not self._fin():
            self._error_actual("No se permiten tokens despues de 'Fin'")
            self._sincronizar_hasta_eof()

        return NodoPrograma(1, 1, sentencias), self.errores

    def parse_sentencia(self) -> Optional[NodoAST]:
        if self._check_lexema(";"):
            self._error_actual("Sentencia vacia")
            self._avanzar()
            return None

        if self._fin() or self._check_lexema("Fin"):
            return None

        if self._es_inicio_lugar():
            sentencia = self.parse_asignacion()
        elif self._check_conjunto(self.CMD_MOVIMIENTO):
            sentencia = self.parse_cmd_movimiento()
        elif self._check_conjunto(self.CMD_FUNCION):
            sentencia = self.parse_cmd_funcion()
        elif self._check_conjunto(self.CALCULOS):
            sentencia = self.parse_calculo()
        else:
            self._error_actual("Se esperaba asignacion, comando o calculo")
            self._sincronizar()
            return None

        if sentencia is None:
            self._sincronizar()
            return None

        if not self._coincidir_lexema(";"):
            self._error_actual("Se esperaba ';' al final de la sentencia")
            self._sincronizar()

        return sentencia

    def parse_asignacion(self) -> Optional[NodoAsignacion]:
        lugar = self.parse_lugar()
        if lugar is None:
            return None

        if not self._coincidir_lexema(":="):
            self._error_actual("Se esperaba ':=' despues del lugar de asignacion")
            return None

        expresion = self.parse_expresion()
        if expresion is None:
            return None

        return NodoAsignacion(
            lugar.linea,
            lugar.columna,
            lugar,
            expresion,
        )

    def parse_cmd_movimiento(self) -> Optional[NodoComando]:
        nombre = self._avanzar()

        if not self._coincidir_lexema("("):
            self._error_actual("Se esperaba '(' despues del comando de movimiento")
            return None

        parametros = self.parse_params()

        if not self._coincidir_lexema(")"):
            self._error_actual("Se esperaba ')' despues de los parametros")
            return None

        return NodoComando(nombre.linea, nombre.columna, nombre, parametros)

    def parse_cmd_funcion(self) -> Optional[NodoComando]:
        nombre = self._avanzar()

        if not self._coincidir_lexema("("):
            self._error_actual("Se esperaba '(' despues del comando")
            return None

        argumento = self.parse_lugar()
        if argumento is None:
            return None

        if not self._coincidir_lexema(")"):
            self._error_actual("Se esperaba ')' despues del argumento")
            return None

        return NodoComando(nombre.linea, nombre.columna, nombre, [argumento])

    def parse_calculo(self) -> Optional[NodoCalculo]:
        nombre = self._avanzar()

        if not self._coincidir_lexema("("):
            self._error_actual("Se esperaba '(' despues del calculo")
            return None

        expresion = self.parse_expresion()
        if expresion is None:
            return None

        if not self._coincidir_lexema(")"):
            self._error_actual("Se esperaba ')' despues de la expresion")
            return None

        return NodoCalculo(nombre.linea, nombre.columna, nombre, expresion)

    def parse_expresion(self) -> Optional[NodoAST]:
        izquierda = self.parse_exp_aritmetica()
        if izquierda is None:
            return None

        if self._check_conjunto(self.OP_RELACIONALES):
            operador = self._avanzar()
            derecha = self.parse_exp_aritmetica()
            if derecha is None:
                return None
            return NodoOperacionRelacional(
                operador.linea,
                operador.columna,
                operador,
                izquierda,
                derecha,
            )

        return izquierda

    def parse_exp_aritmetica(self) -> Optional[NodoAST]:
        izquierda = self.parse_termino()
        if izquierda is None:
            return None

        while self._check_lexema("+", "-"):
            operador = self._avanzar()
            derecha = self.parse_termino()
            if derecha is None:
                return None
            izquierda = NodoOperacion(
                operador.linea,
                operador.columna,
                operador,
                izquierda,
                derecha,
            )

        return izquierda

    def parse_termino(self) -> Optional[NodoAST]:
        izquierda = self.parse_exponencial()
        if izquierda is None:
            return None

        while self._check_lexema("*", "/"):
            operador = self._avanzar()
            derecha = self.parse_exponencial()
            if derecha is None:
                return None
            izquierda = NodoOperacion(
                operador.linea,
                operador.columna,
                operador,
                izquierda,
                derecha,
            )

        return izquierda

    def parse_exponencial(self) -> Optional[NodoAST]:
        izquierda = self.parse_factor()
        if izquierda is None:
            return None

        if self._check_lexema("^"):
            operador = self._avanzar()
            derecha = self.parse_exponencial()
            if derecha is None:
                return None
            return NodoOperacion(
                operador.linea,
                operador.columna,
                operador,
                izquierda,
                derecha,
            )

        return izquierda

    def parse_factor(self) -> Optional[NodoAST]:
        if self._check_tipo(TipoToken.NUM):
            numero = self._avanzar()
            return NodoNumero(numero.linea, numero.columna, numero)

        if self._es_inicio_lugar():
            return self.parse_lugar()

        if self._coincidir_lexema("("):
            apertura = self._anterior()
            expresion = self.parse_expresion()
            if expresion is None:
                return None

            if not self._coincidir_lexema(")"):
                self._error_actual("Se esperaba ')' para cerrar la agrupacion")
                return None

            return NodoAgrupacion(apertura.linea, apertura.columna, expresion)

        if self._check_conjunto(self.CALCULOS):
            return self.parse_calculo()

        self._error_actual("Se esperaba NUM, ID, variable fisica, '(' o calculo")
        return None

    def parse_lugar(self) -> Optional[NodoAST]:
        if self._check_tipo(TipoToken.ID):
            identificador = self._avanzar()

            if self._coincidir_lexema("["):
                indice = self._consumir_numero(
                    "Se esperaba NUM como indice del arreglo"
                )
                if indice is None:
                    return None

                if not self._coincidir_lexema("]"):
                    self._error_actual("Se esperaba ']' para cerrar el acceso de arreglo")
                    return None

                return NodoAccesoArreglo(
                    identificador.linea,
                    identificador.columna,
                    identificador,
                    indice,
                )

            return NodoIdentificador(
                identificador.linea,
                identificador.columna,
                identificador,
            )

        if self._check_var_fisica():
            variable = self._avanzar()
            return NodoVariableFisica(variable.linea, variable.columna, variable)

        self._error_actual("Se esperaba un lugar: ID, acceso de arreglo o variable fisica")
        return None

    def parse_params(self) -> list[NodoAST]:
        parametros: list[NodoAST] = []

        if self._check_lexema(")"):
            self._error_actual("Se esperaba al menos un parametro")
            return parametros

        while not self._fin() and not self._check_lexema(")"):
            variable = self._consumir_var_fisica(
                "Se esperaba una variable fisica como parametro"
            )
            if variable is None:
                return parametros

            if not self._coincidir_lexema(":="):
                self._error_actual("Se esperaba ':=' despues de la variable fisica")
                return parametros

            expresion = self.parse_expresion()
            if expresion is None:
                return parametros

            parametros.append(
                NodoParametro(variable.linea, variable.columna, variable, expresion)
            )

            if not self._coincidir_lexema(","):
                break

            if self._check_lexema(")"):
                self._error_actual("Se esperaba un parametro despues de ','")
                break

        return parametros

    def _consumir_var_fisica(self, mensaje: str) -> Optional[Token]:
        if self._check_var_fisica():
            return self._avanzar()

        self._error_actual(mensaje)
        return None

    def _consumir_numero(self, mensaje: str) -> Optional[Token]:
        if self._check_tipo(TipoToken.NUM):
            return self._avanzar()

        self._error_actual(mensaje)
        return None

    def _coincidir_lexema(self, *lexemas: str) -> bool:
        if self._check_lexema(*lexemas):
            self._avanzar()
            return True
        return False

    def _check_tipo(self, tipo: str) -> bool:
        return not self._fin() and self._actual().tipo == tipo

    def _check_lexema(self, *lexemas: str) -> bool:
        return not self._fin() and self._actual().lexema in lexemas

    def _check_conjunto(self, lexemas: frozenset[str]) -> bool:
        return not self._fin() and self._actual().lexema in lexemas

    def _check_var_fisica(self) -> bool:
        return self._check_conjunto(self.VAR_FISICAS)

    def _es_inicio_lugar(self) -> bool:
        return self._check_tipo(TipoToken.ID) or self._check_var_fisica()

    def _sincronizar(self) -> None:
        while not self._fin() and not self._check_conjunto(self.SINCRONIZACION):
            self._avanzar()

        if self._check_lexema(";"):
            self._avanzar()

    def _sincronizar_hasta_eof(self) -> None:
        while not self._fin():
            self._avanzar()

    def _error_actual(self, mensaje: str) -> None:
        token = self._actual()
        self.errores.append(
            ErrorSintactico(token, mensaje, token.linea, token.columna)
        )

    def _actual(self) -> Token:
        if self._fin():
            return self.eof
        return self.tokens[self.pos]

    def _anterior(self) -> Token:
        if self.pos == 0:
            return self.eof
        return self.tokens[self.pos - 1]

    def _avanzar(self) -> Token:
        token = self._actual()
        if not self._fin():
            self.pos += 1
        return token

    def _fin(self) -> bool:
        return self.pos >= len(self.tokens)

    def _crear_eof(self) -> Token:
        if not self.tokens:
            return Token("", "EOF", "EOF", 1, 1)

        ultimo = self.tokens[-1]
        return Token("", "EOF", "EOF", ultimo.linea, ultimo.columna + len(ultimo.lexema))
