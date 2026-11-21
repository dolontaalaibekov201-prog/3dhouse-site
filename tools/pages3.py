# ---------- каждый раздел — отдельная страница-витрина (с корзиной и поиском), главная — короткая ----------
# Выполняется из build.py через exec после сборки главной.
_HL = [("#printers", "/3d-printery/"), ("#industrial", "/dlya-biznesa/"), ("#filament", "/plastik-dlya-3d-pechati/"),
       ("#parts", "/aksessuary/#parts"), ("#plates", "/aksessuary/#plates"), ("#ams", "/aksessuary/#ams"),
       ("#service", "/servis/"), ("#b2b", "/servis/#b2b"), ("#videos", "/videouroki/")]
def _lr(h, here):
    if here != "/": h = h.replace('href="#top"', 'href="/"')
    for a, u in _HL:
        if u.split("#")[0] == here:
            u = "#" + u.split("#")[1] if "#" in u else "#top"
        h = h.replace('href="%s"' % a, 'href="%s"' % u)
    return h
def _secs(m):
    a = m.index("<main"); b = m.index("</main>"); out = []; i = a; depth = 0; st = 0
    for t in re.finditer(r"<section\b[^>]*>|</section>", m[a:b]):
        if t.group(0) != "</section>":
            if depth == 0:
                st = a + t.start(); tag = t.group(0)
                idm = re.search(r'\bid="([^"]+)"', tag); cm = re.search(r'\bclass="([^" ]+)', tag)
                key = idm.group(1) if idm and idm.group(1) not in ("hero", "promo", "showcase") else (cm.group(1) if cm else "")
            depth += 1
        else:
            depth -= 1
            if depth == 0: out.append((st, a + t.end(), key))
    return out
def _keep(m, keep):
    for st, en, key in reversed(_secs(m)):
        if key not in keep: m = m[:st] + m[en:]
    return m
