from pathlib import Path
import re, json

idx=Path("index.html")
swp=Path("sw.js")
mhp=Path("mh_library.json")

# Curated planner mapping only: these source drills are suitable for FCNE "Vielseitigkeit".
versatile_ids={
    "mh05-ex01", # Team-Kooperation / kognitives Aufwärmen
    "mh07-ex01", # Technikübung / Bewegungsabläufe
    "mh16-ex01", # kognitives Lauf-ABC
    "mh16-ex02", # kommunikative Übungsform
    "mh17-ex01", # Technik / Passübung
    "mh19-ex01", # Technik
    "mh27-ex01", # Technik / Passen mit Zielschuss
}

mh=json.loads(mhp.read_text(encoding="utf-8"))
for e in mh.get("exercises",[]):
    # Preserve original source stage in mhStage; category is the FCNE planner classification.
    if e.get("id") in versatile_ids:
        e["category"]="Vielseitigkeit"
        e["mhPlannerNote"]="Für den FCNE-Planer als Vielseitigkeit eingeordnet; Originalstufe bleibt in mhStage erhalten."
mhp.write_text(json.dumps(mh,ensure_ascii=False,separators=(",",":")),encoding="utf-8")

counts={}
for e in mh["exercises"]:
    counts[e["category"]]=counts.get(e["category"],0)+1
if counts.get("Vielseitigkeit",0)<5:
    raise SystemExit("MH Vielseitigkeit mapping failed")
print("MH categories:",counts)

html=idx.read_text(encoding="utf-8")
html=re.sub(r'<script id="fcne-v248-mh-wizard">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

patch=r'''
<script id="fcne-v248-mh-wizard">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.48 MH-WIZARD-FLOW';

function ensureMHWizardStubs(){
  DATA.filter(e=>e?.fcneBranch==='mh').forEach(e=>{
    const idx=DATA.indexOf(e);
    if(idx<0)return;
    let sec=document.getElementById('detail-'+idx);
    if(!sec){
      sec=document.createElement('section');
      sec.id='detail-'+idx;
      sec.className='exercise-detail';
      document.body.appendChild(sec);
    }
    if(!sec.querySelector('.detail-hero')){
      const img=document.createElement('img');
      img.className='detail-hero';
      img.alt=e.title||'MH Übung';
      img.src=e.image||'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360"><rect width="100%" height="100%" fill="#f3eef9"/><text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" fill="#6d28d9" font-family="Arial" font-size="24">MH / fussballtraining.li</text></svg>'
      );
      sec.appendChild(img);
    }
  });
}

const compose248=window.fcneBranchCompose;
window.fcneBranchCompose=async function(){
  if((window.FCNE_ACTIVE_BRANCH||'sfv')!=='mh'){
    return typeof compose248==='function'?compose248.apply(this,arguments):undefined;
  }
  try{
    await window.fcneLoadMH();
    ensureMHWizardStubs();
    window.FCNE_ACTIVE_BRANCH='mh';

    const pool=window.fcneBranchPool('mh');
    if(!Array.isArray(pool)||!pool.length)throw new Error('MH-Übungen sind noch nicht geladen');

    if(typeof window.eplanClose==='function')window.eplanClose();

    draft={
      name:'MH Training',
      target:75,
      players:10,
      focus:'Gemischt / allgemein',
      date:(typeof v191Today==='function'?v191Today():new Date().toISOString().slice(0,10)),
      notes:'Zweig: MH / fussballtraining.li',
      customDurations:{},
      selections:{},
      sourceBranch:'mh',
      environment:'field'
    };
    window.FCNE_WIZARD_RETURN_CONTEXT={view:'branch',branch:'mh',mode:null};
    window.FCNE_WIZARD_ENTRY_MODE='compose';
    wizardStep=0;
    showScreen('wizard');
    renderWizard();
  }catch(err){
    console.error('FCNE MH wizard flow error',err);
    alert('Training zusammenstellen konnte nicht geöffnet werden: '+(err?.message||String(err)));
  }
};

const render248=window.renderWizard;
window.renderWizard=function(){
  if(typeof draft!=='undefined'&&draft?.sourceBranch==='mh')ensureMHWizardStubs();
  return typeof render248==='function'?render248.apply(this,arguments):undefined;
};

document.querySelectorAll('.app-version').forEach(el=>{
  if(/Version/i.test(el.textContent||''))el.textContent='Version 2.48 · MH Wizard-Flow · Build 2026.11.15';
});
})();
</script>
<script>window.FCNE_APP_VERSION='2.48 MH-WIZARD-FLOW';</script>
'''
html=html.replace("</body>",patch+"\n</body>")
idx.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.48-mh-wizard-flow-20261115';",sw,count=1)
swp.write_text(sw,encoding="utf-8")
print("v2.48 written")
