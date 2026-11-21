# ---------- SKIN v3: «магазин будущего» — сцена-слайдер, категории с фото, нижняя панель, анимации ----------
# Выполняется из build.py через exec: пользуется его переменными (markup, css, PR, CRM, cards, SH, nf, e, WA, TEL).
_ARW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
_byid = {p[0]: p for p in PR}
_cut = lambda pid: os.path.exists(os.path.join(root, "static", "cut", pid + ".webp"))
def _cimg(pid, alt, first=False):
    w, h = _PI.open(os.path.join(root, "static", "cut", pid + ".webp")).size if _PI else (400, 450)
    return '<img %ssrc="/cut/%s.webp" alt="%s" width="%d" height="%d" %s decoding="async">' % (
        'id="heroImg" ' if first else "", pid, e(alt), w, h, 'fetchpriority="high"' if first else 'loading="lazy"')
def _chips(items):
    return '<ul class="hx-ch">%s</ul>' % "".join("<li><b>%s</b><span>%s</span></li>" % (e(a), e(b)) for a, b in items)
def _vis(pid, alt, hud, first=False):
    return ('<div class="hx-vis"><i class="hx-ring" aria-hidden="true"></i><span class="hx-im">%s<i class="hx-scan" aria-hidden="true"></i></span>'
            '<span class="hx-hud" aria-hidden="true">%s</span></div>') % (_cimg(pid, alt, first), e(hud))

_slides = []
# 1 — главный: H1 страницы (тексты с data-h остаются редактируемыми из админки)
_h1pid = "a1" if _cut("a1") else (sh[0][0] if len(sh) else None)
if _h1pid:
    _slides.append(
        '<div class="hx-tx"><p class="eyebrow hx-eb"><i></i><span data-h="eyebrow">Дом для 3D-печати · шоурум в Бишкеке</span></p>'
        '<h1><span data-h="h1">3D-принтеры</span> <em data-h="h1b">в Бишкеке</em></h1>'
        '<p class="lede" data-h="lede">Шоурум 3D-принтеров Bambu Lab, пластик и сервис. Подберём принтер под задачу, настроим и научим. Заказ уходит нам в WhatsApp — отвечаем за 15 минут.</p>'
        '<div class="cta"><a class="btn" href="#printers" data-h="cta">Выбрать принтер</a>'
        '<a class="btn ghost" href="https://wa.me/%s" target="_blank" rel="noopener">Консультация</a></div>%s</div>%s' % (
            WA, _chips([("от %s сом" % nf(min(p[3] for p in PR)), "цены на принтеры"), ("1 день", "доставка по КР"), ("1 кг", "пластика в подарок")]),
            _vis(_h1pid, "3D-принтер Bambu Lab в Бишкеке", "BAMBU LAB · 3D HOUSE · BISHKEK", True)))
# 2 — флагман
for _fp, _ft, _fs, _fc in (("x2d", "Два сопла. Один проход.", "Двухсопловой принтер для инженерных пластиков и мелкой серии.", [("2", "сопла"), ("AMS", "в комплекте"), ("EU", "версия")]),
                           ("p2s", "Закрытый корпус. Инженерный пластик.", "Закрытая камера для ABS, ASA и композитов.", [("AMS", "в комплекте"), ("Combo", "комплект"), ("EU", "версия")])):
    if _fp in _byid and _cut(_fp):
        _p = _byid[_fp]; _q = CRM[_fp]["q"]
        _slides.append(
            '<div class="hx-tx"><p class="eyebrow hx-eb"><i></i><span>%s · %s</span></p>'
            '<h2 class="hx-h">%s</h2><p class="lede">%s %s</p>'
            '<div class="cta"><a class="btn" href="%s">%s сом — подробнее</a></div>%s</div>%s' % (
                e(_p[2]), "в наличии" if _q > 0 else "под заказ", e(_ft), e(_p[2]) + " —", e(_fs[0].lower() + _fs[1:]), _p[1], nf(_p[3]), _chips(_fc),
                _vis(_fp, _p[2], _p[2].upper() + " · " + ("IN STOCK" if _q > 0 else "PRE-ORDER"))))
        break
# 3 — подарок и рассрочка
_gp = next((x for x in ("p1s", "a2l", "a1c") if _cut(x)), None)
if _gp:
    _slides.append(
        '<div class="hx-tx"><p class="eyebrow hx-eb"><i></i><span>Подарок к каждому принтеру</span></p>'
        '<h2 class="hx-h">1 кг пластика <em>в подарок</em></h2>'
        '<p class="lede">Печатайте сразу после запуска: настроим принтер, покажем первую печать и останемся на связи.</p>'
        '<div class="cta"><a class="btn" href="/3d-printery/">В каталог принтеров</a></div>%s</div>%s' % (
            _chips([("0 %", "рассрочка без переплаты"), ("1 год", "гарантия"), ("Запуск", "и обучение")]),
            _vis(_gp, "3D-принтер Bambu Lab с пластиком в подарок", "GIFT · 1 KG FILAMENT")))

