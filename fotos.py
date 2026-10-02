"""
Genera <slug>/foto.jpg a partir de fotos_editadas/ o fotos_originales/<slug>.jpg|jpeg|png
con el estilo de las tarjetas: blanco y negro, fondo oscuro con viñeta,
encuadre de pecho para arriba, cuadrado 600x600.

Uso:
    python fotos.py              -> procesa todas las fotos de fotos_originales/
    python fotos.py rparra       -> procesa solo esa persona
    python fotos.py rparra --preview  -> guarda en fotos_originales/_preview/ sin tocar la carpeta de la persona
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import onnxruntime as ort

RAIZ = Path(__file__).parent
ORIGINALES = RAIZ / "fotos_originales"
EDITADAS = RAIZ / "fotos_editadas"      # fotos ya retocadas (ChatGPT): tienen prioridad
LADO = 600                      # px del cuadrado final
HEADROOM = 0.13                 # aire sobre la cabeza, fracción del lado
ZOOM = 3.2                      # lado del recorte = ZOOM × ancho de la cara
ESPEJO = set()                     # personas cuya foto se voltea horizontalmente
ZOOM_POR_SLUG = {                 # ajustes puntuales aprobados por el usuario (más alto = más lejos)
    "ggimenez": 4.6,
    "rparra": 3.7,
}
FONDO_CENTRO = (0x4a, 0x4a, 0x4d)
FONDO_BORDE = (0x14, 0x12, 0x10)

MODELO = Path.home() / ".rembg" / "models" / "isnet-general-use" / "isnet-general-use.onnx"
MODELO_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx"
_session = None


def session():
    """Modelo ISNet (segmentación de primer plano) ejecutado directo con onnxruntime.
    No se usa rembg como librería porque arrastra numba/llvmlite, que Smart App Control bloquea."""
    global _session
    if _session is None:
        if not MODELO.exists():
            import urllib.request
            MODELO.parent.mkdir(parents=True, exist_ok=True)
            print("Descargando modelo...", MODELO_URL)
            urllib.request.urlretrieve(MODELO_URL, MODELO)
        _session = ort.InferenceSession(str(MODELO), providers=["CPUExecutionProvider"])
    return _session


def remove(img: Image.Image, session=None) -> Image.Image:
    """Devuelve la imagen RGBA con el fondo transparente (misma firma que rembg.remove)."""
    sess = session or globals()["session"]()
    w, h = img.size
    x = np.array(img.convert("RGB").resize((1024, 1024), Image.LANCZOS), np.float32) / 255.0
    x = (x - 0.5) / 1.0
    x = x.transpose(2, 0, 1)[None]
    nombre = sess.get_inputs()[0].name
    pred = sess.run(None, {nombre: x})[0][0][0]
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    mask = Image.fromarray((pred * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def fondo(lado):
    """Gradiente radial oscuro con viñeta."""
    y, x = np.mgrid[0:lado, 0:lado].astype(np.float32)
    cx, cy = lado / 2, lado * 0.42
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (lado * 0.72)
    d = np.clip(d, 0, 1) ** 1.4
    c = np.array(FONDO_CENTRO, np.float32)
    b = np.array(FONDO_BORDE, np.float32)
    img = c * (1 - d[..., None]) + b * d[..., None]
    return Image.fromarray(img.astype(np.uint8), "RGB")


def limpiar_bordes(rgba: Image.Image) -> Image.Image:
    """Quita el halo del fondo original en los bordes semitransparentes (pelo) y afina la máscara.
    1) estima el color del fondo original con los píxeles claramente de fondo,
    2) descontamina: color = (color_mezclado - (1-a)·fondo) / a,
    3) endurece y erosiona un poco el alfa, y lo suaviza al final."""
    arr = np.array(rgba).astype(np.float32)
    rgb, a = arr[..., :3], arr[..., 3:4] / 255.0
    fondo_px = rgb[(a[..., 0] < 0.05)]
    if len(fondo_px) > 100:
        bg = np.median(fondo_px, axis=0)
        mezcla = (a > 0.02) & (a < 0.98)
        limpio = np.clip((rgb - (1 - a) * bg) / np.maximum(a, 0.02), 0, 255)
        rgb = np.where(mezcla, limpio, rgb)
    a2 = np.clip(a[..., 0], 0, 1) ** 1.4
    a_img = Image.fromarray((a2 * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(a_img)
    return out


def ancho_cabeza(alpha):
    """Ancho de la cara: mediana del ancho de la silueta en la franja del 12% al 30%
    de la altura visible (debajo del pelo, arriba del cuello)."""
    filas = np.where(alpha.max(axis=1) > 128)[0]
    top = filas[0]
    alto_total = filas[-1] - top
    a, b = top + int(alto_total * 0.12), top + max(1, int(alto_total * 0.30))
    franja = alpha[a:b]
    anchos = [np.ptp(np.where(f > 128)[0]) for f in franja if (f > 128).any()]
    return top, int(np.percentile(anchos, 10))   # sienes, no el pelo


def procesar(src: Path, dst: Path):
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if src.stem in ESPEJO:
        img = ImageOps.mirror(img)
    # limitar tamaño de trabajo
    img.thumbnail((1600, 1600))

    rgba = remove(img, session=session())
    rgba = limpiar_bordes(rgba)
    alpha = np.array(rgba.getchannel("A"))

    top, w_cabeza = ancho_cabeza(alpha)
    cols = np.where(alpha.max(axis=0) > 128)[0]
    filas_cabeza = alpha[top: top + int(w_cabeza * 1.2)]
    cx = int(np.mean(np.where(filas_cabeza.max(axis=0) > 128)[0])) if filas_cabeza.size else int(cols.mean())

    lado = int(w_cabeza * ZOOM_POR_SLUG.get(src.stem, ZOOM))
    x0 = int(cx - lado / 2)
    y0 = int(top - lado * HEADROOM)

    # si el recorte se sale de la foto, se amplía el lienzo con transparencia
    # (el fondo se reemplaza igual) y se desvanecen los bordes donde la foto se corta
    pad_l = max(0, -x0); pad_t = max(0, -y0)
    pad_r = max(0, x0 + lado - rgba.width); pad_b = max(0, y0 + lado - rgba.height)
    if pad_l or pad_t or pad_r or pad_b:
        lienzo = Image.new("RGBA", (rgba.width + pad_l + pad_r, rgba.height + pad_t + pad_b), (0, 0, 0, 0))
        lienzo.paste(rgba, (pad_l, pad_t))
        rgba = lienzo
        x0 += pad_l; y0 += pad_t

    recorte = rgba.crop((x0, y0, x0 + lado, y0 + lado)).resize((LADO, LADO), Image.LANCZOS)

    # desvanecer el torso hacia abajo y los costados cortados
    a = np.array(recorte.getchannel("A"), np.float32)
    yy = np.linspace(0, 1, LADO)[:, None]
    esc = LADO / lado
    borde_inf = 1 - pad_b * esc / LADO                        # dónde termina la foto original
    fade_y = np.clip((borde_inf - yy) / 0.24, 0, 1) ** 1.5    # 0 en ese borde, 1 un 24% más arriba
    xx = np.linspace(0, 1, LADO)[None, :]
    fade_x = np.ones_like(xx)
    if pad_l: fade_x = np.minimum(fade_x, np.clip((xx - pad_l * esc / LADO) / 0.10, 0, 1))
    if pad_r: fade_x = np.minimum(fade_x, np.clip(((1 - xx) - pad_r * esc / LADO) / 0.10, 0, 1))
    a = a * fade_y * fade_x
    recorte.putalpha(Image.fromarray(a.astype(np.uint8)))

    # sombra suave detrás de la silueta para integrar con el fondo
    a = recorte.getchannel("A")
    sombra = Image.new("RGBA", (LADO, LADO), (0, 0, 0, 0))
    sombra.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.55)))

    base = fondo(LADO).convert("RGBA")
    base.alpha_composite(sombra, (0, 6))
    base.alpha_composite(recorte)

    bn = ImageOps.grayscale(base.convert("RGB"))
    bn = ImageOps.autocontrast(bn, cutoff=0.2)
    bn = ImageEnhance.Brightness(bn).enhance(0.90)
    bn = ImageEnhance.Contrast(bn).enhance(1.04)
    bn = bn.filter(ImageFilter.UnsharpMask(radius=1.0, percent=35, threshold=3))

    dst.parent.mkdir(parents=True, exist_ok=True)
    bn.convert("RGB").save(dst, "JPEG", quality=88, optimize=True, progressive=True)
    return dst


def main(argv):
    preview = "--preview" in argv
    slugs = [a for a in argv if not a.startswith("--")]
    exts = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    fuentes = {}
    for carpeta in (ORIGINALES, EDITADAS):      # la editada pisa a la original
        for e in exts:
            for p in carpeta.glob(e):
                fuentes[p.stem] = p
    fuentes = list(fuentes.values())
    if slugs:
        fuentes = [p for p in fuentes if p.stem in slugs]
    if not fuentes:
        print("No hay fotos para procesar en", ORIGINALES)
        return 1
    for src in sorted(fuentes):
        slug = src.stem
        if preview:
            dst = ORIGINALES / "_preview" / f"{slug}.jpg"
        else:
            if not (RAIZ / slug).is_dir():
                print(f"[saltado] no existe la carpeta {slug}/")
                continue
            dst = RAIZ / slug / "foto.jpg"
        procesar(src, dst)
        print(f"[ok] {src.name} -> {dst.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
