#!/usr/bin/env python3
"""Собирает сайт 3dhouse.kg из src/site.html в папку docs/ (её раздаёт GitHub Pages).
Запуск: python3 build.py
src/site.html — исходник (одна страница со встроенными картинками и данными CRM).
"""
import re, json, base64, hashlib, html, os, shutil, datetime

SITE = "https://3dhouse.kg"
WA = "996559992306"
PHONE = "+996 559 992 306"   # WhatsApp
TEL = "996505400655"; TELF = "+996 505 400 655"   # телефон для звонков (как в 2ГИС)
ADDR = "Бишкек, ул. Туголбай Ата, 32Б"
TITLE = "3D HOUSE — 3D-принтеры Bambu Lab, пластик и сервис в Бишкеке"
TITLE = "3D-принтеры в Бишкеке — купить Bambu Lab | 3D HOUSE"
DESC = ("3D-принтеры в Бишкеке: Bambu Lab A1, A2L, P1S, X2D в наличии. Шоурум, гарантия 1 год, рассрочка, "
        "1 кг пластика в подарок, доставка по Кыргызстану за 1 день.")

root = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(root, "src", "site.html"), encoding="utf-8").read()
dist = os.path.join(root, "docs")
shutil.rmtree(dist, ignore_errors=True)
os.makedirs(os.path.join(dist, "img"))

# ---------- картинки из data: в файлы ----------
EXT = {"png": "png", "jpeg": "jpg", "jpg": "jpg", "webp": "webp", "svg+xml": "svg", "gif": "gif"}
seen = {}
def img_repl(m):
    kind, data = m.group(1), m.group(2)
    if kind not in EXT: return m.group(0)
    raw = base64.b64decode(data)
    h = hashlib.sha1(raw).hexdigest()[:12]
    name = "img/%s.%s" % (h, EXT[kind])
    if h not in seen:
        open(os.path.join(dist, name), "wb").write(raw); seen[h] = name
    return "/" + name
body = src[src.index("<body>") + 6: src.rindex("</body>")]
body = re.sub(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)", img_repl, body)

# ---------- разбор: title/link/style уходят в head ----------
m = re.match(r"\s*<title>.*?</title>\s*((?:<link[^>]*>\s*)+)<style>(.*?)</style>", body, re.S)
assert m, "неожиданное начало страницы"
links, css, rest = m.group(1), m.group(2), body[m.end():]
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)
k = rest.rindex("<script>"); markup, js = rest[:k], rest[k + 8: rest.rindex("</script>")]
open(os.path.join(dist, "app.js"), "w", encoding="utf-8").write(js)
ver = hashlib.sha1((css + js).encode()).hexdigest()[:8]

# ---------- фото для карточек без снимка ----------
PHOTOS = {"p2s": "/photos/p2s.jpg", "cr5": "/photos/cr5.jpg", "fblb": "/photos/fblb.jpg", "fblm": "/photos/fblm.jpg"}
def _photo(m):
    art = m.group(0); pid = m.group(1)
    if pid not in PHOTOS or "<img" in art: return art
    return re.sub(r'<div class="ph (?:model|spool)">.*?</div>', '<div class="ph fit"><img src="%s" alt=""></div>' % PHOTOS[pid], art, count=1, flags=re.S)
markup = re.sub(r'<article class="card[^"]*" data-pid="([^"]+)".*?</article>', _photo, markup, flags=re.S)
css += "\n.ph.fit{background:#f4f4f3}.ph.fit img{object-fit:contain;padding:9%}\n"

# ---------- SEO: один H1 на странице, подписи к картинкам ----------
_h = markup.index("<h1"); _e = markup.index("</h1>", _h) + 5
markup = markup[:_e] + re.sub(r"<h1\b([^>]*)>", r'<div class="h1x" role="heading" aria-level="2"\1>', markup[_e:]).replace("</h1>", "</div>")
markup = re.sub(r'<div class="h1x" role="heading" aria-level="2" class="([^"]*)">', r'<div class="h1x \1" role="heading" aria-level="2">', markup)
assert markup.count("<h1") == 1
css = css.replace(".pp-herotext h1", ".pp-herotext .h1x").replace(".pp-filtext h1", ".pp-filtext .h1x").replace("h1 em,", "h1 em,.h1x em,")
css += "\n.h1x{font-family:'Unbounded',sans-serif;color:var(--ink);text-wrap:balance}\n"
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)
def _alt(m):
    art = m.group(0); h3 = re.search(r"<h3>(.*?)</h3>", art, re.S)
    if not h3: return art
    nm = html.escape(html.unescape(re.sub(r"<[^>]+>", "", h3.group(1)).strip()), quote=True)
    return art.replace('alt=""', 'alt="%s"' % nm)
markup = re.sub(r'<article class="card.*?</article>', _alt, markup, flags=re.S)
markup = re.sub(r'(class="heroimg"[^>]*>\s*<img[^>]*?)alt=""', r'\1alt="3D-принтер Bambu Lab в шоуруме 3D HOUSE, Бишкек"', markup)

# ---------- скорость: размеры картинок, ленивая загрузка ----------
try:
    from PIL import Image as _PI
except Exception: _PI = None
_dim = {}
def _wh(src):
    if _PI is None or not src.startswith("/img/"): return None
    if src not in _dim:
        try: _dim[src] = _PI.open(os.path.join(dist, src.lstrip("/"))).size
        except Exception: _dim[src] = None
    return _dim[src]
_first = [True]
def _imgattrs(m):
    tag = m.group(0); src = re.search(r'src="([^"]+)"', tag)
    if not src: return tag
    add = ""
    wh = _wh(src.group(1))
    if wh and "width=" not in tag: add += ' width="%d" height="%d"' % wh
    if _first[0]:
        _first[0] = False
        if "fetchpriority" not in tag: add += ' fetchpriority="high"'
        tag = tag.replace(' loading="lazy"', "")
    else:
        if "loading=" not in tag: add += ' loading="lazy"'
        if "decoding=" not in tag: add += ' decoding="async"'
    return tag[:-1] + add + ">"
_hi = markup.index('class="heroimg"')
markup = markup[:_hi] + re.sub(r"<img\b[^>]*>", _imgattrs, markup[_hi:])
css += "\nimg{height:auto}\n"
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)

# цена и валюта через пробел — чтобы в поиске не слипалось «23 000сом»
markup = markup.replace("</b><span>сом</span>", "</b> <span>сом</span>")

# ---------- данные для страниц товаров ----------
CRM = json.loads(re.search(r"const CRM = (\{.*?\});\s*const CRM_AT", src, re.S).group(1))
FDESC = json.loads(re.search(r"const FDESC = (\{.*?\});\n", src).group(1))
cards = {}
for a in re.finditer(r'<article class="card[^"]*" data-pid="([^"]+)" data-cat="([^"]+)"[^>]*>(.*?)</article>', markup, re.S):
    pid, cat, inner = a.group(1), a.group(2), a.group(3)
    h3 = re.search(r"<h3>(.*?)</h3>", inner, re.S); d = re.search(r'<p class="d">(.*?)</p>', inner, re.S)
    im = re.search(r'<img[^>]*src="([^"]+)"', inner)
    cards[pid] = dict(cat=cat, n=html.unescape(h3.group(1).strip()) if h3 else pid,
                      d=html.unescape(d.group(1).strip()) if d else "", img=im.group(1) if im else None)
