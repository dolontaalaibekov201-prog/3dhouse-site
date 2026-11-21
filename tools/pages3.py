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
def shop_page(path, title, desc, intro, keep, tail="", lds="", img=None):
    m = _keep(_base, tuple(keep) + ("quizb",))
    ss = _secs(m)
    if not ss: return
    m = m[:ss[-1][1]] + ('<div class="pgt">%s</div>' % tail if tail else "") + m[ss[-1][1]:]
    m = m[:ss[0][0]] + '<div class="pgi">%s</div>' % intro + m[ss[0][0]:]
    out = head(title, desc, path, img, lds) + '<body class="sub">\n' + _lr(m, path) + _SCR + "</body></html>\n"
    d = os.path.join(dist, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    if path not in extra: extra.append(path)
def _split(path, ps):
    t, d, inner, lds, img = PAGEARGS[path]; c = clist(ps)
    a, b = inner.split(c, 1) if c in inner else (inner, "")
    return t, d, a, b.replace(WABTN, ""), lds, img
_cr = lambda n: '<p class="crumbs"><a href="/">Главная</a> / %s</p>' % n
if PR:
    t, d, a, b, l, im = _split("/3d-printery/", PR); shop_page("/3d-printery/", t, d, a, ("printers",), b, l, im)
if FI:
    t, d, a, b, l, im = _split("/plastik-dlya-3d-pechati/", FI); shop_page("/plastik-dlya-3d-pechati/", t, d, a, ("filament",), b, l, im)
if AC:
    t, d, a, b, l, im = _split("/aksessuary/", AC)
    shop_page("/aksessuary/", "Аксессуары для 3D-принтера в Бишкеке — сопла, пластины, AMS | 3D HOUSE",
              "Сопла, хотэнды, печатные пластины и системы подачи AMS для 3D-принтеров Bambu Lab в Бишкеке. Наличие в шоуруме, доставка по Кыргызстану за 1 день.",
              _cr("Аксессуары") + "<h1>Аксессуары для 3D-принтера в Бишкеке</h1><p class=\"lead\">Сопла и хотэнды, печатные пластины, системы подачи AMS и расходники — на полке в Бишкеке.</p>",
              ("parts", "plates", "ams"), b, l, im)
shop_page("/dlya-biznesa/", "Промышленные 3D-принтеры в Бишкеке — оборудование для бизнеса | 3D HOUSE",
          "3D-принтеры для производства, конструкторских бюро и мастерских в Бишкеке: фермы из принтеров Bambu Lab, оборудование под заказ, работа по безналу и с документами.",
          _cr("Для бизнеса") + "<h1>3D-принтеры для бизнеса и производства</h1><p class=\"lead\">Возим оборудование под задачу, считаем смету и окупаемость, работаем по безналу и с документами.</p>",
          ("industrial", "b2b"), SHIP, crumb2("Для бизнеса", "/dlya-biznesa/"))
shop_page("/servis/", "Сервис, запуск и обучение 3D-печати в Бишкеке | 3D HOUSE",
          "Запуск 3D-принтера «под ключ», сервис и запчасти в Бишкеке, обучение 3D-печати. Работаем с юрлицами, школами и производствами.",
          _cr("Сервис") + "<h1>Сервис, запуск и обучение 3D-печати</h1><p class=\"lead\">Подбираем принтер под задачу, запускаем вместе с вами и остаёмся на связи после покупки.</p>",
          ("service", "b2b"), SHIP, crumb2("Сервис", "/servis/"))
shop_page("/videouroki/", "Видеоуроки по 3D-печати — бесплатно | 3D HOUSE, Бишкек",
          "Бесплатные видеоуроки и лайфхаки по 3D-печати от команды 3D HOUSE: настройка принтера, пластик, первая печать.",
          _cr("Видеоуроки") + "<h1>Видеоуроки по 3D-печати</h1><p class=\"lead\">Короткие уроки и лайфхаки от команды 3D HOUSE.</p>",
          ("videos",), "", crumb2("Видеоуроки", "/videouroki/"))

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
.pgt{max-width:860px;padding-top:64px}.pgt h2{font-size:clamp(20px,2.3vw,26px);margin:26px 0 10px}.pgt p{line-height:1.7;color:#444;margin:0 0 12px}.pgt a{text-decoration:underline;text-underline-offset:3px}
@media (max-width:860px){.pgi{padding-top:20px}.pgi .lead{font-size:15px}}
"""
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)
