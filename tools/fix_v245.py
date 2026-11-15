from pathlib import Path
import re

idx=Path("index.html")
swp=Path("sw.js")
html=idx.read_text(encoding="utf-8")

# Idempotent rerun.
html=re.sub(r'<style id="fcne-v245-mh-open">.*?</style>\s*<script id="fcne-v245-mh-open">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

patch=r'''
<style id="fcne-v245-mh-open">
/* v2.45: MH complete-unit overlay must sit ABOVE Training planen on iOS */
#mhUnitOverlay{
  position:fixed!important;
  inset:0!important;
  width:100%!important;
  height:100%!important;
  max-width:none!important;
  z-index:2147483000!important;
  background:#fff!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  -webkit-overflow-scrolling:touch!important;
  display:none!important;
  opacity:1!important;
  visibility:visible!important;
  transform:none!important;
}
#mhUnitOverlay.open{display:block!important}
#mhUnitOverlay .detail-header{
  position:sticky!important;
  top:0!important;
  z-index:10!important;
  background:#fff!important;
}
.fcne-mh-unit-card{
  pointer-events:auto!important;
  -webkit-tap-highlight-color:rgba(124,58,237,.12);
  touch-action:manipulation;
}
</style>
<script id="fcne-v245-mh-open">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.45 MH-OPEN-FIX';
const esc245=v=>typeof escapeHtml==='function'?escapeHtml(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

window.fcneRenderMHUnits=async function(){
  const d=await window.fcneLoadMH();
  const q=(document.getElementById('mhUnitSearch')?.value||'').trim().toLowerCase();
  const th=document.getElementById('mhUnitTheme')?.value||'Alle Schwerpunkte';
  const rows=d.units.filter(u=>(th==='Alle Schwerpunkte'||u.theme===th)&&(!q||[u.title,u.theme,u.intro].join(' ').toLowerCase().includes(q)));
  const count=document.getElementById('mhUnitCount');
  const list=document.getElementById('mhUnitList');
  if(count)count.textContent=rows.length+' Trainingseinheiten gefunden';
  if(!list)return;
  list.innerHTML=rows.map(u=>
    '<button type="button" class="fcne-mh-unit-card" onclick="window.fcneOpenMHUnit(\''+esc245(u.id)+'\');return false;">'+
      '<span class="num">'+String(Number(u.id.slice(2))).padStart(2,'0')+'</span>'+
      '<span class="copy"><b>'+esc245(u.title)+'</b><small>'+esc245(u.theme)+' · '+u.exercise_count+' Originalübungen</small></span>'+
      '<span class="go">›</span>'+
    '</button>'
  ).join('');
};

window.fcneCloseMHUnit=function(){
  const n=document.getElementById('mhUnitOverlay');
  if(n)n.classList.remove('open');
  document.body.style.overflow='';
};

window.fcneOpenMHUnit=async function(id){
  try{
    const d=await window.fcneLoadMH();
    const u=d.units.find(x=>x.id===id);
    if(!u)throw new Error('Trainingseinheit '+id+' wurde nicht gefunden');

    const xs=DATA
      .filter(e=>e.fcneBranch==='mh'&&e.mhUnitId===id)
      .sort((a,b)=>(a.mhOrder||0)-(b.mhOrder||0));
    if(!xs.length)throw new Error('Keine Übungen für diese Trainingseinheit geladen');

    const hasClosing=xs.some(e=>e.category==='Ausklang'||/abschlussspiel/i.test(e.title||''));
    const shown=hasClosing?xs:[...xs,d.closing].filter(Boolean);

    let n=document.getElementById('mhUnitOverlay');
    if(!n){
      n=document.createElement('section');
      n.id='mhUnitOverlay';
      document.body.appendChild(n);
    }
    n.className='exercise-detail';

    const cards=shown.map((e,k)=>{
      const src=esc245(e.source_url||u.url||'https://fussballtraining.li/');
      const media=e.image
        ? '<img src="'+esc245(e.image)+'" alt="'+esc245(e.title)+'" onclick="if(window.openZoom)window.openZoom(this.src)" onerror="this.outerHTML=\'<div class=&quot;mh-img-fallback&quot;>Originalbild konnte nicht geladen werden.<br><a href=&quot;'+src+'&quot; target=&quot;_blank&quot; rel=&quot;noopener&quot;>Originalquelle öffnen</a></div>\'">'
        : '<div class="mh-img-fallback">Für diese Übung ist kein Bild hinterlegt.<br><a href="'+src+'" target="_blank" rel="noopener">Originalquelle öffnen</a></div>';
      return '<div class="mh-unit-ex">'+media+
        '<div class="mh-unit-ex-copy">'+
          '<span class="stage">'+(k+1)+' · '+esc245(e.mhStage||e.category||'Übung')+'</span>'+
          '<h3>'+esc245(e.title)+'</h3>'+
          '<p>'+esc245(e.players||'Spielerzahl variabel')+' · '+esc245(e.category||'')+'</p>'+
          '<button type="button" class="mh-open-ex" onclick="window.fcneOpenMHExerciseFromUnit(\''+esc245(e.id)+'\');return false;">Übung im Detail öffnen</button>'+
        '</div>'+
      '</div>';
    }).join('');

    n.innerHTML=
      '<div class="detail-header">'+
        '<button type="button" class="round-back" onclick="window.fcneCloseMHUnit();return false;">‹</button>'+
        '<div class="detail-title"><strong>'+esc245(u.title)+'</strong><small>MH · '+esc245(u.theme)+' · komplette Einheit</small></div>'+
      '</div>'+
      '<div class="detail-content">'+
        '<div class="mh-unit-intro">'+esc245(u.intro||'Komplette Trainingseinheit aus dem Gratisbuch Fußballtraining.')+'</div>'+
        '<div class="fcne-mh-note"><b>Originalaufbau:</b> Die Übungen sind in der Reihenfolge der Quelle dargestellt.</div>'+
        '<div class="mh-unit-exercises">'+cards+'</div>'+
        '<a class="mh-source-link" href="'+esc245(u.url)+'" target="_blank" rel="noopener">↗ Originaleinheit auf fussballtraining.li öffnen</a>'+
      '</div>';

    document.body.appendChild(n); // move to the very end of body = topmost stacking order
    n.classList.add('open');
    document.body.style.overflow='hidden';
    n.scrollTop=0;
  }catch(err){
    console.error('FCNE MH open error',id,err);
    alert('Trainingseinheit konnte nicht geöffnet werden: '+(err?.message||String(err)));
  }
};

document.querySelectorAll('.app-version').forEach(el=>{
  if(/Version/i.test(el.textContent||''))el.textContent='Version 2.45 · MH Open-Fix · Build 2026.11.15';
});
})();
</script>
<script>window.FCNE_APP_VERSION='2.45 MH-OPEN-FIX';</script>
'''
html=html.replace("</body>",patch+"\n</body>")
idx.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.45-mh-open-fix-20261115';",sw,count=1)
swp.write_text(sw,encoding="utf-8")
print("v2.45 written")
