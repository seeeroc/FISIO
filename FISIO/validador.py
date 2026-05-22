"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: validador.py
 Descripción: Módulo de validación formal de tokens numéricos
              e identificadores según las reglas del lenguaje.
              Implementa los AFD (Autómatas Finitos Deterministas)
              para cada tipo de token.
=============================================================
"""

import re
from typing import Optional


# ─────────────────────────────────────────────────────────────
#  PATRONES COMPILADOS  (expresiones regulares del lenguaje)
# ─────────────────────────────────────────────────────────────

# Identificador válido: inicia con letra, seguido de letras/dígitos
_RE_IDENTIFICADOR = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*$')

# Número entero estricto: 0, o [1-9][0-9]*  (sin ceros a la izquierda)
_RE_ENTERO        = re.compile(r'^(0|[1-9][0-9]*)$')

# Número decimal estricto: parte_entera . parte_decimal  (ambas obligatorias)
_RE_DECIMAL       = re.compile(r'^(0|[1-9][0-9]*)\.[0-9]+$')

# Detecta si una cadena parece ser numérica (contiene dígitos o punto)
_RE_PARECE_NUMERO = re.compile(r'^[0-9.]+$')


# ─────────────────────────────────────────────────────────────
#  CLASE VALIDADOR
# ─────────────────────────────────────────────────────────────
class Validador:
    """
    Valida lexemas según las reglas formales del lenguaje FISIO.
    Cada método retorna una tupla (es_válido: bool, mensaje_error: str).
    Si es_válido es True, el mensaje_error es cadena vacía ''.
    """

    # ── Identificadores ──────────────────────────────────────
    @staticmethod
    def validar_identificador(lexema: str) -> tuple[bool, str]:
        """
        AFD para identificadores:
            q0 -[letra]→ q1 -[letra|dígito]→ q1  (estado de aceptación)
            q0 -[dígito]→ ERROR
            q1 -[otro]→  ERROR
        """
        if not lexema:
            return False, "Identificador vacío."

        if lexema[0].isdigit():
            return False, (
                f"Identificador inválido '{lexema}': "
                "no puede iniciar con un dígito."
            )

        if not _RE_IDENTIFICADOR.match(lexema):
            chars_invalidos = [c for c in lexema if not (c.isalpha() or c.isdigit())]
            return False, (
                f"Identificador inválido '{lexema}': "
                f"contiene caracteres no permitidos {chars_invalidos}."
            )

        return True, ""

    # ── Literales numéricos ──────────────────────────────────
    @staticmethod
    def validar_numero(lexema: str) -> tuple[bool, str]:
        """
        AFD para números según reglas estrictas de FISIO:

        ENTERO:
            q0 -[0]→ q_cero (aceptación, solo si sigue no-dígito)
            q0 -[1-9]→ q_int -[0-9]→ q_int (aceptación)

        DECIMAL:
            q_cero|q_int -[.]→ q_punto -[0-9]→ q_dec -[0-9]→ q_dec (aceptación)
            q_punto -[otro]→ ERROR  (punto sin parte decimal)
        """
        if not lexema:
            return False, "Número vacío."

        # ── Caso: letras mezcladas con números ────────────────
        if any(c.isalpha() for c in lexema):
            return False, (
                f"Número inválido '{lexema}': "
                "no se permiten letras mezcladas con números."
            )

        puntos = lexema.count('.')

        # ── Caso: múltiples puntos ───────────────────────────
        if puntos > 1:
            return False, (
                f"Número inválido '{lexema}': "
                "solo se permite un punto decimal."
            )

        # ── Caso: inicia con punto  (.5) ─────────────────────
        if lexema.startswith('.'):
            return False, (
                f"Número decimal inválido '{lexema}': "
                "se esperaba parte entera antes del punto decimal."
            )

        # ── Caso: termina con punto  (5.) ────────────────────
        if lexema.endswith('.'):
            return False, (
                f"Número inválido '{lexema}': "
                "se esperaba parte decimal después del punto."
            )

        # ── Caso: sin punto → entero ─────────────────────────
        if puntos == 0:
            # Verificar ceros a la izquierda (01, 001, etc.)
            if len(lexema) > 1 and lexema.startswith('0'):
                return False, (
                    f"Número inválido '{lexema}': "
                    "no se permiten ceros a la izquierda."
                )
            if _RE_ENTERO.match(lexema):
                return True, ""
            return False, (
                f"Número inválido '{lexema}': "
                "contiene caracteres no permitidos en un entero."
            )

        # ── Caso: con punto → decimal ────────────────────────
        partes = lexema.split('.')
        parte_entera   = partes[0]
        parte_decimal  = partes[1]

        # Ceros a la izquierda en parte entera (01.5)
        if len(parte_entera) > 1 and parte_entera.startswith('0'):
            return False, (
                f"Número inválido '{lexema}': "
                "no se permiten ceros a la izquierda en la parte entera."
            )

        if not parte_decimal.isdigit():
            return False, (
                f"Número inválido '{lexema}': "
                "la parte decimal contiene caracteres no numéricos."
            )

        if _RE_DECIMAL.match(lexema):
            return True, ""

        return False, (
            f"Número inválido '{lexema}': "
            "formato no reconocido."
        )

    # ── Verificación auxiliar ────────────────────────────────
    @staticmethod
    def parece_numero(lexema: str) -> bool:
        """Retorna True si el lexema tiene apariencia de número."""
        return bool(_RE_PARECE_NUMERO.match(lexema))

    @staticmethod
    def parece_identificador(lexema: str) -> bool:
        """Retorna True si el lexema tiene apariencia de identificador."""
        return bool(lexema and lexema[0].isalpha())
