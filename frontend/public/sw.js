// SlopeGuard Service Worker — Offline-First Cache Strategy
const CACHE_NAME = "slopeguard-v1";
const STATIC_CACHE = "slopeguard-static-v1";
const API_CACHE = "slopeguard-api-v1";

// Assets to cache on install (app shell)
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/favicon.svg",
  "/icons.svg",
  "/assets/react.svg",
  "/assets/vite.svg",
  "/assets/hero.png",
];

// API endpoints that should be cached (short TTL for rainfall, longer for zones)
const CACHEABLE_APIS = [
  "/zones",
  "/simulate",
];

// Network-first endpoints (always try network first)
const NETWORK_FIRST = [
  "/ws/telemetry",
  "/reports",
];

// Install: cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== STATIC_CACHE && key !== CACHE_NAME && key !== API_CACHE).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: routing strategy based on URL
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // 1. Static assets → Cache First
  if (STATIC_ASSETS.includes(url.pathname) || url.pathname.startsWith("/assets/")) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // 2. API: zones / simulate → Stale-While-Revalidate (short-lived cache)
  if (CACHEABLE_APIS.some((p) => url.pathname.startsWith(p))) {
    event.respondWith(staleWhileRevalidate(request, API_CACHE, 5 * 60 * 1000)); // 5 min TTL
    return;
  }

  // 3. WebSocket, reports, everything else → Network First
  event.respondWith(networkFirst(request));
});

// --- Strategy Helpers ---

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (err) {
    // Fallback: return a generic offline response for HTML
    if (request.mode === "navigate") {
      return caches.match("/index.html");
    }
    throw err;
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    throw err;
  }
}

async function staleWhileRevalidate(request, cacheName, ttlMs) {
  const cache = await caches.open(cacheName);
  const cached = await caches.match(request);

  const networkPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  });

  if (cached) {
    const cacheTime = cached.headers.get("sw-cache-time");
    const age = cacheTime ? Date.now() - parseInt(cacheTime, 10) : 0;
    if (age < ttlMs) {
      // Return stale immediately, update in background
      networkPromise.catch(() => {}); // ignore background update failures
      return cached;
    }
  }

  // Either no cache or expired — wait for network
  try {
    const networkResponse = await networkPromise;
    const headers = new Headers(networkResponse.headers);
    headers.set("sw-cache-time", String(Date.now()));
    const fresh = new Response(networkResponse.body, {
      status: networkResponse.status,
      statusText: networkResponse.statusText,
      headers,
    });
    return fresh;
  } catch (err) {
    if (cached) return cached;
    throw err;
  }
}

// Background sync for field reports when offline
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-field-reports") {
    event.waitUntil(syncFieldReports());
  }
});

async function syncFieldReports() {
  // This would read from IndexedDB and retry failed /reports POSTs
  // Implemented as a placeholder for Phase 5
  console.log("[SlopeGuard SW] Background sync: field reports");
}

// Push notifications for CRITICAL alerts
self.addEventListener("push", (event) => {
  if (!event.data) return;
  const data = event.data.json();
  const options = {
    body: data.body || "SlopeGuard alert",
    icon: "/icons.svg",
    badge: "/favicon.svg",
    tag: "slopeguard-alert",
    requireInteraction: data.requireInteraction || false,
    data: data.url || "/",
  };
  event.waitUntil(self.registration.showNotification(data.title || "SlopeGuard Alert", options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data || "/")
  );
});