_h0 = markup.find('<section class="hero">')
if _h0 != -1 and len(_slides) >= 2:
    _h1 = markup.index("</section>", _h0) + len("</section>")
    _tr = re.search(r'<div class="trust">.*?</div>\s*</div>', markup[_h0:_h1], re.S)
    HX = ('<section class="hx" id="hero" aria-roledescription="carousel" aria-label="Главное">'
          '<div class="hx-bg" aria-hidden="true"><i class="hx-grid"></i><i class="hx-glow"></i><i class="hx-c1"></i><i class="hx-c2"></i></div>'
          '<div class="hx-st">%s</div>'
          '<div class="hx-ui"><div class="hx-dots" role="tablist">%s</div>'
          '<div class="hx-ar"><button type="button" class="hx-prev" aria-label="Предыдущий слайд">←</button><button type="button" class="hx-next" aria-label="Следующий слайд">→</button></div></div>'
          '</section>') % (
        "".join('<div class="hx-sl%s" role="group" aria-roledescription="slide" aria-label="%d из %d">%s</div>' % (" on" if i == 0 else "", i + 1, len(_slides), s) for i, s in enumerate(_slides)),
        "".join('<button type="button" role="tab" aria-label="Слайд %d"%s><i></i></button>' % (i + 1, ' class="on"' if i == 0 else "") for i in range(len(_slides))))
    markup = markup[:_h0] + HX + markup[_h1:]

# категории с фото (вместо текстовых плиток)
def _ci(pid):
    return (cards.get(pid) or {}).get("img") or PHOTOS.get(pid)
_cats = [("#printers", "3D-принтеры", "От первого принтера для дома до машин для мелкой серии", ["a1", "p1s"], True),
         ("#filament", "Пластик", "PLA, PETG, TPU и инженерные материалы на складе", ["pla", "fblb", "petg"], False),
         ("#parts", "Аксессуары", "Сопла, хотэнды, пластины и AMS", ["hkit", "noz", "ha1"], False),
         ("#industrial", "Для бизнеса", "Фермы принтеров и оборудование под заказ", ["x2d", "p2s"], True)]
_t0 = markup.find('<section class="tiles')
if _t0 != -1:
    _t1 = markup.index("</section>", _t0) + len("</section>")
    _cc = []
    for n, (href, t, d, pids, cut) in enumerate(_cats):
        if cut:
            im = "".join('<img src="/cut/%s.webp" alt="" width="200" height="220" loading="lazy" decoding="async">' % x for x in pids if _cut(x))
        else:
            src = next((_ci(x) for x in pids if _ci(x)), None)
            im = '<img class="ph" src="%s" alt="" width="300" height="300" loading="lazy" decoding="async">' % src if src else ""
        _cc.append('<a class="cx-c" href="%s"><span class="cx-n">0%d</span><span class="cx-a">%s</span><span class="cx-i%s">%s</span><b>%s</b><p>%s</p></a>' % (
            href, n + 1, _ARW, " two" if cut else "", im, e(t), e(d)))
    markup = markup[:_t0] + '<section class="cx rv" aria-label="Категории">%s</section>' % "".join(_cc) + markup[_t1:]

