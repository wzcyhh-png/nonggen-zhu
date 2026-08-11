const CACHE_NAME = 'site-cache-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/styles.css'
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});
self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate' || (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html'))) {
    event.respondWith(fetch(event.request).then(r => { caches.open(CACHE_NAME).then(c=>c.put(event.request, r.clone())); return r; }).catch(()=>caches.match('/index.html')));
    return;
  }
  event.respondWith(caches.match(event.request).then(res => res || fetch(event.request).then(fetchRes=>{ caches.open(CACHE_NAME).then(c=>c.put(event.request, fetchRes.clone())); return fetchRes;})));
});
