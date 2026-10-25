// sw.js — service worker do modo de treino offline (lab S4.3)
//
// Cacheia apenas recursos PÚBLICOS e estáveis: estático (HTML/CSS/JS) e o
// ranking (que já é público). Nunca cacheia /api/historico, /api/me ou
// qualquer rota que dependa de sessão — dado privado não entra no cache de
// treino offline.

const CACHE_NOME = 'treino-offline-v1';
const RECURSOS_PUBLICOS = [
    '/',
    '/index.html',
    '/script.js',
    '/styles.css',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NOME).then((cache) => cache.addAll(RECURSOS_PUBLICOS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Nunca intercepta rotas privadas — mesmo offline, elas devem falhar
    // explicitamente, não responder com dado cacheado de outra sessão.
    if (url.pathname.startsWith('/api/historico') || url.pathname === '/api/me') {
        return;
    }

    if (url.pathname === '/api/ranking' || RECURSOS_PUBLICOS.includes(url.pathname)) {
        event.respondWith(
            caches.match(event.request).then((cached) => cached || fetch(event.request))
        );
    }
});