SLUG = {"a1mini": "bambu-lab-a1-mini", "a1": "bambu-lab-a1", "a1c": "bambu-lab-a1-combo", "a2l": "bambu-lab-a2l-combo",
        "a2lcn": "bambu-lab-a2l-combo-china", "p1s": "bambu-lab-p1s-combo", "p2s": "bambu-lab-p2s-combo", "x2d": "bambu-lab-x2d-combo",
        "u1": "snapmaker-u1", "cr5": "flashforge-creator-5-pro", "amsl": "bambu-lab-ams-lite", "cut": "bokorezy-pc-170", "glue": "klej-dlya-3d-pechati",
        "pla": "pla-basic", "plam": "pla-matte", "plas": "pla-silk", "petg": "petg-basic", "asa": "asa", "tpu95": "tpu-90a", "tpuams": "bambu-lab-tpu-90a",
        "fplus": "pla-plus", "fpro": "pla-pro", "ftr": "pla-translucent", "fglow": "pla-glow", "fwood": "pla-wood", "fmar": "pla-marble",
        "fgal": "pla-galaxy", "fspk": "pla-sparkle", "fpm": "petg-matte", "fps": "petg-sparkle", "fblb": "bambu-lab-pla-basic", "fblm": "bambu-lab-pla-matte"}
CATNAME = {"printers": ("3D-принтеры", "printers"), "filament": ("Пластик для 3D-печати", "filament"), "ams": ("Аксессуары", "ams")}
CATPATH = {"printers": "/3d-printery/", "filament": "/plastik-dlya-3d-pechati/"}
DEFCAT = "/aksessuary/"
nf = lambda n: "{:,}".format(n).replace(",", "\u00a0")
e = html.escape

def head(title, desc, path, ogimg=None, extra=""):
    return ("""<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s%s">
<meta property="og:type" content="website"><meta property="og:site_name" content="3D HOUSE"><meta property="og:locale" content="ru_RU">
<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s%s">%s
<meta name="theme-color" content="#FBFAF7">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="icon" href="/favicon-48.png" type="image/png" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="shortcut icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
%s<link rel="stylesheet" href="/style.css?v=%s">
%s</head>
""" % (e(title), e(desc), SITE, path, e(title), e(desc), SITE, path,
       ('\n<meta property="og:image" content="%s%s">' % (SITE, ogimg)) if ogimg else "", links, ver, extra))

STORE = {"@context": "https://schema.org", "@type": "Store", "@id": SITE + "/#store", "name": "3D HOUSE", "url": SITE + "/",
         "description": "Магазин 3D-принтеров, пластика и аксессуаров в Бишкеке: продажа, запуск, сервис и обучение.",
         "telephone": "+" + TEL, "priceRange": "200–118000 KGS", "currenciesAccepted": "KGS",
         "address": {"@type": "PostalAddress", "streetAddress": "ул. Туголбай Ата, 32Б", "addressLocality": "Бишкек", "addressCountry": "KG"},
         "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "10:00", "closes": "20:00"},
         "sameAs": ["https://instagram.com/3dhouse.kg"], "areaServed": {"@type": "Country", "name": "Кыргызстан"}}
ld = lambda o: '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>\n"
WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "3D HOUSE", "alternateName": ["3dhouse.kg", "3Д Хаус"], "inLanguage": "ru", "publisher": {"@id": SITE + "/#store"}}

# ---------- главная ----------
hero = re.search(r'class="heroimg"[^>]*>\s*<img[^>]*src="([^"]+)"', markup)

# ---------- страницы товаров ----------
PCSS = """
.pg{max-width:1080px;margin:0 auto;padding:28px 22px 80px}
.pg .crumbs{font-size:13.5px;color:var(--mut);margin:0 0 26px}.pg .crumbs a{color:var(--mut);text-decoration:underline;text-underline-offset:3px}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:start}
.pgimg{border-radius:26px;background:var(--alt);aspect-ratio:1/1;display:grid;place-items:center;overflow:hidden}
.pgimg img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.pgimg.ph-none span{font-family:'Unbounded',sans-serif;font-weight:900;font-size:44px;color:#c9c6bf}
.pg h1{font-size:clamp(26px,3.4vw,40px);line-height:1.12;font-weight:700;margin:0 0 14px}
.pg .lead{font-size:17px;color:var(--mut);line-height:1.6;margin:0 0 22px}
.pgprice{font-family:'Unbounded',sans-serif;font-weight:800;font-size:34px;letter-spacing:-.02em}.pgprice small{font-family:'Manrope',sans-serif;font-size:15px;font-weight:700;color:var(--mut)}
.pgstk{display:inline-block;margin:10px 0 24px;font-size:13px;font-weight:700;border-radius:999px;padding:5px 12px;background:#E8F6EE;color:#1FA35C}
.pgstk.out{background:var(--alt);color:#9a9a9e}
.pgbtns{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:28px}
.pg h2{font-size:20px;font-weight:700;margin:34px 0 12px}
.pg ul{margin:0;padding-left:20px;color:#444;line-height:1.7}.pg p{line-height:1.65;color:#444}
.pgcols{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.pgcols li{font-size:13.5px;font-weight:600;background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 13px}
.pgcols li.out{color:#b0b0b3;text-decoration:line-through}
.pgspec{width:100%;border-collapse:collapse;font-size:15px;max-width:760px}.pgspec th,.pgspec td{text-align:left;padding:11px 0;border-bottom:1px solid var(--line2);vertical-align:top;line-height:1.5}
.pgspec th{width:38%;font-weight:600;color:var(--mut);padding-right:16px}.pgspec td{font-weight:600}
.pgfeat{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px}.pgfeat img{width:100%;height:auto;border-radius:18px;background:var(--alt)}
.pgfeat h3{font-size:16px;margin:12px 0 4px}.pgfeat p{margin:0;font-size:14.5px}
.pgmore{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.pgmore a{display:block;background:#fff;border:1px solid var(--line2);border-radius:18px;padding:16px 18px;font-weight:700}
.pgmore a span{display:block;font-weight:600;font-size:13.5px;color:var(--mut);margin-top:4px}
@media(max-width:760px){.pgrid{grid-template-columns:1fr;gap:22px}.pg{padding:18px 16px 60px}}
@media(max-width:760px){header .hd{display:flex;flex-wrap:wrap;height:auto;padding:10px 16px 6px;gap:4px 12px;align-items:center}
header .hd .logo{order:1}header .hd>span{order:2}header .hd .phone{order:3;display:block;font-size:13px}
header .hd .nav{order:4;width:100%;overflow-x:auto;white-space:nowrap;margin:0 -6px;scrollbar-width:none}header .hd .nav a{padding:6px 8px;font-size:13.5px}}
"""
HDR = ('<header><div class="wrap hd"><a class="logo" href="/" aria-label="3D HOUSE"><span class="wm2"><b>3D</b> HOUSE</span></a>'
       '<nav class="nav" style="display:flex"><a href="/3d-printery/">Принтеры</a><a href="/plastik-dlya-3d-pechati/">Пластик</a><a href="/aksessuary/">Аксессуары</a><a href="/voprosy/">Вопросы</a><a href="/kontakty/">Контакты</a></nav>'
       '<span style="flex:1"></span><a class="phone" href="tel:+%s">%s</a></div></header>' % (TEL, TELF))
FTR = ('<footer><div class="wrap fg"><div><a class="logo" href="/"><span class="wm2"><b>3D</b> HOUSE</span></a><p>Дом для 3D-печати: принтеры, пластик, сервис и обучение.</p></div>'
       '<div><b>Шоурум</b><p>%s<br>ежедневно 10:00–20:00</p></div><div><b>Каталог</b><p><a href="/3d-printery/">3D-принтеры</a> · <a href="/plastik-dlya-3d-pechati/">Пластик</a> · <a href="/aksessuary/">Аксессуары</a><br><a href="/voprosy/">Вопросы и ответы</a> · <a href="/kontakty/">Контакты</a></p></div>'
       '<div><b>Связь</b><p><a href="https://wa.me/%s">WhatsApp %s</a><br><a href="https://instagram.com/3dhouse.kg">Instagram @3dhouse.kg</a></p></div></div></footer>' % (ADDR, WA, PHONE))

