window.GIFT = {"a1": "+ 3 кг филамента в подарок"};
const WA = "996559992306";
const KEY = "bl_cart_v1";
const fmt = (n) => n.toLocaleString("ru-RU").replace(/ /g, " ") + " сом";

var admReady = false;
const isAsk = (id) => admReady && BASE.has(id) && !CRM[id];
const askWA = (n) => { const wa = ((adm && adm.s && adm.s.wa) || WA).replace(/\D/g, ""); window.open("https://wa.me/" + wa + "?text=" + encodeURIComponent("Здравствуйте! Интересует " + n + ". Подскажите, пожалуйста, цену и срок поставки."), "_blank", "noopener"); };
let cart = {};
try { cart = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { cart = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) {} };

const $ = (s) => document.querySelector(s);
const cnt = $("#cnt"), items = $("#items"), total = $("#total");
const fcnt = $("#fcnt");

/* ---------- product controls ---------- */
let acts = [];
let paint = () => {
  acts.forEach((el) => {
    const id = el.dataset.id, q = cart[id]?.q || 0;
    if (isAsk(id)) { el.innerHTML = '<button type="button" class="addb ask">Узнать цену</button>'; return; }
    if (hasVar(id)) { el.innerHTML = '<button type="button" class="addb pick">Выбрать цвет</button>'; return; }
    const st = stockOf(id);
    if (st != null && st <= 0) {
      el.innerHTML = '<button type="button" class="addb dis" disabled>Нет в наличии</button>';
      return;
    }
    if (q > 0) {
      el.innerHTML =
        '<div class="step"><button type="button" data-d="-1" aria-label="Меньше">−</button>' +
        '<i>' + q + '</i><button type="button" data-d="1" aria-label="Больше">+</button></div>';
    } else {
      el.innerHTML = '<button type="button" class="addb">В корзину</button>';
    }
  });
  const n = Object.values(cart).reduce((a, x) => a + x.q, 0);
  cnt.textContent = n;
  fcnt.textContent = n;
  fcnt.classList.toggle("zero", n === 0);
  renderCart();
};

const bump = (el, d) => {
  const id = el.dataset.id;
  if (isAsk(id)) { askWA(el.dataset.n); return; }
  if (hasVar(id)) { openPicker(id); return; }
  const cur = cart[id]?.q || 0;
  const st = stockOf(id);
  if (d > 0 && st != null && cur + d > st) { toast(st <= 0 ? "Товара нет в наличии" : "Осталось всего " + st + " шт"); return; }
  const next = cur + d;
  if (next <= 0) delete cart[id];
  else cart[id] = { n: el.dataset.n, p: +el.dataset.p, q: next };
  save(); paint();
  if (d > 0) {
    fcnt.classList.add("pop");
    setTimeout(() => fcnt.classList.remove("pop"), 190);
  }
  if (d > 0 && cur === 0) toast(el.dataset.n + " — в корзине");
};

document.addEventListener("click", (e) => {
  if (e.target.closest("#items")) return;
  const ask = e.target.closest(".askb");
  if (ask) {
    const wa = (adm?.s?.wa || WA).replace(/\D/g, "");
    const t = "Здравствуйте! Интересует промышленное оборудование: " + ask.dataset.ask +
      "\nРасскажите, пожалуйста, про цену и сроки.";
    window.open("https://wa.me/" + wa + "?text=" + encodeURIComponent(t), "_blank", "noopener");
    return;
  }
  const add = e.target.closest(".addb");
  const st = e.target.closest(".step button");
  if (add) bump(add.closest(".act"), 1);
  else if (st) bump(st.closest(".act"), +st.dataset.d);
});

/* ---------- cart ---------- */
const sum = () => Object.values(cart).reduce((a, x) => a + x.p * x.q, 0);

function renderCart() {
  const keys = Object.keys(cart);
  if (!keys.length) {
    items.innerHTML = '<div class="cempty">Корзина пока пустая.<br>Добавьте принтер, филамент или запчасть.</div>';
  } else {
    items.innerHTML = keys.map((id) => {
      const it = cart[id];
      return '<div class="row"><div class="rn"><b>' + it.n + '</b><span>' +
        fmt(it.p) + " × " + it.q + " = " + fmt(it.p * it.q) + '</span></div>' +
        '<div class="act" data-id="' + id + '" data-n="' + it.n + '" data-p="' + it.p + '">' +
        '<div class="step"><button type="button" data-d="-1">−</button><i>' + it.q +
        '</i><button type="button" data-d="1">+</button></div></div>' +
        '<button class="del" data-del="' + id + '" aria-label="Удалить">×</button></div>';
    }).join("");
  }
  total.textContent = fmt(sum());
}

items.addEventListener("click", (e) => {
  const del = e.target.closest("[data-del]");
  if (del) { delete cart[del.dataset.del]; save(); paint(); return; }
  const st = e.target.closest(".step button");
  if (st) bump(st.closest(".act"), +st.dataset.d);
});

/* ---------- drawer ---------- */
const drawer = $("#drawer"), scrim = $("#scrim");
const openCart = () => { drawer.classList.add("on"); scrim.classList.add("on"); };
const closeCart = () => { drawer.classList.remove("on"); scrim.classList.remove("on"); };
$("#cartBtn").addEventListener("click", openCart);
$("#fabCart").addEventListener("click", openCart);
$("#dClose").addEventListener("click", closeCart);
scrim.addEventListener("click", closeCart);

/* ---------- search ---------- */
let sections = [], allCards = [];
const baseCount = new Map();
const CNUM0 = new Map();
document.querySelectorAll("section.cat").forEach((s) => {
  const el = s.querySelector(".cnum");
  if (el) CNUM0.set(s, el.textContent);
});
function rescan() {
  sections = [...document.querySelectorAll("section.cat")];
  allCards = [...document.querySelectorAll("section.cat .card")];
  acts = [...document.querySelectorAll(".act")];
  sections.forEach((s) => {
    const el = s.querySelector(".cnum");
    if (!el) return;
    const t0 = CNUM0.get(s) || "";
    const n = [...s.querySelectorAll(".card")].filter((c) => !c.classList.contains("off")).length;
    baseCount.set(s, /\d/.test(t0) ? t0.replace(/^\d+/, n) : t0);
  });
}
rescan();
let query = "";

const apply = () => {
  let shown = 0;
  allCards.forEach((c) => {
    const on = !c.classList.contains("off") && (!query || c.dataset.name.includes(query));
    c.classList.toggle("hide", !on);
    if (on) shown++;
  });
  sections.forEach((s) => {
    const vis = [...s.querySelectorAll(".card")].filter((c) => !c.classList.contains("hide") && !c.classList.contains("off")).length;
    s.classList.toggle("hide", vis === 0);
    const el = s.querySelector(".cnum");
    if (el) el.textContent = query ? vis + " найдено" : baseCount.get(s);
  });
  document.body.classList.toggle("searching", !!query);
  $("#empty").classList.toggle("on", shown === 0);
};

$("#q").addEventListener("input", (e) => {
  const was = query;
  query = e.target.value.trim().toLowerCase();
  $("#searchBox").classList.toggle("has", !!e.target.value);
  apply();
  if (!was && query) {
    const t = document.getElementById("searchTop");
    const top = t.getBoundingClientRect().top;
    if (top < 0 || top > innerHeight * 0.5) t.scrollIntoView({ block: "start" });
  }
});

$("#qx").addEventListener("click", () => {
  const q = $("#q");
  q.value = ""; query = "";
  $("#searchBox").classList.remove("has");
  apply(); q.focus();
});
$("#q").addEventListener("keydown", (e) => { if (e.key === "Escape") $("#qx").click(); });

/* ---------- checkout ---------- */
const mask = $("#mask");
const orderText = () => {
  const keys = Object.keys(cart);
  if (!keys.length) return "";
  return keys.map((id) => "• " + cart[id].n + " × " + cart[id].q + " — " + fmt(cart[id].p * cart[id].q)).join("\n") +
    "\nИтого: " + fmt(sum());
};
const fill = () => { $("#orderbox").textContent = orderText() || "Корзина пустая"; };

$("#toCheckout").addEventListener("click", () => {
  if (!Object.keys(cart).length) { toast("Сначала добавьте товар"); return; }
  closeCart(); fill(); $("#ok").classList.remove("on"); mask.classList.add("on");
  setTimeout(() => $("#nm").focus(), 50);
});
$("#mClose").addEventListener("click", () => mask.classList.remove("on"));
mask.addEventListener("click", (e) => { if (e.target === mask) mask.classList.remove("on"); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { mask.classList.remove("on"); closeCart(); }
});

const compose = () => [
  "Заказ с сайта 3D HOUSE",
  "",
  orderText(),
  "",
  "Имя: " + ($("#nm").value.trim() || "—"),
  "Телефон: " + ($("#ph").value.trim() || "—"),
  "Доставка: " + $("#dl").value,
  $("#cm").value.trim() ? "Комментарий: " + $("#cm").value.trim() : null,
].filter((x) => x !== null).join("\n");

const valid = () => {
  if (!$("#nm").value.trim() || !$("#ph").value.trim()) { toast("Заполните имя и телефон"); return false; }
  return true;
};

$("#co").addEventListener("submit", (e) => {
  e.preventDefault();
  if (!valid()) return;
  const txt = compose();
  try { logOrder(); } catch (err) {}
  $("#okPre").textContent = txt;
  $("#ok").classList.add("on");
  window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(txt), "_blank", "noopener");
});

/* ---------- toast ---------- */
let tt;
function toast(msg) {
  const el = $("#toast");
  el.textContent = msg; el.classList.add("on");
  clearTimeout(tt); tt = setTimeout(() => el.classList.remove("on"), 1900);
}

paint();