# рекламный баннер акции (вместо раздела «Популярные модели»)
_ap = "a1"
if _ap in PROMO_OLD and _ap in _byid and _cut(_ap):
    _p = _byid[_ap]; _old = PROMO_OLD[_ap]; _new = PROMO[_ap]["p"]
    _spool = lambda c, k: '<i class="pb-sp pb-s%d" style="--c:%s"></i>' % (k, c)
    PB = ('<section class="pb rv" id="promo" aria-label="Акция"><div class="pb-bg" aria-hidden="true"><i class="pb-g1"></i><i class="pb-g2"></i><span class="pb-big">+3 КГ</span></div>'
          '<div class="pb-tx"><p class="pb-tag"><i></i>Акция · в наличии</p>'
          '<h2>%s <em>+ 3 кг филамента</em> в подарок</h2>'
          '<p class="pb-d">Принтер со столом 256 × 256 × 256 мм и три катушки пластика — можно печатать в день покупки. Запуск и первая печать вместе с нами.</p>'
          '<div class="pb-row"><div class="pb-pr"><s>%s сом</s><b>%s <small>сом</small></b></div>'
          '<div class="pb-btn"><button type="button" class="btn pb-add" data-pid="%s">В корзину</button><a class="btn ghost" href="%s">Подробнее</a></div></div></div>'
          '<div class="pb-vis" aria-hidden="true">%s%s%s<img src="/cut/%s.webp" alt="" width="400" height="446" loading="lazy" decoding="async"><span class="pb-badge"><b>3 кг</b>в подарок</span></div>'
          '</section>') % (e(_p[2]), nf(_old), nf(_new), _ap, _p[1], _spool("#FF6A13", 1), _spool("#F2F2F4", 2), _spool("#2BB673", 3), _ap)
    _c0 = markup.find('<section class="cx ')
    if _c0 != -1:
        _c1 = markup.index("</section>", _c0) + len("</section>")
        markup = markup[:_c1] + "\n" + PB + markup[_c1:]
    css += r"""
.pb{position:relative;display:grid;grid-template-columns:1.1fr .9fr;gap:20px;align-items:center;margin-top:20px;padding:48px 56px;border-radius:36px;overflow:hidden;isolation:isolate;color:#fff;
 background:linear-gradient(120deg,#FF5A00 0%,#FF6A13 38%,#FF9A4D 100%);box-shadow:0 40px 70px -46px rgba(255,90,0,.9)}
body.searching .pb{display:none}
.pb-bg{position:absolute;inset:0;z-index:-1;overflow:hidden}
.pb-g1{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:44px 44px;
 -webkit-mask-image:radial-gradient(70% 90% at 78% 50%,#000,transparent 75%);mask-image:radial-gradient(70% 90% at 78% 50%,#000,transparent 75%);animation:pbg 9s linear infinite}
@keyframes pbg{to{background-position:44px 44px,44px 44px}}
.pb-g2{position:absolute;right:4%;top:50%;width:46%;aspect-ratio:1;transform:translateY(-50%);border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.5),transparent 70%);animation:hxp 5s ease-in-out infinite}
.pb-big{position:absolute;right:-12px;bottom:-54px;font-family:'Unbounded',sans-serif;font-weight:800;font-size:230px;line-height:1;letter-spacing:-.06em;color:rgba(255,255,255,.13);white-space:nowrap}
.pb-tag{display:inline-flex;align-items:center;gap:9px;margin:0 0 16px;padding:7px 13px;border-radius:999px;background:#0E0F12;font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
.pb-tag i{width:8px;height:8px;border-radius:50%;background:#7ED7A5;animation:hxd2 1.8s ease-out infinite}
@keyframes hxd2{from{box-shadow:0 0 0 0 rgba(126,215,165,.8)}to{box-shadow:0 0 0 11px rgba(126,215,165,0)}}
.pb h2{color:#fff;font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(26px,3.3vw,44px);line-height:1.06;letter-spacing:-.04em;text-transform:uppercase;margin:0;text-wrap:balance}
.pb h2 em{font-style:normal;color:#0E0F12}
.pb-d{margin:16px 0 26px;max-width:48ch;font-size:16px;line-height:1.5;color:rgba(255,255,255,.92)}
.pb-row{display:flex;align-items:center;gap:26px;flex-wrap:wrap}
.pb-pr s{display:block;font-size:15px;font-weight:700;color:rgba(255,255,255,.75);text-decoration-thickness:2px}
.pb-pr b{display:block;font-family:'Unbounded',sans-serif;font-weight:800;font-size:38px;line-height:1.05;letter-spacing:-.04em;white-space:nowrap}.pb-pr small{font-family:'Manrope',sans-serif;font-size:15px;font-weight:800;letter-spacing:0}
.pb-btn{display:flex;gap:10px;flex-wrap:wrap}
.pb .btn{background:#0E0F12;border-color:#0E0F12;color:#fff;cursor:pointer;transition:transform .25s var(--s3),box-shadow .25s}.pb .btn:hover{transform:translateY(-2px);box-shadow:0 16px 26px -12px rgba(14,15,18,.7);filter:none}
.pb .btn.ghost{background:rgba(255,255,255,.2);border-color:rgba(255,255,255,.55);color:#fff}.pb .btn.ghost:hover{background:rgba(255,255,255,.32)}
.pb-add.ok{background:#1F9D5B;border-color:#1F9D5B}
.pb-vis{position:relative;height:340px;display:grid;place-items:center}
.pb-vis img{position:relative;z-index:2;max-height:320px;width:auto;filter:drop-shadow(0 34px 26px rgba(120,40,0,.55));animation:hxfl 6s ease-in-out infinite}
.pb-sp{position:absolute;z-index:1;width:112px;aspect-ratio:1;border-radius:50%;
 background:radial-gradient(circle,#17181C 0 17%,#3A3C44 17% 21%,var(--c) 21% 58%,rgba(14,15,18,.9) 58% 61%,#2A2C33 61% 100%);
 box-shadow:inset 0 0 0 3px rgba(255,255,255,.14),0 22px 26px -10px rgba(90,30,0,.6);animation:pbs 7s ease-in-out infinite}
.pb-sp::after{content:"";position:absolute;inset:21%;border-radius:50%;background:repeating-radial-gradient(circle,rgba(0,0,0,.16) 0 1.5px,transparent 1.5px 4px);-webkit-mask-image:radial-gradient(circle,transparent 0 22%,#000 22% 88%,transparent 88%);mask-image:radial-gradient(circle,transparent 0 22%,#000 22% 88%,transparent 88%)}
.pb-s1{left:2%;top:6%}.pb-s2{left:-4%;bottom:6%;width:92px;animation-delay:-2.3s}.pb-s3{right:0;bottom:2%;width:124px;animation-delay:-4.1s}
@keyframes pbs{50%{transform:translateY(-14px) rotate(24deg)}}
.pb-badge{position:absolute;z-index:3;right:2%;top:4%;width:108px;height:108px;border-radius:50%;background:#0E0F12;display:grid;place-content:center;text-align:center;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;
 transform:rotate(12deg);box-shadow:0 18px 30px -12px rgba(14,15,18,.7);animation:pbb 4s ease-in-out infinite}
.pb-badge b{display:block;font-family:'Unbounded',sans-serif;font-size:24px;letter-spacing:-.03em;color:#FF8A3D;line-height:1.1;text-transform:none}
@keyframes pbb{50%{transform:rotate(4deg) scale(1.07)}}
@media (max-width:860px){
 .pb{grid-template-columns:1fr;gap:6px;margin:12px -8px 0;padding:22px 22px 26px;border-radius:28px}
 .pb-vis{order:-1;height:220px}.pb-vis img{max-height:200px}.pb-sp{width:74px}.pb-s2{width:60px;left:2%}.pb-s3{width:82px}.pb-s1{left:8%}
 .pb-badge{width:84px;height:84px;font-size:9px;right:4%}.pb-badge b{font-size:19px}.pb-big{font-size:130px;bottom:auto;top:60px}
 .pb-d{font-size:14.5px;margin:12px 0 18px}.pb-row{gap:14px}.pb-pr b{font-size:32px}.pb-btn{width:100%;flex-wrap:nowrap}.pb-btn .btn{flex:1 1 0;text-align:center;justify-content:center;white-space:nowrap;padding-left:10px;padding-right:10px}
}
@media (prefers-reduced-motion:reduce){.pb-g1,.pb-g2,.pb-vis img,.pb-sp,.pb-badge,.pb-tag i{animation:none!important}}
"""