# ---------- подробности из карточек-«историй» главной (шаблоны pp-*) — на страницы товаров ----------
DET_ALIAS = {"a1c": "a1", "a2lcn": "a2l"}
def _tx(x): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))).strip()
def detail(pid, name, fil):
    m = re.search(r'<template id="pp-%s">(.*?)</template>' % re.escape(DET_ALIAS.get(pid, pid)), markup, re.S)
    if not m: return ""
    g = lambda cls, sec: [_tx(v) for v in re.findall(r'<(?:p|h2|div)\b[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>(.*?)</(?:p|h2|div)>' % cls, sec, re.S)]
    rows, feats, uses = [], [], ""
    for cls, sec in re.findall(r'<section class="([^"]*)"[^>]*>(.*?)</section>', m.group(1), re.S):
        img = re.search(r'<img[^>]*src="([^"]+)"', sec); img = img.group(1) if img else None
        if cls.startswith("pp-stat"):
            eb, sub, note = g("eyebrow", sec), g("pp-sub", sec), g("pp-note", sec)
            num = re.search(r'data-n="([\d.]+)"', sec); unit = g("unit", sec) if False else [_tx(v) for v in re.findall(r'<span class="unit">(.*?)</span>', sec)]
            if not eb or not sub: continue
            val = sub[0]
            if num and unit and num.group(1) not in val.replace(" ", "").replace(" ", ""): val = "%s %s · %s" % (num.group(1), unit[0], val)
            rows.append((eb[0], val)); 
            if note: feats.append((eb[0], note[0], img))
        elif cls.startswith("pp-feat"):
            h2 = re.search(r"<h2[^>]*>(.*?)</h2>", sec, re.S); ps = [_tx(v) for v in re.findall(r'<p class="rv">(.*?)</p>', sec, re.S)]
            eb = g("eyebrow", sec)
            if h2 and ps:
                feats.append(((eb[0] + ": " if eb else "") + _tx(h2.group(1)), ps[0], img))
        elif cls == "pp-mat":
            chips = [_tx(v) for v in re.findall(r"<span[^>]*>(.*?)</span>", sec, re.S)]
            ps = [_tx(v) for v in re.findall(r'<p class="rv">(.*?)</p>', sec, re.S)]
            if chips: rows.append(("Материалы", ", ".join(chips)))
            for t in (ps[0].rstrip(".").split(",") if ps else []):
                t = t.strip(); 
                if t.lower().startswith("сопло"): rows.append(("Температура сопла", t[5:].strip()))
                elif t.lower().startswith("стол"): rows.append(("Температура стола", t[4:].strip()))
        elif cls == "pp-uses" and fil:
            li = [_tx(v) for v in re.findall(r"<li[^>]*>(.*?)</li>", sec, re.S)] or [_tx(v) for v in re.findall(r"<span[^>]*>(.*?)</span>", sec, re.S)]
            ps = [_tx(v) for v in re.findall(r"<p(?![^>]*eyebrow)[^>]*>(.*?)</p>", sec, re.S)]
            ps = [x for x in ps if len(x) > 60]
            uses = ("<h2>Что печатают из %s</h2>" % e(name)) + ("<ul>%s</ul>" % "".join("<li>%s</li>" % e(x) for x in li) if li else "") + "".join("<p>%s</p>" % e(x) for x in ps[:1])
        elif cls == "pp-specs" and fil:
            cells = [_tx(v) for v in re.findall(r"<(?:span|b|small|i|em|dt|dd)\b[^>]*>(.*?)</(?:span|b|small|i|em|dt|dd)>", sec, re.S)]
            cells = [x for x in cells if x]
            for a, b_ in zip(cells[0::2], cells[1::2]): rows.append((a, b_))
            warn = [_tx(v) for v in re.findall(r'<p(?![^>]*eyebrow)[^>]*>(.*?)</p>', sec, re.S)]
            if warn and warn[-1]: rows.append(("Ограничения", warn[-1]))
    out = uses
    if rows:
        seen = set(); rows = [x for x in rows if not (x[0] in seen or seen.add(x[0]))]
        out += ("<h2>%s</h2>" % ("Режим печати" if fil else "Характеристики %s" % e(name))) + '<table class="pgspec">' + "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(a), e(b_)) for a, b_ in rows) + "</table>"
    if feats and not fil:
        out += "<h2>Чем хорош %s</h2>" % e(name) + '<div class="pgfeat">' + "".join(
            '<div>%s<h3>%s</h3><p>%s</p></div>' % ('<img src="%s" alt="%s — %s" width="440" height="440" loading="lazy" decoding="async">' % (im, e(name), e(t[:1].lower() + t[1:] if t[1:2].islower() else t)) if im else "", e(t), e(p_)) for t, p_, im in feats) + "</div>"
    return out


pages = []
for pid, k in CRM.items():
    if pid not in SLUG or pid not in cards: continue
    c = cards[pid]; name = k.get("n") or c["n"]; catn, anchor = CATNAME.get(c["cat"], ("Каталог", "printers"))
    path = "/catalog/%s/" % SLUG[pid]; fil = bool(k.get("v")); price = k["p"]; q = k["q"]
    kind = "пластик для 3D-печати" if fil else ("3D-принтер" if c["cat"] == "printers" else "")
    h1 = ("%s — %s в Бишкеке" % (name, kind)) if kind else ("%s в Бишкеке" % name)
    if fil: title = "Пластик %s — купить в Бишкеке от %s сом | 3D HOUSE" % (name, nf(price))
    elif c["cat"] == "printers": title = "3D-принтер %s — купить в Бишкеке, %s сом" % (name, nf(price))
    else: title = "%s — купить в Бишкеке, %s сом | 3D HOUSE" % (name, nf(price))
    lead = FDESC.get(pid) or (k.get("d") or c["d"])
    desc = "%s в Бишкеке: %s%s сом, %s. %s Шоурум 3D HOUSE, доставка по Кыргызстану за 1 день." % (
        name, "от " if fil else "", nf(price), "в наличии" if q > 0 else "под заказ", lead.rstrip(".") + ".")
    if len(desc) > 160:
        desc = "%s в Бишкеке: %s%s сом, %s. %s" % (name, "от " if fil else "", nf(price), "в наличии" if q > 0 else "под заказ", lead.rstrip(".") + ".")
    if len(desc) > 160: desc = desc[:157].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    wa = "https://wa.me/%s?text=%s" % (WA, __import__("urllib.parse").parse.quote("Здравствуйте! Интересует %s (%s сом)." % (name, nf(price))))
    b = ['<div class="pgimg%s">%s</div>' % ("" if c["img"] else " ph-none", '<img src="%s" alt="%s" width="600" height="600">' % (c["img"], e(name)) if c["img"] else "<span>%s</span>" % e(name.split()[-1]))]
    r = ["<h1>%s</h1>" % e(h1), '<p class="lead">%s</p>' % e(lead),
         '<div class="pgprice">%s%s <small>сом</small></div>' % ("<small>от</small> " if fil else "", nf(price)),
         '<div><span class="pgstk%s">%s</span></div>' % ("" if q > 0 else " out", ("В наличии %d шт" % q) if q > 0 else "Нет в наличии — привезём под заказ"),
         '<div class="pgbtns"><a class="btn" href="%s" target="_blank" rel="noopener">Заказать в WhatsApp</a><a class="btn ghost" href="/#%s">%s</a></div>' % (wa, anchor, "Выбрать цвет в каталоге" if fil else "Открыть каталог")]
    if fil:
        ws = []
        for x in k["v"]:
            if x[5] not in ws: ws.append(x[5])
        for w in ws:
            vs = [x for x in k["v"] if x[5] == w]
            r.append("<h2>Цвета%s — %s сом</h2>" % ((" · " + w) if w else "", nf(vs[0][3])))
            r.append('<ul class="pgcols">' + "".join('<li%s>%s</li>' % ("" if x[4] > 0 else ' class="out"', e(x[1])) for x in vs) + "</ul>")
    else:
        if c["d"] or k.get("d"): r.append("<h2>Коротко</h2><ul>" + "".join("<li>%s</li>" % e(t.strip()) for t in (k.get("d") or c["d"]).split("·") if t.strip()) + "</ul>")
    if c["cat"] == "printers":
        r.append("<h2>Что входит в покупку</h2><ul><li>1 кг пластика в подарок</li><li>Запуск и первая печать вместе с нами</li><li>Гарантия 1 год, сервис в Бишкеке</li><li>Рассрочка — уточняйте условия в WhatsApp</li></ul>")
    r.append("<h2>Доставка и самовывоз</h2><p>Самовывоз из шоурума: %s, ежедневно 10:00–20:00. В регионы Кыргызстана отправляем через «Ылдам Экспресс» — доставка занимает 1 день.</p>" % ADDR)
    prod = {"@context": "https://schema.org", "@type": "Product", "name": name, "description": lead, "brand": {"@type": "Brand", "name": "Bambu Lab" if "Bambu" in name else ("Snapmaker" if "Snapmaker" in name else ("FlashForge" if "FlashForge" in name else "3D HOUSE"))},
            "offers": {"@type": "AggregateOffer" if fil else "Offer", "priceCurrency": "KGS", "availability": "https://schema.org/InStock" if q > 0 else "https://schema.org/PreOrder", "url": SITE + path, "seller": {"@id": SITE + "/#store"}}}
    if fil: prod["offers"].update(lowPrice=price, highPrice=max(x[3] for x in k["v"]), offerCount=len(k["v"]))
    else: prod["offers"]["price"] = price
    if c["img"]: prod["image"] = SITE + c["img"]
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "3D HOUSE", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": catn, "item": SITE + CATPATH.get(c["cat"], DEFCAT)}, {"@type": "ListItem", "position": 3, "name": name}]}
    pages.append((pid, path, name, price, c["cat"], fil, title, desc, c["img"], b, r, ld(prod) + ld(crumbs), catn, anchor))

