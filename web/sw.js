/* Offline support: app shell cache-first, data network-first (falls back to cache offline). */
const VERSION = "foodmap-v2";
const SHELL = [
  "./", "index.html", "style.css", "app.js", "manifest.webmanifest", "icon-192.png", "icon-512.png",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  const isData = sameOrigin && url.pathname.includes("/data/");
  const isShell = sameOrigin || url.hostname === "cdnjs.cloudflare.com";
  if (!isShell) return; // tiles, counters, geocoding: straight to network

  if (isData || req.mode === "navigate" || /\.(js|css|webmanifest)$/.test(url.pathname)) {
    // network-first so redeploys show up immediately; cache is the offline fallback
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
          return res;
        })
        .catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match("index.html"))),
    );
    return;
  }
  e.respondWith(caches.match(req).then((r) => r || fetch(req)));
});
