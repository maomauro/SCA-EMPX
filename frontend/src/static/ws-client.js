/**
 * ws-client.js — cliente WebSocket compartido SCA-EMPX
 * Uso: initWsFeed("id-del-contenedor")
 */
(function (global) {
  var WS_URL = "ws://" + location.host + "/ws/events";
  var RECONNECT_MS = 3000;

  function initWsFeed(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var statusEl = document.createElement("p");
    statusEl.style.cssText = "font-size:.75rem;color:#888;margin:0 0 .4rem";
    container.appendChild(statusEl);

    var listEl = document.createElement("ul");
    listEl.style.cssText = "list-style:none;padding:0;margin:0;max-height:280px;overflow-y:auto;";
    container.appendChild(listEl);

    function connect() {
      statusEl.textContent = "WebSocket: conectando…";
      var ws = new WebSocket(WS_URL);

      ws.onopen = function () {
        statusEl.textContent = "WebSocket: conectado ✓";
        statusEl.style.color = "#16a34a";
      };

      ws.onmessage = function (evt) {
        var msg;
        try { msg = JSON.parse(evt.data); } catch (_) { return; }
        if (msg.type === "acceso") renderAcceso(msg.data);
        if (msg.type === "registro_completado") renderRegistro(msg.data);
      };

      ws.onerror = function () {
        statusEl.style.color = "#dc2626";
        statusEl.textContent = "WebSocket: error";
      };

      ws.onclose = function () {
        statusEl.style.color = "#d97706";
        statusEl.textContent = "WebSocket: reconectando…";
        setTimeout(connect, RECONNECT_MS);
      };

      setInterval(function () {
        if (ws.readyState === WebSocket.OPEN) ws.send("ping");
      }, 20000);
    }

    function renderAcceso(d) {
      var li = document.createElement("li");
      var ts = d.fecha ? new Date(d.fecha).toLocaleTimeString() : "--";
      var badge = d.tipo_acceso === "entrada"
        ? '<span style="color:#16a34a;font-weight:700;">▲ ENTRADA</span>'
        : '<span style="color:#dc2626;font-weight:700;">▼ SALIDA</span>';
      li.style.cssText = "padding:.3rem .5rem;border-bottom:1px solid #f0f0f0;font-size:.82rem";
      li.innerHTML = badge + " <strong>" + d.nombres + "</strong>"
        + " &mdash; " + ts
        + ' <span style="color:#aaa">(sim: ' + (d.similitud || "-") + ")</span>";
      listEl.insertBefore(li, listEl.firstChild);
      while (listEl.children.length > 60) listEl.removeChild(listEl.lastChild);
    }

    function renderRegistro(d) {
      var li = document.createElement("li");
      li.style.cssText = "padding:.3rem .5rem;border-bottom:1px solid #f0f0f0;font-size:.82rem;color:#2563eb";
      li.textContent = "✔ Registro completado: " + d.nombres + " (" + d.n_embeddings + " fotos)";
      listEl.insertBefore(li, listEl.firstChild);
    }

    connect();
  }

  global.initWsFeed = initWsFeed;
})(window);
