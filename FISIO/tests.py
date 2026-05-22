"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: tests.py
 Descripción: Suite de pruebas automatizadas que verifica
              el comportamiento del analizador léxico FISIO.
              Incluye pruebas positivas (tokens válidos) y
              negativas (errores esperados).
=============================================================
"""

import sys
import os

# Asegurar que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer        import Lexer
from token_types  import TipoToken


# ─────────────────────────────────────────────────────────────
#  UTILIDADES DE LA SUITE DE PRUEBAS
# ─────────────────────────────────────────────────────────────

_total   = 0
_pasadas = 0
_fallidas = 0


def _ejecutar(nombre: str, codigo: str,
              tokens_esperados: list[tuple[str, str]] | None = None,
              errores_esperados: list[str]              | None = None) -> bool:
    """
    Ejecuta una prueba individual.

    Parámetros
    ----------
    nombre             : nombre descriptivo de la prueba
    codigo             : código FISIO a analizar
    tokens_esperados   : lista de (lexema, id_token) que deben aparecer
    errores_esperados  : lista de fragmentos de texto que deben estar en los errores
    """
    global _total, _pasadas, _fallidas
    _total += 1

    lex = Lexer(codigo)
    tokens, errores = lex.analizar()

    tok_map = {t.lexema: t.id_tok for t in tokens}
    err_msgs = [e.mensaje for e in errores]

    ok = True
    detalles = []

    # ── Verificar tokens esperados ───────────────────────────
    if tokens_esperados:
        for lexema, id_esperado in tokens_esperados:
            if lexema not in tok_map:
                ok = False
                detalles.append(
                    f"    ✖ Token '{lexema}' no encontrado en la salida."
                )
            elif tok_map[lexema] != id_esperado:
                ok = False
                detalles.append(
                    f"    ✖ Token '{lexema}': se esperaba ID={id_esperado!r} "
                    f"pero se obtuvo {tok_map[lexema]!r}."
                )

    # ── Verificar errores esperados ──────────────────────────
    if errores_esperados:
        for fragmento in errores_esperados:
            if not any(fragmento.lower() in msg.lower() for msg in err_msgs):
                ok = False
                detalles.append(
                    f"    ✖ Error esperado con fragmento '{fragmento}' "
                    "no fue detectado."
                )

    # ── Verificar que sin errores esperados no haya errores ──
    if errores_esperados is None and errores:
        ok = False
        for e in errores:
            detalles.append(f"    ✖ Error inesperado: {e.mensaje}")

    # ── Imprimir resultado ───────────────────────────────────
    estado = "  ✔ PASÓ" if ok else "  ✖ FALLÓ"
    print(f"{estado}  │  {nombre}")
    if not ok:
        for d in detalles:
            print(d)
        _fallidas += 1
    else:
        _pasadas += 1

    return ok


# ─────────────────────────────────────────────────────────────
#  PRUEBAS POSITIVAS — tokens válidos
# ─────────────────────────────────────────────────────────────

def test_palabras_reservadas():
    """Verifica que todas las PR sean reconocidas con su ID correcto."""
    codigo = (
        "mru mrua caida parabolico despejar graficar simular "
        "raiz seno coseno magnitud gravedad posicion velocidad "
        "aceleracion tiempo altura alcance"
    )
    _ejecutar(
        "Palabras reservadas — todas las PR_01 a PR_18",
        codigo,
        tokens_esperados=[
            ("mru",         "PR_01"), ("mrua",        "PR_02"),
            ("caida",       "PR_03"), ("parabolico",  "PR_04"),
            ("despejar",    "PR_05"), ("graficar",    "PR_06"),
            ("simular",     "PR_07"), ("raiz",        "PR_08"),
            ("seno",        "PR_09"), ("coseno",      "PR_10"),
            ("magnitud",    "PR_11"), ("gravedad",    "PR_12"),
            ("posicion",    "PR_13"), ("velocidad",   "PR_14"),
            ("aceleracion", "PR_15"), ("tiempo",      "PR_16"),
            ("altura",      "PR_17"), ("alcance",     "PR_18"),
        ],
    )


def test_operadores_matematicos():
    """Verifica los 5 operadores matemáticos OPM_01 a OPM_05."""
    _ejecutar(
        "Operadores matemáticos — OPM_01 a OPM_05",
        "a + b - c * d / e ^ f",
        tokens_esperados=[
            ("+", "OPM_01"), ("-", "OPM_02"), ("*", "OPM_03"),
            ("/", "OPM_04"), ("^", "OPM_05"),
        ],
    )


def test_operadores_relacionales():
    """Verifica todos los operadores relacionales OPR_01 a OPR_07."""
    _ejecutar(
        "Operadores relacionales — OPR_01 a OPR_07",
        "a := b = c < d > e <= f >= g != h",
        tokens_esperados=[
            (":=", "OPR_01"), ("=",  "OPR_02"), ("<",  "OPR_03"),
            (">",  "OPR_04"), ("<=", "OPR_05"), (">=", "OPR_06"),
            ("!=", "OPR_07"),
        ],
    )


def test_signos():
    """Verifica los 7 signos SIG_01 a SIG_07."""
    _ejecutar(
        "Signos de agrupación y puntuación — SIG_01 a SIG_07",
        "( ) [ ] , . ;",
        tokens_esperados=[
            ("(", "SIG_01"), (")", "SIG_02"), ("[", "SIG_03"),
            ("]", "SIG_04"), (",", "SIG_05"), (".", "SIG_06"),
            (";", "SIG_07"),
        ],
    )


def test_identificadores_validos():
    """Verifica identificadores bien formados."""
    _ejecutar(
        "Identificadores válidos",
        "x y z miVar2 a1 b2c3 varLarga resultado123",
        tokens_esperados=[
            ("x", "ID"), ("y", "ID"), ("z", "ID"),
            ("a1", "ID"), ("resultado123", "ID"),
            ("miVar2", "ID"), ("varLarga", "ID"),
        ],
    )


def test_numeros_enteros_validos():
    """Verifica literales enteros con reglas estrictas."""
    _ejecutar(
        "Números enteros válidos (0, 1, 10, 9999)",
        "a := 0; b := 1; c := 10; d := 9999;",
        tokens_esperados=[
            ("0", "NUM"), ("1", "NUM"), ("10", "NUM"), ("9999", "NUM"),
        ],
    )


def test_numeros_decimales_validos():
    """Verifica literales decimales correctamente formados."""
    _ejecutar(
        "Números decimales válidos (0.5, 9.81, 150.25)",
        "a := 0.5; b := 9.81; c := 150.25; d := 3.14159;",
        tokens_esperados=[
            ("0.5", "NUM"), ("9.81", "NUM"),
            ("150.25", "NUM"), ("3.14159", "NUM"),
        ],
    )


def test_programa_completo_valido():
    """Verifica un programa FISIO completo sin errores."""
    codigo = (
        "mru(velocidad := 20, tiempo := 5);\n"
        "altura := 150.5;\n"
        "caida(gravedad := 9.81);\n"
        "posicion := velocidad * tiempo;\n"
    )
    _ejecutar(
        "Programa MRU/MRUA/Caída completo — sin errores",
        codigo,
        tokens_esperados=[
            ("mru",       "PR_01"), ("velocidad",  "PR_14"),
            ("tiempo",    "PR_16"), ("altura",     "PR_17"),
            ("caida",     "PR_03"), ("gravedad",   "PR_12"),
            ("posicion",  "PR_13"), ("20",         "NUM"),
            ("5",         "NUM"),   ("150.5",      "NUM"),
            ("9.81",      "NUM"),
        ],
    )


# ─────────────────────────────────────────────────────────────
#  PRUEBAS NEGATIVAS — errores esperados
# ─────────────────────────────────────────────────────────────

def test_punto_sin_parte_entera():
    """Error: número decimal sin parte entera (.5)."""
    _ejecutar(
        "Error — decimal sin parte entera (.5)",
        "a := .5;",
        errores_esperados=["parte entera"],
    )


def test_punto_sin_parte_decimal():
    """Error: número que termina con punto (5.)."""
    _ejecutar(
        "Error — número que termina con punto (5.)",
        "b := 5.;",
        errores_esperados=["parte decimal"],
    )


def test_doble_punto():
    """Error: múltiples puntos decimales (1..5)."""
    _ejecutar(
        "Error — múltiples puntos decimales (1..5)",
        "c := 1..5;",
        errores_esperados=["un punto decimal"],
    )


def test_cero_a_la_izquierda_entero():
    """Error: cero a la izquierda en entero (01)."""
    _ejecutar(
        "Error — cero a la izquierda en entero (01)",
        "d := 01;",
        errores_esperados=["ceros a la izquierda"],
    )


def test_cero_a_la_izquierda_decimal():
    """Error: cero a la izquierda en decimal (001.5)."""
    _ejecutar(
        "Error — cero a la izquierda en decimal (001.5)",
        "e := 001.5;",
        errores_esperados=["ceros a la izquierda"],
    )


def test_numero_con_letra():
    """Error: número mezclado con letra (12a, 9.8x)."""
    _ejecutar(
        "Error — número mezclado con letra (12a / 9.8x)",
        "f := 12a; g := 9.8x;",
        errores_esperados=["letras mezcladas", "letras mezcladas"],
    )


def test_simbolo_fuera_alfabeto():
    """Error: símbolo '@' fuera del alfabeto."""
    _ejecutar(
        "Error — símbolo '@' fuera del alfabeto",
        "x := 5@2;",
        errores_esperados=["fuera del alfabeto"],
    )


def test_simbolo_hash():
    """Error: símbolo '#' fuera del alfabeto."""
    _ejecutar(
        "Error — símbolo '#' fuera del alfabeto",
        "y := 3#14;",
        errores_esperados=["fuera del alfabeto"],
    )


def test_operador_incompleto_exclamacion():
    """Error: '!' solo sin '='."""
    _ejecutar(
        "Error — operador incompleto '!' sin '='",
        "a := 5 ! 3;",
        errores_esperados=["incompleto"],
    )


def test_operador_incompleto_dos_puntos():
    """Error: ':' solo sin '='."""
    _ejecutar(
        "Error — operador incompleto ':' sin '='",
        "b : 10;",
        errores_esperados=["incompleto"],
    )


def test_identificador_inicia_digito():
    """
    Error: secuencia que inicia con dígito seguida de letras.
    El lexer intenta leerlo como número y detecta letras mezcladas.
    """
    _ejecutar(
        "Error — secuencia inicia con dígito seguida de letras (1variable)",
        "1variable := 5;",
        errores_esperados=["letras mezcladas"],
    )


def test_sin_espacios():
    """Verifica que el lexer funcione correctamente sin espacios."""
    _ejecutar(
        "Tokens sin espacios (mru(velocidad:=20))",
        "mru(velocidad:=20);",
        tokens_esperados=[
            ("mru",       "PR_01"), ("(",         "SIG_01"),
            ("velocidad", "PR_14"), (":=",        "OPR_01"),
            ("20",        "NUM"),   (")",         "SIG_02"),
            (";",         "SIG_07"),
        ],
    )


def test_comentarios_no_soportados():
    """Verifica que '$' y '%' generen errores (fuera del alfabeto FISIO)."""
    _ejecutar(
        "Detección de caracteres fuera del alfabeto ('$', '%')",
        "precio := 100$; tasa := 50%;" ,
        errores_esperados=["fuera del alfabeto", "fuera del alfabeto"],
    )


# ─────────────────────────────────────────────────────────────
#  RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────

def ejecutar_todas() -> None:
    """Ejecuta toda la suite de pruebas y muestra el resumen."""
    sep = "═" * 65

    print()
    print(sep)
    print("  FISIO — SUITE DE PRUEBAS AUTOMATIZADAS".center(65))
    print(sep)

    # ── Pruebas positivas ─────────────────────────────────────
    print()
    print("  PRUEBAS POSITIVAS (tokens válidos)")
    print("  " + "─" * 61)
    test_palabras_reservadas()
    test_operadores_matematicos()
    test_operadores_relacionales()
    test_signos()
    test_identificadores_validos()
    test_numeros_enteros_validos()
    test_numeros_decimales_validos()
    test_programa_completo_valido()
    test_sin_espacios()

    # ── Pruebas negativas ─────────────────────────────────────
    print()
    print("  PRUEBAS NEGATIVAS (errores esperados)")
    print("  " + "─" * 61)
    test_punto_sin_parte_entera()
    test_punto_sin_parte_decimal()
    test_doble_punto()
    test_cero_a_la_izquierda_entero()
    test_cero_a_la_izquierda_decimal()
    test_numero_con_letra()
    test_simbolo_fuera_alfabeto()
    test_simbolo_hash()
    test_operador_incompleto_exclamacion()
    test_operador_incompleto_dos_puntos()
    test_identificador_inicia_digito()
    test_comentarios_no_soportados()

    # ── Resumen ───────────────────────────────────────────────
    print()
    print(sep)
    print(f"  RESULTADOS FINALES".center(65))
    print(sep)
    print(f"  Total  : {_total:>3} pruebas")
    print(f"  Pasadas: {_pasadas:>3} ✔")
    print(f"  Fallidas:{_fallidas:>3} {'✔ Ninguna' if _fallidas == 0 else '✖'}")
    print()
    if _fallidas == 0:
        print("  ✔  TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    else:
        print(f"  ✖  {_fallidas} PRUEBA(S) FALLARON — revisar detalles arriba")
    print(sep)
    print()


if __name__ == "__main__":
    ejecutar_todas()