/*CRM-MAP-START*/
const CRM_MAP = {"a1mini": {"doc": "ml1ux7tezwuehkmyt8x3", "n": "Bambu Lab A1 mini (Китай)", "d": "180 × 180 × 180 мм · китайская версия: нужен компьютер и Wi-Fi"}, "a1": {"doc": "8tge6lb0389tw2e1d94i", "n": "Bambu Lab A1 (Китай)", "d": "256 × 256 × 256 мм · китайская версия: нужен компьютер и Wi-Fi"}, "a1c": {"doc": "bl-a1-combo-eu", "n": "Bambu Lab A1 Combo (EU)"}, "a2l": {"doc": "bl-a2l-combo-eu", "n": "Bambu Lab A2L Combo (EU)"}, "a2lcn": {"doc": "bl-a2l-combo-cn"}, "p1s": {"doc": "bl-p1s-combo-eu", "n": "Bambu Lab P1S Combo (EU)"}, "p2s": {"doc": "bl-p2s"}, "x2d": {"doc": "bl-x2d-combo-eu"}, "u1": {"doc": "snapmaker-u1"}, "cr5": {"doc": "8f2p48r9wqnecw0sur3i"}, "amsl": {"doc": "bl-ams-lite-eu"}, "cut": {"doc": "imd9w275pkacd8bzlp"}, "glue": {"doc": "glue3dhaus01"}, "pla": {"cat": "Филамент / PLA Basic", "dd": "Универсальный. Сувенирка и прототипы"}, "plam": {"cat": "Филамент / PLA Matte", "dd": "Матовая поверхность без бликов"}, "plas": {"cat": "Филамент / PLA+ Silk", "dd": "Шёлковый блеск и двухцветные переливы", "n": "PLA+ Silk"}, "petg": {"cat": "Филамент / PETG Basic", "dd": "Прочнее PLA, не боится улицы", "n": "PETG Basic"}, "asa": {"cat": "Филамент / ASA", "dd": "Не выгорает на солнце", "n": "ASA"}, "tpu95": {"cat": "Филамент / TPU 90A", "dd": "Гибкий: чехлы, прокладки, ремешки", "n": "TPU 90A"}, "tpuams": {"cat": "Филамент / Bambu Lab TPU 90A", "dd": "Оригинальный гибкий пластик Bambu Lab", "n": "Bambu Lab TPU 90A"}, "fplus": {"cat": "Филамент / PLA+", "dd": "Прочнее обычного PLA"}, "fpro": {"cat": "Филамент / PLA Pro", "dd": "Повышенная прочность"}, "ftr": {"cat": "Филамент / PLA Translucent", "dd": "Полупрозрачный"}, "fglow": {"cat": "Филамент / PLA Glow", "dd": "Светится в темноте"}, "fwood": {"cat": "Филамент / PLA Wood", "dd": "С эффектом дерева"}, "fmar": {"cat": "Филамент / PLA Marble", "dd": "С эффектом камня"}, "fgal": {"cat": "Филамент / PLA Galaxy", "dd": "Переливается разными цветами"}, "fspk": {"cat": "Филамент / PLA Sparkle", "dd": "С блёстками"}, "fpm": {"cat": "Филамент / PETG Matte", "dd": "Матовый PETG"}, "fps": {"cat": "Филамент / PETG Sparkle", "dd": "PETG с блёстками"}, "fblb": {"cat": "Филамент / Bambu Lab PLA Basic", "dd": "Оригинальный пластик Bambu Lab"}, "fblm": {"cat": "Филамент / Bambu Lab PLA Matte", "dd": "Оригинальный Bambu Lab, матовый"}};
/*CRM-MAP-END*/
/*CRM-SYNC-START*/
const CRM = {"a1mini": {"p": 23000, "q": 0, "d": "180 × 180 × 180 мм · китайская версия: нужен компьютер и Wi-Fi", "n": "Bambu Lab A1 mini (Китай)"}, "a1": {"p": 29900, "q": 0, "d": "256 × 256 × 256 мм · китайская версия: нужен компьютер и Wi-Fi", "n": "Bambu Lab A1 (Китай)"}, "a1c": {"p": 47500, "q": 0, "n": "Bambu Lab A1 Combo (EU)"}, "a2l": {"p": 63500, "q": 4, "n": "Bambu Lab A2L Combo (EU)"}, "a2lcn": {"p": 58000, "q": 3}, "p1s": {"p": 66000, "q": 3, "n": "Bambu Lab P1S Combo (EU)"}, "p2s": {"p": 95000, "q": 5}, "x2d": {"p": 118000, "q": 2}, "u1": {"p": 105000, "q": 50}, "cr5": {"p": 80000, "q": 1}, "amsl": {"p": 20000, "q": 8}, "cut": {"p": 200, "q": 37}, "glue": {"p": 1100, "q": 0}, "pla": {"p": 1000, "q": 592, "cl": "Белый, Чёрный, Зелёный, Жёлтый, Серый, Телесный, Пурпурный (маджента), Красный, Ярко-жёлтый, Кофейный, Розовый, Костяной белый, Голубой (циан), Кленовый оранжевый, Нефритово-белый, Тёмное дерево, Синий, Коричневый, Красно-фиолетовый, Ледяной голубой, Индиго, Тёмно-синий (navy), Бирюзовый, Небесно-голубой, Бордовый, Фиолетовый, Тыквенный оранжевый, Шоколадный, Тёмно-синий, Сине-серый, Бирюзово-зелёный, Лавандовый, Тёмно-зелёный, Зелёный (Future Green), Солнечный оранжевый, Синий Кляйна, Технический синий", "d": "Универсальный. Сувенирка и прототипы · 1 кг · 37 цветов", "v": [["ue28g6x85wwjotbqp3yj", "Белый", "White", 1000, 85, "1 кг"], ["iog85cy9if8r2idf61va", "Чёрный", "Black", 1000, 51, "1 кг"], ["9b033ho9z5av1hk1x0or", "Зелёный", "Green", 1000, 37, "1 кг"], ["ozt95eoasl7gw9hk58ba", "Жёлтый", "Yellow", 1000, 33, "1 кг"], ["44ba3alr1ox86d4gsyfo", "Серый", "Grey", 1000, 30, "1 кг"], ["801mdut4j7zmluesjd66", "Телесный", "Skin Tone", 1000, 27, "1 кг"], ["8wbqpaohy5wamlqdi35i", "Пурпурный (маджента)", "Magenta", 1000, 26, "1 кг"], ["34o6s6eg84dkyzsh2fy6", "Красный", "Red", 1000, 22, "1 кг"], ["ykplabasicbrightyellow", "Ярко-жёлтый", "Bright Yellow", 1000, 20, "1 кг"], ["ykplabasiccoffeebrown", "Кофейный", "Coffee Brown", 1000, 20, "1 кг"], ["a5v254h2s8ia0kcxv4l8", "Розовый", "Pink", 1000, 19, "1 кг"], ["ykplabasicbonewhite", "Костяной белый", "Bone White", 1000, 19, "1 кг"], ["ykplabasiccyan", "Голубой (циан)", "Cyan", 1000, 19, "1 кг"], ["ykplabasicmapleorange", "Кленовый оранжевый", "Maple Orange", 1000, 19, "1 кг"], ["zw5xdawbebdlkbm7y3sz", "Нефритово-белый", "Jade White", 1000, 15, "1 кг"], ["9ka65m3fn26w2isnifni", "Тёмное дерево", "Dark Wood", 1000, 14, "1 кг"], ["3zi2b3fhx0cuaifwupup", "Синий", "Blue", 1000, 13, "1 кг"], ["8wphru3ct0ztbma63l19", "Коричневый", "Brown", 1000, 11, "1 кг"], ["sw6ws4j35eftomb3m1i8", "Красно-фиолетовый", "Reddish Purple", 1000, 11, "1 кг"], ["ykplabasiciceblue", "Ледяной голубой", "Ice Blue", 1000, 10, "1 кг"], ["ykplabasicindigopurple", "Индиго", "Indigo Purple", 1000, 10, "1 кг"], ["ykplabasicnavy", "Тёмно-синий (navy)", "Navy", 1000, 10, "1 кг"], ["ykplabasicturquoise", "Бирюзовый", "Turquoise", 1000, 10, "1 кг"], ["nbwj3y2auwqswmkw6ovi", "Небесно-голубой", "Sky Blue", 1000, 9, "1 кг"], ["ykplabasicmardyred", "Бордовый", "PLA Maroon Red", 1000, 9, "1 кг"], ["ykplabasicpurple", "Фиолетовый", "Purple", 1000, 9, "1 кг"], ["3s1k65b7r7lnbm2820a1", "Тыквенный оранжевый", "Pumpkin Orange", 1000, 6, "1 кг"], ["npdqynufxc6rwai6dbtl", "Шоколадный", "Chocolate", 1000, 6, "1 кг"], ["qngml9s8ss4dqnpp0ksq", "Тёмно-синий", "Dark Blue", 1000, 6, "1 кг"], ["5c8knfn56frr2g3nqnzf", "Сине-серый", "Blue Grey", 1000, 5, "1 кг"], ["q0e5uxcpb78hkdl7w82l", "Бирюзово-зелёный", "Turquoise Green", 1000, 5, "1 кг"], ["5m2z9r33cxcxyhxyknv6", "Лавандовый", "Lavender", 1000, 1, "1 кг"], ["6bknpyxof9xa0vvf0etr", "Тёмно-зелёный", "Dark Green", 1000, 1, "1 кг"], ["6d75zmmhe84d7k5w9osm", "Зелёный (Future Green)", "Future Green", 1000, 1, "1 кг"], ["gc30dpw6ytrhixfiinq1", "Солнечный оранжевый", "Sun Orange", 1000, 1, "1 кг"], ["ged2t672t8o92ysywc6b", "Синий Кляйна", "Klein Blue", 1000, 1, "1 кг"], ["gw2m2s3ze7jqd34s6i0s", "Технический синий", "Tech Blue", 1000, 1, "1 кг"], ["dsjqkc95aolo03xgyhwh", "Розовый (сакура)", "Cherry Blossom Pink", 1000, 0, "1 кг"]]}, "plam": {"p": 1100, "q": 267, "cl": "Белый, Чёрный, Серый, Зелёный, Жёлтый, Яблочно-зелёный, Синий, Костяной белый, Коричневый, Тёмно-зелёный, Латинский фиолетовый, Оранжевый, Фиолетовый, Ледяной голубой, Красный, Телесный, Алый", "d": "Матовая поверхность без бликов · 1 кг · 17 цветов", "v": [["imlqsaj08xui6d39zz", "Белый", "White", 1100, 50, "1 кг"], ["im3efr4edt2sywb3wk", "Чёрный", "Black", 1100, 49, "1 кг"], ["imh5dnsipzz5fk2z9r", "Серый", "Gray", 1100, 22, "1 кг"], ["ykplamattegreen", "Зелёный", "Green", 1100, 20, "1 кг"], ["imzzg4zdmen2khvdga", "Жёлтый", "Yellow", 1100, 17, "1 кг"], ["ykplamatteapplegreen", "Яблочно-зелёный", "Apple Green", 1100, 10, "1 кг"], ["ykplamatteblue", "Синий", "Blue", 1100, 10, "1 кг"], ["ykplamattebonewhite", "Костяной белый", "Bone White", 1100, 10, "1 кг"], ["ykplamattebrown", "Коричневый", "Brown", 1100, 10, "1 кг"], ["ykplamattedarkgreen", "Тёмно-зелёный", "Dark Green", 1100, 10, "1 кг"], ["ykplamattelatinpurple", "Латинский фиолетовый", "Latin Purple", 1100, 10, "1 кг"], ["ykplamatteorange", "Оранжевый", "Orange", 1100, 10, "1 кг"], ["ykplamattepurple", "Фиолетовый", "Purple", 1100, 10, "1 кг"], ["ykplamatteiceblue", "Ледяной голубой", "Ice Blue", 1100, 9, "1 кг"], ["ykplamattered", "Красный", "Red", 1100, 9, "1 кг"], ["ykplamatteskintone", "Телесный", "Skin Tone", 1100, 8, "1 кг"], ["imi19r0wyojfljooa5", "Алый", "Scarlet", 1100, 3, "1 кг"], ["ykplamattered250", "Красный", "Red", 250, 10, "250 г"]]}, "plas": {"p": 1100, "q": 97, "cl": "Белый, Зелёный, Золотой, Серый, Золотисто-розовый, Чёрный, Красный, Серебристый, Сине-чёрный (двухцветный), Чёрно-красный (двухцветный), Сине-розовый (двухцветный)", "d": "Шёлковый блеск и двухцветные переливы · 1 кг · 11 цветов", "v": [["imbqcab69m64p2g158", "Белый", "Silk White", 1100, 12, "1 кг"], ["imhkqdlmtt7ns26lrw", "Зелёный", "Silk Green", 1100, 12, "1 кг"], ["imqfoeqh3av90ric7p", "Золотой", "Silk Golden", 1100, 12, "1 кг"], ["im6zv0mwufxbv932by", "Серый", "Grey", 1100, 10, "1 кг"], ["imthjxjqi3ogz5kok1", "Золотисто-розовый", "Gold Pink", 1200, 10, "1 кг"], ["ykplasilkblack", "Чёрный", "Black", 1100, 10, "1 кг"], ["imv7s6ehogfqrclri1", "Красный", "Red", 1100, 9, "1 кг"], ["imz6tnovmizwdiaeq1", "Серебристый", "Silver", 1100, 8, "1 кг"], ["im29be2u66mr26846p", "Сине-чёрный (двухцветный)", "Blue Black", 1200, 5, "1 кг"], ["ykplasilkblackred", "Чёрно-красный (двухцветный)", "Black Red", 1200, 5, "1 кг"], ["ykplasilkbluepink", "Сине-розовый (двухцветный)", "Blue Pink", 1200, 4, "1 кг"], ["imqzj865ufrdl1erbf", "Красно-зелёный (двухцветный)", "Red Green", 1200, 0, "1 кг"], ["im7q9m2i0hz2uep1en", "Сине-красный (двухцветный)", "Blue Red", 1200, 0, "1 кг"]], "n": "PLA+ Silk"}, "petg": {"p": 1000, "q": 736, "cl": "Чёрный, Белый, Глубокий чёрный, Оливковый, Красный, Оранжевый, Жёлтый, Синий, Серый, Прозрачный фиолетовый, Розовый, Зелёный, Фиолетовый, Прозрачный белый, Лавандово-фиолетовый, Золотой, Солнечный оранжевый, Ярко-жёлтый, Тёмно-фиолетовый, Павлиний зелёный, Павлиний синий, Ярко-красный", "d": "Прочнее PLA, не боится улицы · 1 кг · 22 цвета", "v": [["impr16umx1bz99nfd0", "Чёрный", "Black", 1000, 130, "1 кг"], ["im52loi03p8hssrrxq", "Белый", "White", 1000, 111, "1 кг"], ["ykpetgbasicnightblack", "Глубокий чёрный", "Night Black", 1000, 60, "1 кг"], ["im0tdbm50fqo1xo5cv", "Оливковый", "Olive Green", 1000, 59, "1 кг"], ["impzcyc3edqmevxrvc", "Красный", "Red", 1000, 52, "1 кг"], ["im0xzmas6en5mtmo3o", "Оранжевый", "Orange", 1000, 49, "1 кг"], ["imqm2plppjsmuezqp6", "Жёлтый", "Yellow", 1000, 39, "1 кг"], ["im2is5d9ik40vstqqz", "Синий", "Blue", 1000, 34, "1 кг"], ["imez732pgojj7g3f9c", "Серый", "Gray", 1000, 30, "1 кг"], ["im5latjpuu3xf6mzkp", "Прозрачный фиолетовый", "Transparent Purple", 1000, 28, "1 кг"], ["imyxv2kgafrfw0h9ny", "Розовый", "Pink", 1000, 25, "1 кг"], ["imaioctiq71hget7my", "Зелёный", "Green", 1000, 24, "1 кг"], ["imwt1fd4mx82mux4b0", "Фиолетовый", "Purple", 1000, 24, "1 кг"], ["im0ec498uk1geqfng0", "Прозрачный белый", "Transparent White", 1000, 23, "1 кг"], ["imqoaa8t3rup47p9pb", "Лавандово-фиолетовый", "Lavender Purple", 1000, 11, "1 кг"], ["imnfrpyz21tbic145a", "Золотой", "Gold", 1000, 9, "1 кг"], ["imqurtaebog43yq15i", "Солнечный оранжевый", "Sunny Orange", 1000, 7, "1 кг"], ["im21i9mpflv9fupxqm", "Ярко-жёлтый", "Bright Yellow", 1000, 5, "1 кг"], ["imb0y07nyrvd5rxi67", "Тёмно-фиолетовый", "Dark Purple", 1000, 5, "1 кг"], ["imddlz2uhfkvml73ct", "Павлиний зелёный", "Peacock Green", 1000, 5, "1 кг"], ["imqsg5lo50djzdnbj0", "Павлиний синий", "Peacock Blue", 1000, 5, "1 кг"], ["impt49zhkken659o2v", "Ярко-красный", "Bright Red", 1000, 1, "1 кг"], ["im7og3cga4o2xcsohd", "Белый", "White", 250, 40, "200 г"]], "n": "PETG Basic"}, "asa": {"p": 250, "q": 15, "cl": "Серый, Красный, Белый", "d": "Не выгорает на солнце · 250 г · 3 цвета", "v": [["imyfkozm4lncz7kywh", "Серый", "Gray", 250, 7, "250 г"], ["imjpmc9cuhy39t0tp1", "Красный", "Red", 250, 4, "250 г"], ["imyx262lba53p23l4z", "Белый", "White", 250, 4, "250 г"]], "n": "ASA"}, "tpu95": {"p": 1800, "q": 7, "cl": "Синий (желе), Персиково-розовый", "d": "Гибкий: чехлы, прокладки, ремешки · 1 кг · 2 цвета", "v": [["imgeiw1xf266ccifu6", "Синий (желе)", "Jelly Blue", 1800, 6, "1 кг"], ["imfd6yibehmi5skoew", "Персиково-розовый", "Peach Pink", 1800, 1, "1 кг"]], "n": "TPU 90A"}, "tpuams": {"p": 2500, "q": 2, "cl": "Красный (Blaze), Голубой (Frozen)", "d": "Оригинальный гибкий пластик Bambu Lab · 1 кг · 2 цвета", "v": [["im5ocbdawtg7w8o0ti", "Красный (Blaze)", "Blaze", 2500, 1, "1 кг"], ["imnx4kiapj2gejrzqa", "Голубой (Frozen)", "Frozen", 2500, 1, "1 кг"]], "n": "Bambu Lab TPU 90A"}, "fplus": {"p": 1000, "q": 67, "cl": "Пурпурный (маджента), Чёрный, Белый, Серый, Зелёный, Жёлтый, Лавандово-фиолетовый, Оливковый, Красный, Небесно-голубой, Солнечный оранжевый", "d": "Прочнее обычного PLA · 1 кг · 11 цветов", "v": [["imqa3e68f7e4qeqpno", "Пурпурный (маджента)", "Magenta", 1000, 11, "1 кг"], ["imxv9upctnwlavyf4r", "Чёрный", "Black", 1000, 10, "1 кг"], ["imztj0wyuhvauvzhma", "Белый", "White", 1000, 9, "1 кг"], ["im6mp6afqfjzczbtto", "Серый", "Gray", 1000, 7, "1 кг"], ["imf7jyu5jsjc616i76", "Зелёный", "Green", 1000, 6, "1 кг"], ["imsqxezyex1rdrgdsj", "Жёлтый", "Yellow", 1000, 6, "1 кг"], ["imbofbcixgy29db8p5", "Лавандово-фиолетовый", "Lavender Purple", 1000, 5, "1 кг"], ["im35ye4scmejvqtia4", "Оливковый", "Olive Green", 1000, 4, "1 кг"], ["imd5rgn5s7s333h9mt", "Красный", "Red", 1000, 3, "1 кг"], ["imf4bs3e62rynnefj7", "Небесно-голубой", "Sky Blue", 1000, 3, "1 кг"], ["imqxi6rhxo55zbka52", "Солнечный оранжевый", "Sunny Orange", 1000, 3, "1 кг"]]}, "fpro": {"p": 1000, "q": 4, "cl": "Чёрный", "d": "Повышенная прочность · 1 кг · 1 цвет", "v": [["imj8gxbenyjqwx4hh5", "Чёрный", "Black", 1000, 4, "1 кг"]]}, "ftr": {"p": 1000, "q": 70, "cl": "Синий, Зелёный, Оранжевый, Розовый, Фиолетовый, Красный, Жёлтый", "d": "Полупрозрачный · 1 кг · 7 цветов", "v": [["ykplatranslucentblue", "Синий", "Blue", 1000, 10, "1 кг"], ["ykplatranslucentgreen", "Зелёный", "Green", 1000, 10, "1 кг"], ["ykplatranslucentorange", "Оранжевый", "Orange", 1000, 10, "1 кг"], ["ykplatranslucentpink", "Розовый", "Pink", 1000, 10, "1 кг"], ["ykplatranslucentpurple", "Фиолетовый", "Purple", 1000, 10, "1 кг"], ["ykplatranslucentred", "Красный", "Red", 1000, 10, "1 кг"], ["ykplatranslucentyellow", "Жёлтый", "Yellow", 1000, 10, "1 кг"]]}, "fglow": {"p": 1100, "q": 22, "cl": "Звёздный оранжевый, Синий, Зелёный, Оранжевый", "d": "Светится в темноте · 1 кг · 4 цвета", "v": [["3bqm2h900rimjoc8b2ni", "Звёздный оранжевый", "Starry Orange", 1100, 12, "1 кг"], ["15t2b1865gpwoiiuix4f", "Синий", "Blue", 1100, 4, "1 кг"], ["kxm43v1qxpcpgyx94frp", "Зелёный", "Green", 1100, 3, "1 кг"], ["slzf9rgz0v5h6yl0e3mr", "Оранжевый", "Orange", 1100, 3, "1 кг"], ["imujzde8gxd6ncf10e", "Оранжевый", "Orange", 250, 7, "250 г"], ["lua4dazk0b4kbg7z2fr1", "Зелёный", "Green", 250, 5, "250 г"], ["zwzvrisko73a1o35qcnj", "Синий", "Blue", 250, 3, "250 г"]]}, "fwood": {"p": 1400, "q": 48, "cl": "Охра, Американский орех, Белый дуб, Берёза, Китайское красное дерево, Терракота", "d": "С эффектом дерева · 1 кг · 6 цветов", "v": [["im06i8j76b2lajlj4h", "Охра", "Ochre", 1400, 9, "1 кг"], ["im2wxfogo4mvn4a4wf", "Американский орех", "American Walnut", 1400, 9, "1 кг"], ["imnbqns6puq80idw37", "Белый дуб", "Oak White", 1400, 9, "1 кг"], ["imhym4l1vfz3zfkkib", "Берёза", "Birch", 1400, 8, "1 кг"], ["imj3j4wj99ibag7i1m", "Китайское красное дерево", "Chinese Mahogany", 1400, 8, "1 кг"], ["im9du7794g9dpmrcg6", "Терракота", "Terracotta", 1400, 5, "1 кг"]]}, "fmar": {"p": 1100, "q": 41, "cl": "Красный, Белый, Цементно-серый, Гранит, Кирпично-красный", "d": "С эффектом камня · 1 кг · 5 цветов", "v": [["ykplamarblered", "Красный", "Red", 1100, 10, "1 кг"], ["ykplamarblewhite", "Белый", "White", 1100, 10, "1 кг"], ["imj8ht9lgmxg9edn58", "Цементно-серый", "Cement Gray", 1100, 9, "1 кг"], ["im1u33xtplpft75v2s", "Гранит", "Granite", 1100, 7, "1 кг"], ["impf91dhodzdoc9is0", "Кирпично-красный", "Brick Red", 1100, 5, "1 кг"], ["imeh60kvj50ce9uvw5", "Кирпично-красный", "Brick Red", 250, 4, "250 г"]]}, "fgal": {"p": 250, "q": 11, "cl": "Сине-зелёно-золотой, Сине-золото-фиолетовый", "d": "Переливается разными цветами · 250 г · 2 цвета", "v": [["9z3q2n52uerp50ui53ae", "Сине-зелёно-золотой", "Blue Green Gold", 250, 6, "250 г"], ["cxiwzd6qzus70ben5zfk", "Сине-золото-фиолетовый", "Blue Gold Purple", 250, 5, "250 г"]]}, "fspk": {"p": 250, "q": 10, "cl": "Синий, Серо-синий, Розовый", "d": "С блёстками · 250 г · 3 цвета", "v": [["im344tfjgvq4k7bn7x", "Синий", "Blue", 250, 6, "250 г"], ["imj8b7tfq7xkwo886v", "Серо-синий", "GreyBlue", 250, 2, "250 г"], ["imompzom75wbbr4qmw", "Розовый", "Pink", 250, 2, "250 г"]]}, "fpm": {"p": 1050, "q": 28, "cl": "Чёрный, Синий Кляйна, Красный", "d": "Матовый PETG · 1 кг · 3 цвета", "v": [["immmex6l2qagwncxvj", "Чёрный", "Black", 1050, 21, "1 кг"], ["imcnqcnau0xltenc59", "Синий Кляйна", "Klein Blue", 1050, 5, "1 кг"], ["im4e0gz9j8fkzr0st0", "Красный", "Red", 1050, 2, "1 кг"]]}, "fps": {"p": 250, "q": 15, "cl": "Серо-синий, Синий, Розовый", "d": "PETG с блёстками · 250 г · 3 цвета", "v": [["imfzx3kiad9jzfx6kj", "Серо-синий", "GreyBlue", 250, 6, "250 г"], ["imdtw00bxmzzna1k1h", "Синий", "Blue", 250, 5, "250 г"], ["imwsk7kegy5mtic4ud", "Розовый", "Pink", 250, 4, "250 г"]]}, "fblb": {"p": 1500, "q": 25, "cl": "Нефритово-белый, Чёрный", "d": "Оригинальный пластик Bambu Lab · 1 кг · 2 цвета", "v": [["immlzkruykqh7dx297", "Нефритово-белый", "Jade White", 1500, 16, "1 кг"], ["imqkur3jq64nq6puxc", "Чёрный", "Black", 1500, 9, "1 кг"]]}, "fblm": {"p": 1500, "q": 2, "cl": "Лимонный, Розовый", "d": "Оригинальный Bambu Lab, матовый · 1 кг · 2 цвета", "v": [["imgq8zxqyxjxvf2old", "Лимонный", "Lemon Yellow", 1500, 1, "1 кг"], ["ims7qtuacojs106xdi", "Розовый", "розовый", 1500, 1, "1 кг"]]}};
const CRM_AT = "27.11.2026 08:48";
/*CRM-SYNC-END*/
const FV = {};
Object.keys(CRM).forEach((k) => (CRM[k].v || []).forEach((x) => { FV["f:" + x[0]] = { q: x[4], p: x[3] }; }));
function hasVar(id) { return !!admReady && !!(CRM[id] && CRM[id].v); }
const COLORS = {"American Walnut":"#6b4a33","Birch":"#e3cfa8","Chinese Mahogany":"#7a2e22","Oak White":"#d9c9a8","Ochre":"#c98a2b","Terracotta":"#c0603d","Dark Wood":"#4a3324","Brick Red":"#9c4a3c","Cement Gray":"#9a9a96","Granite":"#6e6e70","Blaze":"#e2331f","Frozen":"#8fd3f0","Jade White":"#f3f4ee","Bone White":"#efe8d8","Skin Tone":"#f0c8a8","Mardy Red":"#8e1b2b","Scarlet":"#e0241c","Bright Red":"#f02a2a","Cherry Blossom Pink":"#f7b6c8","Peach Pink":"#f9b5a0","Pink":"#f58ab0","розовый":"#f58ab0","Magenta":"#d6248f","Reddish Purple":"#a3266e","Lavender":"#b9a3e3","Lavender Purple":"#a98ad8","Latin Purple":"#7b3fa6","Indigo Purple":"#4b2e9c","Dark Purple":"#4a1f6e","Purple":"#7d3cc0","Transparent Purple":"#a77be0","Navy":"#1b2a5c","Dark Blue":"#1d3a8a","Klein Blue":"#002fa7","Tech Blue":"#1f6fe0","Blue":"#2463d6","Sky Blue":"#7cc4f2","Ice Blue":"#bfe3f2","Jelly Blue":"#4aa8e8","Peacock Blue":"#0f7f9c","Blue Grey":"#6f8296","GreyBlue":"#6f8296","Cyan":"#19b9d6","Turquoise":"#23c2b3","Turquoise Green":"#1fae8e","Peacock Green":"#0f8f72","Future Green":"#52d68a","Apple Green":"#8fd14f","Green":"#2faa4a","Dark Green":"#1f5c36","Olive Green":"#6f7a34","Silk Green":"#3fb56a","Lemon Yellow":"#f6e84a","Bright Yellow":"#ffd91a","Yellow":"#f7cf1f","Gold":"#c9a13b","Silk Golden":"#d4a83a","Maple Orange":"#e8742a","Pumpkin Orange":"#f0801f","Sun Orange":"#ff8a1f","Sunny Orange":"#ff9a2e","Starry Orange":"#f08a2a","Orange":"#f57c1f","Red":"#d9261c","Brown":"#6e4a2f","Coffee Brown":"#5a3d2b","Chocolate":"#4a2c1e","Black":"#1a1a1a","Night Black":"#101014","White":"#f6f6f4","Silk White":"#f2f0ea","Transparent White":"#e9eef2","Silver":"#b9bcc2","Gray":"#8b8d90","Grey":"#8b8d90"};
const SW = {"pla|Black": ["#1a1a1a"], "pla|Blue": ["#1e5bc6"], "pla|Blue Grey": ["#6b85a3"], "pla|Bone White": ["#ede6d6"], "pla|Bright Yellow": ["#ffea00"], "pla|Brown": ["#6d4c33"], "pla|Cherry Blossom Pink": ["#f7b7c8"], "pla|Chocolate": ["#4a2c1d"], "pla|Coffee Brown": ["#6f4e37"], "pla|Cyan": ["#00b4d8"], "pla|Dark Blue": ["#1f2f6b"], "pla|Dark Green": ["#1f5a3a"], "pla|Dark Wood": ["#4e3524"], "pla|Future Green": ["#3ddc84"], "pla|Green": ["#2e9e44"], "pla|Grey": ["#8e9196"], "pla|Ice Blue": ["#bfe6f5"], "pla|Indigo Purple": ["#3f2a87"], "pla|Jade White": ["#f3f1e7"], "pla|Klein Blue": ["#002fa7"], "pla|Lavender": ["#b9a6e0"], "pla|Magenta": ["#d81b8c"], "pla|Maple Orange": ["#e8731f"], "pla|Mardy Red": ["#8b1e2b"], "pla|Navy": ["#1b2a4a"], "pla|Pink": ["#f48fb1"], "pla|Pumpkin Orange": ["#f26b1d"], "pla|Purple": ["#7b3fa0"], "pla|Red": ["#d32f2f"], "pla|Reddish Purple": ["#9c2a7a"], "pla|Skin Tone": ["#f1c9a5"], "pla|Sky Blue": ["#7ec8f2"], "pla|Sun Orange": ["#ff8f00"], "pla|Tech Blue": ["#2f6fa8"], "pla|Turquoise": ["#30c5c0"], "pla|Turquoise Green": ["#1fb59a"], "pla|White": ["#f7f7f5"], "pla|Yellow": ["#f9d71c"], "fplus|Black": ["#1a1a1a"], "fplus|Gray": ["#8e9196"], "fplus|Green": ["#2e9e44"], "fplus|Lavender Purple": ["#a88bd6"], "fplus|Magenta": ["#d81b8c"], "fplus|Olive Green": ["#7a8b3a"], "fplus|Red": ["#d32f2f"], "fplus|Sky Blue": ["#7ec8f2"], "fplus|Sunny Orange": ["#ff8f00"], "fplus|White": ["#f7f7f5"], "fplus|Yellow": ["#f9d71c"], "fpro|Black": ["#1a1a1a"], "plam|Apple Green": ["#8bc34a"], "plam|Black": ["#1a1a1a"], "plam|Blue": ["#1e5bc6"], "plam|Bone White": ["#ede6d6"], "plam|Brown": ["#6d4c33"], "plam|Dark Green": ["#1f5a3a"], "plam|Gray": ["#8e9196"], "plam|Green": ["#2e9e44"], "plam|Ice Blue": ["#bfe6f5"], "plam|Latin Purple": ["#6a3d9a"], "plam|Orange": ["#f57c00"], "plam|Purple": ["#7b3fa0"], "plam|Red": ["#d32f2f"], "plam|Scarlet": ["#c8102e"], "plam|Skin Tone": ["#f1c9a5"], "plam|White": ["#f7f7f5"], "plam|Yellow": ["#f9d71c"], "ftr|Blue": ["#1e5bc6"], "ftr|Green": ["#2e9e44"], "ftr|Orange": ["#f57c00"], "ftr|Pink": ["#f48fb1"], "ftr|Purple": ["#7b3fa0"], "ftr|Red": ["#d32f2f"], "ftr|Yellow": ["#f9d71c"], "plas|Black": ["#1a1a1a"], "plas|Black Red": ["#1a1a1a", "#d32f2f"], "plas|Blue Black": ["#1e5bc6", "#1a1a1a"], "plas|Blue Pink": ["#1e5bc6", "#f48fb1"], "plas|Gold Pink": ["#d4af37", "#f06292"], "plas|Golden": ["#c9a227"], "plas|Green": ["#2e9e44"], "plas|Grey": ["#8e9196"], "plas|Red": ["#d32f2f"], "plas|Silver": ["#c0c4c8"], "plas|White": ["#f7f7f5"], "plas|Gold": ["#c9a227"], "fwood|American Walnut": ["#6b4a2e"], "fwood|Birch": ["#e3cfa4"], "fwood|Chinese Mahogany": ["#7b3b2a"], "fwood|Oak White": ["#d9c4a0"], "fwood|Ochre": ["#c88a2e"], "fwood|Terracotta": ["#b5603e"], "fmar|Brick Red": ["#a8503c"], "fmar|Cement Gray": ["#a3a3a0"], "fmar|Granite": ["#d9d6cf"], "fmar|Red": ["#d32f2f"], "fmar|White": ["#f7f7f5"], "fspk|Blue": ["#1e5bc6"], "fspk|GreyBlue": ["#6b85a3"], "fspk|Pink": ["#f48fb1"], "fgal|Blue Gold Purple": ["#1e5bc6", "#d4af37", "#7b3fa0"], "fgal|Blue Green Gold": ["#1e5bc6", "#2e9e44", "#d4af37"], "petg|Black": ["#1a1a1a"], "petg|Blue": ["#1e5bc6"], "petg|Bright Red": ["#e53935"], "petg|Bright Yellow": ["#ffea00"], "petg|Dark Purple": ["#4a2470"], "petg|Gold": ["#c9a227"], "petg|Gray": ["#8e9196"], "petg|Green": ["#2e9e44"], "petg|Lavender Purple": ["#a88bd6"], "petg|Night Black": ["#0b0b0d"], "petg|Olive Green": ["#7a8b3a"], "petg|Orange": ["#f57c00"], "petg|Peacock Blue": ["#006e8c"], "petg|Peacock Green": ["#00897b"], "petg|Pink": ["#f48fb1"], "petg|Purple": ["#7b3fa0"], "petg|Red": ["#d32f2f"], "petg|Sunny Orange": ["#ff8f00"], "petg|Transparent Purple": ["#7b3fa0"], "petg|Transparent White": ["#dde6ee"], "petg|White": ["#f7f7f5"], "petg|Yellow": ["#f9d71c"], "fpm|Black": ["#1a1a1a"], "fpm|Klein Blue": ["#002fa7"], "fpm|Red": ["#d32f2f"], "fps|Blue": ["#1e5bc6"], "fps|GreyBlue": ["#6b85a3"], "fps|Pink": ["#f48fb1"], "asa|Gray": ["#8e9196"], "asa|Red": ["#d32f2f"], "asa|White": ["#f7f7f5"], "tpu95|Jelly Blue": ["#3f8fd8"], "tpu95|Peach Pink": ["#ffb89a"], "fblb|Black": ["#1a1a1a"], "fblb|Jade White": ["#f3f1e7"], "fblm|Lemon Yellow": ["#f5e04a"], "fblm|": ["#f48fb1"], "tpuams|Blaze": ["#e8452c"], "tpuams|Frozen": ["#a8d8ea"]};
const FNEW = {"pla": ["Bone White", "Bright Yellow", "Coffee Brown", "Cyan", "Ice Blue", "Indigo Purple", "Maple Orange", "Mardy Red", "Navy", "Purple", "Turquoise"], "plam": ["Apple Green", "Blue", "Bone White", "Brown", "Dark Green", "Green", "Ice Blue", "Latin Purple", "Orange", "Purple", "Red", "Skin Tone"], "ftr": ["Blue", "Green", "Orange", "Pink", "Purple", "Red", "Yellow"], "plas": ["Black", "Black Red", "Blue Pink"], "fmar": ["Red", "White"], "petg": ["Night Black"]};
const FDESC = {"pla": "Базовый PLA — для большинства задач: игрушки, декор, фигурки, прототипы. Легко печатается, без запаха.", "fplus": "Усиленный PLA: прочнее и меньше ломается, чем обычный PLA. Для деталей, которые должны выдерживать нагрузку.", "fpro": "Инженерный PLA повышенной прочности — для функциональных деталей.", "plam": "Матовый PLA — без блеска, хорошо скрывает слои. Для фигурок, декора и подарков.", "ftr": "Полупрозрачный PLA: свет проходит насквозь — для ламп, ночников, витражей и декора с подсветкой.", "plas": "Шёлковый PLA с глянцевым металлическим блеском. Двухцветные меняют оттенок в зависимости от угла.", "fwood": "PLA с древесным наполнителем: фактура и цвет настоящего дерева. Изделия можно шлифовать.", "fglow": "Светится в темноте после зарядки светом. Для ночников, игрушек, знаков и сувениров.", "fmar": "Мраморный PLA — эффект камня с вкраплениями. Для ваз, кашпо и интерьерного декора.", "fspk": "PLA с блёстками — мерцающая поверхность без постобработки.", "fgal": "Переливается тремя цветами — эффект «галактики» на одном изделии.", "petg": "Прочный и термостойкий пластик для функциональных деталей, креплений и изделий для улицы.", "fpm": "Матовый PETG: прочность PETG без блеска.", "fps": "PETG с блёстками — прочность PETG и мерцающая поверхность.", "asa": "Уличный пластик: устойчив к солнцу (UV), влаге и температуре. Для деталей автомобиля и улицы.", "tpu95": "Гибкий резиноподобный пластик: чехлы, прокладки, подошвы, амортизаторы.", "fblb": "Оригинальный филамент Bambu Lab с RFID-меткой: AMS сам распознаёт цвет и тип пластика.", "fblm": "Оригинальный филамент Bambu Lab с RFID-меткой: AMS сам распознаёт цвет и тип пластика.", "tpuams": "Оригинальный филамент Bambu Lab с RFID-меткой: AMS сам распознаёт цвет и тип пластика."};
const swCols = (en, pid) => { if (pid && SW[pid + "|" + en]) return SW[pid + "|" + en]; if (COLORS[en]) return [COLORS[en]]; const w = (en || "").split(/\s+/).map((x) => COLORS[x]).filter(Boolean); return w.length ? w : ["#bdbdbd"]; };
const swBg = (en, pid) => { const c = swCols(en, pid); if (c.length === 1) return c[0]; const st = 100 / c.length; return "linear-gradient(135deg," + c.map((x, i) => x + " " + (i * st) + "% " + ((i + 1) * st) + "%").join(",") + ")"; };
/* ---------- админка ---------- */
const AKEY = "bl_admin_v1";
let adm = { s: {}, p: {}, add: [], o: [], del: [], h: {} };
try {
  const d = JSON.parse(localStorage.getItem(AKEY) || "null");
  if (d) adm = { s: d.s || {}, p: d.p || {}, add: d.add || [], o: d.o || [], del: d.del || [], h: d.h || {} };
} catch (e) {}
const HBASE = {};
document.querySelectorAll("[data-h]").forEach((el) => { HBASE[el.dataset.h] = el.textContent.replace(/\s+/g, " ").trim(); });
const HERO0 = $("#heroImg") ? $("#heroImg").src : "";
const SBASE = {};
document.querySelectorAll("section.cat").forEach((s) => {
  SBASE[s.id] = { t: s.querySelector("h2")?.textContent || "", s: s.querySelector(".csub")?.textContent.trim() || "" };
});
function applyHome() {
  const h = adm.h || {}, tx = h.t || {}, sec = h.sec || {};
  document.querySelectorAll("[data-h]").forEach((el) => {
    const k = el.dataset.h;
    el.textContent = tx[k] != null && tx[k] !== "" ? tx[k] : HBASE[k];
  });
  const im = $("#heroImg");
  if (im) im.src = h.img || HERO0;
  document.querySelectorAll("section.cat").forEach((s) => {
    const o = sec[s.id] || {}, b = SBASE[s.id] || {};
    const h2 = s.querySelector("h2"), cs = s.querySelector(".csub");
    if (h2) h2.textContent = o.t || b.t;
    if (cs) cs.textContent = o.s || b.s;
  });
}
const admSave = () => { try { localStorage.setItem(AKEY, JSON.stringify(adm)); } catch (e) {} };

