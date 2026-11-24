#!/usr/bin/env python3
"""Genera todas las páginas HTML del sitio a partir de sitio.json y apps.json.

Uso (desde la carpeta raíz del sitio):
    python3 _fuente/build.py

No necesita librerías externas. Las páginas generadas son HTML estático
que GitHub Pages sirve tal cual. Las carpetas que empiezan por "_" no se
publican (GitHub Pages / Jekyll las ignora).
"""
import datetime
import html
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "_fuente"

MESES = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
           "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
           "agosto", "settembre", "ottobre", "novembre", "dicembre"],
}

LINKS_GOOGLE = {
    "privacy": "https://policies.google.com/privacy",
    "partners": "https://policies.google.com/technologies/partner-sites",
    "ads": "https://policies.google.com/technologies/ads",
    "adcenter": "https://myadcenter.google.com/",
}

e = html.escape


def fecha(iso: str, lang: str) -> str:
    d = datetime.date.fromisoformat(iso)
    if lang == "es":
        return f"{d.day} de {MESES['es'][d.month - 1]} de {d.year}"
    return f"{d.day} {MESES['it'][d.month - 1]} {d.year}"


# ----------------------------------------------------------------------------
# Plantilla general
# ----------------------------------------------------------------------------

T = {
    "es": {
        "lang": "es", "home": "Aplicaciones", "contact": "Contacto",
        "other": "Italiano", "site": "Políticas de privacidad",
        "footer": "Políticas de privacidad de las aplicaciones Android de",
        "draft": "BORRADOR: faltan datos del desarrollador. No usar todavía en Google Play.",
        "pending": "[pendiente]",
    },
    "it": {
        "lang": "it", "home": "App", "contact": "Contatti",
        "other": "Español", "site": "Informative sulla privacy",
        "footer": "Informative sulla privacy delle app Android di",
        "draft": "BOZZA: mancano i dati dello sviluppatore. Non usare ancora su Google Play.",
        "pending": "[da completare]",
    },
}


def pagina(lang, titulo, descripcion, cuerpo, prof, ruta_es, ruta_it, sitio):
    """prof = nivel de carpeta respecto a la raíz (0, 1 o 2)."""
    t = T[lang]
    up = "../" * prof
    home = f"{up}index.html" if lang == "es" else f"{up}it/index.html"
    contact = f"{up}contacto.html" if lang == "es" else f"{up}it/contatti.html"
    if lang == "es":
        home = f"{up}index.html"
        other_href = f"{up}{ruta_it}"
    else:
        home = f"{up}it/index.html"
        other_href = f"{up}{ruta_es}"
    dev = sitio["desarrollador"] or t["pending"]
    aviso = "" if sitio["desarrollador"] and sitio["email"] else \
        f'<div class="draft-banner" role="alert">{t["draft"]}</div>\n'
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="alternate" hreflang="es" href="{up}{ruta_es}">
<link rel="alternate" hreflang="it" href="{up}{ruta_it}">
<link rel="stylesheet" href="{up}assets/css/styles.css">
</head>
<body>
{aviso}<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{home}"><span class="brand-dot" aria-hidden="true"></span>{t["site"]}</a>
    <nav aria-label="principal">
      <a href="{home}">{t["home"]}</a>
      <a href="{contact}">{t["contact"]}</a>
      <a class="lang" href="{other_href}" hreflang="{'it' if lang == 'es' else 'es'}">{t["other"]}</a>
    </nav>
  </div>
</header>
<main class="wrap">
{cuerpo}
</main>
<footer class="site-footer">
  <div class="wrap">{t["footer"]} {e(dev)}.</div>
