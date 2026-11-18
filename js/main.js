// Scroll-spy for the sidebar nav + mobile menu toggle.
(function () {
  const sidebar = document.getElementById("sidebar");
  const toggle = sidebar.querySelector(".menu-toggle");
  const links = Array.from(document.querySelectorAll(".section-nav a"));
  const sections = links
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  // ----- Mobile menu -----
  function setOpen(open) {
    sidebar.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }
  toggle.addEventListener("click", () => setOpen(!sidebar.classList.contains("open")));
  sidebar.querySelectorAll(".sidebar-panel a").forEach((a) =>
    a.addEventListener("click", () => setOpen(false))
  );
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("open")) {
      setOpen(false);
      toggle.focus();
    }
  });

  // ----- Scroll-spy -----
  let ticking = false;
  function updateActive() {
    ticking = false;
    const marker = window.innerHeight * 0.3;
    const atBottom =
      window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;

    let current = sections[0];
    if (atBottom) {
      current = sections[sections.length - 1];
    } else {
      for (const s of sections) {
        if (s.getBoundingClientRect().top <= marker) current = s;
      }
    }
    links.forEach((a) => {
      const on = a.getAttribute("href") === "#" + current.id;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    });
  }
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(updateActive);
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  updateActive();
})();
