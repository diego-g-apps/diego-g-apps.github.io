#!/usr/bin/env python3
"""Genera todas las páginas HTML del sitio a partir de sitio.json, apps.json y textos.py.

Uso (desde la carpeta raíz del sitio):
    python3 _fuente/build.py

No necesita librerías externas. Las páginas generadas son HTML estático que
GitHub Pages sirve tal cual. Las carpetas que empiezan por "_" no se publican.

Idiomas y rutas:
    es  ->  /index.html, /contacto.html, /privacy/<app>.html        (raíz)
    en  ->  /en/index.html, /en/contact.html, /en/privacy/<app>.html
    it  ->  /it/index.html, /it/contatti.html, /it/privacy/<app>.html
    pt  ->  /pt/index.html, /pt/contato.html, /pt/privacy/<app>.html
Las rutas en español e italiano no deben cambiar: ya están en Google Play.
"""
import datetime
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from textos import (LANGS, LANG_NAME, PREFIX, CONTACT_FILE, MESES,  # noqa: E402
                    FORMATO_FECHA, T)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "_fuente"

GOOGLE = {
    "privacy": "https://policies.google.com/privacy",
    "partners": "https://policies.google.com/technologies/partner-sites",
    "ads": "https://policies.google.com/technologies/ads",
    "adcenter": "https://myadcenter.google.com/",
}

e = html.escape


def fecha(iso, lang):
    d = datetime.date.fromisoformat(iso)
    return FORMATO_FECHA[lang].format(d=d.day, m=MESES[lang][d.month - 1], y=d.year)


def ruta(lang, tipo, slug=None):
    p = PREFIX[lang]
    if tipo == "index":
        return f"{p}index.html"
    if tipo == "contact":
        return f"{p}{CONTACT_FILE[lang]}"
    return f"{p}privacy/{slug}.html"


def profundidad(r):
    return r.count("/")


def iniciales(nombre):
    partes = [x for x in nombre.split() if x[:1].isalpha()]
    return "".join(x[0] for x in partes[:2]).upper()


def icono(app, up, size=56):
    if app.get("icono", True):
        return (f'<img class="app-icon" src="{up}assets/img/{app["slug"]}.png" alt="" '
                f'width="{size}" height="{size}" loading="lazy">')
    return f'<span class="app-icon app-icon--mono" aria-hidden="true">{e(iniciales(app["nombre"]))}</span>'


# ----------------------------------------------------------------------------
# Plantilla general
# ----------------------------------------------------------------------------

def pagina(lang, tipo, slug, titulo, descripcion, cuerpo, sitio):
    t = T[lang]
    actual = ruta(lang, tipo, slug)
    up = "../" * profundidad(actual)
    dev = sitio["desarrollador"] or t["pending"]
    aviso = "" if sitio["desarrollador"] and sitio["email"] else \
        f'<div class="draft-banner" role="alert">{t["draft"]}</div>\n'
    base = (sitio.get("url_base") or "").rstrip("/")

    alternos = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{base}/{ruta(l, tipo, slug)}">' for l in LANGS)
    alternos += f'\n<link rel="alternate" hreflang="x-default" href="{base}/{ruta("es", tipo, slug)}">'
    canonical = f'<link rel="canonical" href="{base}/{actual}">' if base else ""

    idiomas = "\n".join(
        (f'<li><a href="{up}{ruta(l, tipo, slug)}" hreflang="{l}" lang="{l}"'
         + (' aria-current="true"' if l == lang else "")
         + f'><span class="lang-code">{l.upper()}</span><span class="lang-name">{LANG_NAME[l]}</span></a></li>')
        for l in LANGS)

    def nav(href_tipo, texto):
        cur = ' aria-current="page"' if href_tipo == tipo else ""
        return f'<a href="{up}{ruta(lang, href_tipo)}"{cur}>{texto}</a>'

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} · Diego G Apps</title>
<meta name="description" content="{e(descripcion)}">
<meta name="theme-color" content="#0f3d3e">
{canonical}
{alternos}
<link rel="icon" href="{up}assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{up}assets/img/apple-touch-icon.png">
<link rel="stylesheet" href="{up}assets/css/styles.css">
</head>
<body>
<a class="skip" href="#main">{t["skip"]}</a>
{aviso}<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{up}{ruta(lang, "index")}">
      <img class="brand-logo" src="{up}assets/img/logo.png" alt="" width="40" height="40">
      <span class="brand-text">Diego G <span>Apps</span></span>
    </a>
    <nav class="main-nav" aria-label="{t["nav_apps"]}">
      {nav("index", t["nav_apps"])}
      {nav("contact", t["nav_contact"])}
    </nav>
    <details class="lang-menu">
      <summary aria-label="{t["lang_label"]}"><span class="globe" aria-hidden="true"></span>{lang.upper()}</summary>
      <ul>
{idiomas}
      </ul>
    </details>
  </div>
