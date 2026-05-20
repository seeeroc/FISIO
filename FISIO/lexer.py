"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: lexer.py
 Descripción: Clase Lexer — núcleo del analizador léxico.
              Implementa el AFD principal que recorre el código
              fuente carácter a carácter y produce la lista de
              tokens reconocidos y errores detectados.

 ARQUITECTURA DEL AFD PRINCIPAL
 ────────────────────────────────────────────────────────────
  Estado inicial → q0
  Transiciones según el carácter actual:
    ─ letra        → modo IDENTIFICADOR / PALABRA RESERVADA
    ─ dígito       → modo NÚMERO
    ─ '.'          → modo PUNTO (posible decimal mal formado)
    ─ operadores   → modo OPERADOR (1 o 2 caracteres)
    ─ signo        → modo SIGNO
    ─ espacio/tab  → ignorar
    ─ salto línea  → actualizar contador de línea
    ─ otro         → ERROR léxico
=============================================================
"""

import re
from token_model  import Token
from token_types  import (
    TipoToken,
    PALABRAS_RESERVADAS,
    OPERADORES_MATEMATICOS,
    OPERADORES_RELACIONALES,
    SIGNOS,
    ALFABETO_VALIDO,
)
from validador import Validador


class Lexer:
    """
    Analizador léxico del lenguaje FISIO.

    Uso
    ---
        lex = Lexer(codigo_fuente)
        tokens, errores = lex.analizar()
    """

    def __init__(self, fuente: str) -> None:
        """
        Parámetros
        ----------
        fuente : str — código fuente completo como cadena de texto
        """
        self.fuente   : str        = fuente
        self.pos      : int        = 0       # posición actual en la cadena
        self.linea    : int        = 1       # línea actual (1-indexada)
        self.columna  : int        = 1       # columna actual (1-indexada)
        self.tokens   : list[Token] = []
        self.errores  : list[Token] = []

    # ════════════════════════════════════════════════════════
    #  PUNTO DE ENTRADA PRINCIPAL
    # ════════════════════════════════════════════════════════
    def analizar(self) -> tuple[list[Token], list[Token]]:
        """
        Recorre el código fuente y produce la lista de tokens y errores.

        Retorna
        -------
        (tokens, errores) : ambas listas de objetos Token
        """
        while not self._fin():
            caracter = self._actual()

            # ── Espacios en blanco (ignorar) ─────────────────
            if caracter in (' ', '\t', '\r'):
                self._avanzar()
                continue

            # ── Salto de línea ───────────────────────────────
            if caracter == '\n':
                self._avanzar()
                self.linea  += 1
                self.columna = 1
                continue

            # ── Verificación de alfabeto ─────────────────────
            if caracter not in ALFABETO_VALIDO:
                self._registrar_error(
                    caracter,
                    f"Símbolo no reconocido '{caracter}': "
                    "fuera del alfabeto del lenguaje FISIO."
                )
                self._avanzar()
                continue

            # ── Letra → identificador o palabra reservada ────
            if caracter.isalpha():
                self._leer_palabra()
                continue

            # ── Dígito → número ──────────────────────────────
            if caracter.isdigit():
                self._leer_numero()
                continue

            # ── Punto inicial → error decimal mal formado ────
            if caracter == '.':
                self._manejar_punto_inicial()
                continue

            # ── Operadores de 2 caracteres (':=','<=','>=' ,'!=') ─
            if caracter in (':', '<', '>', '!'):
                self._leer_operador_compuesto(caracter)
                continue

            # ── Operadores matemáticos simples ───────────────
            if caracter in OPERADORES_MATEMATICOS:
                self._agregar_token(
                    caracter,
                    *OPERADORES_MATEMATICOS[caracter]
                )
                self._avanzar()
                continue

            # ── Signo '=' simple (solo si no fue consumido) ──
            if caracter == '=':
                self._agregar_token(caracter, *OPERADORES_RELACIONALES['='])
                self._avanzar()
                continue

            # ── Signos de agrupación y puntuación ────────────
            if caracter in SIGNOS:
                self._agregar_token(caracter, *SIGNOS[caracter])
                self._avanzar()
                continue

            # ── Cualquier otro carácter no manejado ──────────
            self._registrar_error(
                caracter,
                f"Carácter inesperado '{caracter}'."
            )
            self._avanzar()

        return self.tokens, self.errores

    # ════════════════════════════════════════════════════════
    #  MÉTODOS DE LECTURA DE TOKENS
    # ════════════════════════════════════════════════════════

    # ── Palabras reservadas / Identificadores ────────────────
    def _leer_palabra(self) -> None:
        """
        AFD para identificadores y palabras reservadas.
        Lee mientras el carácter sea alfanumérico.
        Determina al final si es PR o ID.
        """
        inicio_col = self.columna
        inicio_lin = self.linea
        buffer     = ""

        while not self._fin() and (self._actual().isalnum()):
            buffer += self._actual()
            self._avanzar()

        # Verificar si hay caracteres inválidos pegados (ej: abc@)
        if not self._fin() and self._actual() not in ALFABETO_VALIDO:
            car_invalido = self._actual()
            buffer += car_invalido
            self._avanzar()
            self._registrar_error_en(
                buffer, inicio_lin, inicio_col,
                f"Identificador inválido '{buffer}': "
                f"contiene carácter no permitido '{car_invalido}'."
            )
            return

        # ¿Es palabra reservada?
        if buffer in PALABRAS_RESERVADAS:
            tipo, id_tok = PALABRAS_RESERVADAS[buffer]
            self._agregar_token_en(buffer, tipo, id_tok, inicio_lin, inicio_col)
        else:
            # Es identificador — validar con el AFD del validador
            valido, mensaje = Validador.validar_identificador(buffer)
            if valido:
                self._agregar_token_en(
                    buffer, TipoToken.IDENTIFICADOR, "ID",
                    inicio_lin, inicio_col
                )
            else:
                self._registrar_error_en(buffer, inicio_lin, inicio_col, mensaje)

    # ── Literales numéricos ──────────────────────────────────
    def _leer_numero(self) -> None:
        """
        AFD para literales numéricos con validación estricta:
            q0 -[0-9]→ q_int -[0-9]→ q_int
            q_int -[.]→ q_punto -[0-9]→ q_dec
            q_punto -[no-dígito]→ ERROR  (5.)
        Detecta además mezcla con letras (12a) y símbolos (5@2).
        """
        inicio_col = self.columna
        inicio_lin = self.linea
        buffer     = ""
        tiene_punto = False
        error_forzado = None   # mensaje de error acumulado

        while not self._fin():
            car = self._actual()

            if car.isdigit():
                buffer += car
                self._avanzar()

            elif car == '.':
                # Segundo punto → error
                if tiene_punto:
                    buffer += car
                    self._avanzar()
                    # Seguir acumulando para mostrar el lexema completo
                    while not self._fin() and (
                        self._actual().isdigit() or self._actual() == '.'
                    ):
                        buffer += self._actual()
                        self._avanzar()
                    error_forzado = (
                        f"Número inválido '{buffer}': "
                        "solo se permite un punto decimal."
                    )
                    break
                tiene_punto = True
                buffer += car
                self._avanzar()

            elif car.isalpha():
                # Mezcla de letra con número (12a, 9.8x)
                buffer += car
                self._avanzar()
                while not self._fin() and (
                    self._actual().isalnum() or self._actual() == '.'
                ):
                    buffer += self._actual()
                    self._avanzar()
                error_forzado = (
                    f"Número inválido '{buffer}': "
                    "no se permiten letras mezcladas con números."
                )
                break

            elif car in ALFABETO_VALIDO and car not in (' ', '\t', '\n', '\r'):
                # Símbolo extraño dentro del número (5@2, 3#14) — ya filtrado
                # pero si llega aquí es operador/signo: terminar lectura
                break

            else:
                break

        if error_forzado:
            self._registrar_error_en(buffer, inicio_lin, inicio_col, error_forzado)
            return

        # Validar con el validador formal
        valido, mensaje = Validador.validar_numero(buffer)
        if valido:
            self._agregar_token_en(
                buffer, TipoToken.NUMERO, "NUM",
                inicio_lin, inicio_col
            )
        else:
            self._registrar_error_en(buffer, inicio_lin, inicio_col, mensaje)

    # ── Punto inicial (.5) ───────────────────────────────────
    def _manejar_punto_inicial(self) -> None:
        """
        Detecta el caso donde el código inicia un token con '.'
        sin parte entera previa (ej: .5).
        Si el siguiente carácter es dígito → error decimal.
        Si no → es el signo SIG_06.
        """
        inicio_col = self.columna
        inicio_lin = self.linea

        # Ver si hay dígito después del punto
        siguiente_pos = self.pos + 1
        if siguiente_pos < len(self.fuente) and self.fuente[siguiente_pos].isdigit():
            # Leer todo el número mal formado
            buffer = "."
            self._avanzar()
            while not self._fin() and self._actual().isdigit():
                buffer += self._actual()
                self._avanzar()
            self._registrar_error_en(
                buffer, inicio_lin, inicio_col,
                f"Número decimal inválido '{buffer}': "
                "se esperaba parte entera antes del punto decimal."
            )
        else:
            # Es el signo punto (separador)
            self._agregar_token_en(".", *SIGNOS["."], inicio_lin, inicio_col)
            self._avanzar()

    # ── Operadores compuestos (:=, <=, >=, !=) ───────────────
    def _leer_operador_compuesto(self, primer_car: str) -> None:
        """
        Lee operadores que pueden ser de 1 o 2 caracteres.
        Verifica si el siguiente carácter forma un operador válido.
        """
        inicio_col = self.columna
        inicio_lin = self.linea
        self._avanzar()  # consumir primer carácter

        segundo_car = self._actual() if not self._fin() else ""
        doble       = primer_car + segundo_car

        # ── Intento con 2 caracteres primero ─────────────────
        if doble in OPERADORES_RELACIONALES:
            self._agregar_token_en(
                doble, *OPERADORES_RELACIONALES[doble],
                inicio_lin, inicio_col
            )
            self._avanzar()
            return

        # ── Intento con 1 carácter ───────────────────────────
        if primer_car in OPERADORES_RELACIONALES:
            self._agregar_token_en(
                primer_car, *OPERADORES_RELACIONALES[primer_car],
                inicio_lin, inicio_col
            )
            return

        # ── Error: operador incompleto o inválido ─────────────
        # Ejemplos: '!' sola, ':' sin '='
        self._registrar_error_en(
            primer_car, inicio_lin, inicio_col,
            f"Operador incompleto o inválido '{primer_car}': "
            f"no forma un operador reconocido del lenguaje FISIO."
        )

    # ════════════════════════════════════════════════════════
    #  MÉTODOS AUXILIARES DE NAVEGACIÓN
    # ════════════════════════════════════════════════════════

    def _actual(self) -> str:
        """Retorna el carácter en la posición actual."""
        return self.fuente[self.pos]

    def _avanzar(self) -> None:
        """Avanza la posición y actualiza la columna."""
        self.pos     += 1
        self.columna += 1

    def _fin(self) -> bool:
        """Retorna True si se llegó al final del código fuente."""
        return self.pos >= len(self.fuente)

    # ════════════════════════════════════════════════════════
    #  MÉTODOS DE REGISTRO DE TOKENS Y ERRORES
    # ════════════════════════════════════════════════════════

    def _agregar_token(
        self, lexema: str, tipo: str, id_tok: str
    ) -> None:
        """Registra un token con la línea/columna actuales."""
        self.tokens.append(
            Token(lexema, tipo, id_tok, self.linea, self.columna)
        )

    def _agregar_token_en(
        self, lexema: str, tipo: str, id_tok: str,
        linea: int, columna: int
    ) -> None:
        """Registra un token con línea/columna explícitas."""
        self.tokens.append(Token(lexema, tipo, id_tok, linea, columna))

    def _registrar_error(self, lexema: str, mensaje: str) -> None:
        """Registra un error léxico con la línea/columna actuales."""
        tok = Token(
            lexema, TipoToken.ERROR, "ERROR",
            self.linea, self.columna, mensaje
        )
        self.errores.append(tok)

    def _registrar_error_en(
        self, lexema: str, linea: int, columna: int, mensaje: str
    ) -> None:
        """Registra un error léxico con línea/columna explícitas."""
        tok = Token(
            lexema, TipoToken.ERROR, "ERROR",
            linea, columna, mensaje
        )
        self.errores.append(tok)
