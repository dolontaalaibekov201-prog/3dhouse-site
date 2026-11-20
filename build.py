#!/usr/bin/env python3
"""Собирает сайт 3dhouse.kg из src/site.html в папку docs/ (её раздаёт GitHub Pages).
Запуск: python3 build.py
src/site.html — исходник (одна страница со встроенными картинками и данными CRM).
"""
import re, json, base64, hashlib, html, os, shutil, datetime

SITE = "https://3dhouse.kg"
WA = "996559992306"
PHONE = "+996 559 992 306"
ADDR = "Бишкек, ул. Туголбай Ата, 32Б"
TITLE = "3D HOUSE — 3D-принтеры Bambu Lab, пластик и сервис в Бишкеке"
DESC = ("Купить 3D-принтер в Бишкеке: Bambu Lab A1, A2L, P1S, P2S, X2D, Snapmaker U1. Пластик PLA, PETG, TPU от 1 000 сом. "
        "Шоурум, гарантия 1 год, рассрочка, доставка по Кыргызстану за 1 день.")

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
nf = lambda n: ("%d" % n if n < 10000 else "{:,}".format(n).replace(",", " "))
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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
%s<link rel="stylesheet" href="/style.css?v=%s">
%s</head>
""" % (e(title), e(desc), SITE, path, e(title), e(desc), SITE, path,
       ('\n<meta property="og:image" content="%s%s">' % (SITE, ogimg)) if ogimg else "", links, ver, extra))

STORE = {"@context": "https://schema.org", "@type": "Store", "@id": SITE + "/#store", "name": "3D HOUSE", "url": SITE + "/",
         "description": "Магазин 3D-принтеров, пластика и аксессуаров в Бишкеке: продажа, запуск, сервис и обучение.",
         "telephone": "+996559992306", "priceRange": "200–118000 KGS", "currenciesAccepted": "KGS",
         "address": {"@type": "PostalAddress", "streetAddress": "ул. Туголбай Ата, 32Б", "addressLocality": "Бишкек", "addressCountry": "KG"},
         "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "10:00", "closes": "20:00"},
         "sameAs": ["https://instagram.com/3dhouse.kg"], "areaServed": {"@type": "Country", "name": "Кыргызстан"}}
ld = lambda o: '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>\n"

# ---------- главная ----------
hero = re.search(r'class="heroimg"[^>]*>\s*<img[^>]*src="([^"]+)"', markup)
index = head(TITLE, DESC, "/", hero.group(1) if hero else None, ld(STORE)) + "<body>\n" + markup + '<script src="/app.js?v=%s"></script>\n</body></html>\n' % ver
open(os.path.join(dist, "index.html"), "w", encoding="utf-8").write(index)

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
.pgmore{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.pgmore a{display:block;background:#fff;border:1px solid var(--line2);border-radius:18px;padding:16px 18px;font-weight:700}
.pgmore a span{display:block;font-weight:600;font-size:13.5px;color:var(--mut);margin-top:4px}
@media(max-width:760px){.pgrid{grid-template-columns:1fr;gap:22px}.pg{padding:18px 16px 60px}}
"""
HDR = ('<header><div class="wrap hd"><a class="logo" href="/" aria-label="3D HOUSE"><span class="wm2"><b>3D</b> HOUSE</span></a>'
       '<nav class="nav" style="display:flex"><a href="/#printers">Принтеры</a><a href="/#filament">Пластик</a><a href="/#parts">Запчасти</a><a href="/#videos">Видеоуроки</a></nav>'
       '<span style="flex:1"></span><a class="phone" href="tel:+%s">%s</a></div></header>' % (WA, PHONE))
FTR = ('<footer><div class="wrap fg"><div><a class="logo" href="/"><span class="wm2"><b>3D</b> HOUSE</span></a><p>Дом для 3D-печати: принтеры, пластик, сервис и обучение.</p></div>'
       '<div><b>Шоурум</b><p>%s<br>ежедневно 10:00–20:00</p></div><div><b>Каталог</b><p><a href="/#printers">Принтеры</a> · <a href="/#filament">Пластик</a> · <a href="/#parts">Запчасти</a></p></div>'
       '<div><b>Связь</b><p><a href="https://wa.me/%s">WhatsApp %s</a><br><a href="https://instagram.com/3dhouse.kg">Instagram @3dhouse.kg</a></p></div></div></footer>' % (ADDR, WA, PHONE))

