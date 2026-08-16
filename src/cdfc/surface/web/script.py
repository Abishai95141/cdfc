"""The enhancement script. **It adds behaviour. It never adds a number.**

Served from `/static/app.js` under `script-src 'self'` — one same-origin file, no inline handler,
no `eval`, no CDN. The CSP has no `'unsafe-inline'`, so an injected `onclick=` cannot run even if
one reached the DOM.

## The rule this file exists under

**Every count, row, reason and fraction is already in the HTML when this runs.** Nothing here
fetches data to fill a screen, and nothing here computes a fraction. `docs/FRONTEND-SCOPE.md` §10.1
forbids a client-side settled fraction — two implementations is one more than this project can
defend — and the enforcement is structural: there is no arithmetic in this file to review.

## And the one thing it deliberately does NOT do

**It does not filter a table on the client.** The rejected-candidate list is capped and paged
server-side, so a client-side filter would search the visible page and present the result as though
it had searched all 348 — which is precisely how a truncated list gets read as a complete one. The
filters are ordinary form GETs. The script only submits them sooner.

What it does add: drag-and-drop with real upload progress, copy-to-clipboard on digests, a hover
readout on the history chart, `aria-expanded` wiring on disclosures, `/` to focus a filter, and a
busy state on submit so a 27-second request does not look like a dead page.
"""

from __future__ import annotations


