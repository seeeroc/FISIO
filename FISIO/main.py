"""
=============================================================
 FISIO - Analizador Léxico
 Módulo: main.py
 Descripción: Punto de entrada principal del analizador léxico.
              Permite analizar archivos .txt o entrada manual
              desde la consola.

 Uso
 ───
    python main.py                  → menú interactivo
    python main.py archivo.txt      → analizar archivo directamente
    python main.py --demo           → ejecutar casos de prueba integrados
    python main.py --sin-color      → desactivar colores ANSI
=============================================================
"""

import sys
import os

from lexer   import Lexer
from salida  import FormateadorSalida


# ─────────────────────────────────────────────────────────────
#  CASOS DE PRUEBA INTEGRADOS
# ─────────────────────────────────────────────────────────────

CASOS_PRUEBA = [
    # ── Caso 1: entrada válida completa ──────────────────────
    {
        "titulo": "CASO 1 — Entrada válida completa",
        "descripcion": (
            "Programa FISIO con MRU, MRUA, caída libre y operaciones\n"
            "  básicas. Todos los tokens deben ser reconocidos sin errores."
        ),
        "codigo": """\
mru(velocidad := 20, tiempo := 5);
altura := 150.5;
caida(gravedad := 9.81);
mrua(aceleracion := 3, velocidad := 0, tiempo := 10);
parabolico(alcance := 45, altura := 12.0);
posicion := velocidad + aceleracion * tiempo ^ 2;
raiz(posicion);
seno(angulo);
coseno(angulo);
magnitud(velocidad);
despejar(alcance);
graficar(posicion);
simular(velocidad);
resultado := (posicion + altura) / 2;
""",
    },

    # ── Caso 2: solo operadores y signos ─────────────────────
    {
        "titulo": "CASO 2 — Operadores y signos",
        "descripcion": (
            "Verifica todos los operadores matemáticos, relacionales\n"
            "  y signos de puntuación del alfabeto FISIO."
        ),
        "codigo": """\
x := 10;
y := x + 5;
z := y - 3;
w := z * 2;
v := w / 4;
p := v ^ 2;
a := x = y;
b := x != y;
c := x < y;
d := x > y;
e := x <= y;
f := x >= y;
lista[0];
func(a, b);
""",
    },

    # ── Caso 3: literales numéricos válidos ──────────────────
    {
        "titulo": "CASO 3 — Literales numéricos válidos",
        "descripcion": (
            "Verifica enteros y decimales correctamente formados\n"
            "  según las reglas estrictas del lenguaje FISIO."
        ),
        "codigo": """\
a := 0;
b := 1;
c := 10;
d := 9999;
e := 0.5;
f := 9.81;
g := 150.25;
h := 3.14159;
i := 100;
""",
    },

    # ── Caso 4: errores en literales numéricos ───────────────
    {
        "titulo": "CASO 4 — Errores en literales numéricos",
        "descripcion": (
            "Prueba de errores: ceros a la izquierda, doble punto,\n"
            "  punto sin parte entera, letras mezcladas y más."
        ),
        "codigo": """\
a := .5;
b := 5.;
c := 1..5;
d := 01;
e := 001.5;
f := 12a;
g := 9.8x;
""",
    },

    # ── Caso 5: errores de caracteres fuera del alfabeto ─────
    {
        "titulo": "CASO 5 — Símbolos fuera del alfabeto",
        "descripcion": (
            "Detecta caracteres que no pertenecen al alfabeto FISIO:\n"
            "  @, #, $, %, &, etc."
        ),
        "codigo": """\
x := 5@2;
y := 3#14;
z := valor$extra;
w := 100%;
k := dato&otro;
""",
    },

    # ── Caso 6: operadores incompletos ───────────────────────
    {
        "titulo": "CASO 6 — Operadores incompletos",
        "descripcion": (
            "Detecta operadores que están incompletos o mal formados,\n"
            "  como '!' solo o ':' sin '='."
        ),
        "codigo": """\
a := 5 ! 3;
b : 10;
c := a !b;
""",
    },

    # ── Caso 7: identificadores inválidos ────────────────────
    {
        "titulo": "CASO 7 — Identificadores inválidos",
        "descripcion": (
            "Prueba identificadores que inician con dígito o\n"
            "  contienen caracteres especiales."
        ),
        "codigo": """\
1variable := 5;
2ndValor := 10;
mi@variable := 20;
""",
    },
]


