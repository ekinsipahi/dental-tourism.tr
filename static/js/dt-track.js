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
 * Toplananlar: sayfa görüntüleme (SPA: window.dtTrack.pageview()), sekme görünürken geçen süre, scroll derinliği,
 * bölüm görünürlüğü/süresi, SSS açma + okuma süresi (details ve class tabanlı akordeonlar), video, form başlatma/
 * gönderme, tüm iletişim tıklamaları (tel / WhatsApp / yönlendirme sayfaları / e-posta / harita / Instagram / YouTube),
 * iletişim uygulamasından siteye dönüş. Kimlik: localStorage dt_vid (tüm kardeş sitelerde aynı kimlik ?dtv= ile
 * taşınır); oturum: 30 dk hareketsizlikte yenilenen sessionStorage dt_sid. Çerez yazmaz, GA'ya dokunmaz.
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

  function rnd(n) {
    var out = "", a = new Uint8Array(n / 2);
    if (window.crypto && crypto.getRandomValues) { crypto.getRandomValues(a); for (var i = 0; i < a.length; i++) out += ("0" + a[i].toString(16)).slice(-2); return out; }
    while (out.length < n) out += Math.floor(Math.random() * 16).toString(16);
    return out;
  }
  function store(k, v, s) { try { (s ? sessionStorage : localStorage).setItem(k, v); } catch (e) {} }
  function load(k, s) { try { return (s ? sessionStorage : localStorage).getItem(k) || ""; } catch (e) { return ""; } }

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

  // ── Taşıma: text/plain → CORS ön-uçuşu yok; sendBeacon çıkışta da ulaşır ─────────────────────────────────────
  function post(path, payload, cb) {
    payload.site = SITE; payload.vid = VID; payload.sid = SID; payload.attr = ATTR;
    var body = JSON.stringify(payload), url = API + path;
    touch();
    if (!cb && navigator.sendBeacon) { try { if (navigator.sendBeacon(url, new Blob([body], { type: "text/plain" }))) return; } catch (e) {} }
    try {
      fetch(url, { method: "POST", mode: "cors", credentials: "omit", keepalive: true, headers: { "Content-Type": "text/plain" }, body: body })
        .then(function (r) { return cb ? r.json() : null; }).then(function (j) { if (cb && j) cb(j); }).catch(function () {});
    } catch (e) {}
  }

  var PAGE_URL = location.pathname, PAGE_TYPE = PAGE_HINT;
  var queue = [], qTimer = null, NOW_RE = /_click$|^form_/, MIND_EVENTS = { faq_open: 1, faq_read: 1, before_after_interact: 1, video_play: 1, youtube_click: 1 };
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
    ["nav, header, .site-header, .navbar, .the-nav", "navbar"], ["footer, .site-footer", "footer"],
    [".faq, .faq-section, .faq-item", "faq"], [".cta-band, .final-cta, .cta-box", "cta"], [".contact, #iletisim, #contact", "contact"],
    [".hero, .svc-hero, [class*=hero]", "hero"], [".reviews, .shorts-grid, .yt-section", "reviews"]];
  function positionOf(el) {
    for (var i = 0; i < POSITIONS.length; i++) if (el.closest(POSITIONS[i][0])) return POSITIONS[i][1];
    var sec = el.closest("section[id], [data-track-section]");
    return sec ? (sec.id || sec.getAttribute("data-track-section")) : "content";
  }

  // ── Sayfa görüntüleme (SPA route geçişinde dtTrack.pageview() çağrılır) ────────────────────────────────────
  var TZ = ""; try { TZ = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  function pageview(hint) {
    PAGE_URL = location.pathname; PAGE_TYPE = hint || PAGE_HINT;
    post("/api/t/pageview/", { url: location.href, title: document.title, referrer: document.referrer, tz: TZ,
                                sw: screen.width, sh: screen.height, page_type: PAGE_TYPE, prev_vid: PREV_VID });
    PREV_VID = "";
    fired = {}; seen = {}; dwell = {}; start = Date.now(); segment = 0; flushed = false;
  }

  // ── Scroll ──────────────────────────────────────────────────────────────────────────────────────────────────
  var fired = {};
  addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight, d = h > 0 ? Math.round(scrollY / h * 100) : 100;
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
  var MAP = { whatsapp: "whatsapp_click", phone: "phone_click", cta: "cta_click", maps: "maps_click", instagram: "instagram_click",
              youtube: "youtube_click", email: "email_click", nav: "nav_click", form: "cta_click", booking: "cta_click" };
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
  var CONTACT_KINDS = { phone: "phone", whatsapp: "whatsapp", maps: "maps", email: "email" }, lastContact = null;
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("a[href], button, [data-track], [data-cta]");
    if (!el) return;
    var href = el.getAttribute("href") || el.getAttribute("data-href") || "";
    var type = el.getAttribute("data-track") || el.getAttribute("data-cta") || typeFromHref(href);
    // Kardeş siteye giden link: kimliği taşı (aynı kişi, tek yolculuk)
    if (href.indexOf("http") === 0) { try { var u = new URL(href); if (SISTERS.test(u.hostname) && u.hostname !== location.hostname && !u.searchParams.get("dtv")) { u.searchParams.set("dtv", VID); el.setAttribute("href", u.toString()); if (!type) type = "nav"; } } catch (err) {} }
    if (!type || type === "faq") return;
    var head = el.querySelector("h2, h3, h4");
    var label = (el.getAttribute("aria-label") || (head && head.textContent) || el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 100);
    track(MAP[type] || "cta_click", { element: type, label: label, text: label.slice(0, 60), href: href.slice(0, 200), position: positionOf(el), screen: screen.width + "x" + screen.height });
    if (CONTACT_KINDS[type]) lastContact = { kind: CONTACT_KINDS[type], label: label.slice(0, 60), position: positionOf(el), t: Date.now() };
  }, true);

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

  // ── Formlar ─────────────────────────────────────────────────────────────────────────────────────────────────
  var formsStarted = new WeakMap();
  document.addEventListener("focusin", function (e) {
    var f = e.target.closest && e.target.closest("form"); if (!f || formsStarted.get(f)) return;
    formsStarted.set(f, 1); track("form_start", { form: f.id || f.className || "" });
  }, true);
  function hidden(f, name, value) {
    var el = f.querySelector('input[name="' + name + '"]');
    if (!el) { el = document.createElement("input"); el.type = "hidden"; el.name = name; f.appendChild(el); }
    el.value = value;
  }
  document.addEventListener("submit", function (e) {
    var f = e.target; if (!f || f.tagName !== "FORM") return;
    try { hidden(f, "dt_vid", VID); hidden(f, "dt_sid", SID); hidden(f, "dt_site", SITE); } catch (err) {}  // sunucu tarafı form → kimlik merkeze iletilir
    track("form_submit", { form: f.id || f.className || "" });
  }, true);

  // ── Lead: formdan / chatbot'tan merkeze (yanıt gerekir → fetch) ───────────────────────────────────────────────
  function lead(payload, cb) {
    payload = payload || {};
    payload.site = SITE; payload.vid = VID; payload.sid = SID; payload.attr = ATTR;
    if (!payload.page) payload.page = location.href;
    if (!payload.language) payload.language = (document.documentElement.lang || "").slice(0, 10);
    if (!payload.source) payload.source = "form";
    touch();
    var p = fetch(API + "/api/t/lead/", { method: "POST", mode: "cors", credentials: "omit", keepalive: true,
                                          headers: { "Content-Type": "text/plain" }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json(); });
    if (cb) p.then(cb, function () { cb({ ok: false, error: "network" }); });
    return p;
  }

  // ── Video ───────────────────────────────────────────────────────────────────────────────────────────────────
  document.addEventListener("play", function (e) { if (e.target.tagName === "VIDEO" && !e.target.autoplay && !e.target.muted) track("video_play", {}); }, true);

  // ── Süre: sekme görünürken; çıkışta tek beacon; iletişim uygulamasından dönüş ─────────────────────────────
  var start = Date.now(), flushed = false, hiddenAt = 0, segment = 0, CONTACT_RETURN_WINDOW = 15 * 60000;
  function flush() {
    if (flushed) return; flushed = true;
    Object.keys(faqOpen).forEach(faqClose);
    Object.keys(visibleSince).forEach(function (s) { dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; });
    Object.keys(dwell).forEach(function (s) { if (dwell[s] >= 3) track("section_time", { section: s, seconds: Math.round(dwell[s]) }); });
    var secs = Math.round((Date.now() - start) / 1000);
    track("time_on_page", { seconds: secs, segment: segment });
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
    }
    if (queue.length) flushQueue();
  }
  addEventListener("pagehide", function () { hiddenAt = hiddenAt || Date.now(); flush(); });
  addEventListener("pageshow", function (e) { if (e.persisted) resume(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") { hiddenAt = Date.now(); flush(); } else resume(); });

  // SPA (Nuxt) route geçişi: eski sayfayı kapat, yenisini aç
  window.dtTrack = { track: track, pageview: function (hint) { flush(); pageview(hint); }, lead: lead, vid: VID, sid: SID };
  pageview(PAGE_HINT);
})();