/* разделы каталога */
const CATS = [...document.querySelectorAll("section.cat")]
  .filter((s) => s.querySelector(".grid") && s.id !== "industrial")
  .map((s) => ({ id: s.id, t: s.querySelector("h2").textContent, el: s, grid: s.querySelector(".grid") }));
const catName = (id) => (CATS.find((c) => c.id === id) || {}).t || id;

/* базовые товары со страницы */
const BASE = new Map();
document.querySelectorAll(".card[data-pid]").forEach((c) => {
  BASE.set(c.dataset.pid, {
    n: c.querySelector("h3").textContent,
    d: c.querySelector(".d").textContent,
    p: +c.querySelector(".act").dataset.p,
    cat: c.closest("section").id,
    html: c.querySelector(".vis").innerHTML,
  });
});

const ov = (id) => adm.p[id] || (adm.p[id] = {});
const custom = (id) => adm.add.find((x) => x.id === id);
const item = (id) => {
  const c = custom(id);
  if (c) return { n: c.n, d: c.d, p: +c.price, cat: c.cat, qty: c.qty, off: c.off, badge: c.badge, img: c.img, custom: 1 };
  const b = BASE.get(id), o = adm.p[id] || {}, k = CRM[id];
  return {
    n: o.n || (k && k.n) || b.n, d: o.d || (k && k.d) || b.d, p: k ? k.p : (o.price != null ? +o.price : b.p),
    cat: b.cat, qty: k ? k.q : o.qty, off: o.off, badge: o.badge, html: k && k.v && b.html.indexOf("ph spool") > -1 ? palHTML(k.v, id) : b.html, crm: !!k, ask: !k, cl: k && k.cl, v: k && k.v,
  };
};
const isDel = (id) => (adm.del || []).includes(id);
const allIds = () => [...BASE.keys()].concat(adm.add.map((x) => x.id)).filter((i) => !isDel(i));
admReady = true;
function stockOf(id) {
  if (id && id.slice(0, 2) === "f:") return FV[id] ? FV[id].q : null;
  if (!admReady || !BASE.has(id) && !custom(id)) return null;
  const it = item(id);
  return it.qty === "" || it.qty == null ? null : +it.qty;
}