# ─────────────────────────────────────────────────────────────
#  FUNCIONES PRINCIPALES
# ─────────────────────────────────────────────────────────────

def analizar_codigo(codigo: str, usar_color: bool = True) -> None:
    """
    Ejecuta el análisis léxico sobre el código dado e imprime resultados.

    Parámetros
    ----------
    codigo     : str  — código fuente FISIO
    usar_color : bool — True para habilitar colores ANSI
    """
    lex = Lexer(codigo)
    tokens, errores = lex.analizar()

    fmt = FormateadorSalida(tokens, errores, usar_color=usar_color)
    fmt.imprimir_todo()


def analizar_archivo(ruta: str, usar_color: bool = True) -> None:
    """
    Lee un archivo .txt y ejecuta el análisis léxico.

    Parámetros
    ----------
    ruta       : str  — ruta al archivo de código fuente
    usar_color : bool — True para habilitar colores ANSI
    """
    if not os.path.isfile(ruta):
        print(f"\n  ✖  Archivo no encontrado: '{ruta}'\n")
        return

    extension = os.path.splitext(ruta)[1].lower()
    if extension not in ('.txt', '.fisio', ''):
        print(f"\n  ⚠  Extensión '{extension}' no habitual. Se intentará leer de todas formas.\n")

    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except UnicodeDecodeError:
        with open(ruta, 'r', encoding='latin-1') as f:
            codigo = f.read()

    print(f"\n  Archivo analizado: {ruta}")
    print(f"  Tamaño: {len(codigo)} caracteres | {codigo.count(chr(10))+1} líneas\n")
    analizar_codigo(codigo, usar_color)


def ejecutar_demos(usar_color: bool = True) -> None:
    """Ejecuta todos los casos de prueba integrados."""
    for caso in CASOS_PRUEBA:
        sep = "─" * 70
        print()
        print(sep)
        print(f"  {caso['titulo']}")
        print(f"  {caso['descripcion']}")
        print(sep)
        print()
        print("  CÓDIGO FUENTE:")
        for i, linea in enumerate(caso["codigo"].strip().split('\n'), 1):
            print(f"    {i:>3}  {linea}")
        print()
        analizar_codigo(caso["codigo"], usar_color)
        input("  [ Presione ENTER para continuar al siguiente caso... ] ")


def menu_interactivo(usar_color: bool = True) -> None:
    """Muestra el menú principal del analizador FISIO."""
    sep_dbl = "═" * 60
    sep_sim = "─" * 60

    while True:
        print()
        print(sep_dbl)
        print("  FISIO — ANALIZADOR LÉXICO".center(60))
        print("  Física Clásica · MRU · MRUA · Caída Libre · Parabólico".center(60))
        print(sep_dbl)
        print("  [1]  Ingresar código manualmente")
        print("  [2]  Analizar archivo .txt")
        print("  [3]  Ejecutar casos de prueba (DEMO)")
        print("  [4]  Ver explicación del analizador")
        print("  [0]  Salir")
        print(sep_sim)
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            _entrada_manual(usar_color)

        elif opcion == "2":
            ruta = input("  Ingrese la ruta del archivo (.txt): ").strip()
            if ruta:
                analizar_archivo(ruta, usar_color)
            else:
                print("  ⚠  Ruta vacía, operación cancelada.")

        elif opcion == "3":
            ejecutar_demos(usar_color)

        elif opcion == "4":
            _mostrar_explicacion()

        elif opcion == "0":
            print("\n  ¡Hasta luego!\n")
            break

        else:
            print("  ✖  Opción no válida. Intente de nuevo.")


