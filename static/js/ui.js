/* Site geneli etkileşim + animasyonlar — bağımlılık yok, "hareketi azalt" tercihine saygılı. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var doc = document.documentElement;
  doc.classList.add("js");

  /* ── 1. Scroll reveal: şablonda .reveal olanlar + otomatik seçilen bloklar ── */
  var AUTO = ".section h2, .section .card, .section .review, .chip, .pseo-gallery img, .pseo-hero-photo, " +
             ".h-stat, .faq details, .prose > h2, .prose > ul, .cta-box, .pseo-links";
  Array.prototype.forEach.call(document.querySelectorAll(AUTO), function (el) {
    if (!el.closest(".reveal") && !el.closest(".rv-track")) el.classList.add("reveal");
  });
  var revealEls = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(revealEls, function (el) { el.classList.add("in"); });
  } else {
    // Aynı kapsayıcıdaki kardeşlere kademeli gecikme
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target, d = el.getAttribute("data-delay");
        if (d === null && el.parentElement) {
          var sibs = Array.prototype.filter.call(el.parentElement.children, function (c) { return c.classList.contains("reveal"); });
          d = Math.min(sibs.indexOf(el), 6) * 70;
        }
        el.style.transitionDelay = (d || 0) + "ms";
        el.classList.add("in");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    Array.prototype.forEach.call(revealEls, function (el) { io.observe(el); });
  }

  /* ── 2. Sayaç: [data-count] ── */
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    if (isNaN(target)) return;
    var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var fmt = function (v) { return v.toLocaleString(document.documentElement.lang || undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec }); };
    if (reduce) { el.textContent = fmt(target); return; }
    var start = null, dur = 1400;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.5 });
    Array.prototype.forEach.call(counters, function (el) { cio.observe(el); });
  }

  /* ── 3. Yorum slider'ı: .rv ── */
  Array.prototype.forEach.call(document.querySelectorAll(".rv"), function (rv) {
    var track = rv.querySelector(".rv-track");
    if (!track) return;
    var cards = track.children;
    if (cards.length < 2) { rv.classList.add("rv-static"); return; }
    function stepSize() { return cards[0].getBoundingClientRect().width + 16; }
    function go(dir) {
      var max = track.scrollWidth - track.clientWidth - 4;
      var rtl = getComputedStyle(track).direction === "rtl";
      var left = Math.abs(track.scrollLeft);
      if (dir > 0 && left >= max) { track.scrollTo({ left: 0, behavior: reduce ? "auto" : "smooth" }); return; }
      track.scrollBy({ left: (rtl ? -1 : 1) * dir * stepSize(), behavior: reduce ? "auto" : "smooth" });
    }
    Array.prototype.forEach.call(rv.querySelectorAll("[data-rv]"), function (b) {
      b.addEventListener("click", function () { go(b.getAttribute("data-rv") === "next" ? 1 : -1); restart(); });
    });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") go(1); else if (e.key === "ArrowLeft") go(-1);
    });
    // Fare ile sürükleme (dokunmatikte doğal kaydırma zaten var)
    var down = false, sx = 0, sl = 0;
    track.addEventListener("mousedown", function (e) { down = true; sx = e.pageX; sl = track.scrollLeft; track.classList.add("drag"); });
    window.addEventListener("mouseup", function () { down = false; track.classList.remove("drag"); });
    track.addEventListener("mousemove", function (e) { if (down) { e.preventDefault(); track.scrollLeft = sl - (e.pageX - sx); } });
    // Otomatik oynatma — üzerine gelince / odakta durur
    var timer = null;
    function restart() { if (reduce) return; clearInterval(timer); timer = setInterval(function () { go(1); }, 5500); }
    ["mouseenter", "focusin", "touchstart"].forEach(function (ev) { rv.addEventListener(ev, function () { clearInterval(timer); }, { passive: true }); });
    rv.addEventListener("mouseleave", restart);
    restart();
  });

  /* ── 4. Yıldızlı puan: [data-star-input] ── */
  Array.prototype.forEach.call(document.querySelectorAll("[data-star-input]"), function (fs) {
    var labels = (fs.getAttribute("data-labels") || "").split("|");
    var out = fs.querySelector(".star-text");
    function show(v) { if (out && v) out.textContent = v + "/5 · " + (labels[v - 1] || ""); }
    Array.prototype.forEach.call(fs.querySelectorAll("input[type=radio]"), function (r) {
      r.addEventListener("change", function () { show(parseInt(r.value, 10)); fs.classList.remove("pop"); void fs.offsetWidth; fs.classList.add("pop"); });
      if (r.checked) show(parseInt(r.value, 10));
    });
    Array.prototype.forEach.call(fs.querySelectorAll("label"), function (l) {
      var input = document.getElementById(l.getAttribute("for"));
      l.addEventListener("mouseenter", function () { if (input) show(parseInt(input.value, 10)); });
    });
    fs.addEventListener("mouseleave", function () {
      var c = fs.querySelector("input:checked"); if (c) show(parseInt(c.value, 10));
    });
  });

  /* ── 5. Hafif 3D eğim: .tilt ── */
  if (!reduce && window.matchMedia("(hover: hover)").matches) {
    Array.prototype.forEach.call(document.querySelectorAll(".tilt, .pseo-hero-photo, .card-img"), function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = "perspective(800px) rotateY(" + (x * 6) + "deg) rotateX(" + (-y * 6) + "deg) scale(1.01)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }

  /* ── 6. Header: kaydırınca gölge ── */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  /* ── 7. Dil menüsü / mega menü: dışarı tıklayınca kapan, Esc ile kapan ── */
  document.addEventListener("click", function (e) {
    Array.prototype.forEach.call(document.querySelectorAll("details.lang[open]"), function (d) { if (!d.contains(e.target)) d.removeAttribute("open"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      Array.prototype.forEach.call(document.querySelectorAll("details.lang[open]"), function (d) { d.removeAttribute("open"); });
      if (document.activeElement && document.activeElement.closest(".has-mega")) document.activeElement.blur();
    }
  });
})();
