const CACHE='fcne-training-v2.39-mode-context-20261021';
const APP_SHELL=['./','./index.html','./manifest.webmanifest'];

const FCNE_V239_FIXES=[["  if(wantsEasy)return pool237(currentMode237(typeof draft!=='undefined'?draft:null));","  if(wantsEasy){\n    const chosen=window.FCNE_EASY_MODE;\n    const overlayOpen=!!document.getElementById('eplanOverlay')?.classList.contains('open');\n    if(overlayOpen&&(chosen==='field'||chosen==='hall'))return pool237(chosen);\n    return pool237(currentMode237(typeof draft!=='undefined'?draft:null));\n  }"],["function inferPlanMode238(plan){\n  if(!plan)return null;","function inferPlanMode238(plan){\n  if(!plan)return null;\n  if(plan.fcneModeLocked==='field'||plan.fcneModeLocked==='hall')return plan.fcneModeLocked;\n  if(plan.fcneTrainingMode==='field'||plan.fcneTrainingMode==='hall')return plan.fcneTrainingMode;"],["        const inferred=inferPlanMode238(draft);\n        lockPlan238(draft,inferred||requested);","        lockPlan238(draft,requested);"]];
async function fcneRepairHtml239(resp){
  if(!resp || !resp.ok)return resp;
  const type=resp.headers.get('content-type')||'';
  if(!/text\/html/i.test(type))return resp;
  let html=await resp.text();
  if(html.includes('fcne-v238-mode-lock')&&FCNE_V239_FIXES.every(([oldText])=>html.includes(oldText))){
    for(const [oldText,newText] of FCNE_V239_FIXES)html=html.replace(oldText,newText);
    html=html.replaceAll('Version 2.38 · Mode-Lock Fix · Build 2026.10.21','Version 2.39 · Halle/Feld Kontextfix · Build 2026.10.21')
             .replaceAll('2.38 MODE-LOCK-FIX','2.39 MODE-CONTEXT-FIX');
  }else if(html.includes('fcne-v238-mode-lock')){
    console.warn('FCNE 2.39 context fix: source markup changed, no changes applied');
  }
  const headers=new Headers(resp.headers);
  headers.delete('content-length');headers.delete('content-encoding');headers.delete('etag');
  headers.set('content-type','text/html; charset=utf-8');
  return new Response(html,{status:resp.status,statusText:resp.statusText,headers});
}


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
        .then(async resp=>{
          const copy=resp.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy));
          return fcneRepairHtml239(resp);
        })
        .catch(async()=>fcneRepairHtml239(await caches.match('./index.html')))
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
