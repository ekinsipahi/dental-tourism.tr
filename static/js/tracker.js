/**
 * Birleşik tracker — tek endpoint (/api/tracking/event/) hem dönüşüm takibini
 * hem persona motorunu besler.
 *
 * Toplanan sinyaller: sayfa görüntüleme, scroll derinliği, bölüm görünürlüğü ve
 * bölümde geçirilen süre (data-track-section), tıklamalar (data-track),
 * FAQ açma, video, form başlatma/gönderme, sayfada kalma süresi.
 *
 * Kalıcılık: dt_vid (çerez + localStorage) ile aynı ziyaretçi oturumlar arasında tanınır;
 * gclid/fbclid/utm ilk ve son dokunuş olarak localStorage'da saklanır ve her olayla gönderilir.
 */
(function () {
  "use strict";
  var EVENT_API = "/api/tracking/event/";
  var PAGEVIEW_API = "/api/tracking/pageview/";
  var PAGE_URL = location.pathname;
  var PAGE_TYPE = (window.DENTAL && window.DENTAL.pageType) || document.body.dataset.pageType || "page";

  // ── Kalıcı ziyaretçi kimliği (dt_vid): çerez ↔ localStorage senkron. Çerez silinirse geri yüklenir. ──
  var VID_RE = /^[a-f0-9]{32}$/;
  function getCookie(n) { var m = document.cookie.match("(?:^|; )" + n + "=([^;]*)"); return m ? decodeURIComponent(m[1]) : ""; }
  function setCookie(n, v) { document.cookie = n + "=" + v + "; max-age=" + (400 * 86400) + "; path=/; SameSite=Lax" + (location.protocol === "https:" ? "; Secure" : ""); }
  var VID = "";
  try {
    var c = getCookie("dt_vid"), l = localStorage.getItem("dt_vid");
    VID = VID_RE.test(c) ? c : (VID_RE.test(l || "") ? l : "");
    if (VID) { if (l !== VID) localStorage.setItem("dt_vid", VID); if (c !== VID) setCookie("dt_vid", VID); }
  } catch (e) {}

  // ── Reklam atfı: ilk dokunuş (90 gün kalıcı) + son dokunuş — localStorage ──
  var ATTR_KEYS = ["gclid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  var ATTR = {};
  try {
    var params = new URLSearchParams(location.search), now = Date.now(), fresh = {};
    ATTR_KEYS.forEach(function (k) { var v = params.get(k); if (v) fresh[k] = v.slice(0, 255); });
    var first = JSON.parse(localStorage.getItem("dt_attr_first") || "null");
    if (first && now - (first._t || 0) > 90 * 86400000) first = null;
    if (Object.keys(fresh).length) {
      fresh._t = now;
      if (!first) { first = fresh; localStorage.setItem("dt_attr_first", JSON.stringify(first)); }
      localStorage.setItem("dt_attr_last", JSON.stringify(fresh));
    }
    var last = JSON.parse(localStorage.getItem("dt_attr_last") || "null") || {};
    ATTR_KEYS.forEach(function (k) {
      var v = (last && last[k]) || (first && first[k]); if (v) { ATTR[k] = v; sessionStorage.setItem("dt_" + k, v); }
    });
  } catch (e) {}

  function post(url, payload) {
    var body = JSON.stringify(payload);
    if (navigator.sendBeacon && navigator.sendBeacon(url, new Blob([body], { type: "application/json" }))) return;
    fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: body, keepalive: true, credentials: "same-origin" }).catch(function () {});
  }
  var D = window.DENTAL || {};
  var STAGE = document.documentElement.getAttribute("data-stage") || "";
  /* ── Aklındaki (persona motorunun teşhisi) — aynı cihazda localStorage "dt_mind" ile sürer ──
     Sunucu her sayfada data-mind basar; SSS açma / sertifika / önce-sonra gibi olaylardan sonra
     API yeni teşhisi döner → data-mind anında değişir, mind_nudge.html ilgili mesajı gösterir. */
  var ROOT = document.documentElement, MIND_TTL = 30 * 864e5;
  function setMind(m, fromServer) {
    if (!m || m === "unknown") return;
    var changed = ROOT.getAttribute("data-mind") !== m;
    ROOT.setAttribute("data-mind", m);
    if (window.gtag) try { gtag("set", "user_properties", { persona_mind: m }); } catch (e) {}
    try { localStorage.setItem("dt_mind", JSON.stringify({ p: m, t: Date.now() })); } catch (e) {}
    if (changed || fromServer) document.dispatchEvent(new CustomEvent("dt:mind", { detail: { mind: m, changed: changed } }));
  }
  (function initMind() {
    var server = ROOT.getAttribute("data-mind");
    if (server && server !== "unknown") { setMind(server, true); return; }
    try {
      var saved = JSON.parse(localStorage.getItem("dt_mind") || "null");
      if (saved && saved.p && Date.now() - saved.t < MIND_TTL) setMind(saved.p, true);
    } catch (e) {}
  })();
  window.dtMind = setMind;

  /* ── Google Analytics 4 — tracker'ın topladığı her olay GA4'e de gider (gtag <head>'de, Consent Mode v2) ──
     GA4 → Yönetici → Özel tanımlar'da şu parametreleri "etkinlik kapsamlı boyut" olarak kaydet:
     button_label, button_position, question, section, faq_topic, persona_mind, page_type, funnel_stage
     Anahtar etkinlik (key event) yap: phone_click, whatsapp_click, generate_lead, form_start */
  var GA_NAMES = {
    phone_click: "phone_click", whatsapp_click: "whatsapp_click", form_start: "form_start", form_submit: "generate_lead",
    cta_click: "cta_click", maps_click: "maps_click", instagram_click: "instagram_click", youtube_click: "youtube_click",
    language_switch: "language_switch", scroll_depth: "scroll_depth", faq_open: "faq_open", faq_read: "faq_read",
    section_view: "section_view", section_time: "section_time", before_after_interact: "before_after_view",
    video_play: "video_start", video_time: "video_watch", time_on_page: "page_read", chatbot_open: "chat_open"
  };
  function ga(type, data) {
    var name = GA_NAMES[type];
    if (!name || !window.gtag) return;
    var p = { page_type: PAGE_TYPE || "", funnel_stage: STAGE, persona_mind: ROOT.getAttribute("data-mind") || "" };
    if (data.label) p.button_label = String(data.label).slice(0, 100);
    if (data.position) p.button_position = data.position;
    if (data.q) p.question = String(data.q).slice(0, 100);
    if (data.mind) p.faq_topic = data.mind;
    if (data.section) p.section = data.section;
    if (data.seconds != null) p.seconds = data.seconds;
    if (data.depth != null) p.percent_scrolled = data.depth;
    if (data.href) p.link_url = String(data.href).slice(0, 100);
    if (type === "time_on_page" || type === "section_time" || type === "faq_read") p.transport_type = "beacon";
    try { gtag("event", name, p); } catch (e) {}
  }

  var MIND_EVENTS = { faq_open: 1, faq_read: 1, cert_click: 1, before_after_interact: 1, video_play: 1, youtube_click: 1 };
  function track(type, data) {
    data = data || {};
    data.persona = data.persona || D.persona || ""; data.stage = data.stage || STAGE; data.lang = data.lang || D.lang || "";
    var payload = { event_type: type, data: data, page_url: PAGE_URL, page_type: PAGE_TYPE, vid: VID, attr: ATTR };
    ga(type, data);
    if ((MIND_EVENTS[type] || data.position === "price-note") && !flushed) {  // çıkarken beacon (fetch iptal olabilir)
      // Yanıtı bekle: persona motoru yeni teşhisi döner
      fetch(EVENT_API, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
                         credentials: "same-origin" })
        .then(function (r) { return r.json(); }).then(function (j) { if (j && j.mind) setMind(j.mind); }).catch(function () {});
      return;
    }
    post(EVENT_API, payload);
  }
  // Butonun sayfadaki yeri (admin'de "nereden tıkladı")
  var POSITIONS = [[".stage-dock", "stage-dock"], [".wa-float", "wa-float"], [".mobile-menu", "mobile-menu"], [".mega", "mega-menu"],
    [".site-header", "navbar"], [".site-footer", "footer"], [".side-cta", "sidebar"], [".cta-box", "cta-box"],
    [".pseo-price", "price-note"], [".rv", "reviews"], [".page-head, .h-hero, .hero, [class*=hero]", "hero"]];
  function positionOf(el) {
    for (var i = 0; i < POSITIONS.length; i++) if (el.closest(POSITIONS[i][0])) return POSITIONS[i][1];
    var sec = el.closest("section[id], [data-track-section]");
    return sec ? (sec.id || sec.getAttribute("data-track-section")) : "content";
  }
  window.dtTrack = track;

  // tz: tarayıcı saat dilimi — IP proxy/VPN'den (Zscaler vb.) geçse bile gerçek ülkeyi verir
  var TZ = "";
  try { TZ = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  post(PAGEVIEW_API, { url: location.href, title: document.title, referrer: document.referrer, vid: VID, attr: ATTR,
                       tz: TZ, sw: screen.width, sh: screen.height });

  // Scroll derinliği
  var fired = {};
  addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight;
    var d = h > 0 ? Math.round(scrollY / h * 100) : 100;
    [25, 50, 75, 90].forEach(function (t) { if (d >= t && !fired[t]) { fired[t] = 1; track("scroll_depth", { depth: t }); } });
  }, { passive: true });

  // Bölüm görünürlüğü + bölümde geçirilen süre
  var visibleSince = {}, seen = {}, dwell = {};
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var s = e.target.dataset.trackSection;
        if (e.isIntersecting) {
          visibleSince[s] = Date.now();
          if (!seen[s]) { seen[s] = 1; track("section_view", { section: s }); }
        } else if (visibleSince[s]) {
          dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; delete visibleSince[s];
        }
      });
    }, { threshold: 0.35 });
    document.querySelectorAll("[data-track-section]").forEach(function (el) { io.observe(el); });
  }

  // Tıklamalar
  var MAP = { whatsapp: "whatsapp_click", phone: "phone_click", cta: "cta_click", maps: "maps_click",
              instagram: "instagram_click", youtube: "youtube_click", before_after: "before_after_interact",
              "lang-switch": "language_switch", treatment: "cta_click", form: "cta_click", faq: "faq_open" };
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-track], a[href^='tel:'], a[href*='wa.me/'], a[href*='api.whatsapp.com']");
    if (!el) return;
    var href = el.getAttribute("href") || "";
    var type = el.dataset.track || (href.indexOf("tel:") === 0 ? "phone" : "whatsapp");
    if (type === "faq") return;  // SSS: aşağıdaki "toggle" dinleyicisi ölçer (açtı + kaç sn okudu)
    var label = (el.getAttribute("aria-label") || el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 100);
    track(MAP[type] || "cta_click", { element: type, label: label, text: label.slice(0, 60), href: href.slice(0, 200),
                                      position: positionOf(el), screen: screen.width + "x" + screen.height });
    if ((type === "whatsapp" || type === "phone") && window.fbq) fbq("track", "Contact");  // GA4: ga() gönderir
  });

  // SSS: açtı (zayıf sinyal) + kaç saniye açık tuttu (asıl sinyal). data-mind-q = sorunun persona etiketi
  var faqOpen = {};
  function faqInfo(d) {
    var s = d.querySelector("summary") || d;
    return { q: (s.textContent || "").replace(/\s+/g, " ").trim().slice(0, 160), mind: d.getAttribute("data-mind-q") || "" };
  }
  function faqClose(q) {
    var o = faqOpen[q]; if (!o) return;
    delete faqOpen[q];
    track("faq_read", { q: q, mind: o.mind, seconds: Math.round((Date.now() - o.t) / 1000) });
  }
  document.addEventListener("toggle", function (e) {
    var d = e.target;
    if (!d || !d.matches || !d.matches("details[data-track='faq']")) return;
    var i = faqInfo(d);
    if (d.open) { if (!faqOpen[i.q]) { faqOpen[i.q] = { t: Date.now(), mind: i.mind }; track("faq_open", { q: i.q, mind: i.mind }); } }
    else faqClose(i.q);
  }, true);

  // Form başlatma
  document.querySelectorAll("form").forEach(function (f) {
    var started = false;
    f.addEventListener("focusin", function () { if (!started) { started = true; track("form_start", {}); } });
  });

  // Video
  document.querySelectorAll("video").forEach(function (v) {
    var t0 = 0;
    v.addEventListener("play", function () { t0 = Date.now(); track("video_play", {}); });
    v.addEventListener("pause", function () { if (t0) track("video_time", { seconds: Math.round((Date.now() - t0) / 1000) }); t0 = 0; });
  });

  // Çıkışta: süre + bölüm süreleri
  var start = Date.now(), flushed = false;
  function flush() {
    if (flushed) return; flushed = true;
    Object.keys(faqOpen).forEach(faqClose);
    Object.keys(visibleSince).forEach(function (s) { dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; });
    Object.keys(dwell).forEach(function (s) { if (dwell[s] >= 3) track("section_time", { section: s, seconds: Math.round(dwell[s]) }); });
    var secs = Math.round((Date.now() - start) / 1000);
    track("time_on_page", { seconds: secs });
    if (secs < 10 && !Object.keys(fired).length) track("bounce", {});
  }
  addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
})();