</header>
<main id="main">
{cuerpo}
</main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <p>{t["footer"].format(dev=e(dev))}<br><span class="muted">{t["footer_nocookies"]}</span></p>
    <p><a href="{up}{ruta(lang, "contact")}">{t["nav_contact"]}</a> · © {datetime.date.fromisoformat(sitio["fecha_iso"]).year} {e(dev)}</p>
  </div>
</footer>
</body>
</html>
"""


# ----------------------------------------------------------------------------
# Portada y contacto
# ----------------------------------------------------------------------------

def tarjeta(app, lang, up):
    t = T[lang]
    badges = []
    if app["tipo"] == "admob":
        badges.append(f'<span class="badge badge--ads">{t["badge_ads"]}</span>')
    else:
        badges.append(f'<span class="badge badge--ok">{t["badge_offline"]}</span>')
    if app.get("en_desarrollo"):
        badges.append(f'<span class="badge badge--dev">{t["badge_dev"]}</span>')
    return f"""    <li class="app-card">
      <div class="app-card-head">
        {icono(app, up)}
        <div>
          <h3>{e(app["nombre"])}</h3>
          <div class="badges">{"".join(badges)}</div>
        </div>
      </div>
      <p>{e(app["descripcion"][lang])}</p>
      <a class="button" href="{up}{ruta(lang, "policy", app["slug"])}">{t["btn_policy"]} <span aria-hidden="true">→</span></a>
    </li>"""


def index(apps, lang, sitio):
    t = T[lang]
    up = "../" * profundidad(ruta(lang, "index"))
    principios = "\n".join(
        f'      <li><strong>{e(h)}</strong><span>{e(p)}</span></li>' for h, p in t["principles"])
    cards = "\n".join(tarjeta(a, lang, up) for a in apps)
    cuerpo = f"""<section class="hero">
  <div class="wrap">
    <p class="eyebrow">{t["index_eyebrow"]}</p>
    <h1>{t["index_title"]}</h1>
    <p class="lead">{t["index_lead"]}</p>
    <ul class="principles">
{principios}
    </ul>
  </div>
</section>
<section class="wrap section">
  <h2 class="section-title">{t["index_apps_h"]}</h2>
  <ul class="app-grid">
{cards}
  </ul>
</section>"""
    return pagina(lang, "index", None, t["index_title"], t["index_lead"], cuerpo, sitio)


def contacto(lang, sitio):
    t = T[lang]
    email = sitio["email"]
    mail = f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else t["pending"]
    dev = e(sitio["desarrollador"]) or t["pending"]
    cuerpo = f"""<section class="page-head">
  <div class="wrap narrow">
    <h1>{t["contact_title"]}</h1>
    <p class="lead">{t["contact_intro"]}</p>
  </div>
</section>
<div class="wrap narrow doc">
  <dl class="contact-card">
    <div><dt>{t["contact_dev"]}</dt><dd>{dev}</dd></div>
    <div><dt>{t["contact_email"]}</dt><dd>{mail}</dd></div>
  </dl>
  <p>{t["contact_tip"]}</p>
  <p class="muted">{t["contact_use"]}</p>