def app_script() -> str:
    return r"""
'use strict';
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- 1. The drop screen: drag-and-drop and REAL upload progress ------------------
     The form posts multipart to /v1/filings and works with scripting off. With it on,
     the same request goes through XHR so the reader gets bytes-sent rather than a
     stalled tab -- and every failure path renders the server's own `detail`, because
     the backend's messages carry the argument and a paraphrase would not. */
  var form = $('form.drop-form');
  if (form) {
    var input = $('#filing', form);
    var target = $('.drop-target', form);
    var out = $('#drop-result');
    var bar = $('#drop-progress');

    ['dragenter', 'dragover'].forEach(function (e) {
      target.addEventListener(e, function (ev) {
        ev.preventDefault(); target.setAttribute('data-drag', 'true');
      });
    });
    ['dragleave', 'drop'].forEach(function (e) {
      target.addEventListener(e, function () { target.removeAttribute('data-drag'); });
    });
    target.addEventListener('drop', function (ev) {
      ev.preventDefault();
      if (ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files.length) {
        input.files = ev.dataTransfer.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    input.addEventListener('change', function () {
      var f = input.files && input.files[0];
      var name = $('.drop-chosen', form);
      if (name) { name.textContent = f ? (f.name + ' · ' + fmtBytes(f.size)) : ''; }
      if (out) { out.innerHTML = ''; }
    });

    form.addEventListener('submit', function (ev) {
      var f = input.files && input.files[0];
      if (!f) { return; }
      ev.preventDefault();
      form.setAttribute('data-busy', 'true');
      if (bar) { bar.value = 0; bar.hidden = false; }
      var xhr = new XMLHttpRequest();
      xhr.open('POST', form.getAttribute('action'), true);
      xhr.upload.onprogress = function (e) {
        if (bar && e.lengthComputable) { bar.max = e.total; bar.value = e.loaded; }
      };
      xhr.onload = function () {
        form.removeAttribute('data-busy');
        if (bar) { bar.hidden = true; }
        var body = {};
        try { body = JSON.parse(xhr.responseText); } catch (_e) { body = {}; }
        if (xhr.status === 201 && body.runId) { window.location = '/runs/' + body.runId; return; }
        renderRefusal(out, xhr.status, body, f);
      };
      xhr.onerror = function () {
        form.removeAttribute('data-busy');
        if (bar) { bar.hidden = true; }
        renderRefusal(out, 0, { error: 'network', detail: 'the request did not reach the server' }, f);
      };
      var fd = new FormData();
      fd.append('filing', f, f.name);
      xhr.send(fd);
    });
  }

  function fmtBytes(n) {
    if (n < 1024) { return n + ' bytes'; }
    if (n < 1048576) { return (n / 1024).toFixed(1) + ' KB'; }
    return (n / 1048576).toFixed(1) + ' MB';
  }

  /* The four refusal states from FRONTEND-SCOPE 2. Each renders the server's `detail`
     verbatim, and 422 renders the structural fingerprint as a COPYABLE field -- a 422
     that only says "unknown template" leaves an operator with nothing to act on. */
  function renderRefusal(node, status, body, file) {
    if (!node) { return; }
    var title = ({
      413: 'That file is over the 25 MB cap',
      415: 'That file is not an .xlsx',
      422: 'This template has not been admitted',
      401: 'That path needs an operator token',
      503: 'The server refused rather than guessing'
    })[status] || ('The server refused (' + (status || 'no response') + ')');
    var html = '<div class="err" role="alert"><p class="err-title">' + esc(title) + '</p>';
    html += '<p class="err-detail">' + esc(body.detail || body.error || 'no detail was returned') + '</p>';
    if (status === 413 && file) {
      html += '<p class="err-remedy">this file is <span class="figure">' + esc(fmtBytes(file.size)) + '</span></p>';
    }
    if (body.structuralFingerprint) {
      html += '<p class="err-remedy"><span class="meta">structural fingerprint</span> ' +
              '<code data-copy="' + esc(body.structuralFingerprint) + '">' +
              esc(body.structuralFingerprint) + '</code> ' +
              '<button type="button" class="btn btn-quiet" data-copy-btn>copy</button></p>' +
              '<p class="err-remedy"><a class="btn btn-quiet" href="/templates">begin admission</a></p>';
    }
    node.innerHTML = html + '</div>';
    wireCopy(node);
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  /* ---- 2. Copy buttons on digests -------------------------------------------------
     A 64-character sha256 that has to be transcribed by hand is a digest nobody checks. */
  function wireCopy(root) {
    $$('[data-copy-btn]', root).forEach(function (b) {
      if (b.__wired) { return; }
      b.__wired = true;
      b.addEventListener('click', function () {
        var src = b.previousElementSibling;
        var text = (src && (src.getAttribute('data-copy') || src.textContent)) || '';
        var done = function () { b.textContent = 'copied'; setTimeout(function () { b.textContent = 'copy'; }, 1400); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { b.textContent = 'could not copy'; });
        } else { b.textContent = 'could not copy'; }
      });
    });
  }
  wireCopy(document);

  /* ---- 3. Filters submit sooner, and NEVER filter on the client -------------------
     The list is capped and paged server-side. A client-side filter would search the
     visible page and look like it had searched all of them. */
  $$('form.filters').forEach(function (f) {
    $$('select', f).forEach(function (sel) {
      sel.addEventListener('change', function () { f.submit(); });
    });
    var q = $('input[type=search]', f);
    if (q) {
      var t = null;
      q.addEventListener('input', function () {
        clearTimeout(t);
        t = setTimeout(function () { f.submit(); }, 420);
      });
    }
  });

  /* ---- 4. Busy state on any navigation that can take seconds ---------------------- */
  $$('form:not(.drop-form)').forEach(function (f) {
    f.addEventListener('submit', function () { f.setAttribute('data-busy', 'true'); });
  });

  /* ---- 5. The history chart's hover readout ---------------------------------------
     Reads attributes already on the element. It computes nothing: the counts were
     rendered server-side and this only moves them into a wider line of text. */
  var readout = $('#chart-readout');
  if (readout) {
    $$('.chart .dot').forEach(function (d) {
      var show = function () {
        var cause = d.getAttribute('data-cause');
        readout.innerHTML = '<strong>' + esc(d.getAttribute('data-at')) + '</strong> · ' +
          '<span class="figure">' + esc(d.getAttribute('data-settled')) + '</span> of ' +
          '<span class="figure">' + esc(d.getAttribute('data-surface')) + '</span> cells settled' +
          (cause ? ' <br><span class="meta">why it fell</span> ' + esc(cause) : '');
      };
      d.addEventListener('mouseenter', show);
      d.addEventListener('focus', show);
      d.setAttribute('tabindex', '0');
    });
  }

  /* ---- 6. Keyboard: `/` focuses the first filter on the screen -------------------- */
  document.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) { return; }
    var tag = (document.activeElement && document.activeElement.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') { return; }
    var first = $('form.filters input[type=search]') || $('form.filters select');
    if (first) { e.preventDefault(); first.focus(); }
  });

  /* ---- 7. Disclosures report their state to assistive technology ------------------ */
  $$('details.disclose').forEach(function (d) {
    var s = $('summary', d);
    if (!s) { return; }
    var sync = function () { s.setAttribute('aria-expanded', d.open ? 'true' : 'false'); };
    sync();
    d.addEventListener('toggle', sync);
  });
})();
"""