</footer>
</body>
</html>
"""


# ----------------------------------------------------------------------------
# Página principal y contacto
# ----------------------------------------------------------------------------

def tarjeta(app, lang, prefijo):
    badge = ""
    if app.get("en_desarrollo"):
        badge = '<span class="badge">' + ("En desarrollo" if lang == "es" else "In sviluppo") + "</span>"
    link_txt = "Política de privacidad" if lang == "es" else "Informativa sulla privacy"
    return f"""  <li class="app-card">
    <img src="{prefijo}assets/img/{app['slug']}.png" alt="" width="64" height="64">
    <div>
      <h2>{e(app['nombre'])} {badge}</h2>
      <p>{e(app['descripcion'][lang])}</p>
      <a class="button" href="{prefijo}{'' if lang == 'es' else 'it/'}privacy/{app['slug']}.html">{link_txt} →</a>
    </div>
  </li>"""


def index(apps, lang, sitio):
    if lang == "es":
        intro = ("<h1>Políticas de privacidad</h1>\n<p class=\"lead\">Aquí encontrarás la política de "
                 "privacidad de cada una de mis aplicaciones Android publicadas en Google Play.</p>")
    else:
        intro = ("<h1>Informative sulla privacy</h1>\n<p class=\"lead\">Qui trovi l'informativa sulla "
                 "privacy di ciascuna delle mie app Android pubblicate su Google Play.</p>")
    cards = "\n".join(tarjeta(a, lang, "" if lang == "es" else "../") for a in apps)
    cuerpo = f'<section class="hero">\n{intro}\n</section>\n<ul class="app-list">\n{cards}\n</ul>'
    titulo = "Políticas de privacidad" if lang == "es" else "Informative sulla privacy"
    prof = 0 if lang == "es" else 1
    return pagina(lang, titulo, titulo, cuerpo, prof, "index.html", "it/index.html", sitio)


def contacto(lang, sitio):
    email = sitio["email"]
    t = T[lang]
    mail = f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else t["pending"]
    dev = e(sitio["desarrollador"]) or t["pending"]
    if lang == "es":
        cuerpo = f"""<article class="doc">
<h1>Contacto</h1>
<p>Si tienes preguntas sobre la privacidad de mis aplicaciones, quieres ejercer tus derechos o necesitas ayuda, escríbeme:</p>
<p class="contact-box"><strong>Desarrollador:</strong> {dev}<br><strong>Correo electrónico:</strong> {mail}</p>
<p>Indica el nombre de la aplicación en tu mensaje. Respondo normalmente en unos días.</p>
<p>Solo uso tu dirección de correo y lo que escribas para responderte. No la comparto con nadie.</p>
</article>"""
        return pagina("es", "Contacto", "Contacto del desarrollador", cuerpo, 0,
                      "contacto.html", "it/contatti.html", sitio)
    cuerpo = f"""<article class="doc">