/* ---------- отрисовка витрины ---------- */
const nfmt = (n) => n.toLocaleString("ru-RU").replace(/ /g, " ");

const TIER = { a1mini: "Начальный уровень", a1minic: "Начальный уровень", a1: "Начальный уровень", a1c: "Начальный уровень", a2l: "Большой формат", p1s: "Средний уровень", h2d: "Профессиональный", a2lcn: "Большой формат", p2s: "Средний уровень", x2d: "Профессиональный", u1: "Многоцветный" };
function uniqCols(v) { const seen = {}, out = []; v.forEach((x) => { if (x[4] > 0 && !seen[x[2]]) { seen[x[2]] = 1; out.push(x); } }); return out; }
function swRow(v, pid) {
  const u = uniqCols(v), n = 9;
  return '<div class="swrow">' + u.slice(0, n).map((x) => '<i style="background:' + swBg(x[2], pid) + '" title="' + x[1] + '"></i>').join("") +
    (u.length > n ? "<span>+" + (u.length - n) + "</span>" : "") + "</div>";
}
function palHTML(v, pid) {
  const u = uniqCols(v).slice(0, 12);
  return '<div class="ph pal"><div class="palg n' + Math.min(u.length, 12) + '">' + u.map((x) => '<i style="background:' + swBg(x[2], pid) + '"></i>').join("") + "</div></div>";
}
function cardHTML(id) {
  const it = item(id);
  const st = stockOf(id);
  const vis = it.custom
    ? (it.img
        ? '<div class="ph sample"><img src="' + it.img + '" alt=""></div>'
        : '<div class="ph ico"><svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"><rect x="9" y="9" width="30" height="30" rx="4"/><path d="M9 20h30M20 9v30"/></svg></div>')
    : it.html;
  const badge = it.badge ? '<span class="badge">' + it.badge + "</span>" : "";
  const stock = st == null ? "" :
    (st <= 0 ? '<span class="stk out">Нет в наличии</span>'
             : (st <= 3 ? '<span class="stk low">Осталось ' + st + " шт</span>"
                        : '<span class="stk">В наличии ' + st + " шт</span>"));
  return '<div class="vis">' + vis + badge + "</div>" +
    '<div class="cb">' + (TIER[id] ? '<span class="tier">' + TIER[id] + "</span>" : "") + "<h3>" + it.n + "</h3>" +
    '<p class="d">' + it.d + "</p>" + stock +
    (it.v ? swRow(it.v, id) : "") +
    '<div class="foot">' + (it.ask ? '<div class="pr q">Под заказ</div>' : '<div class="pr"><b>' + (it.cl ? "<small>от</small> " : "") + nfmt(it.p) + "</b><span>сом</span></div>") +
    '<div class="act" data-id="' + id + '" data-n="' + it.n.replace(/"/g, "&quot;") + '" data-p="' + it.p + '"></div>' +
    "</div></div>";
}

function renderShop() {
  /* базовые */
  document.querySelectorAll(".card[data-pid]").forEach((c) => {
    const id = c.dataset.pid, it = item(id), st = stockOf(id);
    c.innerHTML = cardHTML(id);
    c.dataset.name = (it.n + " " + it.d + " " + (it.cl || "")).toLowerCase();
    c.classList.toggle("off", !!it.off || isDel(id));
    c.classList.toggle("soldout", st != null && st <= 0);
  });
  /* добавленные */
  document.querySelectorAll(".card.new").forEach((c) => c.remove());
  adm.add.forEach((x) => {
    if (isDel(x.id)) return;
    const cat = CATS.find((c) => c.id === x.cat);
    if (!cat) return;
    const el = document.createElement("article");
    el.className = "card new";
    el.dataset.pid = x.id;
    el.dataset.cat = x.cat;
    el.innerHTML = cardHTML(x.id);
    el.dataset.name = (x.n + " " + x.d).toLowerCase();
    const st = stockOf(x.id);
    el.classList.toggle("off", !!x.off);
    el.classList.toggle("soldout", st != null && st <= 0);
    cat.grid.appendChild(el);
  });
  rescan();
  paint();
}

function applyAdmin() {
  const s = adm.s;
  const wa = (s.wa || WA).replace(/\D/g, "");
  document.querySelectorAll('a[href*="wa.me/"]').forEach((a) => { a.href = "https://wa.me/" + wa; });
  const ph = $("#phoneTop");
  if (ph && s.phone) { ph.textContent = s.phone; ph.href = "tel:+" + s.phone.replace(/\D/g, ""); }
  const fn = $("#freeNote");
  if (fn && s.free) fn.textContent = "Доставка по Бишкеку — бесплатно от " + fmt(+s.free) + ". По регионам считаем отдельно.";
  const ds = $("#demoStrip");
  if (ds) ds.style.display = s.demo === false ? "none" : "";
  applyHome();
  renderShop();
}

/* ---------- панель ---------- */
const admEl = $("#admin");
const lockEl = $("#aLock");
const SECRET = "#kabinet";
let unlocked = false;
try { unlocked = sessionStorage.getItem("bl_adm_ok") === "1"; } catch (e) {}

const showAdm = () => { admEl.classList.add("on"); drawAll(); document.body.style.overflow = "hidden"; };
const openAdm = () => {
  const pin = adm.s.pin || "";
  if (adm.s.lock === false || !pin || unlocked) { showAdm(); return; }
  lockEl.classList.add("on");
  $("#lPin").value = ""; $("#lErr").textContent = "";
  document.body.style.overflow = "hidden";
  setTimeout(() => $("#lPin").focus(), 60);
};
const closeAdm = () => {
  admEl.classList.remove("on"); lockEl.classList.remove("on");
  document.body.style.overflow = "";
  if (location.hash === SECRET) history.replaceState(null, "", location.pathname + location.search);
};
function tryPin() {
  const v = $("#lPin").value.trim();
  if (v && v === (adm.s.pin || "")) {
    unlocked = true;
    try { sessionStorage.setItem("bl_adm_ok", "1"); } catch (e) {}
    lockEl.classList.remove("on"); showAdm();
  } else {
    $("#lErr").textContent = "Код не подходит";
    $("#lPin").value = ""; $("#lPin").focus();
  }
}
$("#lGo").addEventListener("click", tryPin);
$("#lPin").addEventListener("keydown", (e) => { if (e.key === "Enter") tryPin(); });
lockEl.addEventListener("click", (e) => { if (e.target === lockEl) closeAdm(); });
const flash = (t) => { $("#aState").textContent = t; clearTimeout(flash.t); flash.t = setTimeout(() => { $("#aState").textContent = ""; }, 1500); };

$("#aClose").addEventListener("click", closeAdm);
if (location.hash === SECRET) setTimeout(openAdm, 0);
window.addEventListener("hashchange", () => { if (location.hash === SECRET) openAdm(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && lockEl.classList.contains("on")) closeAdm();
});

admEl.querySelectorAll(".atab").forEach((t) => t.addEventListener("click", () => {
  admEl.querySelectorAll(".atab").forEach((x) => x.classList.toggle("on", x === t));
  admEl.querySelectorAll(".apane").forEach((x) => x.classList.toggle("on", x.id === "pane-" + t.dataset.tab));
}));

function drawStats() {
  const ids = allIds();
  const nOn = ids.filter((i) => !item(i).off && !(stockOf(i) != null && stockOf(i) <= 0)).length;
  const low = ids.filter((i) => { const s = stockOf(i); return s != null && s > 0 && s <= 3; }).length;
  const out = ids.filter((i) => { const s = stockOf(i); return s != null && s <= 0; }).length;
  const nw = adm.o.filter((o) => o.st === "new").length;
  const rev = adm.o.filter((o) => o.st === "done").reduce((a, o) => a + o.total, 0);
  $("#aStats").innerHTML =
    stat("Товаров на сайте", nOn) + stat("Заканчиваются", low, low ? "warn" : "") +
    stat("Нет в наличии", out, out ? "bad" : "") + stat("Новых заявок", nw, nw ? "good" : "") +
    stat("Продано на", fmt(rev));
  $("#tbOrders").textContent = nw;
  $("#tbOrders").classList.toggle("zero", !nw);
}
const stat = (t, v, k) => '<div class="st ' + (k || "") + '"><b>' + v + "</b><span>" + t + "</span></div>";

/* --- товары --- */
let gq = "", gcat = "", gsort = "";
function drawGoods() {
  const sel = $("#aFilter");
  if (sel.options.length < 2) CATS.forEach((c) => sel.add(new Option(c.t, c.id)));
  let ids = allIds().filter((i) => {
    const it = item(i);
    if (gcat && it.cat !== gcat) return false;
    if (gq && !(it.n + " " + it.d).toLowerCase().includes(gq)) return false;
    if (gsort === "off" && !it.off) return false;
    return true;
  });
  if (gsort === "low") ids.sort((a, b) => (stockOf(a) ?? 999) - (stockOf(b) ?? 999));
  else ids.sort((a, b) => CATS.findIndex((c) => c.id === item(a).cat) - CATS.findIndex((c) => c.id === item(b).cat));

  if (!ids.length) { $("#aList").innerHTML = '<p class="aempty">Ничего не нашли</p>'; return; }
  let cat = "", h = "";
  ids.forEach((id) => {
    const it = item(id), st = stockOf(id);
    if (!gsort && it.cat !== cat) { cat = it.cat; h += '<div class="ghead">' + catName(cat) + "</div>"; }
    const cls = it.off ? " isoff" : (st != null && st <= 0 ? " isout" : "");
    h += '<div class="grow' + cls + '" data-id="' + id + '">' +
      '<div class="gname"><b>' + it.n + "</b><span>" + it.d + "</span>" +
        (it.custom ? '<em class="tag">добавлен вами</em>' : "") + "</div>" +
      '<label class="gf">Цена<input class="gp" inputmode="numeric" value="' + it.p + '"></label>' +
      '<label class="gf">Остаток<input class="gq" inputmode="numeric" placeholder="—" value="' + (st == null ? "" : st) + '"></label>' +
      '<label class="chk gh"><input type="checkbox" class="go"' + (it.off ? " checked" : "") + '> скрыть</label>' +
      '<button class="gedit" data-edit="' + id + '">Изменить</button>' +
      '<button class="gdel" data-del="' + id + '" title="Удалить товар">✕</button>' +
      "</div>";
  });
  $("#aList").innerHTML = h;
}
$("#aq").addEventListener("input", (e) => { gq = e.target.value.trim().toLowerCase(); drawGoods(); });
$("#aFilter").addEventListener("change", (e) => { gcat = e.target.value; drawGoods(); });
$("#aSort").addEventListener("change", (e) => { gsort = e.target.value; drawGoods(); });

$("#aList").addEventListener("input", (e) => {
  const row = e.target.closest(".grow"); if (!row) return;
  const id = row.dataset.id, c = custom(id), t = c || ov(id), b = BASE.get(id);
  if (e.target.classList.contains("gp")) {
    const v = +e.target.value.replace(/\D/g, "");
    if (c) c.price = v; else if (v && v !== b.p) t.price = v; else delete t.price;
  }
  if (e.target.classList.contains("gq")) {
    const raw = e.target.value.replace(/\D/g, "");
    t.qty = raw === "" ? "" : +raw;
  }
  if (e.target.classList.contains("go")) {
    if (e.target.checked) t.off = 1; else delete t.off;
  }
  admSave(); applyAdmin(); drawStats();
  row.classList.toggle("isoff", !!item(id).off);
  row.classList.toggle("isout", stockOf(id) != null && stockOf(id) <= 0);
  flash("Сохранено");
});
$("#aList").addEventListener("click", (e) => {
  const b = e.target.closest("[data-edit]");
  if (b) { openProd(b.dataset.edit); return; }
  const d = e.target.closest("[data-del]");
  if (d) delProd(d.dataset.del);
});

function delProd(id) {
  const n = item(id).n;
  adm.del = adm.del || [];
  if (!adm.del.includes(id)) adm.del.push(id);
  delete cart[id]; save();
  admSave(); applyAdmin(); drawAll();
  flash("Удалён: " + n);
}
function restoreProd(id) {
  adm.del = (adm.del || []).filter((x) => x !== id);
  admSave(); applyAdmin(); drawAll(); flash("Возвращён");
}
$("#aTrash").addEventListener("click", (e) => {
  const r = e.target.closest("[data-restore]");
  if (r) restoreProd(r.dataset.restore);
  const w = e.target.closest("#trashWipe");
  if (w) {
    (adm.del || []).forEach((id) => { adm.add = adm.add.filter((x) => x.id !== id); });
    adm.del = []; admSave(); applyAdmin(); drawAll(); flash("Корзина очищена");
  }
});
function drawTrash() {
  const d = adm.del || [];
  if (!d.length) { $("#aTrash").innerHTML = ""; return; }
  $("#aTrash").innerHTML = '<div class="thead">Удалённые (' + d.length + ') ' +
    '<button class="tlink" id="trashWipe">очистить окончательно</button></div>' +
    d.map((id) => {
      const c = custom(id), b = BASE.get(id);
      const n = c ? c.n : (b ? ((adm.p[id] || {}).n || b.n) : id);
      return '<div class="trow"><span>' + n + '</span>' +
        '<button class="tlink" data-restore="' + id + '">вернуть</button></div>';
    }).join("");
}

/* --- модалка товара --- */
let editId = null, editImg = "";
const aMask = $("#aMask");
function openProd(id) {
  editId = id || null;
  const sel = $("#pC");
  if (!sel.options.length) CATS.forEach((c) => sel.add(new Option(c.t, c.id)));
  const it = id ? item(id) : null;
  $("#pTitle").textContent = id ? "Товар" : "Новый товар";
  $("#pN").value = it ? it.n : "";
  $("#pD").value = it ? it.d : "";
  $("#pC").value = it ? it.cat : CATS[0].id;
  $("#pP").value = it ? it.p : "";
  $("#pQ").value = it && stockOf(id) != null ? stockOf(id) : "";
  $("#pB").value = it && it.badge ? it.badge : "";
  editImg = it && it.img ? it.img : "";
  $("#pC").disabled = !!(id && !item(id).custom);
  $("#pDel").style.display = id ? "" : "none";
  drawPrev();
  aMask.classList.add("on");
}
function drawPrev() {
  $("#pPrev").innerHTML = editImg ? '<img src="' + editImg + '">' : '<span>нет фото</span>';
}
$("#aAdd").addEventListener("click", () => openProd(null));
$("#pClose").addEventListener("click", () => aMask.classList.remove("on"));
aMask.addEventListener("click", (e) => { if (e.target === aMask) aMask.classList.remove("on"); });
$("#pPick").addEventListener("click", () => $("#pFile").click());
$("#pDrop").addEventListener("click", () => { editImg = ""; drawPrev(); });
$("#pFile").addEventListener("change", (e) => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    const im = new Image();
    im.onload = () => {
      const S = 620, cv = document.createElement("canvas");
      cv.width = cv.height = S;
      const g = cv.getContext("2d");
      g.fillStyle = "#f4f6f5"; g.fillRect(0, 0, S, S);
      const k = Math.min(S / im.width, S / im.height);
      const w = im.width * k, h = im.height * k;
      g.drawImage(im, (S - w) / 2, (S - h) / 2, w, h);
      editImg = cv.toDataURL("image/jpeg", 0.82);
      drawPrev();
    };
    im.src = r.result;
  };
  r.readAsDataURL(f);
  e.target.value = "";
});
$("#pSave").addEventListener("click", () => {
  const n = $("#pN").value.trim(), d = $("#pD").value.trim();
  const price = +$("#pP").value.replace(/\D/g, "");
  const qraw = $("#pQ").value.replace(/\D/g, "");
  const badge = $("#pB").value.trim();
  if (!n || !price) { flash("Нужно название и цена"); return; }
  if (editId && !item(editId).custom) {
    const o = ov(editId), b = BASE.get(editId);
    o.n = n !== b.n ? n : undefined; if (!o.n) delete o.n;
    o.d = d !== b.d ? d : undefined; if (!o.d) delete o.d;
    if (price !== b.p) o.price = price; else delete o.price;
    o.qty = qraw === "" ? "" : +qraw;
    if (badge) o.badge = badge; else delete o.badge;
  } else {
    const c = editId ? custom(editId) : null;
    const rec = c || { id: "u" + Date.now().toString(36) };
    rec.n = n; rec.d = d; rec.price = price; rec.cat = $("#pC").value;
    rec.qty = qraw === "" ? "" : +qraw; rec.badge = badge; rec.img = editImg;
    if (!c) adm.add.push(rec);
  }
  admSave(); applyAdmin(); drawAll();
  aMask.classList.remove("on");
  flash(editId ? "Сохранено" : "Товар добавлен");
});
$("#pDel").addEventListener("click", () => {
  if (!editId) return;
  delProd(editId);
  aMask.classList.remove("on");
});

