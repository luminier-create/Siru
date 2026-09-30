/* 시루 SIRU 서비스 워커 — build.py 가 버전과 목록을 채운다 */
const VERSION = '__VERSION__';
const CORE = __CORE__;
const ASSETS = __ASSETS__;
const CORE_CACHE = 'siru-core-' + VERSION;
const RT_CACHE = 'siru-rt';

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CORE_CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k.startsWith('siru-core-') && k !== CORE_CACHE).map((k) => caches.delete(k)));
    // 새 버전에서 더 이상 쓰지 않는 그림은 정리
    const rt = await caches.open(RT_CACHE);
    const keep = new Set(ASSETS);
    for (const req of await rt.keys()) {
      const p = new URL(req.url).pathname;
      if (p.startsWith('/assets/img/') && !keep.has(p)) await rt.delete(req);
    }
    if (self.registration.navigationPreload) await self.registration.navigationPreload.enable();
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 페이지: 네트워크 우선, 오프라인이면 저장본
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const res = (await event.preloadResponse) || (await fetch(req));
        const copy = res.clone();
        caches.open(CORE_CACHE).then((c) => c.put('/', copy));
        return res;
      } catch (e) {
        return (await caches.match('/')) || Response.error();
      }
    })());
    return;
  }

  // 그림·폰트·아이콘: 캐시 우선 (내용 해시 이름이라 바뀌지 않음)
  if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/icons/')) {
    event.respondWith((async () => {
      const hit = await caches.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) {
        const copy = res.clone();
        caches.open(RT_CACHE).then((c) => c.put(req, copy));
      }
      return res;
    })());
  }
});