# порядок как в магазине: сцена → категории → популярные модели → выгоды → каталог
_p0 = markup.find('<section class="perks')
_s0 = markup.find('<section class="shw"')
if _p0 != -1 and _s0 != -1 and _p0 < _s0:
    _p1 = markup.index("</section>", _p0) + len("</section>")
    _pk = markup[_p0:_p1]; markup = markup[:_p0] + markup[_p1:]
    _s0 = markup.find('<section class="shw"'); _s1 = markup.index("</section>", _s0) + len("</section>")
    markup = markup[:_s1] + "\n" + _pk + markup[_s1:]
markup = markup.replace("<h2>Выберите свой принтер</h2>", "<h2>Популярные модели</h2>", 1)

# бегущая строка над шапкой
_tk = ["Доставка по Кыргызстану за 1 день", "1 кг пластика в подарок к принтеру", "Рассрочка без переплаты", "Шоурум в Бишкеке", "Запуск и обучение бесплатно", "Гарантия 1 год"]
_tki = "".join("<span>%s</span><i>✦</i>" % e(x) for x in _tk)
TICK = '<div class="tk"><div class="tk-r"><div class="tk-g">%s</div><div class="tk-g" aria-hidden="true">%s</div></div></div>\n' % (_tki, _tki)
_hd = markup.find("<header>")
if _hd != -1: markup = markup[:_hd] + TICK + markup[_hd:]

# нижняя панель на телефоне
_ic = lambda d: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % d
TBAR = ('<nav class="tb" aria-label="Быстрая навигация">'
        '<a href="#top" class="on">%s<span>Главная</span></a>'
        '<a href="#printers">%s<span>Каталог</span></a>'
        '<button type="button" id="tbCart">%s<span>Корзина</span><em id="tbCnt" hidden>0</em></button>'
        '<a href="https://wa.me/%s" target="_blank" rel="noopener">%s<span>WhatsApp</span></a>'
        '<a href="tel:+%s">%s<span>Позвонить</span></a></nav><i class="sp" aria-hidden="true"></i>\n') % (
    _ic('<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9.5h13V10"/>'),
    _ic('<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>'),
    _ic('<path d="M3 4h2.2l2.3 11h10.6l2-8H6.3"/><circle cx="9.5" cy="19" r="1.4"/><circle cx="17" cy="19" r="1.4"/>'), WA,
    _ic('<path d="M4 20l1.3-4.2A8 8 0 1 1 8.4 19z"/><path d="M9 9.5c0 3 2.5 5.3 5.2 5.5l1.1-1.4-1.8-1-.8.8c-.9-.4-1.6-1.1-2-2l.8-.8-1-1.8z"/>'), TEL,
    _ic('<path d="M5 4h4l1.6 4.4-2.2 1.5a11.5 11.5 0 0 0 5.7 5.7l1.5-2.2L20 15v4a1.6 1.6 0 0 1-1.7 1.6A16 16 0 0 1 3.4 5.7A1.6 1.6 0 0 1 5 4z"/>'))
_fb = markup.find('<div class="fab">')
if _fb != -1: markup = markup[:_fb] + TBAR + markup[_fb:]

