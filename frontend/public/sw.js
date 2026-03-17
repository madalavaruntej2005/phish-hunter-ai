const CACHE_NAME = 'phish-hunter-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
];

// Install: cache the app shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch: network-first for API calls, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Bypass service worker for dev server (localhost), HMR WebSocket, and chrome-extension requests
    if (
        url.hostname === 'localhost' ||
        url.hostname === '127.0.0.1' ||
        event.request.url.includes('chrome-extension') ||
        event.request.url.includes('@vite') ||
        event.request.url.includes('__vite')
    ) {
        return;
    }

    // Network-first for API calls, with a fallback for network errors
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch((error) => {
                console.error('Service Worker API fetch failed:', error);
                return new Response(JSON.stringify({ error: 'API is offline' }), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' },
                });
            })
        );
        return;
    }

    // Cache-first for static assets
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request)
                .then((response) => {
                    // Cache successful GET responses
                    if (
                        event.request.method === 'GET' &&
                        response.status === 200 &&
                        event.request.url.startsWith('http') &&
                        !event.request.url.includes('/api/')
                    ) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match('/index.html'));
        })
    );
});