/* --- заявки --- */
let ost = "";
const STL = { new: "Новая", work: "В работе", done: "Выполнена" };
function drawOrders() {
  const list = adm.o.filter((o) => !ost || o.st === ost);
  if (!list.length) { $("#oList").innerHTML = '<p class="aempty">Заявок пока нет. Они появятся здесь, как только клиент оформит заказ на сайте.</p>'; return; }
  $("#oList").innerHTML = list.map((o) => {
    const dt = new Date(o.ts);
    const when = dt.toLocaleDateString("ru-RU") + ", " + dt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    return '<div class="ocard st-' + o.st + '" data-oid="' + o.id + '">' +
      '<div class="oh"><b>' + o.name + '</b><a href="https://wa.me/' + o.phone.replace(/\D/g, "") +
        '" target="_blank" rel="noopener" class="ophone">' + o.phone + "</a>" +
        '<span class="owhen">' + when + "</span>" +
        '<b class="osum">' + fmt(o.total) + "</b></div>" +
      '<div class="oitems">' + o.items.map((i) => "<span>" + i.n + " × " + i.q + "</span>").join("") + "</div>" +
      '<div class="ometa">' + o.dl + (o.cm ? " · " + o.cm : "") + "</div>" +
      '<div class="oacts">' +
        Object.keys(STL).map((k) => '<button class="ost' + (o.st === k ? " on" : "") +
          '" data-st="' + k + '">' + STL[k] + "</button>").join("") +
        '<button class="odel" data-del="1">Удалить</button></div>' +
      "</div>";
  }).join("");
}
admEl.querySelectorAll(".ochip").forEach((c) => c.addEventListener("click", () => {
  admEl.querySelectorAll(".ochip").forEach((x) => x.classList.toggle("on", x === c));
  ost = c.dataset.st; drawOrders();
}));
$("#oList").addEventListener("click", (e) => {
  const card = e.target.closest(".ocard"); if (!card) return;
  const o = adm.o.find((x) => x.id === card.dataset.oid); if (!o) return;
  const st = e.target.closest(".ost");
  if (st) { o.st = st.dataset.st; admSave(); drawOrders(); drawStats(); return; }
  if (e.target.closest(".odel")) {
    adm.o = adm.o.filter((x) => x.id !== o.id); admSave(); drawOrders(); drawStats();
  }
});
$("#oClear").addEventListener("click", () => {
  adm.o = adm.o.filter((o) => o.st !== "done"); admSave(); drawOrders(); drawStats(); flash("Очищено");
});