for pid, path, name, price, cat, fil, title, desc, img, b, r, lds, catn, anchor in pages:
    more = [p for p in pages if p[4] == cat and p[0] != pid][:8]
    out = (head(title, desc, path, img, "<style>%s</style>\n%s" % (PCSS, lds)) + "<body>\n" + HDR +
           '<main class="pg"><p class="crumbs"><a href="/">Главная</a> / <a href="%s">%s</a> / %s</p><div class="pgrid">%s<div>%s</div></div>' % (CATPATH.get(cat, DEFCAT), e(catn), e(name), "".join(b), "".join(r)) +
           detail(pid, name, fil) +
           ('<h2>Ещё в разделе «%s»</h2><div class="pgmore">%s</div>' % (e(catn), "".join('<a href="%s">%s<span>%s%s сом</span></a>' % (p[1], e(p[2]), "от " if p[5] else "", nf(p[3])) for p in more)) if more else "") +
           "</main>" + FTR + "</body></html>\n")
    d = os.path.join(dist, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)


# ---------- разделы, вопросы, контакты ----------
extra = []
def page(path, title, desc, inner, lds="", img=None):
    out = head(title, desc, path, img, "<style>%s%s</style>\n%s" % (PCSS, XCSS, lds)) + "<body>\n" + HDR + '<main class="pg">' + inner + "</main>" + FTR + "</body></html>\n"
    d = os.path.join(dist, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out); extra.append(path)
XCSS = """
.clist{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin-top:8px}
.clist a{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line2);border-radius:20px;padding:12px 12px 16px;font-weight:700}
.clist a i{display:block;aspect-ratio:1/1;border-radius:14px;background:var(--alt);overflow:hidden;margin-bottom:12px}
.clist a i img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.clist a span{font-weight:600;font-size:13.5px;color:var(--mut);margin-top:4px}
.clist a em{font-style:normal;font-family:'Unbounded',sans-serif;font-weight:800;font-size:17px;margin-top:10px}
.clist a em small{font-family:'Manrope',sans-serif;font-size:12.5px;font-weight:700;color:var(--mut)}
.faq details{background:#fff;border:1px solid var(--line2);border-radius:18px;padding:16px 20px;margin-bottom:10px}
.faq summary{font-weight:700;font-size:16.5px;cursor:pointer}.faq details p{margin:10px 0 0}
.pg .lead{max-width:70ch}
@media(max-width:760px){.clist{grid-template-columns:1fr 1fr;gap:10px}.clist a{padding:8px 8px 12px;border-radius:16px;font-size:14px}}
"""
def clist(ps):
    return '<div class="clist">' + "".join(
        '<a href="%s">%s%s<span>%s</span><em>%s%s <small>сом</small></em></a>' % (
            p[1], ('<i><img src="%s" alt="%s" loading="lazy" width="300" height="300"></i>' % (p[8], e(p[2]))) if p[8] else "", e(p[2]),
            "в наличии" if CRM[p[0]]["q"] > 0 else "под заказ", "<small>от</small> " if p[5] else "", nf(p[3])) for p in ps) + "</div>"
def itemlist(ps):
    return ld({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": p[2], "url": SITE + p[1]} for i, p in enumerate(ps)]})
def crumb2(name, path):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "3D HOUSE", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]})
PR = [p for p in pages if p[4] == "printers"]; FI = [p for p in pages if p[4] == "filament"]; AC = [p for p in pages if p[4] not in ("printers", "filament")]
kg = [p[3] for p in FI if any(x[5] == "1 кг" and x[3] == p[3] for x in CRM[p[0]].get("v", []))]
FILMIN = min(kg) if kg else min(p[3] for p in FI)
SHIP = "<h2>Доставка и самовывоз</h2><p>Самовывоз из шоурума: %s, ежедневно 10:00–20:00. В регионы Кыргызстана отправляем через «Ылдам Экспресс» — доставка занимает 1 день.</p>" % ADDR
WABTN = '<div class="pgbtns" style="margin-top:26px"><a class="btn" href="https://wa.me/%s" target="_blank" rel="noopener">Написать в WhatsApp</a><a class="btn ghost" href="/">Весь каталог</a></div>' % WA
if PR:
    page("/3d-printery/", "Купить 3D-принтер в Бишкеке — цены и наличие, от %s сом | 3D HOUSE" % nf(min(p[3] for p in PR)),
         "Цены на 3D-принтеры в Бишкеке: %d моделей Bambu Lab, Snapmaker и FlashForge от %s сом. Наличие, гарантия 1 год, рассрочка, доставка по Кыргызстану." % (len(PR), nf(min(p[3] for p in PR))),
         '<p class="crumbs"><a href="/">Главная</a> / 3D-принтеры</p><h1>Купить 3D-принтер в Бишкеке: цены и наличие</h1>'
         '<p class="lead">%d моделей в шоуруме 3D HOUSE — от %s сом. К каждому принтеру дарим 1 кг пластика, настраиваем и показываем, как печатать. Гарантия 1 год, сервис в Бишкеке.</p>' % (len(PR), nf(min(p[3] for p in PR))) +
         clist(PR) +
         "<h2>Как выбрать 3D-принтер</h2><p>Новичку и для ребёнка подойдёт простая открытая модель — Bambu Lab A1 или A1 mini. Для многоцветной печати берите комплект Combo: в нём есть система подачи нескольких катушек. Для бизнеса и инженерных пластиков — закрытые модели P1S и X2D.</p>"
         "<h2>Китайская и глобальная версия</h2><p>Китайской версии принтера нужны компьютер и Wi-Fi — к телефону и планшету она не подключается. Глобальная (EU) версия подключается к телефону. Версия указана в названии модели.</p>" + SHIP + WABTN,
         itemlist(PR) + crumb2("3D-принтеры", "/3d-printery/"), PR[0][8])
