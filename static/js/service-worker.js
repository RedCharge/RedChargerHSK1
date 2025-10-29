const CACHE_NAME = "hsk1-quiz-cache-v1";
const urlsToCache = [
  "/",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png",
  "/static/main.css", // your CSS if any
  "/static/main.js"   // your JS if any
];

// Install event → pre-cache essential routes
self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// Activate event → clear old caches
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch event → serve cached content or fetch and update
self.addEventListener("fetch", e => {
  e.respondWith(
    caches.match(e.request).then(resp => resp || fetch(e.request))
  );
});