/* --- настройки --- */
function drawSet() {
  const s = adm.s;
  $("#sWa").value = s.wa || WA;
  $("#sPhone").value = s.phone || $("#phoneTop").textContent.trim();
  $("#sFree").value = s.free || 3000;
  $("#sDemo").checked = s.demo !== false;
  $("#sPin").value = s.pin || "";
  $("#sLock").checked = s.lock !== false;
  const u = location.origin + location.pathname + SECRET;
  $("#secretUrl").textContent = u.length > 60 ? SECRET : u;
}
$("#pane-set").addEventListener("input", () => {
  adm.s = {
    wa: $("#sWa").value.replace(/\D/g, "") || WA,
    phone: $("#sPhone").value.trim(),
    free: +$("#sFree").value.replace(/\D/g, "") || 3000,
    demo: $("#sDemo").checked,
    pin: $("#sPin").value.trim(),
    lock: $("#sLock").checked,
  };
  admSave(); applyAdmin(); flash("Сохранено");
});
$("#aReset").addEventListener("click", () => {
  adm = { s: {}, p: {}, add: [], o: [], del: [], h: {} }; admSave(); location.reload();
});
$("#aExport").addEventListener("click", () => {
  const txt = JSON.stringify(adm);
  $("#aJson").value = txt; $("#aPaste").classList.add("on"); $("#aJson").select();
  try { navigator.clipboard.writeText(txt).then(() => flash("Скопировано")); } catch (e) {}
});
$("#aImport").addEventListener("click", () => { $("#aJson").value = ""; $("#aPaste").classList.add("on"); $("#aJson").focus(); });
$("#aPasteClose").addEventListener("click", () => $("#aPaste").classList.remove("on"));
$("#aApply").addEventListener("click", () => {
  try {
    const d = JSON.parse($("#aJson").value.trim());
    adm = { s: d.s || {}, p: d.p || {}, add: d.add || [], o: d.o || [], del: d.del || [], h: d.h || {} };
    admSave(); applyAdmin(); drawAll();
    $("#aPaste").classList.remove("on"); flash("Применено");
  } catch (err) { flash("Текст не читается"); }
});

/* --- главная --- */
function drawHome() {
  const h = adm.h || {}, tx = h.t || {}, sec = h.sec || {};
  admEl.querySelectorAll("[data-hf]").forEach((el) => { el.value = tx[el.dataset.hf] != null ? tx[el.dataset.hf] : HBASE[el.dataset.hf] || ""; });
  $("#hPrev").innerHTML = '<img src="' + (h.img || HERO0) + '">';
  const sf = $("#secFields");
  if (!sf.children.length) {
    sf.innerHTML = Object.keys(SBASE).map((id) =>
      '<div class="secrow" data-sec="' + id + '"><label>Заголовок<input class="st1"></label>' +
      '<label>Описание<input class="st2"></label></div>').join("");
  }
  sf.querySelectorAll(".secrow").forEach((r) => {
    const o = sec[r.dataset.sec] || {}, b = SBASE[r.dataset.sec];
    r.querySelector(".st1").value = o.t || b.t;
    r.querySelector(".st2").value = o.s || b.s;
  });
}
$("#pane-home").addEventListener("input", () => {
  const h = adm.h = adm.h || {};
  h.t = {};
  admEl.querySelectorAll("[data-hf]").forEach((el) => {
    const v = el.value.trim();
    if (v && v !== HBASE[el.dataset.hf]) h.t[el.dataset.hf] = v;
  });
  h.sec = {};
  $("#secFields").querySelectorAll(".secrow").forEach((r) => {
    const id = r.dataset.sec, b = SBASE[id], o = {};
    const t = r.querySelector(".st1").value.trim(), s = r.querySelector(".st2").value.trim();
    if (t && t !== b.t) o.t = t;
    if (s && s !== b.s) o.s = s;
    if (Object.keys(o).length) h.sec[id] = o;
  });
  admSave(); applyHome(); flash("Сохранено");
});
$("#hPick").addEventListener("click", () => $("#hFile").click());
$("#hDrop").addEventListener("click", () => { adm.h = adm.h || {}; delete adm.h.img; admSave(); applyHome(); drawHome(); flash("Исходная картинка"); });
$("#hFile").addEventListener("change", (e) => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    const im = new Image();
    im.onload = () => {
      const W = 1200, H = 900, cv = document.createElement("canvas");
      cv.width = W; cv.height = H;
      const g = cv.getContext("2d");
      const k = Math.max(W / im.width, H / im.height);
      const w = im.width * k, h = im.height * k;
      g.drawImage(im, (W - w) / 2, (H - h) / 2, w, h);
      adm.h = adm.h || {};
      adm.h.img = cv.toDataURL("image/jpeg", 0.84);
      admSave(); applyHome(); drawHome(); flash("Картинка обновлена");
    };
    im.src = r.result;
  };
  r.readAsDataURL(f);
  e.target.value = "";
});