<h1>Contatti</h1>
<p>Se hai domande sulla privacy delle mie app, vuoi esercitare i tuoi diritti o hai bisogno di aiuto, scrivimi:</p>
<p class="contact-box"><strong>Sviluppatore:</strong> {dev}<br><strong>E-mail:</strong> {mail}</p>
<p>Indica il nome dell'app nel messaggio. Di solito rispondo entro pochi giorni.</p>
<p>Uso il tuo indirizzo e-mail e il contenuto del messaggio solo per risponderti. Non li condivido con nessuno.</p>
</article>"""
    return pagina("it", "Contatti", "Contatti dello sviluppatore", cuerpo, 1,
                  "contacto.html", "it/contatti.html", sitio)


# ----------------------------------------------------------------------------
# Políticas
# ----------------------------------------------------------------------------

def lista(items):
    return "<ul>\n" + "\n".join(f"  <li>{x}</li>" for x in items) + "\n</ul>"


def politica_es(app, sitio):
    n = e(app["nombre"])
    dev = e(sitio["desarrollador"]) or T["es"]["pending"]
    email = sitio["email"]
    mail = f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else T["es"]["pending"]
    f = fecha(sitio["fecha_iso"], "es")
    locales = lista([e(x) for x in app["datos_locales"]["es"]])
    admob = app["tipo"] == "admob"
    meta = (f'<p class="meta">Última actualización: {f}<br>Versión de la app revisada: {e(app["version"])} · '
            f'Paquete: <code>{e(app["paquete"])}</code></p>')
    s = [f"<h1>Política de privacidad de {n}</h1>", meta]

    if admob:
        resumen = [
            "No tienes que crear ninguna cuenta ni darnos tu nombre, correo o teléfono.",
            "Lo que guardas en la app (como tus ajustes) se queda solo en tu teléfono.",
            f"La app muestra anuncios de <strong>Google AdMob</strong>. Para mostrarlos y medirlos, Google recoge algunos datos del dispositivo, como el identificador de publicidad.",
            "Como desarrollador no recibo, no vendo y no guardo en servidores propios tus datos personales.",
        ]
    else:
        resumen = [
            "No tienes que crear ninguna cuenta ni darnos tu nombre, correo o teléfono.",
            "La app <strong>no tiene permiso de acceso a Internet</strong>: no envía ningún dato fuera de tu teléfono.",
            "No muestra anuncios y no incluye servicios de análisis ni de terceros.",
            "Tus ajustes se guardan solo en tu teléfono.",
        ]
    s.append('<div class="summary"><h2>En resumen</h2>' + lista(resumen) + "</div>")
    if app.get("en_desarrollo"):
        s.append('<p class="note">Esta app está en desarrollo. Esta política describe la versión indicada arriba; '
                 "si una versión futura añade anuncios, Internet u otras funciones, la actualizaré antes de publicarla.</p>")

    s.append("<h2>1. Responsable</h2>")
    s.append(f"<p>Esta política se aplica a la aplicación <strong>{n}</strong> para Android, distribuida en Google Play. "
             f"Desarrollador y responsable: <strong>{dev}</strong>. Contacto: {mail}.</p>")

    s.append("<h2>2. Datos que la app guarda en tu dispositivo</h2>")
    s.append(f"<p>Para funcionar, la app guarda en el almacenamiento privado de tu teléfono:</p>{locales}"
             "<p>Estos datos no se envían al desarrollador ni a nadie más. Puedes borrarlos cuando quieras desde "
             "<em>Ajustes de Android › Aplicaciones › " + n + " › Almacenamiento › Borrar datos</em>, "
             "o desinstalando la app.</p>")

    if admob:
        s.append("<h2>3. Publicidad: Google AdMob</h2>")
        s.append(f"<p>La app muestra {e(app['anuncio']['es'])} mediante el SDK de anuncios de Google (Google Mobile Ads) "
                 "y la plataforma de consentimiento de Google (User Messaging Platform). Google LLC, o Google Ireland "
                 "Limited si estás en el Espacio Económico Europeo o en Suiza, trata estos datos según sus propias políticas.</p>")
        s.append("<p>Para servir los anuncios, el SDK de Google puede recoger y enviar a Google automáticamente:</p>")
        s.append(lista([
            "El identificador de publicidad de Android y el identificador App Set.",
            "La dirección IP, de la que se puede deducir la ubicación aproximada (país o ciudad). La app no usa el GPS.",
            "Información técnica del dispositivo: modelo, versión de Android, idioma y tipo de conexión.",
            "Interacciones con los anuncios (por ejemplo, impresiones y clics) y datos de diagnóstico y rendimiento del SDK.",
        ]))
        s.append("<p>Google usa estos datos para mostrar y medir los anuncios, prevenir el fraude y el abuso y, "
                 "solo si lo aceptas o si la ley de tu región lo permite, para mostrarte anuncios personalizados.</p>")
        s.append("<h3>Tu consentimiento y cómo cambiarlo</h3>")
        s.append(f"<p>Si estás en el Espacio Económico Europeo, el Reino Unido o Suiza, la app te muestra un formulario de "
                 f"consentimiento de Google antes de cargar anuncios. Puedes cambiar tu elección en cualquier momento con "
                 f"{e(app['boton_privacidad']['es'])} (aparece cuando tu región lo requiere).</p>"
                 "<p>También puedes restablecer o eliminar tu identificador de publicidad en los ajustes de Android "
                 "(normalmente en <em>Ajustes › Privacidad › Anuncios</em> o <em>Ajustes › Google › Anuncios</em>) y gestionar "
                 f'tus preferencias de anuncios en <a href="{LINKS_GOOGLE["adcenter"]}">Mi Centro de Anuncios de Google</a>.</p>')

        s.append("<h2>4. Permisos de Android</h2>")
        s.append("<p>La versión revisada declara estos permisos:</p>")
        s.append('<table class="perms"><thead><tr><th>Permiso</th><th>Para qué sirve</th></tr></thead><tbody>'
                 "<tr><td><code>INTERNET</code>, <code>ACCESS_NETWORK_STATE</code></td><td>Cargar los anuncios y comprobar si hay conexión.</td></tr>"
                 "<tr><td><code>AD_ID</code></td><td>Permite al SDK de Google leer el identificador de publicidad.</td></tr>"
                 "<tr><td><code>READ_BASIC_PHONE_STATE</code></td><td>Lo añaden las bibliotecas de Google incluidas. Da acceso a información básica y no sensible del teléfono (como el tipo de red). La app no lee tu número de teléfono, tus llamadas ni tus contactos.</td></tr>"
                 "<tr><td><code>WAKE_LOCK</code>, <code>FOREGROUND_SERVICE</code></td><td>Los usan internamente componentes de Android y de Google incluidos en la app para sus tareas técnicas. La app no tiene servicios propios en segundo plano.</td></tr>"
                 "</tbody></table>")
        s.append("<p>La app <strong>no</strong> pide acceso a tu ubicación precisa, cámara, micrófono, contactos, fotos ni archivos.</p>")
        k = 5
    else:
        s.append("<h2>3. Permisos de Android</h2>")
        s.append("<p>La versión revisada <strong>no declara ningún permiso</strong>: ni Internet, ni ubicación, ni cámara, "
                 "micrófono, contactos, fotos o archivos.</p>")
        k = 4

    s.append(f"<h2>{k}. Lo que no hago</h2>")
    no = ["No pido registro ni cuenta de usuario.",
          "No uso servicios de análisis ni de estadísticas propios (por ejemplo, Firebase Analytics).",
          "No vendo ni alquilo datos personales.",
          "No tengo servidores propios donde se guarden datos de los usuarios."]
    if not admob:
        no.insert(1, "No muestro anuncios.")
    s.append(lista(no))
    k += 1

    s.append(f"<h2>{k}. Con quién se comparten los datos</h2>")
    if admob:
        s.append("<p>Solo con Google, a través de AdMob, como se explica en el apartado 3. No comparto datos con nadie más.</p>")
    else:
        s.append("<p>Con nadie: la app no envía datos fuera de tu teléfono.</p>")
    k += 1

    s.append(f'<h2 id="conservacion">{k}. Conservación y eliminación de datos</h2>')
    cons = ["<strong>Datos en tu teléfono:</strong> se conservan hasta que los borras o desinstalas la app.",
            "<strong>Correos que me envíes:</strong> los conservo solo el tiempo necesario para responderte y después los elimino. Puedes pedirme que los borre antes."]
    if admob:
        cons.insert(1, f'<strong>Datos tratados por Google:</strong> Google los conserva según su <a href="{LINKS_GOOGLE["privacy"]}">política de privacidad</a>. Puedes eliminar o restablecer tu identificador de publicidad en cualquier momento.')
    s.append(lista(cons))
    s.append("<p>La app no tiene cuentas de usuario, así que no hay ninguna cuenta que eliminar.</p>")
    k += 1

    s.append(f"<h2>{k}. Seguridad</h2>")
    seg = "<p>Los datos que guarda la app están en su almacenamiento privado, al que otras apps no pueden acceder."
    if admob:
        seg += " Las comunicaciones del SDK de Google con sus servidores van cifradas."
    s.append(seg + "</p>")
    k += 1

    s.append(f"<h2>{k}. Tus derechos</h2>")
    s.append("<p>Según la normativa que te aplique (por ejemplo, el Reglamento General de Protección de Datos de la UE), "
             "tienes derecho a acceder a tus datos, rectificarlos, suprimirlos, oponerte a su tratamiento, limitarlo, pedir "
             "su portabilidad y retirar tu consentimiento en cualquier momento. Como yo no guardo datos tuyos (salvo los "
             "correos que me envíes), para los datos de anuncios puedes usar las opciones de consentimiento de la app y las "
             f"herramientas de Google. Para cualquier solicitud, escríbeme a {mail}. También puedes presentar una reclamación "
             "ante la autoridad de protección de datos de tu país (en Italia, el Garante per la protezione dei dati personali; "
             "en España, la Agencia Española de Protección de Datos).</p>")
    k += 1

    s.append(f"<h2>{k}. Menores</h2>")
    menores = "<p>La app no pide la edad, el nombre ni ningún dato que identifique a quien la usa."
    if admob:
        menores += " Los anuncios los sirve Google AdMob según sus políticas."
    menores += (" Si eres padre, madre o tutor y crees que un menor me ha enviado datos personales por correo, "
                "escríbeme y los eliminaré.</p>")
    s.append(menores)
    k += 1

    s.append(f"<h2>{k}. Cambios en esta política</h2>")
    s.append("<p>Si una versión nueva de la app cambia el uso de los datos (por ejemplo, al añadir anuncios, permisos o "
             "servicios), actualizaré esta página y la fecha de arriba.</p>")
    k += 1

    s.append(f"<h2>{k}. Contacto</h2>")
    s.append(f"<p>{dev} · {mail}</p>")

    if admob:
        s.append('<h2>Enlaces útiles</h2>' + lista([
            f'<a href="{LINKS_GOOGLE["privacy"]}">Política de privacidad de Google</a>',
            f'<a href="{LINKS_GOOGLE["partners"]}">Cómo usa Google los datos de las apps que usan sus servicios</a>',
            f'<a href="{LINKS_GOOGLE["ads"]}">Cómo usa Google la información en publicidad</a>',
        ]))
    return '<article class="doc">\n' + "\n".join(s) + "\n</article>"


def politica_it(app, sitio):
    n = e(app["nombre"])
    dev = e(sitio["desarrollador"]) or T["it"]["pending"]
    email = sitio["email"]
    mail = f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else T["it"]["pending"]
    f = fecha(sitio["fecha_iso"], "it")
    locales = lista([e(x) for x in app["datos_locales"]["it"]])
    admob = app["tipo"] == "admob"
    meta = (f'<p class="meta">Ultimo aggiornamento: {f}<br>Versione dell\'app esaminata: {e(app["version"])} · '
            f'Pacchetto: <code>{e(app["paquete"])}</code></p>')
    s = [f"<h1>Informativa sulla privacy di {n}</h1>", meta]

    if admob:
        resumen = [
            "Non devi creare alcun account né fornirci nome, e-mail o telefono.",
            "Ciò che salvi nell'app (come le impostazioni) resta solo sul tuo telefono.",
            "L'app mostra annunci di <strong>Google AdMob</strong>. Per mostrarli e misurarli, Google raccoglie alcuni dati del dispositivo, come l'ID pubblicità.",
            "Come sviluppatore non ricevo, non vendo e non conservo su server miei i tuoi dati personali.",
        ]
    else:
        resumen = [
            "Non devi creare alcun account né fornirci nome, e-mail o telefono.",
            "L'app <strong>non ha il permesso di accesso a Internet</strong>: non invia alcun dato fuori dal tuo telefono.",
            "Non mostra annunci e non include servizi di analisi o di terze parti.",
            "Le tue impostazioni restano solo sul tuo telefono.",
        ]
    s.append('<div class="summary"><h2>In breve</h2>' + lista(resumen) + "</div>")
    if app.get("en_desarrollo"):
        s.append('<p class="note">Questa app è in sviluppo. L\'informativa descrive la versione indicata sopra; '
                 "se una versione futura aggiungerà annunci, Internet o altre funzioni, la aggiornerò prima di pubblicarla.</p>")

    s.append("<h2>1. Titolare</h2>")
    s.append(f"<p>Questa informativa si applica all'app <strong>{n}</strong> per Android, distribuita su Google Play. "
             f"Sviluppatore e titolare del trattamento: <strong>{dev}</strong>. Contatto: {mail}.</p>")

    s.append("<h2>2. Dati salvati dall'app sul tuo dispositivo</h2>")
    s.append(f"<p>Per funzionare, l'app salva nella memoria privata del tuo telefono:</p>{locales}"
             "<p>Questi dati non vengono inviati allo sviluppatore né ad altri. Puoi cancellarli quando vuoi da "
             "<em>Impostazioni di Android › App › " + n + " › Spazio di archiviazione › Cancella dati</em>, "
             "oppure disinstallando l'app.</p>")

    if admob:
        s.append("<h2>3. Pubblicità: Google AdMob</h2>")
        s.append(f"<p>L'app mostra {e(app['anuncio']['it'])} tramite l'SDK pubblicitario di Google (Google Mobile Ads) "
                 "e la piattaforma di consenso di Google (User Messaging Platform). Google LLC, o Google Ireland Limited "
                 "se ti trovi nello Spazio economico europeo o in Svizzera, tratta questi dati secondo le proprie norme.</p>")
        s.append("<p>Per pubblicare gli annunci, l'SDK di Google può raccogliere e inviare a Google automaticamente:</p>")
        s.append(lista([
            "L'ID pubblicità di Android e l'identificatore App Set.",
            "L'indirizzo IP, da cui si può dedurre la posizione approssimativa (paese o città). L'app non usa il GPS.",
            "Informazioni tecniche sul dispositivo: modello, versione di Android, lingua e tipo di connessione.",
            "Interazioni con gli annunci (ad esempio visualizzazioni e clic) e dati diagnostici e di prestazione dell'SDK.",
        ]))
        s.append("<p>Google usa questi dati per mostrare e misurare gli annunci, prevenire frodi e abusi e, "
                 "solo se lo accetti o se la legge della tua regione lo consente, per mostrarti annunci personalizzati.</p>")
        s.append("<h3>Il tuo consenso e come modificarlo</h3>")
        s.append(f"<p>Se ti trovi nello Spazio economico europeo, nel Regno Unito o in Svizzera, l'app ti mostra un modulo di "
                 f"consenso di Google prima di caricare gli annunci. Puoi cambiare la tua scelta in qualsiasi momento con "
                 f"{e(app['boton_privacidad']['it'])} (compare quando la tua regione lo richiede).</p>"
                 "<p>Puoi anche reimpostare o eliminare l'ID pubblicità nelle impostazioni di Android "
                 "(di solito in <em>Impostazioni › Privacy › Annunci</em> o <em>Impostazioni › Google › Annunci</em>) e gestire "
                 f'le tue preferenze sugli annunci in <a href="{LINKS_GOOGLE["adcenter"]}">Il mio Centro annunci di Google</a>.</p>')

        s.append("<h2>4. Autorizzazioni Android</h2>")
        s.append("<p>La versione esaminata dichiara queste autorizzazioni:</p>")
        s.append('<table class="perms"><thead><tr><th>Autorizzazione</th><th>A cosa serve</th></tr></thead><tbody>'
                 "<tr><td><code>INTERNET</code>, <code>ACCESS_NETWORK_STATE</code></td><td>Caricare gli annunci e verificare la connessione.</td></tr>"
                 "<tr><td><code>AD_ID</code></td><td>Consente all'SDK di Google di leggere l'ID pubblicità.</td></tr>"
                 "<tr><td><code>READ_BASIC_PHONE_STATE</code></td><td>Aggiunta dalle librerie di Google incluse. Dà accesso a informazioni di base e non sensibili sul telefono (come il tipo di rete). L'app non legge il tuo numero di telefono, le chiamate o i contatti.</td></tr>"
                 "<tr><td><code>WAKE_LOCK</code>, <code>FOREGROUND_SERVICE</code></td><td>Usate internamente da componenti di Android e di Google incluse nell'app per le loro attività tecniche. L'app non ha servizi propri in background.</td></tr>"
                 "</tbody></table>")
        s.append("<p>L'app <strong>non</strong> chiede accesso alla posizione precisa, fotocamera, microfono, contatti, foto o file.</p>")
        k = 5
    else:
        s.append("<h2>3. Autorizzazioni Android</h2>")
        s.append("<p>La versione esaminata <strong>non dichiara alcuna autorizzazione</strong>: né Internet, né posizione, "
                 "fotocamera, microfono, contatti, foto o file.</p>")
        k = 4

    s.append(f"<h2>{k}. Cosa non faccio</h2>")
    no = ["Non chiedo registrazione né account utente.",
          "Non uso servizi di analisi o statistiche propri (ad esempio Firebase Analytics).",
          "Non vendo né cedo dati personali.",
          "Non ho server miei dove vengano salvati dati degli utenti."]
    if not admob:
        no.insert(1, "Non mostro annunci.")
    s.append(lista(no))
    k += 1

    s.append(f"<h2>{k}. Con chi vengono condivisi i dati</h2>")
    if admob:
        s.append("<p>Solo con Google, tramite AdMob, come spiegato al punto 3. Non condivido dati con nessun altro.</p>")
    else:
        s.append("<p>Con nessuno: l'app non invia dati fuori dal tuo telefono.</p>")
    k += 1

    s.append(f'<h2 id="conservazione">{k}. Conservazione e cancellazione dei dati</h2>')
    cons = ["<strong>Dati sul telefono:</strong> restano finché non li cancelli o disinstalli l'app.",
            "<strong>E-mail che mi invii:</strong> le conservo solo per il tempo necessario a risponderti, poi le elimino. Puoi chiedermi di cancellarle prima."]
    if admob:
        cons.insert(1, f'<strong>Dati trattati da Google:</strong> Google li conserva secondo la propria <a href="{LINKS_GOOGLE["privacy"]}">informativa sulla privacy</a>. Puoi eliminare o reimpostare l\'ID pubblicità in qualsiasi momento.')
    s.append(lista(cons))
    s.append("<p>L'app non ha account utente, quindi non c'è alcun account da eliminare.</p>")
    k += 1

    s.append(f"<h2>{k}. Sicurezza</h2>")
    seg = "<p>I dati salvati dall'app si trovano nella sua memoria privata, a cui le altre app non possono accedere."
    if admob:
        seg += " Le comunicazioni dell'SDK di Google con i suoi server sono cifrate."
    s.append(seg + "</p>")
    k += 1

    s.append(f"<h2>{k}. I tuoi diritti</h2>")
    s.append("<p>In base alla normativa applicabile (ad esempio il Regolamento generale sulla protezione dei dati dell'UE), "
             "hai diritto di accedere ai tuoi dati, rettificarli, cancellarli, opporti al trattamento, limitarlo, chiederne "
             "la portabilità e revocare il consenso in qualsiasi momento. Poiché non conservo tuoi dati (tranne le e-mail che "
             "mi invii), per i dati pubblicitari puoi usare le opzioni di consenso dell'app e gli strumenti di Google. Per "
             f"qualsiasi richiesta scrivimi a {mail}. Puoi anche presentare reclamo all'autorità di protezione dei dati del tuo "
             "paese (in Italia, il Garante per la protezione dei dati personali).</p>")
    k += 1

    s.append(f"<h2>{k}. Minori</h2>")
    menores = "<p>L'app non chiede l'età, il nome né alcun dato che identifichi chi la usa."
    if admob:
        menores += " Gli annunci sono forniti da Google AdMob secondo le sue norme."
    menores += (" Se sei un genitore o tutore e pensi che un minore mi abbia inviato dati personali via e-mail, "
                "scrivimi e li eliminerò.</p>")
    s.append(menores)
    k += 1

    s.append(f"<h2>{k}. Modifiche a questa informativa</h2>")
    s.append("<p>Se una nuova versione dell'app cambia l'uso dei dati (ad esempio aggiungendo annunci, autorizzazioni o "
             "servizi), aggiornerò questa pagina e la data indicata sopra.</p>")
    k += 1

    s.append(f"<h2>{k}. Contatti</h2>")
    s.append(f"<p>{dev} · {mail}</p>")

    if admob:
        s.append('<h2>Link utili</h2>' + lista([
            f'<a href="{LINKS_GOOGLE["privacy"]}">Norme sulla privacy di Google</a>',
            f'<a href="{LINKS_GOOGLE["partners"]}">Come Google utilizza i dati delle app che usano i suoi servizi</a>',
            f'<a href="{LINKS_GOOGLE["ads"]}">Come Google utilizza le informazioni nella pubblicità</a>',
        ]))
    return '<article class="doc">\n' + "\n".join(s) + "\n</article>"


# ----------------------------------------------------------------------------

def escribir(ruta: str, contenido: str):
    p = RAIZ / ruta
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenido, encoding="utf-8")
    print("  ", ruta)


def main():
    sitio = json.loads((FUENTE / "sitio.json").read_text(encoding="utf-8"))
    apps = json.loads((FUENTE / "apps.json").read_text(encoding="utf-8"))
    print("Generando páginas:")
    escribir("index.html", index(apps, "es", sitio))
    escribir("it/index.html", index(apps, "it", sitio))
    escribir("contacto.html", contacto("es", sitio))
    escribir("it/contatti.html", contacto("it", sitio))
    for app in apps:
        ruta_es = f"privacy/{app['slug']}.html"
        ruta_it = f"it/privacy/{app['slug']}.html"
        escribir(ruta_es, pagina("es", f"Política de privacidad – {app['nombre']}",
                                 f"Política de privacidad de la app Android {app['nombre']}",
                                 politica_es(app, sitio), 1, ruta_es, ruta_it, sitio))
        escribir(ruta_it, pagina("it", f"Informativa sulla privacy – {app['nombre']}",
                                 f"Informativa sulla privacy dell'app Android {app['nombre']}",
                                 politica_it(app, sitio), 2, ruta_es, ruta_it, sitio))
    if not (sitio["desarrollador"] and sitio["email"]):
        print("\nAVISO: faltan 'desarrollador' o 'email' en _fuente/sitio.json. "
              "Las páginas llevan un aviso de BORRADOR. No publicar así.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
