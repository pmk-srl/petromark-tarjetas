# Tarjetas digitales NFC — Petromark

Sistema: tarjeta impresa en 3D con un tag NFC adentro. Al acercar el celular, abre una
página web con los datos de contacto y un botón para guardar el contacto en la agenda.

```
tarjeta-nfc/
├── img/
│   ├── wordmark.png     ← "petromark" (logo texto, fondo transparente)
│   └── escudo.png       ← escudo celeste (fondo transparente)
├── rparra/
│   ├── index.html       ← página de Rolo (una carpeta por persona)
│   └── foto.jpg         ← (opcional) foto cuadrada, 76×76 o mayor
├── tarjeta_nfc.scad     ← modelo 3D paramétrico con bolsillo para el tag
└── README.md
```

## 1. Agregar una persona

1. Copiar la carpeta `rparra/` con el nombre de la persona (minúsculas, sin espacios): `juan/`, `mperez/`.
2. Abrir `index.html` y editar SOLO el bloque `const persona = { ... }` al final del archivo:
   - `telefono` en formato internacional sin espacios: `+542991234567`
   - `web`, `email`, `cargo`, etc.
3. Opcional: poner `foto.jpg` en la carpeta. Si no existe, el recuadro se oculta solo.
4. El botón "Guardar contacto" genera el `.vcf` a partir de esos mismos datos: no hay que mantener dos archivos.

Las áreas de servicio están en el HTML (sección `<ul class="lista">`); son los mismos para toda la empresa.

## 2. Hosting (gratis)

### Opción A — GitHub Pages (recomendada)
1. Crear un repo `petromark-tarjetas` (puede ser privado en plan Pro; público funciona siempre).
2. Subir el contenido de `tarjeta-nfc/` a la raíz del repo.
3. Settings → Pages → Source: `Deploy from a branch` → `main` / `/ (root)` → Save.
4. En un minuto queda en `https://contacto.petromark.com.ar/rparra/`.

### Opción B — Cloudflare Pages
Igual de simple: Workers & Pages → Create → Pages → Upload assets (arrastrar la carpeta).
Da una URL `https://petromark-tarjetas.pages.dev/rparra/`.

### Subdominio propio (opcional pero recomendable)
Si controlan el DNS de `petromark.com.ar`, agregar un registro CNAME:

| Tipo  | Nombre    | Valor                                  |
|-------|-----------|----------------------------------------|
| CNAME | `tarjeta` | `pmk-srl.github.io` (o el `.pages.dev`) |

Luego en GitHub Pages → Custom domain → `contacto.petromark.com.ar`. Queda
`https://contacto.petromark.com.ar/rparra/`. Conviene decidir esto ANTES de grabar los tags,
porque la URL grabada es la que va a durar años.

## 3. Grabar los tags

App: **NFC Tools** (gratis, Android e iOS).

1. Escribir → Agregar registro → **URL/URI** → pegar `https://contacto.petromark.com.ar/rparra/`.
2. Escribir → acercar el tag al celular (en iPhone, la antena está arriba; en Android suele estar en el centro/arriba de la tapa).
3. Probar: bloquear el celular, acercar el tag → debe aparecer la notificación con el link.
4. Opcional: Otros → **Bloquear tag** (solo lectura). Es irreversible: nadie puede regrabarlo, ni vos. Recomendable para las tarjetas que se entregan.

Tag recomendado: NTAG213 o NTAG215, formato coin 25 mm. Una URL ocupa ~40 bytes; sobra en cualquiera.

## 4. Imprimir la tarjeta

Modelo: `tarjeta_nfc.scad` (abrir con OpenSCAD, F6, exportar STL).

- Filamento: PLA o PETG. **No** usar filamentos con carga metálica ni fibra de carbono (bloquean la señal).
- Capas de 0.2 mm, sin soportes. La tapa del bolsillo (25 mm de puente) se imprime sin problema.
- El script muestra en la consola de OpenSCAD en qué altura Z pausar. Con los valores por defecto: **Z = 1.8 mm → capa 9**.
- Agregar la pausa en el slicer:
  - **Bambu Studio / OrcaSlicer**: vista previa → arrastrar la barra de capas hasta la 9 → clic derecho → "Add pause".
  - **PrusaSlicer**: vista previa → botón `+` en la barra de capas → "Add pause print (M601)".
  - **Cura**: Extensiones → Post Processing → Modify G-Code → "Pause at height" → altura 1.8 mm.
- Cuando la impresora se detiene: apoyar el tag en el hueco (si es adhesivo, pegarlo; si no, una gota de cianoacrilato en el borde para que no se mueva), reanudar.
- La muesca en la cara de abajo marca de qué lado está el tag: apoyar ese lado contra el celular.

## 5. Lista de compras

- Tags NFC NTAG213 o NTAG215, formato coin/moneda 25 mm, pack ×10 o ×20
- Filamento PLA o PETG (sin carga metálica), color a elección
- Cianoacrilato (para fijar el tag en el bolsillo si no viene adhesivo)
- Opcional: filamento de segundo color para el logo, si la impresora es multicolor
