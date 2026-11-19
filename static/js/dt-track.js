/**
 * dt-track.js — kardeş siteler için çerezsiz davranış izleyici (drdevrim.com, devrimbirikensipahi.com.tr).
 * Merkez: dentaltourism.tr /api/t/ (çok siteli takip + persona). Kullanım:
 *
 *   <script src="https://dentaltourism.tr/static/js/dt-track.js" data-site="drd" defer></script>
 *   data-api   (isteğe bağlı) merkez kök URL — varsayılan https://dentaltourism.tr
 *   data-page  (isteğe bağlı) sayfa türü ipucu (home, pseo-area, treatment …) — yoksa <meta name="dt-page">,
 *              o da yoksa merkez URL'den çıkarır
 *
 * Lead: window.dtTrack.lead({name, phone, email, message, source}, cb) → POST /api/t/lead/ (site/vid/sid/page
 * otomatik eklenir, JSON yanıtı döner). Sunucu tarafı formlar için her submit'te forma dt_vid / dt_sid / dt_site
 * gizli alanları eklenir — arka uç bunları X-DT-Key ile merkeze iletir.
 *
 * Toplananlar (hepsi "neden yazdı / neden yazmadı" sorusu için):
 *   sayfa görüntüleme (SPA: window.dtTrack.pageview()), ilk insan hareketi (engaged — bot ayrımı), sekme görünürken
 *   geçen süre + en derin kaydırma, scroll eşikleri, bölüm görünürlüğü/süresi, SSS açma + okuma süresi, tüm tıklamalar
 *   (tel / WhatsApp / yönlendirme sayfaları / e-posta / harita / Instagram / YouTube / randevu; iç bağlantılar = nav_click,
 *   dış bağlantılar = outbound_click, href'siz butonlar = ui_click, dil değişimi = language_switch), galeri fotoğrafına
 *   dokunma, gömülü harita/YouTube/Calendly'ye tıklama, Calendly adımları (randevu alındı = form_submit), telefon
 *   numarası kopyalama, form başlatma/gönderme/yarım bırakma, video, çıkış niyeti (masaüstü), başka sekmeden dönüş,
 *   iletişim uygulamasından dönüş, sinirli tıklama, JS hatası.
 * Kimlik: localStorage dt_vid (kardeş sitelerde ?dtv= ile taşınır); oturum: 30 dk hareketsizlikte yenilenen
 * sessionStorage dt_sid. Çerez yazmaz, GA'ya dokunmaz.
 */