function drawAll() { drawStats(); drawGoods(); drawTrash(); drawOrders(); drawHome(); drawSet(); }

/* приём заявки с сайта */
function logOrder() {
  const items = Object.keys(cart).map((id) => ({ id, n: cart[id].n, p: cart[id].p, q: cart[id].q }));
  if (!items.length) return;
  adm.o.unshift({
    id: "o" + Date.now().toString(36), ts: Date.now(), st: "new",
    name: $("#nm").value.trim(), phone: $("#ph").value.trim(),
    dl: $("#dl").value, cm: $("#cm").value.trim(),
    items, total: sum(),
  });
  items.forEach((i) => {
    const st = stockOf(i.id);
    if (st != null) {
      const c = custom(i.id), t = c || ov(i.id);
      t.qty = Math.max(0, st - i.q);
    }
  });
  adm.o = adm.o.slice(0, 300);
  admSave(); applyAdmin();
}

if (!adm.s.pin) { adm.s.pin = "2026"; adm.s.lock = true; admSave(); }
applyAdmin();

/* =====================  АНИМАЦИИ  ===================== */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* появление при прокрутке — работает и в окне, и внутри страницы товара */
function makeRevealer(root) {
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target;
      el.classList.add("in");
      const n = el.matches(".num") ? el : el.querySelector(".num");
      if (n && !n.dataset.done) countUp(n);
      io.unobserve(el);
    });
  }, { root, rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  return io;
}
function countUp(el) {
  el.dataset.done = 1;
  const target = +el.dataset.n, t0 = performance.now(), dur = 1100;
  if (REDUCED) { el.textContent = target; return; }
  const tick = (t) => {
    const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
    el.textContent = Math.round(target * e);
    if (k < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
const pageIO = makeRevealer(null);
function observeReveals(scope, io) {
  scope.querySelectorAll(".rv, .grid .card, .num").forEach((el, i) => {
    if (el.classList.contains("card")) el.style.transitionDelay = ((i % 4) * 60) + "ms";
    io.observe(el);
  });
}
function markReveals() {
  document.querySelectorAll(".chead, .csub").forEach((el) => el.classList.add("rv"));
  document.querySelectorAll(".pp-chips span").forEach((s, i) => s.style.setProperty("--i", i));
}
markReveals();
observeReveals(document, pageIO);
/* карточки, которые перерисовываются админкой */
const _renderShop = renderShop;
renderShop = function () { _renderShop(); document.querySelectorAll(".grid .card").forEach((c, i) => {
  if (!c.classList.contains("in")) { c.style.transitionDelay = ((i % 4) * 60) + "ms"; pageIO.observe(c); }
}); };

/* hero главной: лёгкий параллакс */
(function () {
  const img = $(".heroimg img"), txt = $(".hero > div:first-child");
  if (!img || REDUCED) return;
  let ticking = false;
  const run = () => {
    ticking = false;
    const y = Math.min(scrollY, 700), k = y / 700;
    img.style.transform = "scale(" + (1 + k * 0.08) + ") translateY(" + (k * 40) + "px)";
    txt.style.opacity = 1 - k * 0.55;
    txt.style.transform = "translateY(" + (k * 30) + "px)";
  };
  addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(run); } }, { passive: true });
  run();
})();

/* история: смена картинки по шагам */
(function () {
  const steps = [...document.querySelectorAll(".step-item")], imgs = [...document.querySelectorAll(".story-stage img")];
  if (!steps.length) return;
  const set = (i) => {
    steps.forEach((s, j) => s.classList.toggle("on", j === i));
    imgs.forEach((im, j) => im.classList.toggle("on", j === i));
  };
  set(0);
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting) set(+e.target.dataset.step); });
  }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });
  steps.forEach((s) => io.observe(s));
})();

/* =====================  СТРАНИЦА ТОВАРА  ===================== */
const ppEl = $("#ppage"), ppScroll = $("#ppscroll");
let ppId = null, ppIO = null, ppScrub = null;

function genericPageHTML(it) {
  const img = it.img ? '<img src="' + it.img + '" alt="">' : (it.html || "");
  const cols = it.cl ? '<p class="rv ppcols"><b>Цвета в наличии:</b> ' + it.cl + "</p>" : "";
  return '<div class="pp theme-light simple"><section class="pp-hero small" data-scrub><div class="pp-pin">' +
    '<div class="pp-heroimg">' + img + '</div><div class="pp-herotext"><p class="eyebrow">3D HOUSE</p><h1>' + it.n +
    '</h1><p class="pp-name">' + it.d + '</p></div><div class="pp-hint"><span>Листайте вниз</span><i></i></div></div></section>' +
    '<section class="pp-cta"><div><h2 class="rv">' + it.n + '</h2><p class="rv">' + it.d + '</p>' + cols +
    '<div class="pp-actions rv"><button class="btn" data-pp-add>' + (it.ask ? "Узнать цену" : "В корзину") + '</button>' +
    '<a class="btn wa" data-pp-wa href="#" target="_blank" rel="noopener">Спросить в WhatsApp</a></div></div></section></div>';
}

function openPage(id) {
  const it = item(id); if (!it) return;
  const PP_ALIAS = { a1minic: "a1mini", a1c: "a1" };
  const tpl = document.getElementById("pp-" + (PP_ALIAS[id] || id));
  if (it.v) { openPicker(id); return; }
  if (!tpl && !it.img) return;
  ppScroll.innerHTML = tpl ? tpl.innerHTML : genericPageHTML(it);
  ppId = id;
  $("#ppTitle").textContent = it.n;
  $("#ppPrice").textContent = it.ask ? "Под заказ" : (it.cl ? "от " : "") + fmt(it.p);
  const st = stockOf(id);
  $("#ppStock").textContent = st == null ? "" : (st <= 0 ? "нет в наличии" : "в наличии " + st + " шт");
  const act = $("#ppAct");
  act.dataset.id = id; act.dataset.n = it.n; act.dataset.p = it.p;
  acts = [...document.querySelectorAll(".act")]; paint();
  /* кнопки внутри страницы */
  ppScroll.querySelectorAll("[data-pp-add]").forEach((b) => b.addEventListener("click", () => bump(act, 1)));
  const wa = (adm.s.wa || WA).replace(/\D/g, "");
  ppScroll.querySelectorAll("[data-pp-wa]").forEach((a) => {
    a.href = "https://wa.me/" + wa + "?text=" + encodeURIComponent("Здравствуйте! Интересует " + it.n + " — есть в наличии?");
  });
  /* показать */
  ppEl.classList.add("on"); ppEl.setAttribute("aria-hidden", "false");
  document.body.classList.add("pp-open");
  ppScroll.scrollTop = 0;
  const setH = () => ppEl.style.setProperty("--ppH", ppScroll.clientHeight + "px");
  setH(); addEventListener("resize", setH);
  if (ppIO) ppIO.disconnect();
  ppIO = makeRevealer(ppScroll);
  ppScroll.querySelectorAll(".pp-chips span").forEach((s, i) => s.style.setProperty("--i", i));
  observeReveals(ppScroll, ppIO);
  /* hero-скраб */
  const heroImg = ppScroll.querySelector(".pp-heroimg img"), heroTxt = ppScroll.querySelector(".pp-herotext"),
        hero = ppScroll.querySelector(".pp-hero");
  const scrub = () => {
    if (!hero) return;
    const H = hero.offsetHeight - ppScroll.clientHeight, y = Math.min(Math.max(ppScroll.scrollTop, 0), H), k = H > 0 ? y / H : 1;
    if (heroImg) heroImg.style.transform = "scale(" + (1.12 - k * 0.12) + ")";
    const hint = ppScroll.querySelector(".pp-hint");
    if (hint) hint.classList.toggle("off", ppScroll.scrollTop > 40);
    if (heroTxt) {
      const t = Math.min(1, Math.max(0, (k - 0.15) / 0.5));
      heroTxt.style.opacity = t; heroTxt.style.transform = "translateY(" + ((1 - t) * 30) + "px)";
    }
  };
  if (REDUCED) { if (heroTxt) { heroTxt.style.opacity = 1; heroTxt.style.transform = "none"; } if (heroImg) heroImg.style.transform = "none"; }
  else {
    let tk = false;
    ppScrub = () => { if (!tk) { tk = true; requestAnimationFrame(() => { tk = false; scrub(); }); } };
    ppScroll.addEventListener("scroll", ppScrub, { passive: true });
    scrub();
  }
  if (location.hash !== "#p/" + id) history.pushState({ pp: id }, "", "#p/" + id);
}
function closePage(back) {
  if (!ppEl.classList.contains("on")) return;
  ppEl.classList.remove("on"); ppEl.setAttribute("aria-hidden", "true");
  document.body.classList.remove("pp-open");
  if (ppScrub) ppScroll.removeEventListener("scroll", ppScrub);
  ppScroll.innerHTML = ""; ppId = null;
  acts = [...document.querySelectorAll(".act")];
  if (back !== false && location.hash.startsWith("#p/")) history.replaceState(null, "", location.pathname + location.search);
}
$("#ppBack").addEventListener("click", () => closePage());
$("#ppCart").addEventListener("click", () => { openCart(); });
addEventListener("popstate", () => { if (!location.hash.startsWith("#p/")) closePage(false); else openPage(location.hash.slice(3)); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closePage(); });

/* клик по карточке (не по кнопкам) */
document.addEventListener("click", (e) => {
  const card = e.target.closest(".card[data-pid]");
  if (!card || e.target.closest(".act, .addb, .step, button, a, details")) return;
  openPage(card.dataset.pid);
});
/* в корзине — кнопка "Оформить" должна закрыть страницу товара */
$("#toCheckout").addEventListener("click", () => closePage());
/* счётчик корзины на странице товара */
const _paint = paint;
paint = function () { _paint(); const c = $("#ppCnt"); if (c) c.textContent = Object.values(cart).reduce((a, x) => a + x.q, 0); };
/* открыть по ссылке */
if (location.hash.startsWith("#p/")) setTimeout(() => openPage(location.hash.slice(3)), 50);