def _entrada_manual(usar_color: bool) -> None:
    """Permite al usuario escribir código FISIO línea a línea."""
    print()
    print("  Ingrese el código FISIO (escriba 'FIN' en una línea para terminar):")
    lineas = []
    while True:
        try:
            linea = input("  > ")
        except EOFError:
            break
        if linea.strip().upper() == "FIN":
            break
        lineas.append(linea)

    codigo = "\n".join(lineas)
    if not codigo.strip():
        print("  ⚠  No se ingresó código.")
        return

    print()
    analizar_codigo(codigo, usar_color)


def _mostrar_explicacion() -> None:
    """Imprime una explicación del funcionamiento del analizador."""
    print("""
  ╔══════════════════════════════════════════════════════════════════╗
  ║         EXPLICACIÓN DEL ANALIZADOR LÉXICO FISIO                ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                                                                  ║
  ║  El análisis léxico es la PRIMERA fase de un compilador.        ║
  ║  Su función es leer el código fuente carácter a carácter y      ║
  ║  agruparlos en unidades mínimas con significado: los TOKENS.    ║
  ║                                                                  ║
  ║  ARQUITECTURA DEL ANALIZADOR FISIO                              ║
  ║  ─────────────────────────────────────────────────────────────  ║
  ║  • token_types.py  → Diccionarios de tokens y alfabeto          ║
  ║  • token_model.py  → Clase Token (lexema, tipo, ID, pos)        ║
  ║  • validador.py    → AFDs formales para números e IDs           ║
  ║  • lexer.py        → AFD principal, tokenización                ║
  ║  • salida.py       → Tablas, reportes de error y estadísticas   ║
  ║  • main.py         → Punto de entrada, menú, demos              ║
  ║                                                                  ║
  ║  AUTÓMATA FINITO DETERMINISTA (AFD) PRINCIPAL                   ║
  ║  ─────────────────────────────────────────────────────────────  ║
  ║  Estado q0 (inicial):                                           ║
  ║    letra    → leer_palabra() → PR o ID                         ║
  ║    dígito   → leer_numero()  → NUM                             ║
  ║    '.'      → punto inicial  → SIG_06 o ERROR                  ║
  ║    +,-,*,/,^→ OPM directo                                      ║
  ║    :,<,>,!  → leer_op_compuesto() → OPR (1 o 2 chars)         ║
  ║    (,),...  → SIG directo                                      ║
  ║    espacio  → ignorar                                           ║
  ║    salto_ln → actualizar línea                                  ║
  ║    otro     → ERROR léxico                                      ║
  ║                                                                  ║
  ║  EXPRESIONES REGULARES IMPLEMENTADAS                            ║
  ║  ─────────────────────────────────────────────────────────────  ║
  ║  Identificador : [a-zA-Z][a-zA-Z0-9]*                          ║
  ║  Entero        : 0 | [1-9][0-9]*                               ║
  ║  Decimal       : (0|[1-9][0-9]*)\\.[0-9]+                       ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
""")


# ─────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    usar_color = "--sin-color" not in args
    args = [a for a in args if a != "--sin-color"]

    if "--demo" in args:
        ejecutar_demos(usar_color)
    elif "--cli" in args:
        # Forzar modo CLI
        args = [a for a in args if a != "--cli"]
        if args:
            analizar_archivo(args[0], usar_color)
        else:
            menu_interactivo(usar_color)
    elif args:
        # Primer argumento = ruta al archivo
        analizar_archivo(args[0], usar_color)
    else:
        # Por defecto, iniciar la interfaz gráfica (GUI)
        try:
            import gui
            gui.main()
        except ImportError as e:
            print(f"No se pudo cargar la interfaz gráfica (GUI): {e}")
            print("Iniciando modo consola interactivo...")
            menu_interactivo(usar_color)