pages = []
for pid, k in CRM.items():
    if pid not in SLUG or pid not in cards: continue
    c = cards[pid]; name = k.get("n") or c["n"]; catn, anchor = CATNAME.get(c["cat"], ("Каталог", "printers"))
    path = "/catalog/%s/" % SLUG[pid]; fil = bool(k.get("v")); price = k["p"]; q = k["q"]
    kind = "пластик для 3D-печати" if fil else ("3D-принтер" if c["cat"] == "printers" else "")
    h1 = ("%s — %s в Бишкеке" % (name, kind)) if kind else ("%s в Бишкеке" % name)
    title = "%s — купить в Бишкеке, цена %s%s сом | 3D HOUSE" % (name, "от " if fil else "", nf(price))
    lead = FDESC.get(pid) or (k.get("d") or c["d"])
    desc = "%s в Бишкеке: %s%s сом, %s. %s Шоурум 3D HOUSE, доставка по Кыргызстану за 1 день." % (
        name, "от " if fil else "", nf(price), "в наличии" if q > 0 else "под заказ", lead.rstrip(".") + ".")
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
        {"@type": "ListItem", "position": 1, "name": "3D HOUSE", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": catn, "item": SITE + "/#" + anchor}, {"@type": "ListItem", "position": 3, "name": name}]}
    pages.append((pid, path, name, price, c["cat"], fil, title, desc, c["img"], b, r, ld(prod) + ld(crumbs), catn, anchor))

for pid, path, name, price, cat, fil, title, desc, img, b, r, lds, catn, anchor in pages:
    more = [p for p in pages if p[4] == cat and p[0] != pid][:8]
    out = (head(title, desc, path, img, "<style>%s</style>\n%s" % (PCSS, lds)) + "<body>\n" + HDR +
           '<main class="pg"><p class="crumbs"><a href="/">Главная</a> / <a href="/#%s">%s</a> / %s</p><div class="pgrid">%s<div>%s</div></div>' % (anchor, e(catn), e(name), "".join(b), "".join(r)) +
           ('<h2>Ещё в разделе «%s»</h2><div class="pgmore">%s</div>' % (e(catn), "".join('<a href="%s">%s<span>%s%s сом</span></a>' % (p[1], e(p[2]), "от " if p[5] else "", nf(p[3])) for p in more)) if more else "") +
           "</main>" + FTR + "</body></html>\n")
    d = os.path.join(dist, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)

# ---------- служебные файлы ----------
today = datetime.date.today().isoformat()
urls = [("/", "1.0")] + [(p[1], "0.8") for p in pages]
open(os.path.join(dist, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (SITE, u, today, pr) for u, pr in urls) + "</urlset>\n")
open(os.path.join(dist, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
open(os.path.join(dist, "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1D1D1F"/><text x="32" y="43" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="28" fill="#FF6A13">3D</text></svg>')
open(os.path.join(dist, "CNAME"), "w").write("3dhouse.kg\n")
open(os.path.join(dist, ".nojekyll"), "w").write("")
open(os.path.join(dist, "404.html"), "w", encoding="utf-8").write(head("Страница не найдена | 3D HOUSE", "Такой страницы нет.", "/404.html") + "<body>" + HDR +
    '<main class="wrap" style="padding:90px 22px;text-align:center"><h1 style="font-size:34px">Страница не найдена</h1><p style="color:var(--mut);margin:14px 0 26px">Возможно, товар переехал. Посмотрите каталог.</p><a class="btn" href="/">На главную</a></main>' + FTR + "</body></html>")
print("ok: %d картинок, %d страниц товаров, index %d КБ" % (len(seen), len(pages), len(index) // 1024))
