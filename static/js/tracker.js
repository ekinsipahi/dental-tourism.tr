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
  function track(type, data) {
    post(EVENT_API, { event_type: type, data: data || {}, page_url: PAGE_URL, page_type: PAGE_TYPE, vid: VID, attr: ATTR });
  }
  window.dtTrack = track;

  post(PAGEVIEW_API, { url: location.href, title: document.title, referrer: document.referrer, vid: VID, attr: ATTR });

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
    var el = e.target.closest("[data-track]");
    if (!el) return;
    var type = el.dataset.track;
    if (type === "faq") { if (!el.open) track("faq_open", { q: (el.textContent || "").trim().slice(0, 80) }); return; }
    track(MAP[type] || "cta_click", { element: type, text: (el.textContent || "").trim().slice(0, 60), href: el.href || "" });
    if (type === "whatsapp") {
      if (window.gtag) gtag("event", "whatsapp_click");
      if (window.fbq) fbq("track", "Contact");
    }
  });

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
    Object.keys(visibleSince).forEach(function (s) { dwell[s] = (dwell[s] || 0) + (Date.now() - visibleSince[s]) / 1000; });
    Object.keys(dwell).forEach(function (s) { if (dwell[s] >= 3) track("section_time", { section: s, seconds: Math.round(dwell[s]) }); });
    var secs = Math.round((Date.now() - start) / 1000);
    track("time_on_page", { seconds: secs });
    if (secs < 10 && !Object.keys(fired).length) track("bounce", {});
  }
  addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
})();
