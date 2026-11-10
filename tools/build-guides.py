#!/usr/bin/env python3
"""Builds the /guides/ section from markdown in tools/guides-src/{en,es}/*.md.

Run from the site root:  python3 tools/build-guides.py
Writes guides/<slug>/index.html, es/guides/<slug>/index.html, both index pages and sitemap.xml.
Markdown subset: ## / ### headings, paragraphs, - lists, 1. lists, pipe tables, **bold**, *italic*, [links](url), `code`.
Frontmatter: title, description, slug, other (slug of the other language), date, updated (optional).
Marker {{cta}} drops in the store buttons. A "## FAQ" / "## Preguntas frecuentes" section (### question, then answer)
becomes a visible FAQ and FAQPage JSON-LD. Stdlib only."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "guides-src"
HOST = "https://dialed.frusoft.dev"
APP_ID = "6816949019"
IOS = f"https://apps.apple.com/app/apple-store/id{APP_ID}?pt=128885457&ct={{ct}}&mt=8"
PLAY = "https://play.google.com/store/apps/details?id=com.frusoft.dialed&referrer=utm_source%3Dfrusoft-site%26utm_medium%3Dweb%26utm_campaign%3D{ct}"
APPLE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.6c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.7-3.18-1.73-1.35-.14-2.64.8-3.33.8-.69 0-1.74-.78-2.86-.76-1.47.02-2.83.86-3.59 2.17-1.53 2.65-.39 6.58 1.1 8.73.73 1.05 1.6 2.23 2.73 2.19 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.07 2.65-2.13.84-1.22 1.18-2.4 1.2-2.46-.03-.01-2.3-.88-2.3-3.49zM14.2 6.13c.6-.73 1.01-1.75.9-2.76-.87.04-1.92.58-2.54 1.31-.56.64-1.05 1.68-.92 2.67.97.08 1.96-.49 2.56-1.22z"/></svg>'
PLAY_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.6 2.3c-.2.2-.3.6-.3 1v17.4c0 .4.1.8.3 1l9.7-9.7L3.6 2.3zm10.8 10.8 2.6 2.6-11.6 6.6 9-9.2zm3.9-4 3 1.7c.9.5.9 1.3 0 1.8l-3 1.7-2.9-2.6 2.9-2.6zM5.4 1.7l11.6 6.6-2.6 2.6-9-9.2z"/></svg>'

L = {
    "en": dict(base="/guides/", home="/", other_home="/es/", other_lang="Español", other_code="es", locale="en_US",
               skip="Skip to content", brand="Dialed home", nav="Primary", guides="Guides", get="Get the app",
               idx_title="Espresso guides: dial in and fix shots | Dialed",
               idx_desc="Practical espresso guides: how to read a shot, what to change when it tastes sour or bitter, and how to use shot time. By the makers of Dialed.",
               idx_h1="Espresso guides", idx_lede="Short, practical guides for dialing in espresso. Each one tells you what to change, and why.",
               quick_h="The five-line version",
               quick=["Start at 1:2 (for example 18 g in, 36 g out) in about 25 to 30 seconds.","Sour or thin: grind finer, or let a little more into the cup.","Bitter or dry: grind coarser, or stop the shot earlier.","Sour and bitter together: fix distribution and tamp before the grind.","Change one thing at a time and write it down."],
               intro="Dialing in means finding the grind, dose and yield that make a particular coffee taste good on your machine. The routine is always the same: keep the dose fixed, taste the shot, change one thing, and write down what happened. Sour and bitter tell you which way to go, shot time tells you whether the flow is sensible, and a log keeps you from repeating shots you have already pulled. These guides cover each part in plain language, with the reasoning behind every change, so you can adapt it to your own grinder, machine and beans.",
               cta_h="Your next shot will be better.", cta_p="Free on iPhone and Android. No account, no ads.",
               dl="Download on the", gp="Get it on", more="More guides", updated="Updated", by="By Frusoft",
               footer="Footer", support="Support", privacy="Privacy", terms="Terms of Use", faq="FAQ", faq_keys=("FAQ",),
               home_crumb="Dialed", store_ios_ct="guide", ),
    "es": dict(base="/es/guides/", home="/es/", other_home="/", other_lang="English", other_code="en", locale="es_ES",
               skip="Saltar al contenido", brand="Inicio de Dialed", nav="Principal", guides="Guías", get="Descargar la app",
               idx_title="Guías de espresso: calibrar y corregir shots | Dialed",
               idx_desc="Guías prácticas de espresso: cómo leer un shot, qué cambiar cuando sale ácido o amargo y cómo usar el tiempo del shot. De los creadores de Dialed.",
               idx_h1="Guías de espresso", idx_lede="Guías cortas y prácticas para calibrar espresso. Cada una te dice qué cambiar y por qué.",
               quick_h="La versión en cinco líneas",
               quick=["Empieza en 1:2 (por ejemplo 18 g de entrada y 36 g de salida) en unos 25 a 30 segundos.","Ácido o aguado: muele más fino, o deja caer un poco más en la taza.","Amargo o seco: muele más grueso, o corta el shot antes.","Ácido y amargo a la vez: corrige distribución y tamp antes que la molienda.","Cambia una sola cosa a la vez y anótalo."],
               intro="Calibrar significa encontrar la molienda, la dosis y la bebida con las que un café determinado sabe bien en tu máquina. La rutina es siempre la misma: dosis fija, probar el shot, cambiar una sola cosa y anotar qué pasó. Ácido y amargo te dicen hacia dónde ir, el tiempo del shot te dice si el flujo es razonable, y un registro evita que repitas shots que ya sacaste. Estas guías cubren cada parte en lenguaje simple y con el razonamiento detrás de cada cambio, para que lo adaptes a tu molino, tu máquina y tus granos.",
               cta_h="Tu próximo shot va a salir mejor.", cta_p="Gratis en iPhone y Android. Sin cuenta, sin anuncios.",
               dl="Descárgalo en el", gp="Disponible en", more="Más guías", updated="Actualizado", by="Por Frusoft",
               footer="Pie de página", support="Soporte", privacy="Privacidad", terms="Términos de uso", faq="Preguntas frecuentes",
               faq_keys=("Preguntas frecuentes", "FAQ"), home_crumb="Dialed", store_ios_ct="guide-es"),
}
LABELS = {"en": ("Sour or bitter?",), "es": ()}


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


def strip_tags(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def md_blocks(lines, cta_html):
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.strip() == "{{cta}}":
            out.append(cta_html); i += 1
        elif ln.startswith("## "):
            txt = ln[3:].strip()
            out.append(f'<h2 id="{slug_id(txt)}">{inline(txt)}</h2>'); i += 1
        elif ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:].strip())}</h3>"); i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
        elif re.match(r"[-*] ", ln):
            items = []
            while i < len(lines) and re.match(r"[-*] ", lines[i]):
                items.append(inline(lines[i][2:].strip())); i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
        elif re.match(r"\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                items.append(inline(re.sub(r"^\d+\.\s*", "", lines[i]))); i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||[-*] |\d+\. |\{\{)", lines[i]):
                para.append(lines[i].strip()); i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def slug_id(t):
    t = re.sub(r"[^a-z0-9]+", "-", strip_tags(t).lower().encode("ascii", "ignore").decode()).strip("-")
    return t or "s"


def parse(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    return meta, m.group(2).strip().splitlines()


def campaign(lang, short):
    ct = f"guide-{short}" + ("-es" if lang == "es" else "")
    assert len(ct) <= 40 and re.fullmatch(r"[a-z0-9-]+", ct), ct
    return ct


def links(text, ct):
    return text.replace("{{ios}}", IOS.format(ct=ct)).replace("{{play}}", PLAY.format(ct=ct))


def cta(lang, ct):
    c = L[lang]
    return (f'<aside class="cta-box"><p class="cta-h">{c["cta_h"]}</p><p>{c["cta_p"]}</p><div class="stores">'
            f'<a class="store" data-store="ios" href="{html.escape(IOS.format(ct=ct))}">{APPLE_SVG}<span><small>{c["dl"]}</small><b>App Store</b></span></a>'
            f'<a class="store" data-store="android" href="{html.escape(PLAY.format(ct=ct))}">{PLAY_SVG}<span><small>{c["gp"]}</small><b>Google Play</b></span></a>'
            f'</div></aside>')


APP_LD = {"@type": "SoftwareApplication", "name": "Dialed: Espresso Log & Journal", "alternateName": "Dialed",
          "applicationCategory": "LifestyleApplication", "operatingSystem": "iOS 17 or later, Android",
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
          "installUrl": [f"https://apps.apple.com/app/id{APP_ID}", "https://play.google.com/store/apps/details?id=com.frusoft.dialed"],
          "url": HOST + "/"}


def head(lang, title, desc, canonical, alts, jsonld, og_type="article"):
    c = L[lang]
    alt_tags = "\n".join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in alts)
    og_img = f"{HOST}/og-es.jpg" if lang == "es" else f"{HOST}/og.jpg"
    other = [h for h, _ in alts if h not in (lang, "x-default")]
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{alt_tags}
<meta name="theme-color" content="#F6F3EC" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101210" media="(prefers-color-scheme: dark)">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Dialed">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{c["locale"]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icon.png">
<link rel="apple-touch-icon" href="/icon.png">
<link rel="stylesheet" href="/site.css">
<link rel="stylesheet" href="/guides.css">
<script defer src="/analytics.js" data-mid="G-0E2XVT06CY"></script>
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
</script>
</head>'''


def chrome_top(lang, other_url):
    c = L[lang]
    return f'''<body>
<a class="skip" href="#main">{c["skip"]}</a>
<header class="top" id="top">
  <div class="wrap">
    <a class="brand" href="{c["home"]}" aria-label="{c["brand"]}"><img src="/icon.png" alt="" width="34" height="34">Dialed</a>
    <nav aria-label="{c["nav"]}"><a href="{c["base"]}" aria-current="page">{c["guides"]}</a></nav>
    <a class="lang" href="{other_url}" hreflang="{c["other_code"]}" lang="{c["other_code"]}">{c["other_lang"]}</a>
    <a class="btn" href="/get/?src=guide" rel="nofollow">{c["get"]}</a>
  </div>
</header>
<main id="main">'''


def chrome_bottom(lang, other_url):
    c = L[lang]
    return f'''</main>
<footer>
  <div class="wrap">
    <a class="brand" href="{c["home"]}"><img src="/icon.png" alt="" width="34" height="34" loading="lazy">Dialed</a>
    <span>© 2026 Frusoft</span>
    <nav aria-label="{c["footer"]}">
      <a href="{c["base"]}">{c["guides"]}</a>
      <a href="/support/">{c["support"]}</a>
      <a href="/privacy/">{c["privacy"]}</a>
      <a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">{c["terms"]}</a>
      <a href="mailto:support@frusoft.dev">support@frusoft.dev</a>
      <a href="{other_url}" hreflang="{c["other_code"]}" lang="{c["other_code"]}">{c["other_lang"]}</a>
    </nav>
  </div>
</footer>
<script src="/site.js" defer></script>
</body>
</html>
'''


def build():
    guides = {}  # lang -> list of dict
    for lang in ("en", "es"):
        guides[lang] = []
        for p in sorted((SRC / lang).glob("*.md")):
            meta, lines = parse(p)
            guides[lang].append(dict(meta=meta, lines=lines))
    pages = {}  # path -> html
    sitemap = []
    for lang in ("en", "es"):
        c = L[lang]
        other = "es" if lang == "en" else "en"
        for g in guides[lang]:
            m = g["meta"]
            slug = m["slug"]
            url = f'{HOST}{c["base"]}{slug}/'
            other_url = f'{HOST}{L[other]["base"]}{m["other"]}/'
            alts = [(lang, url), (other, other_url)]
            alts.append(("x-default", url if lang == "en" else other_url))
            alts.sort(key=lambda a: (a[0] != "en", a[0]))
            # split body / FAQ
            body, faq, in_faq, cur = [], [], False, None
            for ln in g["lines"]:
                if ln.startswith("## "):
                    in_faq = ln[3:].strip() in c["faq_keys"]
                    if in_faq:
                        faq_title = ln[3:].strip(); continue
                if in_faq:
                    if ln.startswith("### "):
                        cur = [ln[4:].strip(), []]; faq.append(cur)
                    elif cur and ln.strip():
                        cur[1].append(ln.strip())
                else:
                    body.append(ln)
            ct = campaign(lang, m["short"])
            body = [links(x, ct) for x in body]
            faq = [(q, [links(x, ct) for x in a]) for q, a in faq]
            body_html = md_blocks(body, cta(lang, ct))
            faq_html = "\n".join(f'<details{" open" if i == 0 else ""}><summary>{inline(q)}</summary><p>{inline(" ".join(a))}</p></details>' for i, (q, a) in enumerate(faq))
            published = m["date"]; modified = m.get("updated", published)
            sibs = [x for x in guides[lang] if x["meta"]["slug"] != slug]
            more = "".join(f'<li><a href="{c["base"]}{x["meta"]["slug"]}/">{html.escape(x["meta"]["title"])}</a></li>' for x in sibs)
            ld = {"@context": "https://schema.org", "@graph": [
                {"@type": "Article", "headline": m["title"], "description": m["description"], "inLanguage": lang,
                 "datePublished": published, "dateModified": modified, "mainEntityOfPage": url,
                 "image": f"{HOST}/og-es.jpg" if lang == "es" else f"{HOST}/og.jpg",
                 "author": {"@type": "Organization", "name": "Frusoft", "url": HOST + "/"},
                 "publisher": {"@type": "Organization", "name": "Frusoft", "logo": {"@type": "ImageObject", "url": f"{HOST}/icon.png"}}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": c["home_crumb"], "item": HOST + c["home"]},
                    {"@type": "ListItem", "position": 2, "name": c["guides"], "item": HOST + c["base"]},
                    {"@type": "ListItem", "position": 3, "name": m["title"], "item": url}]},
            ]}
            ld["@graph"].append(APP_LD)
            if faq:
                ld["@graph"].append({"@type": "FAQPage", "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(inline(" ".join(a)))}} for q, a in faq]})
            title_tag = m["title"] + " | Dialed"
            if len(title_tag) > 65:
                title_tag = m["title"]
            page = head(lang, title_tag, m["description"], url, alts, ld) + "\n" + chrome_top(lang, other_url.replace(HOST, ""))
            page += f'''
<article class="guide wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{c["home"]}">{c["home_crumb"]}</a> › <a href="{c["base"]}">{c["guides"]}</a></nav>
  <h1>{html.escape(m["title"])}</h1>
  <p class="meta">{c["by"]} · {c["updated"]} <time datetime="{modified}">{modified}</time></p>
  <p class="lede">{html.escape(m["description"])}</p>
{body_html}
  <h2 id="faq">{faq_title}</h2>
  <div class="faq">
{faq_html}
  </div>
  {cta(lang, ct)}
  <h2>{c["more"]}</h2>
  <ul class="more">{more}<li><a href="{c["base"]}">{c["guides"]}</a></li></ul>
</article>
'''
            page += chrome_bottom(lang, other_url.replace(HOST, ""))
            pages[f'{c["base"].strip("/")}/{slug}/index.html'] = page
            sitemap.append((url, alts, modified))
        # index
        url = f'{HOST}{c["base"]}'
        other_url = f'{HOST}{L[other]["base"]}'
        alts = sorted([(lang, url), (other, other_url), ("x-default", f'{HOST}/guides/')], key=lambda a: (a[0] != "en", a[0]))
        cards = "".join(f'<li><a href="{c["base"]}{g["meta"]["slug"]}/"><b>{html.escape(g["meta"]["title"])}</b><span>{html.escape(g["meta"]["description"])}</span></a></li>' for g in guides[lang])
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["idx_h1"], "description": c["idx_desc"], "inLanguage": lang, "url": url,
              "hasPart": [{"@type": "Article", "headline": g["meta"]["title"], "url": f'{HOST}{c["base"]}{g["meta"]["slug"]}/'} for g in guides[lang]]}
        ld = {"@context": "https://schema.org", "@graph": [ld, APP_LD]}
        page = head(lang, c["idx_title"], c["idx_desc"], url, alts, ld, "website") + "\n" + chrome_top(lang, L[other]["base"])
        page += f'''
<section class="guide wrap">
  <h1>{c["idx_h1"]}</h1>
  <p class="lede">{c["idx_lede"]}</p>
  <p>{c["intro"]}</p>
  <h2>{c["quick_h"]}</h2>
  <ul>{"".join(f"<li>{x}</li>" for x in c["quick"])}</ul>
  <ul class="cards">{cards}</ul>
  {cta(lang, "guides" + ("-es" if lang == "es" else ""))}
</section>
'''
        page += chrome_bottom(lang, L[other]["base"])
        pages[f'{c["base"].strip("/")}/index.html'] = page
        sitemap.append((url, alts, max(g["meta"].get("updated", g["meta"]["date"]) for g in guides[lang])))
    for rel, content in pages.items():
        f = ROOT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    write_sitemap(sitemap)
    print(f"built {len(pages)} pages")


def write_sitemap(guide_entries):
    def entry(loc, lastmod, alts=None):
        a = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in (alts or []))
        return f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>{a}\n  </url>"
    home_alts = [("en", HOST + "/"), ("es", HOST + "/es/"), ("x-default", HOST + "/")]
    parts = [entry(HOST + "/", "2026-11-09", home_alts), entry(HOST + "/es/", "2026-11-09", home_alts)]
    parts += [entry(u, lm, a) for u, a, lm in guide_entries]
    parts += [entry(HOST + "/support/", "2026-11-03"), entry(HOST + "/privacy/", "2026-11-06")]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(parts) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(xml)


if __name__ == "__main__":
    build()
