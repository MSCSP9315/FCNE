const CACHE='fcne-training-v2.34-halle-feld-20261030';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./fcne-modefix-v234.js','./fcne-swap-ui-v234.js','./fcne-hall-game-v234.js','./fcne-swap-lock-v234.js'];

self.addEventListener('install',e=>{
  e.waitUntil(
    caches.open(CACHE)
      .then(c=>Promise.all(APP_SHELL.map(url=>fetch(url,{cache:'no-store'}).then(r=>{
        if(!r.ok) throw new Error('HTTP '+r.status+' '+url);
        return c.put(url,r);
      }))))
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate',e=>{
  e.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(k=>k.startsWith('fcne-training-')&&k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);

  if(e.request.mode==='navigate'){
    e.respondWith(
      fetch(e.request,{cache:'no-store'})
        .then(resp=>{
          const copy=resp.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy));
          return resp;
        })
        .catch(()=>caches.match('./index.html'))
    );
    return;
  }

  if(u.origin===self.location.origin){
    e.respondWith(
      fetch(e.request,{cache:'no-store'})
        .then(resp=>{
          const copy=resp.clone();
          caches.open(CACHE).then(c=>c.put(e.request,copy));
          return resp;
        })
        .catch(()=>caches.match(e.request))
    );
  }
});
