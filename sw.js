/* 構造エッジ・ダッシュボード service worker
 * 方針: アプリシェルはキャッシュ優先、data/*.json はネットワーク優先
 * （オフライン時は最後に取得できたデータを表示する）。
 * index.html を更新したら CACHE のバージョンを必ず上げること。
 */
const CACHE = "edge-dashboard-v1.0.0";
const SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./data/watchlist.json",
  "./data/prices.json",
  "./icon-180.png",
  "./icon-192.png",
  "./icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;

  // データはネットワーク優先（成功したらキャッシュ更新、失敗したらキャッシュ）
  if (url.pathname.includes("/data/")) {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // アプリシェルはキャッシュ優先
  e.respondWith(
    caches.match(e.request).then((hit) => hit || fetch(e.request))
  );
});
