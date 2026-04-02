// AurumSci Service Worker — Auto-update v1
var CACHE_NAME = 'aurumsci-aluno-v1';
var urlsToCache = [
  '/aluno',
  '/static/app_aluno_v22.html',
];

// Instala e cacheia os arquivos principais
self.addEventListener('install', function(event) {
  self.skipWaiting(); // Ativa imediatamente sem esperar fechar abas
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});

// Ativa e limpa caches antigos
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(name) {
          return name !== CACHE_NAME;
        }).map(function(name) {
          return caches.delete(name);
        })
      );
    }).then(function() {
      return self.clients.claim(); // Assume controle imediatamente
    })
  );
});

// Estratégia: Network First — sempre tenta buscar versão nova da rede
// Se falhar (offline), usa o cache
self.addEventListener('fetch', function(event) {
  // Ignora requests não-GET e APIs
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/app-aluno/')) return;
  if (event.request.url.includes('/auth/')) return;
  if (event.request.url.includes('/aluno-portal/')) return;

  event.respondWith(
    fetch(event.request).then(function(response) {
      // Salva cópia no cache
      var responseClone = response.clone();
      caches.open(CACHE_NAME).then(function(cache) {
        cache.put(event.request, responseClone);
      });
      return response;
    }).catch(function() {
      // Offline: usa cache
      return caches.match(event.request);
    })
  );
});
