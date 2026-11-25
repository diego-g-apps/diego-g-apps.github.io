# Políticas de privacidad – Diego G Apps

Web estática (HTML + CSS, sin servidor, sin cookies y sin scripts) publicada gratis con **GitHub Pages**
en **https://diego-g-apps.github.io** (repositorio `diego-g-apps/diego-g-apps.github.io`).

Cada app tiene su política en **español, inglés, italiano y portugués**. La raíz incluye también
`app-ads.txt` para AdMob.

## Direcciones

| Idioma | Portada | Contacto | Política de cada app |
|---|---|---|---|
| Español | `/` | `/contacto.html` | `/privacy/<app>.html` ← la que va en Google Play |
| Inglés | `/en/` | `/en/contact.html` | `/en/privacy/<app>.html` |
| Italiano | `/it/` | `/it/contatti.html` | `/it/privacy/<app>.html` |
| Portugués | `/pt/` | `/pt/contato.html` | `/pt/privacy/<app>.html` |

No cambies las rutas en español ni en italiano: ya están puestas en Google Play.

## Estructura

```
app-ads.txt                 Vendedores autorizados de AdMob (una línea, vale para todas las apps)
index.html, contacto.html   Español (raíz)
en/, it/, pt/               Los otros idiomas
privacy/<app>.html          Políticas en español
assets/css/styles.css       Estilos
assets/img/<app>.png        Iconos de las apps (128×128)
assets/img/favicon.svg      Icono de la pestaña del navegador
_fuente/sitio.json          Nombre del desarrollador, correo, dirección de la web y fecha de actualización
_fuente/apps.json           Datos de cada app en los 4 idiomas
_fuente/textos.py           Todos los textos de la web en los 4 idiomas
_fuente/build.py            Genera todas las páginas a partir de los archivos anteriores
```

Las carpetas que empiezan por `_` **no se publican** (GitHub Pages las ignora).

## Regenerar las páginas

```
python3 _fuente/build.py
```

No necesita instalar nada. El script comprueba que cada app tenga sus textos en los 4 idiomas y su icono.

## Añadir una app nueva

1. Revisar el proyecto y el AAB: permisos del manifiesto, SDK incluidos (AdMob, Firebase…), acceso a
   Internet, qué se guarda en `user://` y si abre enlaces externos.
2. Añadir un bloque en `_fuente/apps.json` copiando uno existente, con los textos en `es`, `en`, `it` y `pt`:
   - `"tipo": "admob"` si muestra anuncios de AdMob con el formulario de consentimiento de Google (UMP).
     Rellenar `anuncio` y `boton_privacidad`.
   - `"tipo": "sin_red"` si **no** tiene permiso de Internet ni SDK de terceros.
   - `"anuncios_g": true` si la app limita los anuncios a contenido para todos los públicos.
   - `"enlaces_externos": true` si la app abre enlaces a webs externas.
   - `"en_desarrollo": true` si aún no está publicada.
   - `"icono": false` si todavía no tiene icono (se muestran sus iniciales).
   - `"copia_android": true` si el juego permite la copia de seguridad de Android (`allowBackup`) y
     ofrece conservar los datos al desinstalar. La política lo explica en «Datos que la app guarda».
   - `"fecha_iso"` en una app usa esa fecha de actualización solo para su política (si no, la de `sitio.json`).
   - Si la app usa algo distinto (Firebase, compras, cuentas, ubicación…), hay que ampliar `build.py` y
     `textos.py` con una sección nueva. No reutilices un tipo que no describa la realidad.
3. Poner el icono en `assets/img/<slug>.png` (128×128) y quitar `"icono": false`.
4. Cambiar `fecha_iso` en `sitio.json`, ejecutar `python3 _fuente/build.py`, revisar y publicar.

## Cuándo actualizar una política

Cuando una versión nueva añade o quita anuncios, SDK de terceros, permisos, cuentas, compras, multijugador
online o envío de datos a un servidor, o cambia el público objetivo. Después hay que revisar también el
formulario **Seguridad de los datos** de esa app en Play Console.

**Inca Chess:** la versión 0.2.0 tiene el modo online desactivado y no pide Internet. Si se activa el modo
online, hay que reescribir su política antes de publicar esa versión.

**Alpaca Racing:** la versión 0.1.0 no tiene Internet ni anuncios. Antes de publicar la versión con AdMob,
cambiar `"tipo"` a `"admob"`, rellenar `anuncio` y `boton_privacidad`, actualizar `version` y la fecha, y regenerar.

**Mr. Hero: Greek Myths:** la versión 0.4.0 lleva AdMob (banner en el menú principal e intersticial cada 2
derrotas al pulsar «Reintentar»), contenido de anuncios G, copia de seguridad de Android activada y opción de
conservar los datos al desinstalar. Al exportar su primer AAB, comprobar que los permisos del manifiesto coinciden
con la tabla de la política (son los mismos del SDK de Google que en Crucigrama de Jergas).