css += r"""
/* ===== SKIN v3 ===== */
:root{--bg:#F3F4F6;--alt:#ECEDF0;--ink:#0E0F12;--line:#E1E3E8;--line2:#E9EAEE;--s3:cubic-bezier(.2,.8,.2,1)}
body{background:var(--bg)}
header{background:rgba(243,244,246,.82);border-bottom-color:rgba(14,15,18,.07)}
.search{background:#fff}
.sp{position:fixed;left:0;top:0;height:3px;width:100%;z-index:60;background:linear-gradient(90deg,#FF6A13,#FFB36B);transform-origin:0 50%;transform:scaleX(var(--sp,0));pointer-events:none}
.tk{background:#0E0F12;color:#EDEEF1;overflow:hidden;font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap}
.tk-r{display:flex;width:max-content;animation:tkm 38s linear infinite}.tk-g{display:flex;align-items:center;gap:22px;padding:9px 11px}
.tk i{font-style:normal;color:#FF6A13;font-size:10px}.tk:hover .tk-r{animation-play-state:paused}
@keyframes tkm{to{transform:translateX(-50%)}}
body.searching .hx,body.searching .cx,body.searching .shw{display:none}

/* сцена */
.hx{position:relative;margin-top:20px;border-radius:36px;background:#0B0C10;color:#fff;overflow:hidden;isolation:isolate;box-shadow:0 40px 80px -50px rgba(11,12,16,.8)}
.hx-bg{position:absolute;inset:0;z-index:-1;overflow:hidden}
.hx-grid{position:absolute;left:-30%;right:-30%;bottom:-4%;height:74%;transform:perspective(420px) rotateX(58deg);transform-origin:50% 100%;
 background-image:linear-gradient(rgba(255,138,61,.34) 1px,transparent 1px),linear-gradient(90deg,rgba(255,138,61,.34) 1px,transparent 1px);background-size:56px 56px;
 -webkit-mask-image:linear-gradient(to top,#000 0%,transparent 80%);mask-image:linear-gradient(to top,#000 0%,transparent 80%);animation:hxg 7s linear infinite}
@keyframes hxg{to{background-position:0 56px,0 0}}
.hx-glow{position:absolute;right:-6%;top:-20%;width:62%;aspect-ratio:1;border-radius:50%;background:radial-gradient(closest-side,rgba(255,106,19,.42),rgba(255,106,19,.08) 55%,transparent 72%);animation:hxp 6s ease-in-out infinite}
@keyframes hxp{50%{transform:scale(1.1);opacity:.75}}
.hx-c1,.hx-c2{position:absolute;width:26px;height:26px;border:2px solid rgba(255,255,255,.26)}
.hx-c1{left:22px;top:22px;border-right:0;border-bottom:0;border-radius:10px 0 0 0}.hx-c2{right:22px;bottom:22px;border-left:0;border-top:0;border-radius:0 0 10px 0}
.hx-st{display:grid}
.hx-sl{grid-area:1/1;display:grid;grid-template-columns:1.08fr .92fr;gap:24px;align-items:center;padding:64px 64px 92px;opacity:0;visibility:hidden;transition:opacity .5s ease,visibility 0s .5s}
.hx-sl.on{opacity:1;visibility:visible;transition:opacity .5s ease}
.hx-tx>*{opacity:0;transform:translateY(22px)}
.hx-sl.on .hx-tx>*{opacity:1;transform:none;transition:opacity .6s ease,transform .7s var(--s3)}
.hx-sl.on .hx-tx>*:nth-child(2){transition-delay:.07s}.hx-sl.on .hx-tx>*:nth-child(3){transition-delay:.14s}.hx-sl.on .hx-tx>*:nth-child(4){transition-delay:.21s}.hx-sl.on .hx-tx>*:nth-child(5){transition-delay:.28s}
.hx .hx-eb{display:flex;align-items:center;gap:10px;color:#FF8A3D;margin:0 0 18px;font-weight:800}
.hx .eyebrow::before{display:none}
.hx-eb i{width:8px;height:8px;border-radius:50%;background:#FF6A13;box-shadow:0 0 0 0 rgba(255,106,19,.7);animation:hxd 1.8s ease-out infinite;flex:none}
@keyframes hxd{to{box-shadow:0 0 0 12px rgba(255,106,19,0)}}
.hx h1,.hx-h{font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(34px,4.5vw,60px);line-height:1.03;letter-spacing:-.04em;text-transform:uppercase;margin:0;color:#fff;text-wrap:balance}
.hx h1 em,.hx-h em{font-style:normal;color:transparent;background:linear-gradient(92deg,#FF6A13,#FFB36B 60%,#FF6A13);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;animation:hxs 5s linear infinite}
@keyframes hxs{to{background-position:-200% 0}}
.hx .lede{color:rgba(255,255,255,.72);margin:20px 0 28px;max-width:46ch}
.hx .cta{display:flex;gap:12px;flex-wrap:wrap}
.hx .btn{position:relative;overflow:hidden;box-shadow:0 14px 34px -12px rgba(255,106,19,.8)}
.hx .btn::after{content:"";position:absolute;top:0;bottom:0;left:-60%;width:40%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.45),transparent);transform:skewX(-20deg);animation:hxb 3.6s ease-in-out infinite}
@keyframes hxb{0%,55%{left:-60%}100%{left:130%}}
.hx .btn.ghost{background:rgba(255,255,255,.07);color:#fff;border-color:rgba(255,255,255,.22);box-shadow:none;backdrop-filter:blur(6px)}.hx .btn.ghost::after{display:none}
.hx .btn.ghost:hover{background:rgba(255,255,255,.14)}
.hx-ch{list-style:none;display:flex;gap:10px;flex-wrap:wrap;margin:30px 0 0;padding:0}
.hx-ch li{border:1px solid rgba(255,255,255,.16);border-radius:14px;padding:10px 14px;background:rgba(255,255,255,.04);backdrop-filter:blur(6px);min-width:104px}
.hx-ch b{display:block;font-family:'Unbounded',sans-serif;font-size:15px;font-weight:700;letter-spacing:-.02em;white-space:nowrap}
.hx-ch span{display:block;font-size:11.5px;color:rgba(255,255,255,.6);margin-top:2px}
.hx-vis{position:relative;display:grid;place-items:center;min-height:400px}
.hx-ring{position:absolute;width:min(400px,86%);aspect-ratio:1;border-radius:50%;border:1px dashed rgba(255,255,255,.2);animation:hxr 40s linear infinite}
.hx-ring::before{content:"";position:absolute;inset:11%;border-radius:50%;border:1px solid rgba(255,106,19,.3)}
.hx-ring::after{content:"";position:absolute;left:50%;top:-5px;width:10px;height:10px;margin-left:-5px;border-radius:50%;background:#FF6A13;box-shadow:0 0 18px 4px rgba(255,106,19,.7)}
@keyframes hxr{to{transform:rotate(360deg)}}
.hx-im{position:relative;display:block;transform:translate3d(calc(var(--hx,0)*18px),calc(var(--hy,0)*14px),0);transition:transform .5s ease-out}
.hx-im img{display:block;width:auto;height:auto;max-width:min(400px,100%);max-height:400px;filter:drop-shadow(0 38px 30px rgba(0,0,0,.6));clip-path:inset(100% 0 0 0)}
.hx-sl.on .hx-im img{animation:hxprint 1.5s .15s var(--s3) both,hxfl 6s 1.8s ease-in-out infinite}
@keyframes hxprint{from{clip-path:inset(100% 0 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes hxfl{50%{transform:translateY(-12px)}}
.hx-scan{position:absolute;left:-6%;right:-6%;height:2px;bottom:0;background:linear-gradient(90deg,transparent,#FF6A13 20%,#FFD2B0 50%,#FF6A13 80%,transparent);box-shadow:0 0 22px 5px rgba(255,106,19,.6);opacity:0}
.hx-sl.on .hx-scan{animation:hxscan 1.5s .15s var(--s3) both}
@keyframes hxscan{0%{bottom:0;opacity:1}90%{opacity:1}100%{bottom:100%;opacity:0}}
.hx-hud{position:absolute;right:0;bottom:6px;font:700 10.5px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.16em;color:rgba(255,255,255,.45)}
.hx-ui{position:absolute;left:64px;right:64px;bottom:30px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.hx-dots{display:flex;gap:8px}.hx-dots button{width:54px;height:22px;padding:0;border:0;background:none;cursor:pointer;display:grid;align-items:center}
.hx-dots i{display:block;height:3px;border-radius:3px;background:rgba(255,255,255,.2);overflow:hidden;position:relative}
.hx-dots i::after{content:"";position:absolute;inset:0;background:#FF6A13;transform:scaleX(0);transform-origin:0 50%}
.hx-dots .on i::after{animation:hxbar var(--hxt,6.5s) linear forwards}.hx.hold .hx-dots .on i::after{animation-play-state:paused}
@keyframes hxbar{to{transform:scaleX(1)}}
.hx-ar{display:flex;gap:8px}.hx-ar button{width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.06);color:#fff;font-size:17px;cursor:pointer;transition:background .2s,border-color .2s,transform .2s}
.hx-ar button:hover{background:#FF6A13;border-color:#FF6A13;transform:scale(1.06)}

/* категории */
.cx{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding-top:20px}
.cx-c{position:relative;display:flex;flex-direction:column;background:#fff;border-radius:28px;padding:22px 22px 24px;overflow:hidden;border:1px solid rgba(14,15,18,.05);
 transition:transform .45s var(--s3),box-shadow .45s var(--s3);isolation:isolate}
.cx-c::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(260px circle at var(--mx,50%) var(--my,0%),rgba(255,106,19,.16),transparent 65%);opacity:0;transition:opacity .35s}
.cx-c:hover{transform:translateY(-6px);box-shadow:0 34px 50px -34px rgba(14,15,18,.4)}.cx-c:hover::before{opacity:1}
.cx-n{font:700 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.14em;color:#9A9CA5}
.cx-a{position:absolute;right:16px;top:16px;width:36px;height:36px;border-radius:50%;background:var(--bg);display:grid;place-items:center;color:#FF6A13;transition:background .3s,color .3s,transform .45s var(--s3)}
.cx-c:hover .cx-a{background:#FF6A13;color:#fff;transform:rotate(45deg)}
.cx-i{height:158px;display:flex;align-items:center;justify-content:center;margin:10px 0 16px;border-radius:18px;background:linear-gradient(160deg,#F5F6F8,#E9EAEE);overflow:hidden;transition:transform .5s var(--s3)}
.cx-i img{transition:transform .6s var(--s3)}.cx-c:hover .cx-i img{transform:scale(1.08)}
.cx-i img{max-height:132px;width:auto;max-width:100%;object-fit:contain;filter:drop-shadow(0 14px 12px rgba(14,15,18,.2))}
.cx-i img.ph{width:100%;height:100%;max-height:none;object-fit:cover;filter:none}
.cx-i.two img{max-height:128px;max-width:52%}.cx-i.two img+img{margin-left:-10%;max-height:108px}
.cx-c b{font-family:'Unbounded',sans-serif;font-size:16.5px;font-weight:700;letter-spacing:-.02em;text-transform:uppercase;line-height:1.2}
.cx-c p{margin:8px 0 0;font-size:13.5px;line-height:1.45;color:var(--mut)}

/* выгоды и каталог */
.perks{padding-top:28px}.perk{border-radius:26px;border-color:rgba(14,15,18,.05);transition:transform .4s var(--s3),box-shadow .4s var(--s3)}
.perk:hover{transform:translateY(-4px);box-shadow:0 26px 44px -30px rgba(14,15,18,.4)}
.perk.dk{background:#0E0F12;border-color:#0E0F12}
.shw-head h2,.chead h2{text-transform:uppercase;letter-spacing:-.03em}
.chead h2{position:relative;padding-left:20px}.chead h2::before{content:"";position:absolute;left:0;top:.14em;bottom:.14em;width:6px;border-radius:3px;background:linear-gradient(#FF6A13,#FFB36B)}
.card{position:relative;border-radius:24px;border-color:rgba(14,15,18,.06);background:#fff;transition:transform .4s var(--s3),box-shadow .4s var(--s3),border-color .3s;isolation:isolate}
.card::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:radial-gradient(240px circle at var(--mx,50%) var(--my,0%),rgba(255,106,19,.13),transparent 65%);opacity:0;transition:opacity .3s;z-index:1}
@media (hover:hover){.card:hover{transform:translateY(-6px);box-shadow:0 34px 50px -34px rgba(14,15,18,.42);border-color:rgba(255,106,19,.4)}.card:hover::after{opacity:1}
 .card .ph img{transition:transform .6s var(--s3)}.card:hover .ph img{transform:scale(1.06)}}
.card .cb,.card .vis{position:relative;z-index:2}
.card .pr b{font-family:'Unbounded',sans-serif;letter-spacing:-.03em}
.badge{background:#FF6A13;border-radius:999px;padding:5px 11px}
.act .addb{border-radius:12px;transition:transform .2s,box-shadow .25s,filter .2s}.act .addb:not(.dis):hover{transform:translateY(-1px);box-shadow:0 12px 22px -10px rgba(255,106,19,.8)}

/* нижняя панель */
.tb{display:none}
@media (max-width:860px){
 .tk{font-size:10px;letter-spacing:.12em}.tk-g{gap:16px;padding:7px 8px}
 .hx{margin:12px -8px 0;border-radius:28px}
 .hx-sl{grid-template-columns:1fr;gap:0;padding:26px 22px 78px;align-content:start}
 .hx-vis{order:-1;min-height:196px;margin-bottom:12px}.hx-ring{width:196px}
 .hx-im img{max-height:186px;max-width:220px}
 .hx h1,.hx-h{font-size:clamp(29px,8.6vw,40px)}
 .hx .lede{font-size:15px;margin:14px 0 20px}
 .hx .cta{gap:8px;flex-wrap:nowrap}.hx .cta .btn{flex:1 1 0;text-align:center;justify-content:center;padding-left:10px;padding-right:10px;font-size:14px;white-space:nowrap}
 .hx-ch{gap:8px;margin-top:20px;flex-wrap:nowrap}.hx-ch li{min-width:0;flex:1 1 0;padding:9px 10px;border-radius:12px}.hx-ch b{font-size:12.5px}.hx-ch span{font-size:10.5px;line-height:1.25}
 .hx-ui{left:22px;right:22px;bottom:22px}.hx-ar{display:none}.hx-dots{width:100%}.hx-dots button{flex:1;width:auto}
 .hx-hud{display:none}.hx-c1{left:14px;top:14px}.hx-c2{right:14px;bottom:14px}
 .cx{grid-template-columns:1fr 1fr;gap:10px;padding-top:12px}.cx-c{border-radius:22px;padding:16px 14px 18px}.cx-i{height:108px;margin:8px 0 12px;border-radius:14px}.cx-i img{max-height:92px}.cx-i.two img{max-height:90px}.cx-i.two img+img{max-height:76px}
 .cx-c b{font-size:13px}.cx-c p{font-size:12px}.cx-a{width:30px;height:30px;right:10px;top:10px}
 .card{border-radius:20px}
 .fab{display:none}
 body{padding-bottom:calc(66px + env(safe-area-inset-bottom))}
 .tb{position:fixed;left:10px;right:10px;bottom:calc(8px + env(safe-area-inset-bottom));z-index:46;display:grid;grid-template-columns:repeat(5,1fr);height:60px;border-radius:22px;
  background:rgba(14,15,18,.9);-webkit-backdrop-filter:blur(16px) saturate(1.5);backdrop-filter:blur(16px) saturate(1.5);box-shadow:0 18px 40px -14px rgba(14,15,18,.6);color:rgba(255,255,255,.62);transition:transform .35s var(--s3)}
 .tb.hide{transform:translateY(140%)}
 .tb a,.tb button{position:relative;display:grid;place-items:center;align-content:center;gap:3px;border:0;background:none;color:inherit;font:700 10px/1 'Manrope',sans-serif;padding:0;cursor:pointer;-webkit-tap-highlight-color:transparent}
 .tb a.on,.tb button.on{color:#fff}.tb a.on svg{color:#FF6A13}
 .tb em{position:absolute;top:7px;left:calc(50% + 6px);min-width:17px;height:17px;border-radius:9px;background:#FF6A13;color:#fff;font:800 10px/17px 'Manrope',sans-serif;font-style:normal;text-align:center;padding:0 4px}
 .tb em.pop{animation:tbp .45s var(--s3)}
}
@keyframes tbp{40%{transform:scale(1.5)}}
@media (max-width:860px) and (max-height:500px){.tb{display:none}body{padding-bottom:0}}
@media (prefers-reduced-motion:reduce){
 .tk-r,.hx-grid,.hx-glow,.hx-ring,.hx-eb i,.hx h1 em,.hx-h em,.hx .btn::after,.hx-scan,.hx-dots .on i::after{animation:none!important}
 .hx-im img,.hx-sl.on .hx-im img{clip-path:none;animation:none}.hx-tx>*{opacity:1;transform:none}
}
"""
open(os.path.join(dist, "style.css"), "w", encoding="utf-8").write(css)