if FI:
    page("/plastik-dlya-3d-pechati/", "Пластик для 3D-печати в Бишкеке — PLA, PETG от %s сом | 3D HOUSE" % nf(FILMIN),
         "Пластик для 3D-принтера в Бишкеке: PLA, PETG, TPU, ASA — %d серий, от %s сом за катушку 1 кг. Наличие по цветам, самовывоз и доставка по Кыргызстану за 1 день." % (len(FI), nf(FILMIN)),
         '<p class="crumbs"><a href="/">Главная</a> / Пластик для 3D-печати</p><h1>Пластик для 3D-печати в Бишкеке</h1>'
         '<p class="lead">%d серий филамента: PLA, PETG, TPU и ASA. Катушка 1 кг — от %s сом. На странице каждой серии — цвета и наличие.</p>' % (len(FI), nf(FILMIN)) +
         clist(FI) +
         "<h2>Какой пластик выбрать</h2><p>PLA — универсальный: сувениры, прототипы, игрушки. PETG прочнее PLA и не боится улицы. TPU — гибкий: чехлы, прокладки, ремешки. ASA не выгорает на солнце. Не уверены — напишите, что хотите печатать, подскажем.</p>" + SHIP + WABTN,
         itemlist(FI) + crumb2("Пластик для 3D-печати", "/plastik-dlya-3d-pechati/"), FI[0][8])
if AC:
    page("/aksessuary/", "Аксессуары для 3D-принтера в Бишкеке | 3D HOUSE",
         "Аксессуары для 3D-печати в Бишкеке: %s. Самовывоз из шоурума и доставка по Кыргызстану." % ", ".join(p[2] for p in AC),
         '<p class="crumbs"><a href="/">Главная</a> / Аксессуары</p><h1>Аксессуары для 3D-принтера в Бишкеке</h1>'
         '<p class="lead">То, что пригодится при печати: система подачи пластика, инструмент и расходники.</p>' + clist(AC) + SHIP + WABTN,
         itemlist(AC) + crumb2("Аксессуары", "/aksessuary/"), AC[0][8])
FAQ = [
 ("Где купить 3D-принтер в Бишкеке?", "В шоуруме 3D HOUSE: %s, ежедневно с 10:00 до 20:00. Принтер можно посмотреть вживую до покупки." % ADDR),
 ("Какой 3D-принтер выбрать новичку?", "Простую открытую модель — Bambu Lab A1 или A1 mini. Для многоцветной печати — комплект Combo. Для бизнеса и инженерных пластиков — закрытые модели P1S и X2D."),
 ("Чем китайская версия принтера отличается от глобальной?", "Китайской версии нужны компьютер и Wi-Fi — к телефону и планшету она не подключается. Глобальная (EU) версия подключается к телефону."),
 ("Сколько стоит 3D-принтер?", "От %s сом. Актуальные цены и наличие — на страницах моделей." % nf(min(p[3] for p in PR)) if PR else ""),
 ("Сколько стоит пластик для 3D-печати?", "От %s сом за катушку 1 кг. К принтеру дарим 1 кг пластика." % nf(FILMIN)),
 ("Есть ли гарантия?", "Да, гарантия 1 год, сервис в Бишкеке. При покупке настраиваем принтер и показываем, как печатать."),
 ("Можно ли купить в рассрочку?", "Да, есть рассрочка на 3 месяца через М+ (Мбанк), Пайда и Зеро. Точные условия уточняйте в WhatsApp."),
 ("Доставляете ли вы по Кыргызстану?", "Да, в регионы отправляем через курьерскую службу «Ылдам Экспресс». Доставка занимает 1 день и стоит около 1 000–1 500 сом, точная сумма зависит от города."),
 ("Что делать, если нужной модели нет в наличии?", "Привезём под заказ в течение 4 дней, возможно раньше."),
 ("Какой пластик выбрать?", "PLA — универсальный, для сувениров и прототипов. PETG прочнее и не боится улицы. TPU — гибкий. ASA не выгорает на солнце."),
]
FAQ = [f for f in FAQ if f[1]]
page("/voprosy/", "Вопросы и ответы о 3D-принтерах и пластике | 3D HOUSE, Бишкек",
     "Где купить 3D-принтер в Бишкеке, какую модель выбрать, сколько стоит пластик, гарантия, рассрочка и доставка по Кыргызстану — ответы магазина 3D HOUSE.",
     '<p class="crumbs"><a href="/">Главная</a> / Вопросы и ответы</p><h1>Вопросы и ответы</h1><div class="faq" style="margin-top:22px">' +
     "".join("<details%s><summary>%s</summary><p>%s</p></details>" % (" open" if i < 3 else "", e(q), e(a)) for i, (q, a) in enumerate(FAQ)) + "</div>" + WABTN,
     ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}) + crumb2("Вопросы и ответы", "/voprosy/"))
page("/kontakty/", "Контакты и адрес шоурума 3D HOUSE в Бишкеке",
     "Шоурум 3D-принтеров 3D HOUSE: %s. Ежедневно 10:00–20:00. Телефон %s, WhatsApp %s." % (ADDR, TELF, PHONE),
     '<p class="crumbs"><a href="/">Главная</a> / Контакты</p><h1>Контакты 3D HOUSE</h1>'
     '<p class="lead">Шоурум 3D-принтеров и пластика в Бишкеке. Приезжайте посмотреть принтеры вживую.</p>'
     "<h2>Адрес</h2><p>%s</p><h2>Часы работы</h2><p>Ежедневно, 10:00–20:00</p>"
     '<h2>Телефон</h2><p><a href="tel:+%s">%s</a></p><h2>WhatsApp</h2><p><a href="https://wa.me/%s">%s — написать</a></p>'
     '<h2>Instagram</h2><p><a href="https://instagram.com/3dhouse.kg">@3dhouse.kg</a></p>' % (ADDR, TEL, TELF, WA, PHONE) + SHIP,
     ld(STORE) + crumb2("Контакты", "/kontakty/"))

# ---------- главная (со ссылками на все страницы) ----------
instock = [p for p in PR if CRM[p[0]]["q"] > 0]
SEOTXT = ('<section class="wrap" style="padding-top:72px"><div style="max-width:860px">'
          '<h2 style="font-size:clamp(22px,2.6vw,30px);margin:0 0 16px">3D-принтеры в Бишкеке — шоурум 3D HOUSE</h2>'
          '<p style="line-height:1.7;color:#444;margin:0 0 12px">3D HOUSE — магазин 3D-принтеров в Бишкеке с шоурумом на %s. '
          'В каталоге %d моделей от %s сом, %d из них сейчас в наличии: %s. Принтер можно посмотреть в работе до покупки.</p>'
          '<p style="line-height:1.7;color:#444;margin:0 0 12px">К каждому 3D-принтеру дарим 1 кг пластика, настраиваем и показываем, как печатать. '
          'Гарантия 1 год, сервис в Бишкеке, рассрочка на 3 месяца. Если нужной модели нет — привезём под заказ в течение 4 дней. '
          'В Ош, Джалал-Абад, Каракол и другие города Кыргызстана отправляем курьерской службой за 1 день.</p>'
          '<p style="line-height:1.7;color:#444;margin:0">Не знаете, какой 3Д-принтер выбрать? Новичку подойдёт Bambu Lab A1, для многоцветной печати — комплект Combo, '
          'для бизнеса и инженерных пластиков — закрытые P1S и X2D. <a href="/3d-printery/" style="text-decoration:underline;text-underline-offset:3px">Цены на все 3D-принтеры</a> · '
          '<a href="/plastik-dlya-3d-pechati/" style="text-decoration:underline;text-underline-offset:3px">пластик для 3D-печати</a> · '
          '<a href="/voprosy/" style="text-decoration:underline;text-underline-offset:3px">вопросы и ответы</a></p></div></section>\n') % (
          ADDR.replace("Бишкек, ", ""), len(PR), nf(min(p[3] for p in PR)), len(instock),
          ", ".join('<a href="%s" style="text-decoration:underline;text-underline-offset:3px">%s</a> — %s сом' % (p[1], e(p[2]), nf(p[3])) for p in instock))
