# CLAUDE.md — Tarjetas digitales NFC Petromark

Este repo es un sitio estático hosteado en GitHub Pages. Cada persona de Petromark tiene
una carpeta con su `index.html`; un tag NFC en su tarjeta impresa apunta a esa URL.

## Estructura

```
/
├── img/
│   ├── wordmark.png      logo "petromark" (no tocar)
│   └── escudo.png        escudo celeste (no tocar)
├── rparra/               plantilla de referencia: copiar, nunca borrar
│   ├── index.html
│   └── foto.jpg          opcional
├── <slug>/index.html     una carpeta por persona
├── tarjeta_nfc.scad      modelo 3D de la tarjeta
├── README.md             instrucciones de hosting, tags e impresión
└── CLAUDE.md             este archivo
```

URL base: `https://pmk-srl.github.io/petromark-tarjetas/` (o `https://tarjeta.petromark.com.ar/`
si ya está el subdominio). La tarjeta de una persona queda en `<URL base>/<slug>/`.

## Reglas para editar

- **Los datos de una persona viven SOLO en el bloque `const persona = { ... }`** al final de
  su `index.html`. No editar el HTML de arriba para cambiar nombre, cargo, teléfono, etc.
- No modificar la sección `<style>` ni la estructura del HTML salvo que se pida explícitamente
  un cambio de diseño; en ese caso aplicarlo a **todas** las carpetas de personas para que
  queden iguales.
- La lista de áreas de servicio (`<ul class="lista">`) es igual para toda la empresa. Si se cambia
  uno, replicarlo en todas las carpetas.
- `teléfono` siempre en formato internacional sin espacios ni guiones: `+542991234567`.
- `web` con `https://`.
- `linkedin` puede quedar `""`.
- El slug de carpeta es el nombre en minúsculas, sin tildes, espacios ni puntos: `jperez`, `mgomez`.
- Nunca borrar `rparra/`: es la plantilla.
- Al editar, entregar el `index.html` completo, no fragmentos.

## Tareas típicas

### "Agregá a <Nombre Apellido>, <cargo>, tel <...>, mail <...>"
1. `cp -r rparra/ <slug>/`
2. Borrar `<slug>/foto.jpg` si existe (cada persona pone la suya).
3. Editar el bloque `persona` en `<slug>/index.html` con los datos dados. Si falta algún dato,
   preguntar antes de inventar.
4. Agregar la línea a la tabla del final de este archivo.
5. Commit: `Agrega tarjeta de <Nombre Apellido>`.
6. Responder con la URL final de la tarjeta, que es lo que hay que grabar en el tag.

### "Cambiá el teléfono/cargo/mail de <persona>"
Editar solo el campo correspondiente en el bloque `persona` de su `index.html`. Commit y push.
Los tags ya grabados no necesitan cambios.

### "Cambiá <algo del diseño>"
Aplicar el cambio en `rparra/index.html` primero, verificar, y luego replicar exactamente el
mismo cambio en cada `<slug>/index.html`. Los bloques `persona` de cada uno no se tocan.

### "Sacá a <persona>"
Borrar la carpeta. Avisar que el tag físico de esa persona va a quedar apuntando a un 404.

### "Subí las fotos" / "procesá las fotos"
Las fotos van en `fotos_editadas/<slug>.jpg|png` si ya vienen retocadas (ChatGPT) o en
`fotos_originales/<slug>.jpg` si son crudas del celular; ambas carpetas están ignoradas por git. El script
`fotos.py` las convierte al estilo de la tarjeta: recorte de fondo con IA local (modelo ISNet vía
onnxruntime, sin rembg porque Smart App Control bloquea numba), fondo gris oscuro con viñeta,
blanco y negro, encuadre de cabeza, hombros y algo de pecho, torso desvanecido hacia abajo, 600×600 JPEG.

```powershell
python fotos.py --preview          # genera fotos_originales/_preview/<slug>.jpg sin tocar las carpetas
python fotos.py                    # escribe <slug>/foto.jpg para todas las que tengan carpeta
python fotos.py ecanullo rparra    # solo esas personas
```

Procedimiento:
1. Correr en `--preview` y mostrar al usuario un boceto (render de la tarjeta con la foto) antes
   de publicar. Si alguna foto sale mal (recorte, encuadre, luz), avisar y no publicar esa.