(function () {
  "use strict";
  var me = document.currentScript || (function () { var s = document.querySelectorAll("script[data-site]"); return s[s.length - 1]; })();
  if (!me) return;
  var SITE = me.getAttribute("data-site") || "";
  var API = (me.getAttribute("data-api") || "https://dentaltourism.tr").replace(/\/$/, "");
  var PAGE_HINT = me.getAttribute("data-page") || (function () { var m = document.querySelector('meta[name="dt-page"]'); return (m && m.getAttribute("content")) || ""; })();
  if (!SITE) return;
  var ID_RE = /^[a-f0-9]{16,40}$/, SISTERS = /(^|\.)(dentaltourism\.tr|drdevrim\.com|devrimbirikensipahi\.com\.tr)$/i;
  var LANGS = /^(tr|en|de|fr|nl|it|es|pl|ru|uk|bg|sv|da|no|ro|ar|az)$/;

  function rnd(n) {
    var out = "", a = new Uint8Array(n / 2);
    if (window.crypto && crypto.getRandomValues) { crypto.getRandomValues(a); for (var i = 0; i < a.length; i++) out += ("0" + a[i].toString(16)).slice(-2); return out; }
    while (out.length < n) out += Math.floor(Math.random() * 16).toString(16);
    return out;
  }
  function store(k, v, s) { try { (s ? sessionStorage : localStorage).setItem(k, v); } catch (e) {} }
  function load(k, s) { try { return (s ? sessionStorage : localStorage).getItem(k) || ""; } catch (e) { return ""; } }
  function txt(el, n) { return ((el && (el.getAttribute("aria-label") || el.textContent)) || "").replace(/\s+/g, " ").trim().slice(0, n || 100); }

  // ── Kimlik: ?dtv= (kardeş siteden geçiş) > localStorage > yeni ───────────────────────────────────────────────
  var VID = load("dt_vid"), PREV_VID = "";
  try {
    var handoff = new URLSearchParams(location.search).get("dtv") || "";
    if (ID_RE.test(handoff) && handoff !== VID) { PREV_VID = VID; VID = handoff; }
  } catch (e) {}
  if (!ID_RE.test(VID)) VID = rnd(32);
  store("dt_vid", VID);

  // ── Oturum: 30 dk hareketsizlikte yeni sid ───────────────────────────────────────────────────────────────────
  var SID = load("dt_sid", true), SID_T = parseInt(load("dt_sid_t", true) || "0", 10) || 0, NOW = Date.now();
  if (!ID_RE.test(SID) || NOW - SID_T > 30 * 60000) SID = rnd(24);
  function touch() { store("dt_sid", SID, true); store("dt_sid_t", String(Date.now()), true); }
  touch();

  // ── Reklam atfı (ilk + son dokunuş, localStorage) ───────────────────────────────────────────────────────────
  var ATTR_KEYS = ["gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"], ATTR = {};
  try {
    var params = new URLSearchParams(location.search), fresh = {};
    ATTR_KEYS.forEach(function (k) { var v = params.get(k); if (v) fresh[k] = v.slice(0, 255); });
    var first = JSON.parse(load("dt_attr_first") || "null");
    if (first && NOW - (first._t || 0) > 90 * 86400000) first = null;
    if (Object.keys(fresh).length) { fresh._t = NOW; if (!first) { first = fresh; store("dt_attr_first", JSON.stringify(first)); } store("dt_attr_last", JSON.stringify(fresh)); }
    var last = JSON.parse(load("dt_attr_last") || "null") || {};
    ATTR_KEYS.forEach(function (k) { var v = (last && last[k]) || (first && first[k]); if (v) ATTR[k] = v; });
  } catch (e) {}

  // ── Kişiselleştirme kararı: merkez {persona, level, message} döner → <html data-dt-persona data-dt-level>, "dt:persona" olayı
  // Kardeş site isterse bu olaya göre nazik bir mesaj gösterir (dentaltourism'deki mind_nudge gibi). Varsayılan: yalnızca işaret.
  function applyDecision(d) {
    if (!d || !d.persona) return;
    var root = document.documentElement, changed = root.getAttribute("data-dt-persona") !== d.persona || root.getAttribute("data-dt-level") !== (d.level || "weak");
    root.setAttribute("data-dt-persona", d.persona); root.setAttribute("data-dt-level", d.level || "weak");
    if (window.dtTrack) window.dtTrack.decision = d;
    try { document.dispatchEvent(new CustomEvent("dt:persona", { detail: { decision: d, changed: changed } })); } catch (e) {}
  }

  // ── Taşıma: text/plain → CORS ön-uçuşu yok; sendBeacon çıkışta da ulaşır ─────────────────────────────────────
  function post(path, payload, cb) {
    payload.site = SITE; payload.vid = VID; payload.sid = SID; payload.attr = ATTR;
    var body = JSON.stringify(payload), url = API + path;
    touch();
    if (!cb && navigator.sendBeacon) { try { if (navigator.sendBeacon(url, new Blob([body], { type: "text/plain" }))) return; } catch (e) {} }
    try {
      fetch(url, { method: "POST", mode: "cors", credentials: "omit", keepalive: true, headers: { "Content-Type": "text/plain" }, body: body })
        .then(function (r) { return r.json(); }).then(function (j) { if (j && j.decision) applyDecision(j.decision); if (cb && j) cb(j); }).catch(function () {});
    } catch (e) {}
  }

  var PAGE_URL = location.pathname, PAGE_TYPE = PAGE_HINT;
  var queue = [], qTimer = null, NOW_RE = /_click$|^form_|^phone_copy$|^booking_step$/,
      MIND_EVENTS = { faq_open: 1, faq_read: 1, before_after_interact: 1, video_play: 1, youtube_click: 1, booking_step: 1 };
  function flushQueue() {
    if (qTimer) { clearTimeout(qTimer); qTimer = null; }
    if (!queue.length) return;
    var batch = queue; queue = [];
    post("/api/t/event/", { events: batch });
  }
  function track(type, data) {
    data = data || {}; data.lang = data.lang || document.documentElement.lang || "";
    var ev = { event_type: type, data: data, page_url: PAGE_URL, page_type: PAGE_TYPE };
    if (MIND_EVENTS[type] && !flushed) {
      post("/api/t/event/", { events: [ev] }, function (j) { if (j && j.mind) document.dispatchEvent(new CustomEvent("dt:mind", { detail: { mind: j.mind } })); });
      return;
    }
    queue.push(ev);
    if (flushed) return;
    if (NOW_RE.test(type)) flushQueue(); else if (!qTimer) qTimer = setTimeout(flushQueue, 4000);
  }

  // ── Konum: butonun sayfadaki yeri ─────────────────────────────────────────────────────────────────────────
  var POSITIONS = [[".brand-bar, .watermark, .floating, .float-buttons, .fixed-buttons, #floating-buttons", "float"],
    [".mind-nudge, .dt-nudge, #mind-nudge", "mind-nudge"],
    ["nav, header, .site-header, .navbar, .the-nav", "navbar"], ["footer, .site-footer", "footer"],
    [".faq, .faq-section, .faq-item", "faq"], [".cta-band, .final-cta, .cta-box", "cta"], [".contact, #iletisim, #contact", "contact"],
    [".hero, .svc-hero, [class*=hero]", "hero"], [".reviews, .shorts-grid, .yt-section", "reviews"]];
  function positionOf(el) {
    if (!el || !el.closest) return "content";
    for (var i = 0; i < POSITIONS.length; i++) if (el.closest(POSITIONS[i][0])) return POSITIONS[i][1];
    var sec = el.closest("section[id], [data-track-section]");
    return sec ? (sec.id || sec.getAttribute("data-track-section")) : "content";
  }

  // ── Sayfa görüntüleme (SPA route geçişinde dtTrack.pageview() çağrılır) ────────────────────────────────────
  var TZ = ""; try { TZ = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  var WD = 0; try { WD = navigator.webdriver ? 1 : 0; } catch (e) {}
  function pageview(hint) {
    PAGE_URL = location.pathname; PAGE_TYPE = hint || PAGE_HINT;
    post("/api/t/pageview/", { url: location.href, title: document.title, referrer: document.referrer, tz: TZ,
                                sw: screen.width, sh: screen.height, page_type: PAGE_TYPE, prev_vid: PREV_VID,
                                wd: WD, tp: navigator.maxTouchPoints || 0, lg: (navigator.languages || []).length, dpr: window.devicePixelRatio || 1 },
         function () {});  // fetch yolu: karar yanıtta döner (sendBeacon yanıt vermez)
    PREV_VID = "";
    fired = {}; seen = {}; dwell = {}; start = Date.now(); segment = 0; flushed = false; maxDepth = 0; clicks = 0;
    exitSent = false; galleryT = 0; rageSent = false; iframeSeen = {}; startedForms = [];
  }

  // ── İlk insan hareketi: parmak / fare / klavye / tekerlek (kaydırma değil: başsız tarayıcılar da kaydırır) ──
  var ENGAGED = false, T0 = Date.now(), moves = 0, clicks = 0;
  function engage(kind) { if (ENGAGED) return; ENGAGED = true; track("engaged", { kind: kind, after_ms: Date.now() - T0 }); }
  addEventListener("pointerdown", function () { clicks++; engage("pointer"); }, true);
  addEventListener("touchstart", function () { engage("touch"); }, { passive: true, capture: true });
  addEventListener("keydown", function () { engage("key"); }, true);
  addEventListener("wheel", function () { engage("wheel"); }, { passive: true, capture: true });
  addEventListener("mousemove", function () { if (++moves >= 3) engage("mouse"); }, { passive: true, capture: true });

  // ── Scroll ──────────────────────────────────────────────────────────────────────────────────────────────────
  var fired = {}, maxDepth = 0;
  addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight, d = h > 0 ? Math.round(scrollY / h * 100) : 100;
    if (d > maxDepth) maxDepth = Math.min(d, 100);
    [25, 50, 75, 90].forEach(function (t) { if (d >= t && !fired[t]) { fired[t] = 1; track("scroll_depth", { depth: t }); } });
  }, { passive: true });

  // ── Bölüm görünürlüğü / süresi ─────────────────────────────────────────────────────────────────────────────
  var visibleSince = {}, seen = {}, dwell = {};
  function sectionName(el) { return el.getAttribute("data-track-section") || el.id || ""; }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var s = sectionName(e.target); if (!s) return;
        if (e.isIntersecting) { visibleSince[s] = Date.now(); if (!seen[s]) { seen[s] = 1; track("section_view", { section: s }); } }
        else if (visibleSince[s]) { dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; delete visibleSince[s]; }
      });
    }, { threshold: 0.35 });
    function observeSections() { document.querySelectorAll("[data-track-section], section[id]").forEach(function (el) { io.observe(el); }); }
    observeSections();
    if ("MutationObserver" in window) new MutationObserver(function () { observeSections(); }).observe(document.body, { childList: true, subtree: true });
  }

  // ── Tıklamalar: href'ten tür çıkarımı (sayfa sayfa data-attr gerekmez) ──────────────────────────────────────
  var MAP = { whatsapp: "whatsapp_click", whatsapp_call: "whatsapp_click", phone: "phone_click", cta: "cta_click", maps: "maps_click",
              instagram: "instagram_click", youtube: "youtube_click", email: "email_click", nav: "nav_click", form: "cta_click",
              booking: "cta_click", outbound: "outbound_click", ui: "ui_click", lang: "language_switch", "lang-switch": "language_switch",
              treatment: "nav_click", partner: "nav_click", blog: "nav_click", before_after: "before_after_interact", gallery: "gallery_view",
              chatbot_open: "chatbot_open", chatbot_toggle: "chatbot_open", chatbot_message: "chatbot_message", faq_tab: "ui_click" };
  function typeFromHref(href) {
    if (!href) return "";
    if (href.indexOf("tel:") === 0 || /telefon-yonlendirme/.test(href)) return "phone";
    if (href.indexOf("mailto:") === 0) return "email";
    if (/wa\.me\/|api\.whatsapp\.com|whatsapp-yonlendirme/.test(href)) return "whatsapp";
    if (/instagram\.com|instagram-yonlendirme/.test(href)) return "instagram";
    if (/youtube\.com|youtu\.be/.test(href)) return "youtube";
    if (/google\.[a-z.]+\/maps|maps\.app\.goo\.gl|maps\.google|g\.page|maps-yonlendirme/.test(href)) return "maps";
    if (/randevu|calendly|appointment|termin/.test(href)) return "booking";
    return "";
  }
  function langOfPath(p) { var m = (p || "").match(/^\/(?:lang\/)?([a-z]{2})(?=\/|$)/); return m && LANGS.test(m[1]) ? m[1] : ""; }
  var CUR_LANG = langOfPath(location.pathname) || (document.documentElement.lang || "tr").slice(0, 2).toLowerCase();
  // İç bağlantı → nav (dil öneki değiştiyse language_switch); başka site → outbound; href'siz / # → ui
  function classifyLink(el, href) {
    if (el.tagName !== "A" || !href || href.charAt(0) === "#" || /^javascript:/i.test(href)) return { type: "ui" };
    var u; try { u = new URL(href, location.href); } catch (e) { return { type: "ui" }; }
    if (!/^https?:$/.test(u.protocol)) return { type: "" };
    if (u.hostname !== location.hostname) return { type: SISTERS.test(u.hostname) ? "nav" : "outbound" };
    var to = langOfPath(u.pathname) || "tr";
    if (to !== CUR_LANG && (langOfPath(u.pathname) || (u.pathname === "/" || u.pathname.split("/").length <= 2))) return { type: "lang", to: to };
    return { type: "nav" };
  }
  var CONTACT_KINDS = { phone: "phone", whatsapp: "whatsapp", maps: "maps", email: "email" }, lastContact = null;
  var lastClick = { k: "", t: 0 }, rage = { el: null, n: 0, t: 0 }, rageSent = false, galleryT = 0;
  function galleryClick(img) {
    var now = Date.now(); if (now - galleryT < 2000) return; galleryT = now;
    var sec = img.closest("[data-track-section], section[id], [class*=gallery], [class*=galeri], [class*=lightbox], [class*=swiper], [class*=before], [class*=once], figure");
    var name = sec ? (sec.getAttribute("data-track-section") || sec.id || String(sec.className || "").split(" ")[0]) : "";
    var n = String(name).toLowerCase(), cls = String((img.closest("[class*=gallery], [class*=galeri], [class*=lightbox], [class*=swiper], figure") || {}).className || "").toLowerCase();
    var data = { section: name.slice(0, 40), label: (img.alt || "").slice(0, 60), position: positionOf(img) };
    if (/before|after|once|sonra|vorher|nachher/.test(n + " " + cls)) track("before_after_interact", data);
    else if (/galeri|gallery|foto|photo|lightbox|swiper|kareler|figure/.test(n + " " + cls) || img.closest("figure")) track("gallery_view", data);
    else { data.element = "image"; track("ui_click", data); }   // hero / arka plan görseli: kayıt var, persona ağırlığı yok
  }
  document.addEventListener("click", function (e) {
    var t = e.target; if (!t || !t.closest) return;
    var now = Date.now();
    if (rage.el === t && now - rage.t < 1000) rage.n++; else { rage.el = t; rage.n = 1; }
    rage.t = now;
    if (rage.n >= 3 && !rageSent) { rageSent = true; track("rage_click", { label: txt(t, 60), position: positionOf(t) }); }
    var el = t.closest("a[href], button, [role=button], [data-track], [data-cta], summary");
    if (!el) { if (t.tagName === "IMG") galleryClick(t); return; }
    if (el.tagName === "SUMMARY" || el.closest("details > summary")) return;   // SSS: toggle dinleyicisi ölçer
    var href = el.getAttribute("href") || el.getAttribute("data-href") || "";
    var type = el.getAttribute("data-track") || el.getAttribute("data-cta") || typeFromHref(href), to = "";
    // Kardeş siteye giden link: kimliği taşı (aynı kişi, tek yolculuk)
    if (href.indexOf("http") === 0) { try { var u = new URL(href); if (SISTERS.test(u.hostname) && u.hostname !== location.hostname && !u.searchParams.get("dtv")) { u.searchParams.set("dtv", VID); el.setAttribute("href", u.toString()); if (!type) type = "nav"; } } catch (err) {} }
    if (type === "faq") return;
    if (!type) {
      if (t.tagName === "IMG" && el.tagName !== "A" && !el.closest("button")) { galleryClick(t); return; }
      var c = classifyLink(el, href); type = c.type; to = c.to || "";
      if (!type) return;
      if (type === "ui" && el.closest("form") && (el.type === "submit" || (el.tagName === "BUTTON" && !el.type))) return;  // form_submit sayar
    }
    var head = el.querySelector("h2, h3, h4");
    var label = (el.getAttribute("aria-label") || (head && head.textContent) || el.textContent || el.title || "").replace(/\s+/g, " ").trim().slice(0, 100);
    if (!label && el.querySelector("img")) label = (el.querySelector("img").alt || "").slice(0, 100);
    var name = MAP[type] || "ui_click", key = name + "|" + label + "|" + href;
    if (key === lastClick.k && now - lastClick.t < 1500) return;   // iç içe öğelerden çift tetiklenme
    lastClick = { k: key, t: now };
    var data = { element: type, label: label, text: label.slice(0, 60), href: href.slice(0, 200), position: positionOf(el), screen: screen.width + "x" + screen.height };
    if (to) data.to = to;
    track(name, data);
    if (CONTACT_KINDS[type]) lastContact = { kind: CONTACT_KINDS[type], label: label.slice(0, 60), position: positionOf(el), t: now };
  }, true);

  // ── Telefon numarası / adres kopyalama (masaüstünde aramanın karşılığı) ────────────────────────────────────
  document.addEventListener("copy", function () {
    var s = "", node = null;
    try { var sel = getSelection(); s = String(sel || ""); node = sel && sel.anchorNode && (sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement); } catch (e) {}
    s = s.replace(/\s+/g, " ").trim(); if (!s) return;
    var digits = (s.match(/\d/g) || []).length;
    if (digits >= 7 && s.length <= 40) track("phone_copy", { label: s.slice(0, 40), position: positionOf(node) });
    else if (s.length >= 15) track("text_copy", { label: s.slice(0, 80), position: positionOf(node) });
  });

  // ── SSS: <details> (drdevrim) ve class tabanlı akordeonlar (devrimbirikensipahi: .faq-toggle / .faq-q) ────────
  var faqOpen = {};
  function qText(el) { var s = el.querySelector("summary, h3, h4, .faq-q, button") || el; return (s.textContent || "").replace(/\s+/g, " ").trim().slice(0, 160); }
  function faqStart(q) { if (!q || faqOpen[q]) return; faqOpen[q] = Date.now(); track("faq_open", { q: q }); }
  function faqClose(q) { var t = faqOpen[q]; if (!t) return; delete faqOpen[q]; track("faq_read", { q: q, seconds: Math.round((Date.now() - t) / 1000) }); }
  document.addEventListener("toggle", function (e) {
    var d = e.target; if (!d || !d.matches || !d.matches("details")) return;
    var q = qText(d); if (d.open) faqStart(q); else faqClose(q);
  }, true);
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".faq-toggle, .faq-q, [data-faq], .accordion-button, .faq-question");
    if (!b || b.closest("details")) return;
    var item = b.closest(".faq-item, .faq-group > div, li, .accordion-item") || b, q = qText(b);
    setTimeout(function () {  // sınıf değişimi tıklama işleyicisinden sonra olur
      var opened = item.classList.contains("open") || item.classList.contains("active") || b.getAttribute("aria-expanded") === "true" ||
                   (function () { var c = b.nextElementSibling; return c && !c.classList.contains("hidden") && c.offsetHeight > 0; })();
      if (opened) faqStart(q); else faqClose(q);
    }, 50);
  }, true);

  // ── Formlar: başlangıç, son alan, gönderim, yarım bırakma ─────────────────────────────────────────────────
  var startedForms = [];
  function formRec(f) { for (var i = 0; i < startedForms.length; i++) if (startedForms[i].f === f) return startedForms[i]; return null; }
  function formName(f) { return (f.id || f.getAttribute("name") || f.getAttribute("data-form") || f.className || "form").toString().slice(0, 60); }
  document.addEventListener("focusin", function (e) {
    var el = e.target, f = el.closest && el.closest("form"); if (!f) return;
    var r = formRec(f);
    if (!r) { r = { f: f, field: "", done: false }; startedForms.push(r); track("form_start", { form: formName(f) }); }
    if (el.name || el.id) r.field = (el.name || el.id).slice(0, 40);
  }, true);
  function hidden(f, name, value) {
    var el = f.querySelector('input[name="' + name + '"]');
    if (!el) { el = document.createElement("input"); el.type = "hidden"; el.name = name; f.appendChild(el); }
    el.value = value;
  }
  document.addEventListener("submit", function (e) {
    var f = e.target; if (!f || f.tagName !== "FORM") return;
    try { hidden(f, "dt_vid", VID); hidden(f, "dt_sid", SID); hidden(f, "dt_site", SITE); } catch (err) {}  // sunucu tarafı form → kimlik merkeze iletilir
    var r = formRec(f); if (r) r.done = true;
    track("form_submit", { form: formName(f) });
  }, true);
  function abandonForms() {
    startedForms.forEach(function (r) { if (!r.done && !r.abandoned) { r.abandoned = true; track("form_abandon", { form: formName(r.f), field: r.field, label: r.field }); } });
  }

  // ── Lead: formdan / chatbot'tan merkeze (yanıt gerekir → fetch) ───────────────────────────────────────────────
  function lead(payload, cb) {
    payload = payload || {};
    payload.site = SITE; payload.vid = VID; payload.sid = SID; payload.attr = ATTR;
    if (!payload.page) payload.page = location.href;
    if (!payload.language) payload.language = (document.documentElement.lang || "").slice(0, 10);
    if (!payload.source) payload.source = "form";
    touch();
    startedForms.forEach(function (r) { r.done = true; });
    var p = fetch(API + "/api/t/lead/", { method: "POST", mode: "cors", credentials: "omit", keepalive: true,
                                          headers: { "Content-Type": "text/plain" }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json(); });
    if (cb) p.then(cb, function () { cb({ ok: false, error: "network" }); });
    return p;
  }

  // ── Video: <video> oynatma + izleme süresi ─────────────────────────────────────────────────────────────────
  var vidT0 = 0, vidSecs = 0;
  document.addEventListener("play", function (e) { var v = e.target; if (v.tagName === "VIDEO" && !v.autoplay && !v.muted) { vidT0 = Date.now(); track("video_play", { label: (v.title || v.getAttribute("aria-label") || "").slice(0, 60), position: positionOf(v) }); } }, true);
  function videoStop() { if (vidT0) { vidSecs += (Date.now() - vidT0) / 1000; vidT0 = 0; } }
  document.addEventListener("pause", function (e) { if (e.target.tagName === "VIDEO") videoStop(); }, true);
  document.addEventListener("ended", function (e) { if (e.target.tagName === "VIDEO") videoStop(); }, true);

  // ── Gömülü harita / YouTube / Calendly: iframe'e tıklama (pencere odağı iframe'e geçer) ──────────────────────
  var iframeSeen = {};
  addEventListener("blur", function () {
    setTimeout(function () {
      var a = document.activeElement; if (!a || a.tagName !== "IFRAME") return;
      var src = a.src || a.getAttribute("data-src") || "", host = ""; try { host = new URL(src, location.href).hostname; } catch (e) {}
      if (iframeSeen[src || host]) return; iframeSeen[src || host] = 1;
      var pos = positionOf(a);
      if (/youtube|youtu\.be|vimeo/.test(host)) track("video_play", { embed: host, label: a.title || "video (gömülü)", position: pos });
      else if (/maps/.test(src) && /google/.test(host)) track("maps_click", { element: "maps", label: "harita (gömülü)", position: pos, embed: 1 });
      else if (/calendly/.test(host)) track("booking_step", { step: "focus", label: "Calendly takvimine tıkladı", position: pos });
      else if (host && !/googletagmanager|doubleclick|facebook|recaptcha/.test(host)) track("ui_click", { element: "iframe", label: host, position: pos });
    }, 0);
  });
  // Calendly adımları (postMessage): takvime baktı → saat seçti → randevu aldı (= lead)
  addEventListener("message", function (e) {
    var host = ""; try { host = new URL(e.origin).hostname; } catch (x) {}
    if (!/(^|\.)calendly\.com$/.test(host)) return;
    var ev = e.data && e.data.event; if (!ev || String(ev).indexOf("calendly.") !== 0) return;
    var step = String(ev).slice(9, 49);
    track("booking_step", { step: step, label: step });
    if (step === "event_scheduled") track("form_submit", { form: "calendly", label: "Calendly randevu" });
  });

  // ── JS hatası (bozuk buton = kayıp hasta) ───────────────────────────────────────────────────────────────────
  var errSent = false;
  addEventListener("error", function (e) {
    if (errSent || !e || !e.message || e.message === "Script error.") return; errSent = true;
    track("js_error", { label: String(e.message).slice(0, 120), src: String(e.filename || "").slice(-80), line: e.lineno || 0 });
  });

  // ── Süre: sekme görünürken; çıkışta tek beacon; iletişim uygulamasından / başka sekmeden dönüş ───────────────
  var start = Date.now(), flushed = false, hiddenAt = 0, segment = 0, CONTACT_RETURN_WINDOW = 15 * 60000, exitSent = false;
  function flush() {
    if (flushed) return; flushed = true;
    Object.keys(faqOpen).forEach(faqClose);
    videoStop(); if (vidSecs >= 1) { track("video_time", { seconds: Math.round(vidSecs) }); vidSecs = 0; }
    abandonForms();
    Object.keys(visibleSince).forEach(function (s) { dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; });
    Object.keys(dwell).forEach(function (s) { if (dwell[s] >= 3) track("section_time", { section: s, seconds: Math.round(dwell[s]) }); });
    var secs = Math.round((Date.now() - start) / 1000);
    track("time_on_page", { seconds: secs, segment: segment, max_scroll: maxDepth, clicks: clicks, engaged: ENGAGED });
    if (segment === 0 && secs < 10 && !maxDepth && !clicks) track("bounce", {});
    flushQueue();
  }
  function resume() {
    if (!flushed) return;
    flushed = false; segment++;
    var away = hiddenAt ? Math.round((Date.now() - hiddenAt) / 1000) : 0;
    hiddenAt = 0; start = Date.now(); dwell = {};
    Object.keys(visibleSince).forEach(function (s) { visibleSince[s] = Date.now(); });
    if (lastContact && Date.now() - lastContact.t < CONTACT_RETURN_WINDOW) {
      track("contact_return", { kind: lastContact.kind, label: lastContact.label, position: lastContact.position, away_seconds: away, likely_contacted: away >= 8 });
      lastContact = null;
    } else if (away >= 20) {
      track("tab_return", { away_seconds: away, label: away + " sn" });   // başka sekmelerde dolaştı (karşılaştırma)
    }
    if (queue.length) flushQueue();
  }
  addEventListener("pagehide", function () { hiddenAt = hiddenAt || Date.now(); flush(); });
  addEventListener("pageshow", function (e) { if (e.persisted) resume(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") { hiddenAt = Date.now(); flush(); } else resume(); });
  // Çıkış niyeti (masaüstü): fare pencereyi üstten terk etti — bir kez
  try {
    if (matchMedia("(pointer:fine)").matches) document.addEventListener("mouseout", function (e) {
      if (exitSent || e.relatedTarget || e.clientY > 0) return; exitSent = true;
      track("exit_intent", { after_sec: Math.round((Date.now() - start) / 1000), max_scroll: maxDepth, label: maxDepth + "%" });
    });
  } catch (e) {}

  // SPA (Nuxt) route geçişi: eski sayfayı kapat, yenisini aç
  window.dtTrack = { track: track, pageview: function (hint) { flush(); pageview(hint); }, lead: lead, vid: VID, sid: SID,
                     decision: null,
                     refresh: function (cb) { post("/api/t/persona/", { url: location.href }, function (j) { if (cb) cb(j && j.decision); }) } };
  pageview(PAGE_HINT);
})();
