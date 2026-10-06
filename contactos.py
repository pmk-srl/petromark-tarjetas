"""
Genera <slug>/contacto.vcf a partir del bloque `const persona = {...}` de cada <slug>/index.html.
Correr después de agregar o modificar una persona:

    python contactos.py            -> todas las carpetas
    python contactos.py rparra     -> solo esa
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).parent


def leer_persona(html: str) -> dict:
    bloque = re.search(r"const persona = \{(.*?)\n  \};", html, re.S).group(1)
    datos = {}
    for m in re.finditer(r'^\s*(\w+):\s*"((?:[^"\\]|\\.)*)"', bloque, re.M):
        datos[m.group(1)] = m.group(2).encode().decode("unicode_escape").encode("latin-1").decode("utf-8")
    return datos


def esc(v: str) -> str:
    """Escapa coma, punto y coma y barra invertida según vCard 3.0."""
    return v.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def vcard(p: dict) -> str:
    lineas = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(p['apellido'])};{esc(p['nombre'])};;;",
        f"FN:{esc(p['nombre'])} {esc(p['apellido'])}",
        f"ORG:{esc(p['empresa'])}",
        f"TITLE:{esc(p['cargo'])}",
        f"TEL;TYPE=CELL,VOICE:{p['telefono']}",
        f"EMAIL;TYPE=WORK:{p['email']}",
        f"URL:{p['web']}",
        f"ADR;TYPE=WORK:;;{esc(p['direccion'])};;;;",
    ]
    if p.get("linkedin"):
        lineas.append(f"URL;TYPE=LinkedIn:{p['linkedin']}")
    lineas.append("END:VCARD")
    return "\r\n".join(lineas) + "\r\n"


def main(argv):
    slugs = argv or sorted(d.name for d in RAIZ.iterdir() if (d / "index.html").is_file())
    for slug in slugs:
        html = (RAIZ / slug / "index.html").read_text(encoding="utf-8")
        p = leer_persona(html)
        (RAIZ / slug / "contacto.vcf").write_bytes(vcard(p).encode("utf-8"))
        print(f"[ok] {slug}/contacto.vcf  {p['nombre']} {p['apellido']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