2. Con el aprobado, correr sin `--preview`, commit `Agrega fotos de <personas>` y push.
3. Parámetros en la cabecera de `fotos.py`: `ZOOM` (3.2, más alto = más lejos), `HEADROOM`
   (0.13), brillo (`Brightness 0.90`). Fueron ajustados con el usuario; no cambiarlos sin pedir.
4. Pautas para la toma: pared lisa, luz de ventana de frente, celular a la altura de los ojos a
   unos 2 metros con zoom 2x, encuadre de pecho para arriba con aire sobre la cabeza, ropa oscura,
   modo retrato apagado. Si la persona sale más lejos, mejor: el script tiene más margen.

Requiere Python 3.12 (`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`) con `onnxruntime`,
`pillow` y `numpy`.

## Cómo publicar

```bash
git add .
git commit -m "<mensaje>"
git push
```

GitHub Pages publica solo en uno o dos minutos. No hay build.

## Probar en local

Abrir `<slug>/index.html` con doble clic en el navegador, o usar la extensión Live Server
de VS Code. El navegador interno de VS Code (Simple Browser) no abre archivos locales.

## Personas cargadas

| Slug   | Nombre | Cargo | URL grabada en el tag |
|--------|--------|-------|-----------------------|
| `rparra` | Rolando Parra | Representante Técnico / I+D | `https://pmk-srl.github.io/petromark-tarjetas/rparra/` |
| `jstalldecker` | Jorge Stalldecker | Gerente de Producto PC/PAT | `https://pmk-srl.github.io/petromark-tarjetas/jstalldecker/` |
| `gtwardowski` | Gustavo Twardowski | Gerente General | `https://pmk-srl.github.io/petromark-tarjetas/gtwardowski/` |
| `sacosta` | Sandro Acosta | Gerente de Producto END | `https://pmk-srl.github.io/petromark-tarjetas/sacosta/` |
| `aacuna` | Andrea Acuña | Líder Técnico | `https://pmk-srl.github.io/petromark-tarjetas/aacuna/` |
| `oamache` | Oriana Amache | Representante Técnico END | `https://pmk-srl.github.io/petromark-tarjetas/oamache/` |
| `lamenabar` | Luis Amenabar | Representante Técnico ILAP | `https://pmk-srl.github.io/petromark-tarjetas/lamenabar/` |
| `ecanullo` | Emilio Canullo | Responsable Técnico END | `https://pmk-srl.github.io/petromark-tarjetas/ecanullo/` |
| `ldedios` | Lucio De Dios | Representante Técnico | `https://pmk-srl.github.io/petromark-tarjetas/ldedios/` |
| `ggimenez` | Gonzalo Gimenez | Representante Técnico PC/PAT NOC | `https://pmk-srl.github.io/petromark-tarjetas/ggimenez/` |
| `fibarra` | Fernando Ibarra | Responsable de Compras, Mantenimiento y Logística | `https://pmk-srl.github.io/petromark-tarjetas/fibarra/` |
| `jjimenez` | Jose Jimenez | Representante Técnico END | `https://pmk-srl.github.io/petromark-tarjetas/jjimenez/` |
| `llinares` | Lizeth Linares | Líder Técnico en Corrosión/Protección Catódica | `https://pmk-srl.github.io/petromark-tarjetas/llinares/` |
| `lohara` | Luis Ohara | Líder Técnico END | `https://pmk-srl.github.io/petromark-tarjetas/lohara/` |
| `apinto` | Alejandro Pinto | Líder Técnico PAT | `https://pmk-srl.github.io/petromark-tarjetas/apinto/` |
| `nrojo` | Norman Rojo | Supervisor Técnico | `https://pmk-srl.github.io/petromark-tarjetas/nrojo/` |
| `ftartaglia` | Fredy Tartaglia | Responsable Técnico END | `https://pmk-srl.github.io/petromark-tarjetas/ftartaglia/` |
| `dtorres` | Daniel Torres | Supervisor PC | `https://pmk-srl.github.io/petromark-tarjetas/dtorres/` |
| `yturra` | Yerimen Turra | Responsable Técnico PC y PAT | `https://pmk-srl.github.io/petromark-tarjetas/yturra/` |
