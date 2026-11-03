(function () {
  // Taste picker (WAI-ARIA tabs).
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".taste"));
  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on);
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      panel.hidden = !on;
      panel.classList.toggle("on", on);
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { select(t); });
    t.addEventListener("keydown", function (e) {
      var d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      if (d) { e.preventDefault(); select(tabs[(i + d + tabs.length) % tabs.length], true); }
    });
  });

  // Ratio calculator.
  var dose = document.getElementById("dose"), ratio = document.getElementById("ratio-in");
  if (dose && ratio) {
    var fmt = function (n) { return (Math.round(n * 10) / 10).toString().replace(/\.0$/, ""); };
    var update = function () {
      var d = +dose.value, r = +ratio.value;
      document.getElementById("dose-o").textContent = fmt(d) + " g";
      document.getElementById("ratio-o").textContent = "1:" + r.toFixed(1);
      document.getElementById("yield").textContent = fmt(d * r) + " g";
      document.getElementById("style").textContent = r < 1.7 ? "Ristretto" : r <= 2.4 ? "Normale" : "Lungo";
    };
    dose.addEventListener("input", update); ratio.addEventListener("input", update); update();
  }

  // On a phone, lead with the store that phone can use.
  var ua = navigator.userAgent || "";
  var isAndroid = /Android/.test(ua);
  var isIOS = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  if (isAndroid || isIOS) {
    document.querySelectorAll(".stores").forEach(function (s) {
      var mine = s.querySelector('[data-store="' + (isIOS ? "ios" : "android") + '"]');
      if (mine) s.insertBefore(mine, s.firstChild);
    });
  }

  // Header border once scrolled, and reveal-on-scroll.
  var top = document.getElementById("top");
  var onScroll = function () { top.classList.toggle("scrolled", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  // Only content that starts below the fold is hidden, so nothing stays invisible if the observer never fires.
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.remove("pre"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll(".rv").forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add("pre"); io.observe(el); }
    });
  }
})();