SMAP = ('<section class="wrap" style="padding-top:56px"><h2 style="font-size:22px;margin:0 0 16px">Каталог 3D HOUSE</h2>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:22px;font-size:14.5px;line-height:1.9">' +
        "".join('<div><a href="%s" style="font-weight:800">%s</a><br>%s</div>' % (cp, cn, "<br>".join('<a href="%s" style="color:var(--mut)">%s</a>' % (p[1], e(p[2])) for p in ps))
                for cp, cn, ps in (("/3d-printery/", "3D-принтеры в Бишкеке", PR), ("/plastik-dlya-3d-pechati/", "Пластик для 3D-печати", FI), ("/aksessuary/", "Аксессуары", AC)) if ps) +
        '<div><b>Покупателю</b><br><a href="/voprosy/" style="color:var(--mut)">Вопросы и ответы</a><br><a href="/kontakty/" style="color:var(--mut)">Контакты и адрес шоурума</a></div></div></section>\n')
# ---------- витрина принтеров: активная модель раскрывается в панель (SHOWCASE v2) ----------
SH = {  # pid: (подпись, код-водяной знак, [факты])
 "a1":    ("Для старта", "A1", ["Стол 256 × 256 × 256 мм", "Китайская версия", "Нужен компьютер и Wi-Fi"]),
 "a1c":   ("Многоцветная печать", "A1", ["Комплект Combo", "Версия EU", "Подключается к телефону"]),
 "a2l":   ("XL-формат", "A2L", ["Стол 330 × 320 × 325 мм", "Комплект Combo", "Версия EU"]),
 "a2lcn": ("XL-формат", "A2L", ["Стол 330 × 320 × 325 мм", "Комплект Combo", "Китайская версия"]),
 "p1s":   ("Закрытый корпус", "P1S", ["Печатает ABS, ASA, PA-CF", "Комплект Combo", "Версия EU"]),
 "p2s":   ("Закрытый корпус", "P2S", ["AMS в комплекте", "Комплект Combo", "Версия EU"]),
 "x2d":   ("Для бизнеса", "X2D", ["Инженерные пластики", "Комплект Combo с AMS", "Версия EU"]),
 "u1":    ("Многоцветный", "U1", ["Четыре печатающие головы", "Многоцветная печать"]),
 "a1mini":("Компактный", "A1", ["Стол 180 × 180 × 180 мм", "Китайская версия", "Нужен компьютер и Wi-Fi"]),
}
SH_IMG = {"a2lcn": "a2l"}
sh = [p for p in PR if p[0] in SH and os.path.exists(os.path.join(root, "static", "cut", SH_IMG.get(p[0], p[0]) + ".webp"))]
sh.sort(key=lambda p: (CRM[p[0]]["q"] <= 0, p[3]))
if len(sh) >= 3:
    def _shi(p):
        q = CRM[p[0]]["q"]; tag, wm, facts = SH[p[0]]
        im = _PI.open(os.path.join(root, "static", "cut", SH_IMG.get(p[0], p[0]) + ".webp")).size if _PI else (400, 400)
        return ('<div class="shw-it" data-pid="%s" data-url="%s" tabindex="0" role="group" aria-label="%s">'
                '<div class="shw-card"><span class="shw-wm" aria-hidden="true">%s</span><span class="shw-tag">%s</span><b>%s</b>'
                '<ul class="shw-sp">%s</ul>'
                '<div class="shw-bot"><span class="shw-pr">%s <small>сом</small><i class="%s">%s</i></span>'
                '<span class="shw-btns"><button type="button" class="shw-more">Подробнее</button>'
                '<button type="button" class="shw-add" aria-label="%s">%s</button></span></div></div>'
                '<span class="shw-fl"><img class="shw-img" src="/cut/%s.webp" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></span>'
                '<span class="shw-nm">%s<small>%s сом</small></span></div>') % (
            p[0], p[1], e(p[2]), e(wm), e(tag), e(p[2]), "".join("<li>%s</li>" % e(f) for f in facts + ["Гарантия 1 год"]),
            nf(p[3]), "in" if q > 0 else "out", "в наличии" if q > 0 else "под заказ · 4 дня",
            "В корзину" if q > 0 else "Подробнее", "+" if q > 0 else "→", SH_IMG.get(p[0], p[0]), e(p[2]), im[0], im[1], e(p[2]), nf(p[3]))
    SHOW = ('<section class="shw" id="showcase"><div class="shw-head"><div><h2>Выберите свой принтер</h2>'
            '<p><span class="shw-h1">Наведите на модель — она раскроется</span><span class="shw-h2">Листайте — модель раскроется</span></p></div>'
            '<div class="shw-nav"><button type="button" class="shw-prev" aria-label="Предыдущая модель">←</button><span class="shw-cnt"><b>1</b> / %d</span>'
            '<button type="button" class="shw-next" aria-label="Следующая модель">→</button></div></div>'
            '<div class="shw-prog" aria-hidden="true">%s</div><div class="shw-row">%s</div></section>\n') % (len(sh), "<i><b></b></i>" * len(sh), "".join(_shi(p) for p in sh))
    css += """
.shw{padding-top:88px}.shw-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:6px}
.shw-head h2{font-size:clamp(26px,3vw,40px);letter-spacing:-.03em;margin:0 0 8px}.shw-head p{margin:0;color:var(--mut);font-size:15px}
.shw-h2{display:none}@media (hover:none){.shw-h1{display:none}.shw-h2{display:inline}}
.shw-nav{display:flex;align-items:center;gap:10px}.shw-nav button{width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:#fff;font-size:18px;cursor:pointer;transition:background .2s,color .2s,border-color .2s}
.shw-nav button:hover{background:#1D1D1F;color:#fff;border-color:#1D1D1F}.shw-cnt{font-size:13.5px;font-weight:700;color:var(--mut);min-width:44px;text-align:center}.shw-cnt b{color:var(--ink)}
.shw-row{display:flex;gap:6px;overflow-x:auto;padding:30px 4px 40px;margin:0 -4px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.shw-row::-webkit-scrollbar{display:none}
.shw-it{position:relative;flex:0 0 214px;height:430px;cursor:pointer;outline:0;-webkit-tap-highlight-color:transparent;transition:flex-basis .6s cubic-bezier(.2,.8,.2,1)}
.shw-card{position:absolute;inset:0;border-radius:32px;background:radial-gradient(120% 90% at 85% 30%,rgba(255,106,19,.22),transparent 55%),linear-gradient(165deg,#2B2B2F,#17171A);color:#fff;padding:28px 28px 24px;
 display:flex;flex-direction:column;overflow:hidden;opacity:0;transform:translateY(46px) scale(.9);transition:opacity .4s ease,transform .6s cubic-bezier(.2,.8,.2,1);box-shadow:0 36px 64px -30px rgba(29,29,31,.6);pointer-events:none}
.shw-wm{position:absolute;right:-14px;bottom:-46px;font-family:'Unbounded',sans-serif;font-weight:800;font-size:190px;line-height:1;letter-spacing:-.06em;color:rgba(255,255,255,.055);white-space:nowrap;pointer-events:none;
 transform:translateX(40px);transition:transform .9s cubic-bezier(.2,.8,.2,1)}
.shw-tag{font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#FF8A3D;position:relative}
.shw-card b{font-family:'Unbounded',sans-serif;font-weight:700;font-size:21px;line-height:1.18;letter-spacing:-.03em;margin-top:10px;max-width:232px;position:relative}
.shw-sp{list-style:none;margin:18px 0 0;padding:0;display:flex;flex-direction:column;gap:9px;max-width:232px;position:relative}
.shw-sp li{font-size:14px;font-weight:600;color:rgba(255,255,255,.82);padding-left:20px;position:relative;opacity:0;transform:translateX(-14px);transition:opacity .45s ease,transform .5s cubic-bezier(.2,.8,.2,1)}
.shw-sp li::before{content:"";position:absolute;left:0;top:7px;width:7px;height:7px;border-radius:50%;background:#FF6A13}
.shw-bot{margin-top:auto;display:flex;align-items:flex-end;justify-content:space-between;gap:12px;position:relative}
.shw-pr{font-family:'Unbounded',sans-serif;font-weight:700;font-size:26px;letter-spacing:-.03em;line-height:1.1;white-space:nowrap}
.shw-pr small{font-family:'Manrope',sans-serif;font-size:13px;font-weight:700;opacity:.7}
.shw-pr i{display:block;font-style:normal;font-family:'Manrope',sans-serif;font-size:12.5px;font-weight:700;margin-top:6px;letter-spacing:0}.shw-pr i.in{color:#7ED7A5}.shw-pr i.out{color:#c9c9cf}
.shw-btns{display:flex;gap:8px;align-items:center}
.shw-more{height:48px;padding:0 18px;border-radius:16px;border:1px solid rgba(255,255,255,.22);background:transparent;color:#fff;font:800 13.5px 'Manrope',sans-serif;cursor:pointer;transition:background .2s}
.shw-more:hover{background:rgba(255,255,255,.1)}
.shw-add{flex:none;width:48px;height:48px;border-radius:16px;border:0;background:#FF6A13;color:#fff;font-size:26px;font-weight:500;line-height:1;cursor:pointer;display:grid;place-items:center;transition:transform .2s ease,background .2s ease}
.shw-add:hover{transform:scale(1.08);background:#ff7d30}
.shw-fl{position:absolute;left:50%;top:112px;width:170px;height:170px;transform:translate(-50%,0);z-index:2;pointer-events:none;
 transition:left .6s cubic-bezier(.2,.8,.2,1),top .6s cubic-bezier(.2,.8,.2,1),width .6s cubic-bezier(.2,.8,.2,1),height .6s cubic-bezier(.2,.8,.2,1)}
.shw-img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 14px 14px rgba(29,29,31,.14));transition:filter .4s ease,transform .25s ease-out;transform:translate(var(--tx,0),var(--ty,0))}
.shw-nm{position:absolute;left:0;right:0;top:304px;text-align:center;font-weight:800;font-size:14.5px;line-height:1.3;padding:0 10px;transition:opacity .25s ease}
.shw-nm small{display:block;font-weight:700;font-size:13px;color:var(--mut);margin-top:3px}
.shw-it:not(.on):hover .shw-fl{top:104px}
.shw-it.on{flex-basis:580px}
.shw-it.on .shw-card{opacity:1;transform:none;pointer-events:auto}
.shw-it.on .shw-wm{transform:none}
.shw-it.on .shw-sp li{opacity:1;transform:none}
.shw-it.on .shw-sp li:nth-child(1){transition-delay:.18s}.shw-it.on .shw-sp li:nth-child(2){transition-delay:.26s}.shw-it.on .shw-sp li:nth-child(3){transition-delay:.34s}.shw-it.on .shw-sp li:nth-child(4){transition-delay:.42s}
.shw-it.on .shw-fl{left:calc(100% - 158px);top:58px;width:286px;height:286px;animation:shwfl 5s ease-in-out .7s infinite}
.shw-it.on .shw-img{filter:drop-shadow(0 26px 22px rgba(0,0,0,.5))}
.shw-it.on .shw-nm{opacity:0}
@keyframes shwfl{0%,100%{margin-top:0}50%{margin-top:-10px}}
.shw-prog{display:none}
@media (max-width:860px){
 .shw{padding-top:56px;overflow:hidden}.shw-nav{display:none}
 .shw-prog{display:flex;gap:5px;margin:16px 0 0}.shw-prog i{flex:1;height:3px;border-radius:3px;background:rgba(29,29,31,.12);overflow:hidden}
 .shw-prog b{display:block;height:100%;width:0;background:#FF6A13;border-radius:3px}.shw-prog i.done b{width:100%}
 .shw-prog i.run b{width:100%;transition:width 5s linear}
 .shw-row{scroll-snap-type:x mandatory;gap:0;padding:22px calc(50% - 39vw) 34px;margin:0 -16px;perspective:1100px}
 .shw-it,.shw-it.on{flex:0 0 78vw;height:510px;scroll-snap-align:center;scroll-snap-stop:always;transition:none;
  transform:scale(calc(.82 + .18*var(--p,0))) rotateY(calc(var(--d,0)*-14deg));opacity:calc(.5 + .5*var(--p,0));will-change:transform}
 .shw-card,.shw-it.on .shw-card{opacity:1;transform:none;pointer-events:auto;padding:24px 22px 22px;border-radius:30px;transition:none;
  background:radial-gradient(110% 70% at calc(60% + var(--d,0)*40%) 34%,rgba(255,106,19,.3),transparent 60%),linear-gradient(165deg,#2B2B2F,#17171A)}
 .shw-card b{font-size:22px;max-width:none}
 .shw-wm,.shw-it.on .shw-wm{font-size:170px;bottom:auto;top:170px;right:auto;left:50%;transition:none;transform:translateX(calc(-50% + var(--d,0)*120px));color:rgba(255,255,255,.06)}
 .shw-fl,.shw-it.on .shw-fl{left:50%;top:122px;width:216px;height:216px;transition:none;animation:none;
  transform:translate(calc(-50% + var(--d,0)*-90px),calc((1 - var(--p,0))*26px)) rotate(calc(var(--d,0)*-9deg)) scale(calc(.8 + .2*var(--p,0)))}
 .shw-it.on .shw-fl{animation:shwfl 5s ease-in-out .4s infinite}
 .shw-img,.shw-it.on .shw-img{filter:drop-shadow(0 26px 22px rgba(0,0,0,.5))}
 .shw-nm{display:none}
 .shw-sp{margin-top:auto;gap:7px;max-width:none;flex-direction:row;flex-wrap:wrap}
 .shw-sp li,.shw-it.on .shw-sp li{font-size:12.5px;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.1);opacity:calc(var(--p,0)*var(--p,0));transform:translateY(calc((1 - var(--p,0))*16px));transition:none}
 .shw-sp li::before{display:none}.shw-sp li:nth-child(n+3){display:none}.shw-sp li{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
 .shw-bot{margin-top:16px}.shw-pr{font-size:24px}.shw-more{display:none}
 .shw-add[aria-label="В корзину"]{width:auto;padding:0 18px 0 14px;gap:6px;font-size:22px;display:flex;align-items:center}
 .shw-add[aria-label="В корзину"]::after{content:"В корзину";font:800 14.5px 'Manrope',sans-serif}
}
@media (prefers-reduced-motion:reduce){.shw-card,.shw-fl,.shw-it,.shw-sp li,.shw-wm{transition:none}.shw-it.on .shw-fl{animation:none}}
"""
    open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)
    SHJS = """<script>(function(){var row=document.querySelector('.shw-row');if(!row)return;var its=[].slice.call(row.querySelectorAll('.shw-it'));
var cnt=document.querySelector('.shw-cnt b'),cur=-1,lock=0,touch=matchMedia('(hover:none)').matches;
function on(i,scroll){i=(i+its.length)%its.length;if(i===cur)return;cur=i;its.forEach(function(x,k){x.classList.toggle('on',k===i)});if(cnt)cnt.textContent=i+1;lock=Date.now()+(scroll?1250:560);
if(scroll)setTimeout(function(){var el=its[i],r=el.getBoundingClientRect(),m=row.getBoundingClientRect();row.scrollBy({left:r.left+r.width/2-(m.left+m.width/2),behavior:'smooth'})},touch?0:330)}
function open(pid){var c=document.querySelector('article.card[data-pid="'+pid+'"] .ph'),pp=document.getElementById('ppage');if(c)c.dispatchEvent(new MouseEvent('click',{bubbles:true}));
setTimeout(function(){if(!pp||!pp.classList.contains('on')){var u=document.querySelector('.shw-it[data-pid="'+pid+'"]').getAttribute('data-url');if(u)location.href=u}},120)}
its.forEach(function(el,i){var tm;
el.addEventListener('mouseenter',function(){if(touch)return;clearTimeout(tm);tm=setTimeout(function(){if(Date.now()>lock)on(i,true)},130)});
el.addEventListener('mouseleave',function(){clearTimeout(tm);var im=el.querySelector('.shw-img');im.style.removeProperty('--tx');im.style.removeProperty('--ty')});
el.addEventListener('mousemove',function(ev){if(touch||!el.classList.contains('on'))return;var r=el.getBoundingClientRect(),im=el.querySelector('.shw-img');
im.style.setProperty('--tx',((ev.clientX-r.left)/r.width-.5)*-16+'px');im.style.setProperty('--ty',((ev.clientY-r.top)/r.height-.5)*-12+'px')});
el.addEventListener('focus',function(){on(i,true)});
el.addEventListener('click',function(ev){var pid=el.getAttribute('data-pid'),was=el.classList.contains('on');on(i,true);var a=ev.target.closest('.shw-add');
if(a){var b=document.querySelector('.act[data-id="'+pid+'"] .addb');
if(b&&!b.disabled&&!b.classList.contains('ask')&&!b.classList.contains('dis')&&!b.classList.contains('pick')){b.click();a.textContent='✓';setTimeout(function(){a.textContent='+'},1100);return}open(pid);return}
if(ev.target.closest('.shw-more')){open(pid);return}
if(was)open(pid)});
el.addEventListener('keydown',function(ev){if(ev.key==='Enter')el.click();if(ev.key==='ArrowRight'){on(cur+1,true);its[cur].focus()}if(ev.key==='ArrowLeft'){on(cur-1,true);its[cur].focus()}})});
var p=document.querySelector('.shw-prev'),n=document.querySelector('.shw-next');if(p)p.addEventListener('click',function(){on(cur-1,true)});if(n)n.addEventListener('click',function(){on(cur+1,true)});
var mob=matchMedia('(max-width:860px)'),prog=[].slice.call(document.querySelectorAll('.shw-prog i')),raf=0,auto=0,hold=0,vis=false;
function bars(i,run){prog.forEach(function(x,k){x.className=k<i?'done':'';});if(prog[i]&&run){void prog[i].offsetWidth;prog[i].className='run'}}
function measure(){raf=0;if(!mob.matches){its.forEach(function(x){x.style.removeProperty('--d');x.style.removeProperty('--p')});return}
var m=row.getBoundingClientRect(),cx=m.left+m.width/2,best=0,bp=-1;
its.forEach(function(x,k){var r=x.getBoundingClientRect(),w=x.offsetWidth||1,d=(x.offsetLeft+w/2-row.scrollLeft-row.clientWidth/2)/w;d=Math.max(-1.4,Math.min(1.4,d));var pp=Math.max(0,1-Math.abs(d));
x.style.setProperty('--d',d.toFixed(3));x.style.setProperty('--p',pp.toFixed(3));if(pp>bp){bp=pp;best=k}});
if(best!==cur){cur=best;its.forEach(function(x,k){x.classList.toggle('on',k===best)});if(cnt)cnt.textContent=best+1;bars(best,vis&&Date.now()>hold)}}
function ask(){if(!raf)raf=requestAnimationFrame(measure)}
function go(i){i=(i+its.length)%its.length;var x=its[i];row.scrollTo({left:x.offsetLeft+x.offsetWidth/2-row.clientWidth/2,behavior:'smooth'})}
row.addEventListener('scroll',ask,{passive:true});addEventListener('resize',ask);
['touchstart','pointerdown'].forEach(function(ev){row.addEventListener(ev,function(){hold=Date.now()+9000;bars(cur,false)},{passive:true})});
function tick(){if(mob.matches&&vis&&Date.now()>hold){go(cur+1)}}
if('IntersectionObserver' in window){new IntersectionObserver(function(en){vis=en[0].isIntersecting;clearInterval(auto);if(vis&&mob.matches&&!matchMedia('(prefers-reduced-motion:reduce)').matches){bars(cur<0?0:cur,Date.now()>hold);auto=setInterval(function(){if(Date.now()>hold){tick()}else{}} ,5000)}},{threshold:.55}).observe(row)}
if(mob.matches){cur=-1;measure()}else{on(0,false)}})();</script>
"""
    kk = markup.index('<section id="printers"')
    markup = markup[:kk] + SHOW + markup[kk:]
