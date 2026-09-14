/* Keep the permanent portfolio URL fresh even when GitHub Pages sends a
   ten-minute browser cache header for index.html. */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));

self.addEventListener('fetch', event => {
    if (event.request.mode !== 'navigate') return;

    event.respondWith(
        fetch(event.request, { cache: 'reload' })
            .catch(() => fetch(event.request))
    );
});
