from pathlib import Path
import re, json

idx=Path("index.html")
swp=Path("sw.js")
html=idx.read_text(encoding="utf-8")

# Remove previous v2.44 patch on reruns.
html=re.sub(r'<style id="fcne-v244-ui">.*?</style>\s*<script id="fcne-v244-ui">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

patch=r'''
<style id="fcne-v244-ui">
/* v2.44: MH branch gets the same visual weight as SFV / Easy2Coach */
#fcneMhBranchCard.fcne-branch-mh{
  background:linear-gradient(145deg,#5b21b6 0%,#7c3aed 55%,#9333ea 100%)!important;
  border:0!important;
  box-shadow:0 14px 30px rgba(91,33,182,.22)!important;
  color:#fff!important;
}
#fcneMhBranchCard.fcne-branch-mh *{color:#fff!important}
#fcneMhBranchCard.fcne-branch-mh small{color:rgba(255,255,255,.88)!important}
#fcneMhBranchCard.fcne-branch-mh .ep-icon{
  background:rgba(255,255,255,.16)!important;
  border:1px solid rgba(255,255,255,.22)!important;
  color:#fff!important;
  box-shadow:none!important;
}
#fcneMhBranchCard.fcne-branch-mh .fcne-branch-label{
  color:rgba(255,255,255,.82)!important;
}
.fcne-mh-unit-card{
  cursor:pointer!important;
  transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease;
}
.fcne-mh-unit-card:active{transform:scale(.985)}
.fcne-mh-unit-card:focus-visible{outline:3px solid #8b5cf6;outline-offset:2px}
.mh-img-fallback{
  min-height:145px;display:grid;place-items:center;text-align:center;padding:18px;
  background:#f5f2f9;color:#665b70;font-size:12px;font-weight:800;
}
.mh-img-fallback a{
  display:inline-block;margin-top:9px;padding:8px 11px;border-radius:10px;
  background:#6d28d9;color:#fff!important;text-decoration:none;
}
</style>
<script id="fcne-v244-ui">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.44 MH-UI-FIX';

const esc244=v=>typeof escapeHtml==='function'?escapeHtml(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

/* Replace only the MH complete-training list renderer.
   Cards use a real data id + direct event handler, so taps on iOS cannot get lost. */
window.fcneRenderMHUnits=async function(){
  const d=await window.fcneLoadMH();
  const q=(document.getElementById('mhUnitSearch')?.value||'').trim().toLowerCase();
  const th=document.getElementById('mhUnitTheme')?.value||'Alle Schwerpunkte';
  const rows=d.units.filter(u=>(th==='Alle Schwerpunkte'||u.theme===th)&&(!q||[u.title,u.theme,u.intro].join(' ').toLowerCase().includes(q)));
  const count=document.getElementById('mhUnitCount'), list=document.getElementById('mhUnitList');
  if(count)count.textContent=rows.length+' Trainingseinheiten gefunden';
  if(!list)return;
  list.innerHTML=rows.map(u=>'<button type="button" class="fcne-mh-unit-card" data-mh-unit="'+esc244(u.id)+'"><span class="num">'+String(Number(u.id.slice(2))).padStart(2,'0')+'</span><span class="copy"><b>'+esc244(u.title)+'</b><small>'+esc244(u.theme)+' · '+u.exercise_count+' Originalübungen</small></span><span class="go">›</span></button>').join('');
  list.querySelectorAll('.fcne-mh-unit-card').forEach(btn=>{
    btn.addEventListener('click',ev=>{
      ev.preventDefault();ev.stopPropagation();
      const id=btn.dataset.mhUnit;
      if(id)window.fcneOpenMHUnit(id);
    });
  });
};

/* Robust MH unit opener independent of the previous closure.
   Every exercise gets either its original image or a clear source fallback. */
window.fcneOpenMHUnit=async function(id){
  try{
    const d=await window.fcneLoadMH();
    const u=d.units.find(x=>x.id===id);
    if(!u)throw new Error('Trainingseinheit nicht gefunden');
    const xs=DATA.filter(e=>e.fcneBranch==='mh'&&e.mhUnitId===id).sort((a,b)=>(a.mhOrder||0)-(b.mhOrder||0));
    const hasClosing=xs.some(e=>e.category==='Ausklang'||/abschlussspiel/i.test(e.title||''));
    const shown=hasClosing?xs:[...xs,d.closing];

    let n=document.getElementById('mhUnitOverlay');
    if(!n){n=document.createElement('section');n.id='mhUnitOverlay';n.className='exercise-detail';document.body.appendChild(n)}

    const cards=shown.map((e,k)=>{
      const src=esc244(e.source_url||u.url||'https://fussballtraining.li/');
      const media=e.image
        ? '<img src="'+esc244(e.image)+'" alt="'+esc244(e.title)+'" onclick="if(window.openZoom)openZoom(this.src)" onerror="this.outerHTML=\'<div class=&quot;mh-img-fallback&quot;>Originalbild konnte nicht geladen werden.<br><a href=&quot;'+src+'&quot; target=&quot;_blank&quot; rel=&quot;noopener&quot;>Originalquelle öffnen</a></div>\'">'
        : '<div class="mh-img-fallback">Für diese Übung ist kein Bild hinterlegt.<br><a href="'+src+'" target="_blank" rel="noopener">Originalquelle öffnen</a></div>';
      return '<div class="mh-unit-ex">'+media+'<div class="mh-unit-ex-copy"><span class="stage">'+(k+1)+' · '+esc244(e.mhStage||e.category)+'</span><h3>'+esc244(e.title)+'</h3><p>'+esc244(e.players||'Spielerzahl variabel')+' · '+esc244(e.category||'')+'</p><button type="button" class="mh-open-ex" data-mh-ex="'+esc244(e.id)+'">Übung im Detail öffnen</button></div></div>';
    }).join('');

    n.innerHTML='<div class="detail-header"><button type="button" class="round-back" id="mhUnitBack">‹</button><div class="detail-title"><strong>'+esc244(u.title)+'</strong><small>MH · '+esc244(u.theme)+' · komplette Einheit</small></div></div><div class="detail-content"><div class="mh-unit-intro">'+esc244(u.intro||'Komplette Trainingseinheit aus dem Gratisbuch Fußballtraining.')+'</div><div class="fcne-mh-note"><b>Originalaufbau:</b> Die Übungen sind in der Reihenfolge der Quelle dargestellt.</div><div class="mh-unit-exercises">'+cards+'</div><a class="mh-source-link" href="'+esc244(u.url)+'" target="_blank" rel="noopener">↗ Originaleinheit auf fussballtraining.li öffnen</a></div>';

    n.querySelector('#mhUnitBack')?.addEventListener('click',()=>window.fcneCloseMHUnit?.());
    n.querySelectorAll('[data-mh-ex]').forEach(btn=>btn.addEventListener('click',()=>{
      const e=DATA.find(x=>x.id===btn.dataset.mhEx);
      if(e){window.fcneCloseMHUnit?.();window.openExercise?.(DATA.indexOf(e))}
    }));
    n.classList.add('open');document.body.style.overflow='hidden';
  }catch(err){
    alert('Trainingseinheit konnte nicht geöffnet werden: '+(err?.message||err));
  }
};

/* Refresh the branch card and the outdated intro copy when opening Training planen. */
const home244=window.eplanHome;
window.eplanHome=function(){
  const r=typeof home244==='function'?home244.apply(this,arguments):undefined;
  const intro=document.querySelector('#epMain .fcne-branch-intro');
  if(intro)intro.textContent='Wähle deine Bibliothek: SFV, Easy2Coach oder MH / fussballtraining.li. Alle drei bleiben vollständig getrennt.';
  const card=document.getElementById('fcneMhBranchCard');
  if(card){
    card.innerHTML='<span class="ep-icon">⚽</span><span class="fcne-branch-label">ZWEIG 3</span><b>MH / fussballtraining.li</b><small>29 komplette Trainingseinheiten · 129 Einzelübungen mit Originalgrafiken.</small>';
  }
  document.querySelectorAll('.app-version').forEach(el=>{if(/Version/i.test(el.textContent||''))el.textContent='Version 2.44 · MH UI-Fix · Build 2026.11.15'});
  return r;
};
setTimeout(()=>window.eplanHome?.(),0);
})();
</script>
<script>window.FCNE_APP_VERSION='2.44 MH-UI-FIX';</script>
'''

html=html.replace("</body>",patch+"\n</body>")
idx.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.44-mh-ui-fix-20261115';",sw,count=1)
swp.write_text(sw,encoding="utf-8")

print("v2.44 patch written")
