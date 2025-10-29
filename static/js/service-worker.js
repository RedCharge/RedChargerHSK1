// Simple service worker to make your app installable
self.addEventListener('install', e => {
  e.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', e => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
  // Optionally cache offline content here
});