</div>"""
    return pagina(lang, "contact", None, t["contact_title"], t["contact_intro"], cuerpo, sitio)


# ----------------------------------------------------------------------------
# Políticas
# ----------------------------------------------------------------------------

def lista(items, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f"<ul{c}>\n" + "\n".join(f"  <li>{x}</li>" for x in items) + "\n</ul>"


def politica(app, lang, sitio):
    t = T[lang]
    n = e(app["nombre"])
    dev = e(sitio["desarrollador"]) or t["pending"]
    email = sitio["email"]
    mail = f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else t["pending"]
    admob = app["tipo"] == "admob"
    up = "../" * profundidad(ruta(lang, "policy", app["slug"]))

    secciones = []  # (id, título, html)

    def sec(sid, titulo, contenido):
        secciones.append((sid, titulo, contenido))

    sec("responsable", t["s_resp_h"], f'<p>{t["s_resp"].format(n=n, dev=dev, mail=mail)}</p>')

    locales = lista([e(x) for x in app["datos_locales"][lang]])
    sec("datos", t["s_local_h"],
        f'<p>{t["s_local_intro"]}</p>{locales}'
        f'<p>{t["s_local_after"].format(path=t["android_path"].format(n=n))}</p>')

    if admob:
        c = f'<p>{t["s_ads_p1"].format(anuncio=e(app["anuncio"][lang]))}</p>'
        if app.get("anuncios_g"):
            c += f'<p>{t["s_ads_g"]}</p>'
        c += f'<p>{t["s_ads_p2"]}</p>' + lista(t["s_ads_items"]) + f'<p>{t["s_ads_p3"]}</p>'
        c += f'<h3>{t["s_consent_h"]}</h3>'
        c += f'<p>{t["s_consent_p1"].format(boton=e(app["boton_privacidad"][lang]))}</p>'
        c += f'<p>{t["s_consent_p2"].format(adcenter=GOOGLE["adcenter"])}</p>'
        sec("publicidad", t["s_ads_h"], c)

        codigos = ["<code>INTERNET</code>, <code>ACCESS_NETWORK_STATE</code>",
                   "<code>AD_ID</code>",
                   "<code>READ_BASIC_PHONE_STATE</code>",
                   "<code>WAKE_LOCK</code>, <code>FOREGROUND_SERVICE</code>"]
        filas = "".join(f"<tr><td>{c_}</td><td>{d}</td></tr>" for c_, d in zip(codigos, t["perm_rows"]))
        th1, th2 = t["perm_th"]
        sec("permisos", t["s_perm_h"],
            f'<p>{t["s_perm_intro"]}</p>'
            f'<div class="table-wrap"><table class="perms"><thead><tr><th>{th1}</th><th>{th2}</th></tr></thead>'
            f'<tbody>{filas}</tbody></table></div><p>{t["s_perm_no"]}</p>')
    else:
        sec("permisos", t["s_perm_h"], f'<p>{t["s_perm_none"]}</p>')

    if app.get("enlaces_externos"):
        sec("enlaces", t["s_links_h"], f'<p>{t["s_links_p"]}</p>')

    no = list(t["no_items"])
    if not admob:
        no.insert(1, t["no_ads"])
    sec("no-hago", t["s_no_h"], lista(no, "checks"))

    sec("compartir", t["s_share_h"], f'<p>{t["s_share_admob"] if admob else t["s_share_offline"]}</p>')

    cons = [t["keep_local"], t["keep_mail"]]
    if admob:
        cons.insert(1, t["keep_google"].format(privacy=GOOGLE["privacy"]))
    sec("conservacion", t["s_keep_h"], lista(cons) + f'<p>{t["keep_noacc"]}</p>')

    sec("seguridad", t["s_sec_h"], f'<p>{t["sec"]}{" " + t["sec_admob"] if admob else ""}</p>')
    sec("derechos", t["s_rights_h"], f'<p>{t["rights"].format(mail=mail)}</p>')
    sec("menores", t["s_kids_h"],
        f'<p>{t["kids1"]}{" " + t["kids_admob"] if admob else ""} {t["kids2"]}</p>')
    sec("cambios", t["s_changes_h"], f'<p>{t["changes"]}</p>')
    sec("contacto", t["s_contact_h"], f'<p>{dev} · {mail}</p>')

    resumen = t["sum_admob"] if admob else t["sum_offline"]
    nota = f'<p class="note">{t["dev_note"]}</p>' if app.get("en_desarrollo") else ""

    toc = "\n".join(f'        <li><a href="#{sid}">{titulo}</a></li>' for sid, titulo, _ in secciones)
    if admob:
        toc += f'\n        <li><a href="#enlaces-utiles">{t["useful_h"]}</a></li>'

    cuerpo_secciones = "\n".join(
        f'<section id="{sid}"><h2><span class="num">{i}</span>{titulo}</h2>\n{contenido}\n</section>'
        for i, (sid, titulo, contenido) in enumerate(secciones, 1))

    utiles = ""
    if admob:
        enlaces = [f'<a href="{GOOGLE[k]}">{txt}</a>' for k, txt in zip(("privacy", "partners", "ads"), t["useful"])]
        utiles = f'<section id="enlaces-utiles"><h2>{t["useful_h"]}</h2>\n{lista(enlaces)}\n</section>'

    badges = (f'<span class="badge badge--ads">{t["badge_ads"]}</span>' if admob
              else f'<span class="badge badge--ok">{t["badge_offline"]}</span>')
    if app.get("en_desarrollo"):
        badges += f'<span class="badge badge--dev">{t["badge_dev"]}</span>'

    return f"""<section class="page-head">
  <div class="wrap">
    <a class="back" href="{up}{ruta(lang, "index")}"><span aria-hidden="true">←</span> {t["back"]}</a>
    <div class="policy-title">
      {icono(app, up, 72)}
      <div>
        <h1>{t["title"].format(n=n)}</h1>
        <div class="badges">{badges}</div>
      </div>
    </div>
    <dl class="meta">
      <div><dt>{t["meta_updated"]}</dt><dd>{fecha(sitio["fecha_iso"], lang)}</dd></div>
      <div><dt>{t["meta_version"]}</dt><dd>{e(app["version"])}</dd></div>
      <div><dt>{t["meta_package"]}</dt><dd><code>{e(app["paquete"])}</code></dd></div>
    </dl>
  </div>
