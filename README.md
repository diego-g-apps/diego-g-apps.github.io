# Políticas de privacidad – apps Android de Diego G

Web estática (HTML + CSS, sin servidor ni base de datos) publicada gratis con **GitHub Pages**.
Cada app tiene su propia página en español y en italiano.

## Estructura

```
index.html                         Portada (español)
contacto.html                      Contacto (español)
privacy/<app>.html                 Política de cada app (español)  ← URL para Google Play
it/index.html                      Portada (italiano)
it/contatti.html                   Contatti (italiano)
it/privacy/<app>.html              Informativa di ogni app (italiano)
assets/css/styles.css              Estilos
assets/img/<app>.png               Iconos de las apps (128×128)
_fuente/sitio.json                 Nombre del desarrollador, correo y fecha de actualización
_fuente/apps.json                  Datos de cada app (lo que guarda, anuncios, versión revisada…)
_fuente/build.py                   Genera todas las páginas HTML a partir de los dos JSON
```

Las carpetas que empiezan por `_` **no se publican** (GitHub Pages las ignora).

## Cómo regenerar las páginas

```
python3 _fuente/build.py
```

No necesita instalar nada. Si faltan el nombre o el correo en `sitio.json`, las páginas salen con un
aviso rojo de BORRADOR y el script termina con error. No publiques así.

## Añadir una app nueva

1. Revisar el AAB/APK publicado: permisos del manifiesto, SDK incluidos (AdMob, Firebase…), acceso a Internet,
   qué se guarda en `user://`.
2. Añadir un bloque en `_fuente/apps.json` copiando uno existente:
   - `"tipo": "admob"` si la app muestra anuncios de AdMob con el formulario de consentimiento de Google (UMP).
   - `"tipo": "sin_red"` si la app **no** tiene permiso de Internet ni SDK de terceros.
   - Si la app usa algo distinto (Firebase, compras, cuenta de usuario, ubicación…), hay que ampliar
     `build.py` con una sección nueva. No reutilices un tipo que no describa la realidad.
3. Poner el icono en `assets/img/<slug>.png` (128×128).
4. Ejecutar `python3 _fuente/build.py`, revisar las páginas y publicar.

## Cuándo actualizar una política

Hay que revisar la política y cambiar `fecha_iso` en `sitio.json` cuando una versión nueva:

- añade o quita anuncios, o cambia de red publicitaria;
- añade SDK de terceros (Firebase, Analytics, Crashlytics, Unity, Facebook…);
- añade permisos (Internet, ubicación, cámara, micrófono, contactos, archivos, notificaciones…);
- añade cuentas de usuario, compras dentro de la app, multijugador online o envío de datos a un servidor;
- cambia el público objetivo (por ejemplo, si incluye menores de 13 años).

Después hay que revisar también el formulario **Seguridad de los datos** de esa app en Play Console,
para que coincida con la política.

## Alpaca Racing

La versión 0.1.0 no tiene permiso de Internet ni anuncios. Antes de publicar la versión con AdMob:
cambiar `"tipo"` a `"admob"`, rellenar `anuncio` y `boton_privacidad`, actualizar `version` y la fecha, y regenerar.