SK3JS = """<script>(function(){
var rm=matchMedia('(prefers-reduced-motion:reduce)').matches,d=document;
/* слайдер сцены */
var hx=d.querySelector('.hx');if(hx){var sl=[].slice.call(hx.querySelectorAll('.hx-sl')),dt=[].slice.call(hx.querySelectorAll('.hx-dots button')),cur=0,tm=0,T=6500,vis=true;
function show(i){i=(i+sl.length)%sl.length;if(i===cur)return;sl[cur].classList.remove('on');dt[cur].classList.remove('on');cur=i;sl[i].classList.add('on');void dt[i].offsetWidth;dt[i].classList.add('on');arm()}
function arm(){clearTimeout(tm);if(rm||!vis||hx.classList.contains('hold'))return;tm=setTimeout(function(){show(cur+1)},T)}
dt.forEach(function(b,i){b.addEventListener('click',function(){show(i)})});
var pv=hx.querySelector('.hx-prev'),nx=hx.querySelector('.hx-next');if(pv)pv.addEventListener('click',function(){show(cur-1)});if(nx)nx.addEventListener('click',function(){show(cur+1)});
hx.addEventListener('mouseenter',function(){hx.classList.add('hold');clearTimeout(tm)});hx.addEventListener('mouseleave',function(){hx.classList.remove('hold');dt[cur].classList.remove('on');void dt[cur].offsetWidth;dt[cur].classList.add('on');arm()});
hx.addEventListener('mousemove',function(ev){var r=hx.getBoundingClientRect();hx.style.setProperty('--hx',((ev.clientX-r.left)/r.width-.5).toFixed(3));hx.style.setProperty('--hy',((ev.clientY-r.top)/r.height-.5).toFixed(3))});
var x0=null,y0=0;hx.addEventListener('touchstart',function(ev){x0=ev.touches[0].clientX;y0=ev.touches[0].clientY},{passive:true});
hx.addEventListener('touchend',function(ev){if(x0===null)return;var dx=ev.changedTouches[0].clientX-x0,dy=ev.changedTouches[0].clientY-y0;x0=null;if(Math.abs(dx)>46&&Math.abs(dx)>Math.abs(dy)*1.4)show(cur+(dx<0?1:-1))},{passive:true});
if('IntersectionObserver' in window){new IntersectionObserver(function(en){vis=en[0].isIntersecting;if(vis)arm();else clearTimeout(tm)},{threshold:.3}).observe(hx)}
d.addEventListener('visibilitychange',function(){if(d.hidden)clearTimeout(tm);else arm()});arm()}
/* баннер акции: в корзину */
var pa=d.querySelector('.pb-add');if(pa)pa.addEventListener('click',function(){var x=d.querySelector('.act[data-id="'+pa.dataset.pid+'"] .addb:not(.dis)');if(x){x.click();pa.classList.add('ok');pa.textContent='Добавлено ✓';setTimeout(function(){pa.classList.remove('ok');pa.textContent='В корзину'},1800)}else{location.href=pa.nextElementSibling.href}});
/* подсветка за курсором */
if(matchMedia('(hover:hover)').matches){d.addEventListener('pointermove',function(ev){var c=ev.target.closest&&ev.target.closest('.card,.cx-c');if(!c)return;var r=c.getBoundingClientRect();c.style.setProperty('--mx',(ev.clientX-r.left)+'px');c.style.setProperty('--my',(ev.clientY-r.top)+'px')},{passive:true})}
/* полоса прокрутки и нижняя панель */
var sp=d.querySelector('.sp'),tb=d.querySelector('.tb'),ly=0,tk=0;
function sc(){tk=0;var y=scrollY,h=d.documentElement.scrollHeight-innerHeight;if(sp)sp.style.setProperty('--sp',h>0?(y/h).toFixed(4):0);
if(tb){var a=tb.querySelectorAll('a');var inCat=!d.body.classList.contains('home');a[0].classList.toggle('on',!inCat);a[1].classList.toggle('on',!!inCat)}ly=y}
addEventListener('scroll',function(){if(!tk)tk=requestAnimationFrame(sc)},{passive:true});sc();
var tc=d.getElementById('tbCart'),fc=d.getElementById('fabCart'),fn=d.getElementById('fcnt'),tn=d.getElementById('tbCnt');
if(tc&&fc)tc.addEventListener('click',function(){fc.click()});
function syn(){if(!fn||!tn)return;var v=parseInt(fn.textContent,10)||0;if(String(v)!==tn.textContent&&v>0){tn.classList.remove('pop');void tn.offsetWidth;tn.classList.add('pop')}tn.textContent=v;tn.hidden=v<1}
if(fn&&tn&&'MutationObserver' in window){new MutationObserver(syn).observe(fn,{childList:true,characterData:true,subtree:true});syn()}
})();</script>
"""
