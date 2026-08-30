const CACHE_NAME = "site-cache-20260830231711";
const ASSETS = [
  '/',
  '/index.html',
  '/styles.css?v=20260830231711'
];
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(k => { if (k !== CACHE_NAME) return caches.delete(k); })
    ))
  );
  self.clients.claim();
});
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.mode === 'navigate' || req.destination === 'document' || url.pathname.endsWith('/index.html')) {
    event.respondWith(fetch(req).then(res => { caches.open(CACHE_NAME).then(c=>c.put(req, res.clone())); return res; }).catch(()=>caches.match('/index.html')));
    return;
  }
  if (req.destination === 'style' || url.pathname.endsWith('/styles.css') || url.search.includes('styles.css')) {
    event.respondWith(fetch(req).then(res => { caches.open(CACHE_NAME).then(c=>c.put(req, res.clone())); return res; }).catch(()=>caches.match('/styles.css?v=20260830231711')));
    return;
  }
  event.respondWith(caches.match(req).then(cached => cached || fetch(req).then(res => { caches.open(CACHE_NAME).then(c=>c.put(req, res.clone())); return res; })));
});
