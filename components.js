(function() {
  function initNav() {
    // Follow Us dropdown
    var btn = document.querySelector('.nav-follow-btn');
    var dd  = document.querySelector('.nav-dropdown');
    if (btn && dd) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var open = dd.style.display === 'flex';
        dd.style.display = open ? 'none' : 'flex';
      });
      document.addEventListener('click', function() {
        if (dd) dd.style.display = 'none';
      });
    }

    // Hamburger menu
    var ham    = document.getElementById('navHamburger');
    var drawer = document.getElementById('navDrawer');
    if (ham && drawer) {
      ham.addEventListener('click', function(e) {
        e.stopPropagation();
        var open = drawer.classList.contains('open');
        drawer.classList.toggle('open', !open);
        ham.classList.toggle('open', !open);
      });
      drawer.querySelectorAll('a').forEach(function(a) {
        a.addEventListener('click', function() {
          drawer.classList.remove('open');
          ham.classList.remove('open');
        });
      });
      document.addEventListener('click', function() {
        drawer.classList.remove('open');
        ham.classList.remove('open');
      });
    }
  }

  function loadPartial(id, url, callback) {
    var el = document.getElementById(id);
    if (!el) { if (callback) callback(); return; }
    fetch(url)
      .then(function(r) { return r.text(); })
      .then(function(html) {
        el.outerHTML = html;
        if (callback) callback();
      })
      .catch(function() {
        if (callback) callback();
      });
  }

  // Load nav first, then footer, then init nav JS
  loadPartial('site-nav', '/nav.html', function() {
    loadPartial('site-footer', '/footer.html', function() {
      initNav();
    });
  });
})();