else:
    SHJS = ""

SK3JS = ""
exec(open(os.path.join(root, "tools", "skin3.py"), encoding="utf-8").read())

# квиз-вопросы уезжают вниз: сначала товары, как в магазине
_q0 = markup.find('<section class="quizb')
if _q0 != -1:
    _q1 = markup.index('</section>', _q0) + len('</section>')
    _qb = markup[_q0:_q1]; markup = markup[:_q0] + markup[_q1:]
    _qa = markup.find('<section class="igb')
    if _qa == -1: _qa = markup.rindex("<footer")
    markup = markup[:_qa] + _qb + "\n" + markup[_qa:]
k = markup.rindex("<footer")
markup = markup[:k] + SEOTXT + SMAP + markup[k:]
index = head(TITLE, DESC, "/", hero.group(1) if hero else None, ld(STORE) + ld(WEBSITE)) + "<body>\n" + markup + '<script src="/app.js?v=%s"></script>\n' % ver + SHJS + SK3JS + '</body></html>\n'
open(os.path.join(dist, "index.html"), "w", encoding="utf-8").write(index)

# ---------- готовые файлы (карточки для объявлений) ----------
if os.path.isdir(os.path.join(root, "static")): shutil.copytree(os.path.join(root, "static"), dist, dirs_exist_ok=True)

