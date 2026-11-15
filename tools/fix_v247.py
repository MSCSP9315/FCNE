from pathlib import Path
import re

idx=Path("index.html")
swp=Path("sw.js")
html=idx.read_text(encoding="utf-8")
html=re.sub(r'<script id="fcne-v247-mh-wizard">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

patch=r'''
<script id="fcne-v247-mh-wizard">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.47 MH-WIZARD-FIX';

function ensureMHWizardStubs(){
  const mh=DATA.filter(e=>e?.fcneBranch==='mh');
  mh.forEach(e=>{
    const idx=DATA.indexOf(e);
    if(idx<0)return;
    let sec=document.getElementById('detail-'+idx);
    if(!sec){
      sec=document.createElement('section');
      sec.id='detail-'+idx;
      sec.className='exercise-detail';
      document.body.appendChild(sec);
    }
    // The legacy wizard expects this exact DOM image to exist before it renders
    // every choice card and the final summary.
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

const compose247=window.fcneBranchCompose;
window.fcneBranchCompose=async function(){
  if((window.FCNE_ACTIVE_BRANCH||'sfv')!=='mh'){
    return typeof compose247==='function'?compose247.apply(this,arguments):undefined;
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

    if(typeof showScreen!=='function'||typeof renderWizard!=='function')throw new Error('Trainings-Wizard nicht verfügbar');
    showScreen('wizard');
    renderWizard();
  }catch(err){
    console.error('FCNE MH wizard error',err);
    alert('Training zusammenstellen konnte nicht geöffnet werden: '+(err?.message||String(err)));
  }
};

// If an MH plan is restored later, make sure its legacy image dependencies exist too.
const render247=window.renderWizard;
window.renderWizard=function(){
  if(typeof draft!=='undefined'&&draft?.sourceBranch==='mh')ensureMHWizardStubs();
  return typeof render247==='function'?render247.apply(this,arguments):undefined;
};

document.querySelectorAll('.app-version').forEach(el=>{
  if(/Version/i.test(el.textContent||''))el.textContent='Version 2.47 · MH Wizard-Fix · Build 2026.11.15';
});
})();
</script>
<script>window.FCNE_APP_VERSION='2.47 MH-WIZARD-FIX';</script>
'''
html=html.replace("</body>",patch+"\n</body>")
idx.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.47-mh-wizard-fix-20261115';",sw,count=1)
swp.write_text(sw,encoding="utf-8")
print("v2.47 written")