</section>
<div class="wrap policy-layout">
  <aside class="toc">
    <nav aria-label="{t["toc"]}">
      <p class="toc-title">{t["toc"]}</p>
      <ol>
{toc}
      </ol>
    </nav>
  </aside>
  <article class="doc">
    <div class="summary">
      <h2>{t["summary_h"]}</h2>
      {lista(resumen, "checks")}
    </div>
    {nota}
{cuerpo_secciones}
{utiles}
  </article>
</div>"""


# ----------------------------------------------------------------------------

def escribir(r, contenido):
    p = RAIZ / r
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenido, encoding="utf-8")
    print("  ", r)


def main():
    sitio = json.loads((FUENTE / "sitio.json").read_text(encoding="utf-8"))
    apps = json.loads((FUENTE / "apps.json").read_text(encoding="utf-8"))
    errores = []
    for app in apps:
        for campo in ["descripcion", "datos_locales"] + (["anuncio", "boton_privacidad"] if app["tipo"] == "admob" else []):
            for l in LANGS:
                if l not in app.get(campo, {}):
                    errores.append(f"{app['slug']}: falta '{campo}' en '{l}'")
        if app.get("icono", True) and not (RAIZ / "assets/img" / f"{app['slug']}.png").exists():
            errores.append(f"{app['slug']}: falta assets/img/{app['slug']}.png (o pon \"icono\": false)")
    if errores:
        print("ERRORES en apps.json:\n  " + "\n  ".join(errores))
        return 1

    print("Generando páginas:")
    for l in LANGS:
        escribir(ruta(l, "index"), index(apps, l, sitio))
        escribir(ruta(l, "contact"), contacto(l, sitio))
        for app in apps:
            t = T[l]
            titulo = t["title"].format(n=app["nombre"])
            escribir(ruta(l, "policy", app["slug"]),
                     pagina(l, "policy", app["slug"], titulo, titulo, politica(app, l, sitio), sitio))
    if not (sitio["desarrollador"] and sitio["email"]):
        print("\nAVISO: faltan 'desarrollador' o 'email' en _fuente/sitio.json. No publicar así.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