/* ---------- квиз ---------- */
(function () {
  const QZ = [
    { q: "Для чего нужен принтер?", a: [["Для дома и хобби", "home"], ["Зарабатывать на печати", "earn"], ["Для бизнеса или производства", "biz"], ["Для учёбы и детей", "edu"]] },
    { q: "Какого размера детали будете печатать?", a: [["Небольшие — до 18 см", "s"], ["Средние — до 25 см", "m"], ["Крупные — 30 см и больше", "l"]] },
    { q: "Нужна многоцветная печать?", a: [["Да, хочу цветные модели", "y"], ["Нет, хватит одного цвета", "n"], ["Пока не знаю", "u"]] },
    { q: "Какие материалы планируете?", a: [["Обычные: PLA, PETG, TPU", "std"], ["Инженерные: ABS, ASA, нейлон", "eng"], ["Пока не знаю", "u"]] },
    { q: "Какой бюджет?", a: [["До 35 000 сом", "lo"], ["До 70 000 сом", "mid"], ["Выше 70 000 сом", "hi"]] },
  ];
  const WHY = {
    u1: "Четыре печатающие головы — многоцветная печать без долгой смены пластика.",
    cr5: "Четыре головы и закрытая камера с подогревом — многоцветная печать и инженерные пластики.",
    a1mini: "Компактный и простой — хороший первый принтер для небольших моделей.",
    a1minic: "Компактный принтер с AMS lite — печать в несколько цветов.",
    a1: "Универсальная модель с полем 256 мм — подходит для большинства задач.",
    a1c: "A1 с AMS lite — многоцветная печать без ручной смены пластика.",
    a2l: "Увеличенное поле печати 330 × 320 × 325 мм — для крупных деталей.",
    p1s: "Закрытый корпус — можно печатать ABS, ASA и другими инженерными пластиками.",
    p2s: "Закрытый корпус и комплект с AMS — для инженерных пластиков и многоцветной печати.",
    x2d: "Старшая модель в комплекте Combo — для сложных материалов и мелкой серии.",
    a2lcn: "Увеличенное поле печати 330 × 320 × 325 мм. Китайская версия: нужен компьютер и Wi-Fi.",
    h2d: "Два сопла и подогреваемая камера — для инженерных материалов и мелкой серии.",
  };
  const mask = $("#quizMask"), body = $("#quizBody"), qEl = $("#quizQ"), stepEl = $("#quizStep"), bar = $("#quizBar"), back = $("#quizBack");
  if (!mask) return;
  let ans = [], i = 0;
  const ok = (id) => BASE.has(id) && !isDel(id) && !item(id).off && !item(id).ask;
  const inStock = (id) => { const st = stockOf(id); return st == null || st > 0; };
  /* размер поля: s — 180 мм, m — 256 мм, l — 330 мм; mc — многоцветная печать; eng — закрытый корпус для инженерных пластиков */
  const SPEC = {
    a1mini: { sz: "s" }, a1minic: { sz: "s", mc: 1 }, a1: { sz: "m" }, a1c: { sz: "m", mc: 1 },
    a2lcn: { sz: "l", mc: 1 }, a2l: { sz: "l", mc: 1 }, p1s: { sz: "m", mc: 1, eng: 1 },
    p2s: { sz: "m", mc: 1, eng: 1 }, x2d: { sz: "m", mc: 1, eng: 1, pro: 1 }, h2d: { sz: "l", mc: 1, eng: 1, pro: 1 },
    u1: { sz: "m", mc: 1, heads: 1 },
    cr5: { sz: "m", mc: 1, eng: 1, heads: 1 },
  };
  function pick() {
    const [use, size, color, mat, bud] = ans;
    const lo = bud === "lo" ? 0 : bud === "mid" ? 35000 : 70000;
    const cap = bud === "lo" ? 35000 : bud === "mid" ? 70000 : Infinity;
    let all = Object.keys(SPEC).filter(ok);
    if (all.some(inStock)) all = all.filter(inStock);
    const score = (id) => {
      const sp = SPEC[id], p = item(id).p; let s = 0;
      if (p > lo && p <= cap) s += 20;                 // в бюджете — главное
      else if (p > cap) s -= 40;                       // дороже бюджета — почти никогда
      else s -= (lo - p) / 5000;                       // дешевле выбранного бюджета — ниже в списке
      if (size === "l") s += sp.sz === "l" ? 15 : -15;
      if (size === "s" && sp.sz === "s") s += 3;
      if (mat === "eng") s += sp.eng ? 15 : -15;
      if (color === "y") s += sp.mc ? 8 : -8;
      if (color === "u" && sp.mc) s += 2;
      if (color === "y" && sp.heads) s += 4;                 // несколько голов — многоцвет без отходов
      if (id === "a1" || id === "p2s") s += 3;              // хиты продаж
      if ((use === "biz" || use === "earn") && (sp.eng || sp.pro)) s += 3;
      if (use === "biz" && sp.pro) s += 5;
      if ((use === "edu" || use === "home") && color === "n" && !sp.eng && bud !== "hi") s += 2;
      return s;
    };
    const o = all.map((id) => [id, score(id)]).sort((a, b) => b[1] - a[1] || item(a[0]).p - item(b[0]).p).map((x) => x[0]);
    const best = o[0];
    return { best, alt: o.filter((x) => x !== best && item(x).p <= cap)[0] };
  }
  function show() {
    back.style.visibility = i > 0 ? "visible" : "hidden";
    if (i < QZ.length) {
      stepEl.textContent = "Вопрос " + (i + 1) + " из " + QZ.length;
      bar.style.width = (i / QZ.length * 100) + "%";
      qEl.textContent = QZ[i].q;
      body.innerHTML = '<div class="qopts">' + QZ[i].a.map((a) =>
        '<button type="button" data-v="' + a[1] + '"' + (ans[i] === a[1] ? ' class="on"' : "") + ">" + a[0] + "</button>").join("") + "</div>";
      return;
    }
    bar.style.width = "100%";
    stepEl.textContent = "Ваш результат";
    const r = pick();
    if (!r.best) { qEl.textContent = "Подберём вместе"; body.innerHTML = '<p class="qwhy">Напишите нам — подскажем модель под вашу задачу.</p>'; return; }
    const it = item(r.best), wa = ((adm && adm.s && adm.s.wa) || WA).replace(/\D/g, "");
    const txt = "Здравствуйте! Прошёл квиз на сайте, мне подошёл " + it.n + ". Ответы: " +
      QZ.map((q, k) => (q.a.find((a) => a[1] === ans[k]) || [""])[0]).join("; ") + ".";
    qEl.textContent = "Вам подойдёт " + it.n;
    let h = '<div class="qres"><div class="qimg">' + (it.html || "") + "</div><div>" +
      '<p class="qwhy">' + (WHY[r.best] || it.d) + "</p>" +
      '<div class="pr"><b>' + nfmt(it.p) + "</b><span>сом</span></div>" +
      '<p class="qgift">' + ((window.GIFT && GIFT[r.best]) || "+ 1 кг пластика в подарок") + "</p></div></div>" +
      '<div class="qacts"><div class="act" data-id="' + r.best + '" data-n="' + it.n.replace(/"/g, "&quot;") + '" data-p="' + it.p + '"></div>' +
      '<a class="btn ghost" href="https://wa.me/' + wa + "?text=" + encodeURIComponent(txt) + '" target="_blank" rel="noopener">Обсудить в WhatsApp</a></div>';
    if (r.alt) h += '<p class="qalt">Ещё вариант: <b>' + item(r.alt).n + "</b> — " + nfmt(item(r.alt).p) + " сом</p>";
    h += '<button type="button" class="qagain" id="quizAgain">Пройти заново</button>';
    body.innerHTML = h;
    rescan(); paint();
  }
  const open = () => { ans = []; i = 0; show(); mask.classList.add("on"); };
  const close = () => { mask.classList.remove("on"); body.innerHTML = ""; rescan(); };
  $("#quizOpen").addEventListener("click", open);
  $("#quizX").addEventListener("click", close);
  mask.addEventListener("click", (e) => { if (e.target === mask) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && mask.classList.contains("on")) close(); });
  back.addEventListener("click", () => { if (i > 0) { i--; show(); } });
  body.addEventListener("click", (e) => {
    const b = e.target.closest(".qopts button");
    if (b) { ans[i] = b.dataset.v; i++; show(); return; }
    if (e.target.closest("#quizAgain")) { ans = []; i = 0; show(); }
  });
})();

/* ---------- видеоуроки ---------- */
(function () {
  const IG = "https://instagram.com/3dhouse.kg";
  /* t — название, d — описание, url — ссылка на видео (YouTube / Instagram), tag — подпись */
  const VIDEOS = [
    { t: "Первые шаги", d: "Распаковка, запуск и первая печать", url: IG, tag: "Для новичков" },
    { t: "Лайфхаки печати", d: "Как печатать быстрее и без брака", url: IG, tag: "Советы" },
    { t: "Материалы", d: "Какой пластик выбрать под задачу", url: IG, tag: "Пластик" },
    { t: "Заработок на печати", d: "Что печатать на продажу", url: IG, tag: "Бизнес" },
  ];
  const g = document.getElementById("vgrid"); if (!g) return;
  const yt = (u) => { const m = /(?:youtu\.be\/|v=|shorts\/|embed\/)([\w-]{11})/.exec(u || ""); return m ? m[1] : null; };
  g.innerHTML = VIDEOS.map((v, i) => {
    const id = yt(v.url);
    return '<a class="vcard" href="' + v.url + '" target="_blank" rel="noopener">' +
      '<div class="vth"' + (id ? ' style="background-image:url(https://i.ytimg.com/vi/' + id + '/hqdefault.jpg)"' : "") + '><span class="vnum">' + String(i + 1).padStart(2, "0") + '</span><i class="vplay"></i>' +
      (v.tag ? '<span class="vtag">' + v.tag + "</span>" : "") + "</div>" +
      "<b>" + v.t + "</b><p>" + v.d + '</p><span class="vsrc">' + (id ? "Смотреть на YouTube" : "Смотреть в Instagram") + " →</span></a>";
  }).join("");
})();

/* ---------- выбор цвета пластика ---------- */
function openPicker(pid) {
  const k = CRM[pid]; if (!k || !k.v) return;
  const it = item(pid), m = $("#fpMask");
  const ws = []; k.v.forEach((x) => { if (ws.indexOf(x[5]) < 0) ws.push(x[5]); });
  let w = ws[0], cur = null;
  $("#fpT").textContent = it.n;
  $("#fpD").textContent = FDESC[pid] || (it.d || "").split(" · ")[0];
  const list = () => k.v.filter((x) => x[5] === w);
  function sel(x) {
    cur = x;
    $("#fpSpool").style.setProperty("--bg", swBg(x[2], pid));
    $("#fpC").textContent = x[1];
    $("#fpNew").hidden = !((FNEW[pid] || []).indexOf(x[2]) > -1);
    $("#fpP").textContent = nfmt(x[3]);
    const q = $("#fpQ");
    q.className = "stk" + (x[4] <= 0 ? " out" : x[4] <= 3 ? " low" : "");
    q.textContent = x[4] <= 0 ? "Нет в наличии" : x[4] <= 3 ? "Осталось " + x[4] + " шт" : "В наличии " + x[4] + " шт";
    const a = $("#fpAct");
    a.dataset.id = "f:" + x[0]; a.dataset.n = it.n + " · " + x[1] + (x[5] ? " · " + x[5] : ""); a.dataset.p = x[3];
    acts = [...document.querySelectorAll(".act")]; paint();
    marks();
  }
  function marks() {
    $("#fpSw").querySelectorAll("button").forEach((b) => {
      b.classList.toggle("on", cur && b.dataset.i === cur[0]);
      const n = (cart["f:" + b.dataset.i] || {}).q || 0;
      b.dataset.n = n || "";
    });
  }
  function draw() {
    $("#fpW").innerHTML = ws.length > 1 ? ws.map((x) => '<button type="button" data-w="' + x + '"' + (x === w ? ' class="on"' : "") + ">" + x + "</button>").join("") : (w ? "<span>" + w + "</span>" : "");
    const l = list();
    $("#fpSw").innerHTML = l.map((x) => '<button type="button" data-i="' + x[0] + '" class="' + (x[4] <= 0 ? "out" : "") + '" style="--b:' + swBg(x[2], pid) + '" title="' + x[1] + '" aria-label="' + x[1] + '"></button>').join("");
    sel(l.find((x) => x[4] > 0) || l[0]);
  }
  m.onclick = (e) => {
    if (e.target === m || e.target.closest("#fpX")) { m.classList.remove("on"); $("#fpAct").innerHTML = ""; return; }
    const wb = e.target.closest("#fpW button"); if (wb) { w = wb.dataset.w; draw(); return; }
    const sb = e.target.closest("#fpSw button"); if (sb) { sel(k.v.find((x) => x[0] === sb.dataset.i)); return; }
    setTimeout(marks, 0);
  };
  draw();
  m.classList.add("on");
}
document.addEventListener("keydown", (e) => { if (e.key === "Escape") { const m = $("#fpMask"); if (m) m.classList.remove("on"); } });
/* фильтр по типам пластика */
(function () {
  const G = { pla: ["pla", "plam", "plas", "fplus", "fpro", "ftr", "fglow", "fwood", "fmar", "fgal", "fspk"], petg: ["petg", "fpm", "fps"],
    flex: ["tpu95", "tpuams", "asa", "abs", "pacf", "pva"], bl: ["fblb", "fblm", "tpuams"] };
  const box = document.getElementById("ffilter"); if (!box) return;
  box.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    const g = b.dataset.g;
    document.querySelectorAll("#filament .card[data-pid]").forEach((c) => c.classList.toggle("fhide", g !== "all" && G[g].indexOf(c.dataset.pid) < 0));
  });
})();

/* счётчики разделов */
(function () {
  const pl = (n, a, b, c) => { const x = n % 10, y = n % 100; return x === 1 && y !== 11 ? a : (x >= 2 && x <= 4 && !(y >= 12 && y <= 14) ? b : c); };
  const set = (id, a, b, c) => { const s = document.getElementById(id), el = s && s.querySelector(".cnum"); if (!el) return;
    const n = s.querySelectorAll(".card[data-pid]:not(.off)").length; el.textContent = n + " " + pl(n, a, b, c); };
  set("printers", "модель", "модели", "моделей"); set("filament", "вид", "вида", "видов");
})();