# ---------- служебные файлы ----------
today = datetime.date.today().isoformat()
urls = [("/", "1.0")] + [(u, "0.9") for u in extra] + [(p[1], "0.8") for p in pages]
open(os.path.join(dist, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (SITE, u, today, pr) for u, pr in urls) + "</urlset>\n")
open(os.path.join(dist, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
open(os.path.join(dist, "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1D1D1F"/><text x="32" y="43" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="28" fill="#FF6A13">3D</text></svg>')
open(os.path.join(dist, "CNAME"), "w").write("3dhouse.kg\n")
open(os.path.join(dist, ".nojekyll"), "w").write("")
# подтверждение прав в Яндекс Вебмастере — файл не удалять
open(os.path.join(dist, "yandex_ea1a9dc4360e0d48.html"), "w").write('<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n    </head>\n    <body>Verification: ea1a9dc4360e0d48</body>\n</html>\n')
open(os.path.join(dist, "404.html"), "w", encoding="utf-8").write(head("Страница не найдена | 3D HOUSE", "Такой страницы нет.", "/404.html") + "<body>" + HDR +
    '<main class="wrap" style="padding:90px 22px;text-align:center"><h1 style="font-size:34px">Страница не найдена</h1><p style="color:var(--mut);margin:14px 0 26px">Возможно, товар переехал. Посмотрите каталог.</p><a class="btn" href="/">На главную</a></main>' + FTR + "</body></html>")
print("ok: %d картинок, %d страниц товаров, index %d КБ" % (len(seen), len(pages), len(index) // 1024))