_base = markup.replace(SEOTXT, "").replace(SMAP, "")
_SCR = '<script src="/app.js?v=%s"></script>\n' % ver + SHJS + SK3JS
def shop_page(path, title, desc, intro, keep, tail="", lds="", img=None, chips=(), vis="", links=()):
    m = _keep(_base, tuple(keep) + ("quizb",))
    ss = _secs(m)
    if not ss: return
    # лишние шаблоны «историй» товаров на странице раздела не нужны: меньше вес и дублей текста
    _on = set(re.findall(r'<article class="card[^"]*" data-pid="([^"]+)"', m))
    m = re.sub(r'<template id="pp-([^"]+)">.*?</template>\s*', lambda t: t.group(0) if t.group(1) in _on else "", m, flags=re.S)
    if links:
        tail = (tail or "") + '<h2>Модели и цены</h2><p class="pgl">%s</p>' % "".join(
            '<a href="%s">%s <b>%s%s сом</b></a>' % (p[1], e(p[2]), "от " if p[5] else "", nf(p[3])) for p in links)
    if tail:
        bl = [x for x in re.split(r"(?=<h2>)", tail) if x.strip()]
        tail = '<div class="pgt">%s</div>' % "".join('<div class="pgt-c">%s</div>' % x for x in bl)
    m = m[:ss[-1][1]] + tail + m[ss[-1][1]:]
    ch = '<ul class="hx-ch">%s</ul>' % "".join("<li><b>%s</b><span>%s</span></li>" % (e(a), e(b)) for a, b in chips) if chips else ""
    hero = ('<div class="phx"><div class="hx-bg" aria-hidden="true"><i class="hx-grid"></i><i class="hx-glow"></i><i class="hx-c1"></i><i class="hx-c2"></i></div>'
            '<div class="phx-tx">%s%s</div><div class="phx-vis" aria-hidden="true">%s</div></div>') % (intro, ch, vis)
    m = m[:ss[0][0]] + hero + m[ss[0][0]:]
    out = head(title, desc, path, img, lds) + '<body class="sub">\n' + _lr(m, path) + _SCR + "</body></html>\n"
    d = os.path.join(dist, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    if path not in extra: extra.append(path)
def _split(path, ps):
    t, d, inner, lds, img = PAGEARGS[path]; c = clist(ps)
    a, b = inner.split(c, 1) if c in inner else (inner, "")
    return t, d, a, b.replace(WABTN, ""), lds, img
def _cuts(*ids):
    return '<i class="hx-ring"></i>' + "".join('<img class="phx-c phx-c%d" src="/cut/%s.webp" alt="" width="300" height="330" decoding="async">' % (i + 1, x)
                                                 for i, x in enumerate([y for y in ids if os.path.exists(os.path.join(root, "static", "cut", y + ".webp"))][:3]))
def _spools(*cols):
    return '<i class="hx-ring"></i>' + "".join('<i class="phx-sp phx-sp%d" style="--c:%s"></i>' % (i + 1, c) for i, c in enumerate(cols))
def _tiles(*ids):
    srcs = [(cards.get(x) or {}).get("img") for x in ids]; srcs = [x for x in srcs if x][:3]
    return '<i class="hx-ring"></i>' + "".join('<span class="phx-t phx-t%d"><img src="%s" alt="" width="300" height="300" decoding="async"></span>' % (i + 1, x) for i, x in enumerate(srcs))
_PLAY = '<i class="hx-ring"></i><span class="phx-play"><i></i></span>'
_cr = lambda n: '<p class="crumbs"><a href="/">Главная</a> / %s</p>' % n
if PR:
    t, d, a, b, l, im = _split("/3d-printery/", PR); shop_page("/3d-printery/", t, d, a, ("printers",), b, l, im,
        [("%d" % len(PR), "моделей в каталоге"), ("от %s сом" % nf(min(p[3] for p in PR)), "цены"), ("1 год", "гарантия")], _cuts("p1s", "a1", "x2d"), PR)
if FI:
    t, d, a, b, l, im = _split("/plastik-dlya-3d-pechati/", FI); shop_page("/plastik-dlya-3d-pechati/", t, d, a, ("filament",), b, l, im,
        [("%d" % len(FI), "серий пластика"), ("от %s сом" % nf(FILMIN), "катушка 1 кг"), ("1 день", "доставка по КР")], _spools("#FF6A13", "#F2F2F4", "#2BB673", "#3B82F6"), FI)
if AC:
    t, d, a, b, l, im = _split("/aksessuary/", AC)
    shop_page("/aksessuary/", "Аксессуары для 3D-принтера в Бишкеке — сопла, пластины, AMS | 3D HOUSE",
              "Сопла, хотэнды, печатные пластины и системы подачи AMS для 3D-принтеров Bambu Lab в Бишкеке. Наличие в шоуруме, доставка по Кыргызстану за 1 день.",
              _cr("Аксессуары") + "<h1>Аксессуары для 3D-принтера в Бишкеке</h1><p class=\"lead\">Сопла и хотэнды, печатные пластины, системы подачи AMS и расходники — на полке в Бишкеке.</p>",
              ("parts", "plates", "ams"), b, l, im,
              [("Сопла", "и хотэнды"), ("Пластины", "для печати"), ("AMS", "системы подачи")], _tiles("hkit", "ams2", "pltex"), AC)
shop_page("/dlya-biznesa/", "Промышленные 3D-принтеры в Бишкеке — оборудование для бизнеса | 3D HOUSE",
          "3D-принтеры для производства, конструкторских бюро и мастерских в Бишкеке: фермы из принтеров Bambu Lab, оборудование под заказ, работа по безналу и с документами.",
          _cr("Для бизнеса") + "<h1>3D-принтеры для бизнеса и производства</h1><p class=\"lead\">Возим оборудование под задачу, считаем смету и окупаемость, работаем по безналу и с документами.</p>",
          ("industrial", "b2b"), SHIP, crumb2("Для бизнеса", "/dlya-biznesa/"), None,
          [("Безнал", "счёт и договор"), ("Документы", "для бухгалтерии"), ("Пусконаладка", "на месте")], _cuts("x2d", "p2s", "p1s"), [p for p in PR if p[0] in ("x2d", "p2s", "p1s", "cr5", "u1")])
shop_page("/servis/", "Сервис, запуск и обучение 3D-печати в Бишкеке | 3D HOUSE",
          "Запуск 3D-принтера «под ключ», сервис и запчасти в Бишкеке, обучение 3D-печати. Работаем с юрлицами, школами и производствами.",
          _cr("Сервис") + "<h1>Сервис, запуск и обучение 3D-печати</h1><p class=\"lead\">Подбираем принтер под задачу, запускаем вместе с вами и остаёмся на связи после покупки.</p>",
          ("service", "b2b"), SHIP, crumb2("Сервис", "/servis/"), None,
          [("Запуск", "в подарок"), ("1 год", "гарантия"), ("Обучение", "с первой печати")], _cuts("a1", "p1s"))
shop_page("/videouroki/", "Видеоуроки по 3D-печати — бесплатно | 3D HOUSE, Бишкек",
          "Бесплатные видеоуроки и лайфхаки по 3D-печати от команды 3D HOUSE: настройка принтера, пластик, первая печать.",
          _cr("Видеоуроки") + "<h1>Видеоуроки по 3D-печати</h1><p class=\"lead\">Короткие уроки и лайфхаки от команды 3D HOUSE.</p>",
          ("videos",), "", crumb2("Видеоуроки", "/videouroki/"), None,
          [("Бесплатно", "все уроки"), ("Коротко", "по делу")], _PLAY)

# главная: без длинного каталога — только избранные принтеры; полный каталог остаётся для поиска
_feat = [p[0] for p in sorted(PR, key=lambda p: (p[0] not in PROMO_OLD, p[3])) if CRM[p[0]]["q"] > 0][:4]
_home = index
for _f in _feat:
    _home = re.sub(r'<article class="card([^"]*)" data-pid="%s"' % _f, r'<article class="card feat\1" data-pid="%s"' % _f, _home, count=1)
_ps = _home.find('<section id="printers"')
if _ps != -1:
    _pe = _home.index("</section>", _ps)
    _home = _home[:_pe] + '<a class="btn more3" href="/3d-printery/">Все %d принтеров →</a>' % len(PR) + _home[_pe:]
for _k in ("videos", "layers", "b2b"):
    pass
_home = _lr(_home.replace("<body>", '<body class="home">', 1), "/")
open(os.path.join(dist, "index.html"), "w", encoding="utf-8").write(_home)

css += r"""
/* ===== страницы разделов ===== */
.more3{display:none}
body.home:not(.searching) .cat:not(#printers),body.home:not(.searching) .videos,body.home:not(.searching) .layers,body.home:not(.searching) .b2b{display:none}
body.home:not(.searching) #printers .card:not(.feat){display:none}
body.home:not(.searching) #printers .more3{display:inline-flex;margin-top:26px}
body.home:not(.searching) #printers .cnum,body.home:not(.searching) #printers .chips,body.home:not(.searching) #printers .chiphint{display:none}
.pgi{padding:34px 0 0}.pgi .crumbs{font-size:13.5px;color:var(--mut);margin:0 0 14px}.pgi .crumbs a{text-decoration:underline;text-underline-offset:3px}
.pgi h1{font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(28px,3.6vw,46px);line-height:1.06;letter-spacing:-.04em;text-transform:uppercase;margin:0;text-wrap:balance}
.pgi .lead{font-size:17px;line-height:1.55;color:var(--mut);max-width:70ch;margin:14px 0 0}
body.sub .cat:first-of-type{padding-top:34px}
body.searching .pgi,body.searching .pgt{display:none}
.phx{position:relative;display:grid;grid-template-columns:1.15fr .85fr;gap:20px;align-items:center;margin-top:20px;padding:46px 56px 50px;border-radius:36px;background:#0B0C10;color:#fff;overflow:hidden;isolation:isolate;box-shadow:0 40px 80px -50px rgba(11,12,16,.8)}
body.searching .phx,body.searching .pgt{display:none}
.phx .crumbs{font-size:12.5px;font-weight:700;letter-spacing:.06em;color:rgba(255,255,255,.55);margin:0 0 16px}.phx .crumbs a{color:#FF8A3D}
.phx h1{font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(26px,3.3vw,44px);line-height:1.06;letter-spacing:-.04em;text-transform:uppercase;margin:0;color:#fff;text-wrap:balance}
.phx h1::after{content:"";display:block;width:84px;height:5px;border-radius:3px;margin-top:20px;background:linear-gradient(90deg,#FF6A13,#FFB36B);transform-origin:0 50%;animation:phxl 1s .3s var(--s3) both}
@keyframes phxl{from{transform:scaleX(0)}}
.phx .lead{font-size:16.5px;line-height:1.55;color:rgba(255,255,255,.72);max-width:54ch;margin:18px 0 0}
.phx-tx>*{animation:phxu .8s var(--s3) both}.phx-tx>*:nth-child(2){animation-delay:.08s}.phx-tx>*:nth-child(3){animation-delay:.16s}.phx-tx>*:nth-child(4){animation-delay:.24s}
@keyframes phxu{from{opacity:0;transform:translateY(22px)}}
.phx-vis{position:relative;height:300px;display:grid;place-items:center}.phx-vis .hx-ring{width:290px}
.phx-c{position:absolute;width:auto;height:auto;max-height:250px;max-width:46%;filter:drop-shadow(0 30px 24px rgba(0,0,0,.6));animation:hxprint 1.4s .2s var(--s3) both,hxfl 6s 1.7s ease-in-out infinite}
.phx-c1{z-index:2}.phx-c2{left:0;bottom:8px;max-height:190px;z-index:3;animation-delay:.45s,2.4s}.phx-c3{right:0;bottom:8px;max-height:200px;z-index:1;animation-delay:.7s,3.1s}
.phx-sp{position:absolute;width:150px;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#17181C 0 17%,#3A3C44 17% 21%,var(--c) 21% 58%,rgba(14,15,18,.9) 58% 61%,#2A2C33 61% 100%);
 box-shadow:inset 0 0 0 3px rgba(255,255,255,.14),0 26px 30px -12px rgba(0,0,0,.7);animation:phxs 7s ease-in-out infinite,phxu .9s var(--s3) both}
.phx-sp1{left:4%;top:4%}.phx-sp2{right:2%;top:14%;width:118px;animation-delay:-2s,.15s}.phx-sp3{left:22%;bottom:0;width:128px;animation-delay:-4s,.3s}.phx-sp4{right:14%;bottom:4%;width:96px;animation-delay:-5.5s,.45s}
@keyframes phxs{50%{translate:0 -14px;rotate:26deg}}
.phx-t{position:absolute;width:168px;aspect-ratio:1;border-radius:26px;overflow:hidden;background:#fff;box-shadow:0 30px 40px -18px rgba(0,0,0,.75);animation:phxu .9s var(--s3) both,phxt 7s ease-in-out infinite}
.phx-t img{width:100%;height:100%;object-fit:cover}
.phx-t1{z-index:2;rotate:-4deg}.phx-t2{left:0;top:6px;width:132px;rotate:-12deg;animation-delay:.15s,-2s}.phx-t3{right:0;bottom:4px;width:138px;rotate:10deg;animation-delay:.3s,-4s}
@keyframes phxt{50%{translate:0 -12px}}
.phx-play{position:relative;width:132px;height:132px;border-radius:50%;background:linear-gradient(135deg,#FF6A13,#FFB36B);display:grid;place-items:center;box-shadow:0 0 0 0 rgba(255,106,19,.6);animation:phxp 2.2s ease-out infinite}
.phx-play i{width:0;height:0;border-left:38px solid #fff;border-top:24px solid transparent;border-bottom:24px solid transparent;margin-left:10px}
@keyframes phxp{to{box-shadow:0 0 0 46px rgba(255,106,19,0)}}
body.sub .cat{padding-top:56px}
.pgt{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;padding-top:64px}
.pgt-c{background:#fff;border:1px solid rgba(14,15,18,.05);border-radius:26px;padding:26px 28px;transition:transform .4s var(--s3),box-shadow .4s var(--s3)}
.pgt-c:hover{transform:translateY(-4px);box-shadow:0 26px 44px -30px rgba(14,15,18,.4)}
.pgt h2{font-size:18px;text-transform:uppercase;letter-spacing:-.02em;margin:0 0 12px;padding-left:16px;position:relative}
.pgt h2::before{content:"";position:absolute;left:0;top:.1em;bottom:.1em;width:5px;border-radius:3px;background:linear-gradient(#FF6A13,#FFB36B)}
.pgt-c:has(.pgl){grid-column:1/-1}.pgl{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:4px 26px}.pgl a{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px dashed var(--line);text-decoration:none!important;font-weight:600;font-size:14.5px}.pgl a:hover{color:#FF6A13}.pgl b{white-space:nowrap;font-weight:800}
.pgt p{line-height:1.65;color:#4A4C55;margin:0 0 10px;font-size:15px}.pgt p:last-child{margin:0}.pgt a{text-decoration:underline;text-underline-offset:3px}
@media (max-width:860px){
 .phx{grid-template-columns:1fr;gap:0;margin:12px -8px 0;padding:22px 22px 28px;border-radius:28px}
 .phx-vis{order:-1;height:190px;margin-bottom:8px}.phx-vis .hx-ring{width:186px}
 .phx-c{max-height:160px}.phx-c2{max-height:120px}.phx-c3{max-height:126px}
 .phx-sp{width:96px}.phx-sp2{width:76px}.phx-sp3{width:84px}.phx-sp4{width:62px}
 .phx-t{width:112px;border-radius:20px}.phx-t2{width:88px}.phx-t3{width:92px}.phx-play{width:96px;height:96px}.phx-play i{border-left-width:28px;border-top-width:18px;border-bottom-width:18px}
 .phx .lead{font-size:15px;margin-top:14px}.phx h1::after{margin-top:14px}
 .pgt{grid-template-columns:1fr;gap:10px;padding-top:40px}.pgt-c{border-radius:22px;padding:20px}
 body.sub .cat{padding-top:36px}
}
@media (prefers-reduced-motion:reduce){.phx-tx>*,.phx-c,.phx-sp,.phx-t,.phx-play,.phx h1::after{animation:none!important}.phx-c{clip-path:none}}
"""
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)
