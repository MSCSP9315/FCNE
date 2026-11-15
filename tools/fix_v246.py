from pathlib import Path
import re

idx=Path("index.html")
swp=Path("sw.js")
html=idx.read_text(encoding="utf-8")
html=re.sub(r'<script id="fcne-v246-mh-compose">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

patch=r'''
<script id="fcne-v246-mh-compose">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.46 MH-COMPOSE-FIX';

const previousCompose246=window.fcneBranchCompose;

window.fcneBranchCompose=async function(){
  const branch=window.FCNE_ACTIVE_BRANCH||'sfv';
  if(branch!=='mh'){
    return typeof previousCompose246==='function'
      ? previousCompose246.apply(this,arguments)
      : undefined;
  }

  try{
    await window.fcneLoadMH();
    window.FCNE_ACTIVE_BRANCH='mh';

    const pool=window.fcneBranchPool('mh');
    if(!Array.isArray(pool)||!pool.length){
      throw new Error('MH-Übungen sind noch nicht geladen');
    }

    if(typeof window.eplanClose==='function')window.eplanClose();

    // Start the existing FCNE wizard directly. Do not route through startWizard,
    // because startWizard is later replaced by the Training-plan overlay.
    draft={
      name:'',
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

    if(typeof showScreen!=='function')throw new Error('Trainings-Wizard nicht verfügbar');
    if(typeof renderWizard!=='function')throw new Error('Wizard-Darstellung nicht verfügbar');

    showScreen('wizard');
    renderWizard();
  }catch(err){
    console.error('FCNE MH compose error',err);
    alert('Training zusammenstellen konnte nicht geöffnet werden: '+(err?.message||String(err)));
  }
};

document.querySelectorAll('.app-version').forEach(el=>{
  if(/Version/i.test(el.textContent||''))el.textContent='Version 2.46 · MH Compose-Fix · Build 2026.11.15';
});
})();
</script>
<script>window.FCNE_APP_VERSION='2.46 MH-COMPOSE-FIX';</script>
'''
html=html.replace("</body>",patch+"\n</body>")
idx.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.46-mh-compose-fix-20261115';",sw,count=1)
swp.write_text(sw,encoding="utf-8")
print("v2.46 written")
