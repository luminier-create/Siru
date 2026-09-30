/* 시루 SIRU 서비스 워커 — build.py 가 버전과 목록을 채운다 */
const VERSION = '62bd96ed57';
const CORE = ["/", "/manifest.webmanifest", "/assets/fonts/pretendard/pretendard.css", "/assets/img/ecd25d9aeab4.png", "/icons/icon-192.png"];
const ASSETS = ["/assets/img/05aaba5b451a.png", "/assets/img/08ddc442e2a2.png", "/assets/img/0a56ca2be286.png", "/assets/img/0a5911023900.png", "/assets/img/0af200a51f90.png", "/assets/img/0d6770be470b.png", "/assets/img/0ee00a0816df.png", "/assets/img/10dd7a9d1c07.png", "/assets/img/1100a5f4fbb6.png", "/assets/img/1ab002db57f9.png", "/assets/img/1ffdafaf5d19.png", "/assets/img/23bfdec3359f.png", "/assets/img/23c2cb4a7b50.png", "/assets/img/24301ea90e47.png", "/assets/img/2edc1b79a2b0.png", "/assets/img/2fe87a1d2a92.png", "/assets/img/31f58fb0afa1.png", "/assets/img/358fe5f22de7.png", "/assets/img/37993c3f9481.png", "/assets/img/3c7c9a140968.png", "/assets/img/4f87beebe613.png", "/assets/img/5d1bb9aa0a81.png", "/assets/img/5e710fbd3e5a.png", "/assets/img/6147cba59303.png", "/assets/img/67509e9814e3.png", "/assets/img/6977ecb3b97e.png", "/assets/img/707237eb620c.png", "/assets/img/7cd8217f6750.png", "/assets/img/8374e1eef62a.png", "/assets/img/879d812b6580.png", "/assets/img/883e45b65f65.png", "/assets/img/90be063661e6.png", "/assets/img/92e4a5949555.png", "/assets/img/a1929e14b68e.png", "/assets/img/a9cc4ec8519b.png", "/assets/img/b1b6b3450932.png", "/assets/img/b3508a3ddf78.png", "/assets/img/b6730924798e.png", "/assets/img/b966e1092568.png", "/assets/img/bf97c1c6e5e9.png", "/assets/img/c5a4c1a0412a.png", "/assets/img/c61ec641b0c5.png", "/assets/img/c7d57eede443.png", "/assets/img/cbc5f282d20d.png", "/assets/img/d0342d767727.png", "/assets/img/d5fc8f1d2798.png", "/assets/img/d89bbcd772d5.png", "/assets/img/dd9945dbcaff.png", "/assets/img/e395de7f6e68.png", "/assets/img/eaf532e50a63.png", "/assets/img/ecd25d9aeab4.png", "/assets/img/f14da82036e9.png", "/assets/img/f74344f9c225.png", "/assets/img/fab360bacf5f.png", "/assets/img/fb13457f9f44.png", "/assets/img/fcbbeb562bd3.png"];
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
