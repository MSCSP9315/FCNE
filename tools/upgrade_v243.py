import json, re, html as htmllib
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT=Path(".")
INDEX=ROOT/"index.html"
SW=ROOT/"sw.js"
MHFILE=ROOT/"mh_library.json"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/155 Safari/537.36"

UNITS=[
("mh01","Ballzirkulation","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/81-ballzirkulation-durch-spiel-zum-dritten"),
("mh02","Viererkette","https://fussballtraining.li/viererkette/viererkette-trainieren-jahr-2022"),
("mh03","Spielaufbau","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/79-spielaufbau-sicherer-balltransport-ins-mittelfeld"),
("mh04","Pressing","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/83-pressing-balleroberung-in-gegnerischer-tornaehe"),
("mh05","Gegenpressing","https://fussballtraining.li/fussballtraining/trainingsformen/13-fussballtraining-mit-nur-vier-huetchen-zum-thema-gegenpressing"),
("mh06","Konterspiel","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/91-konterspiel-als-aussenseiter-zum-sieg"),
("mh07","1 gegen 1","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/10-offensives-1-gegen-1-angriffsspiel-variabel-gestalten"),
("mh08","Tiefenläufe","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/84-tiefenlauf-hohe-abwehrketten-knacken"),
("mh09","Übergangsspiel","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/78-uebergangsspiel-balltransport-ins-gegner-drittel"),
("mh10","Zusammenspiel Mittelfeld / Sturm","https://fussballtraining.li/fussballtraining/80-torerfolg-durch-zusammenspiel-mit-dem-sturm"),
("mh11","90-Grad-Ball","https://fussballtraining.li/fussballtraining/86-90-grad-ball-tore-vorbereiten-von-der-grundlinie"),
("mh12","Pass in den Rücken der Abwehr","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/93-offensivpower-pass-in-den-ruecken-der-abwehr"),
("mh13","Klatsch-Steil-Prinzip","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/94-offensivpower-durch-das-klatsch-steil-prinzip"),
("mh14","Torerfolg","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/87-torerfolg-das-moderne-torschusstraining"),
("mh15","Ballzirkulation","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/34-komplette-trainingseinheit-perfekte-ballzirkulation"),
("mh16","Ballzirkulation","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/11-professionelles-fussballtraining-ballzirkulation-mit-kognitiven-und-athletischen-aspekten"),
("mh17","Ballzirkulation","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/7-ballzirkulation-verbesserung-des-zusammenspiels"),
("mh18","Ballzirkulation","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/106-fussballtraining-mehr-ballbesitz-durch-direktes-spiel-zum-dritten"),
("mh19","90-Grad-Ball","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/6-90-grad-ball-angriffsspiel-ueber-aussen"),
("mh20","Spielaufbau","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/97-innenverteidiger-im-spielaufbau-pressing-linie-ueberdribbeln"),
("mh21","Gegenpressing","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/69-drei-profi-uebungen-ballhalten-und-gegenpressing"),
("mh22","Gegenpressing","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/90-gegenpressing-oder-zurueck-umschaltverhalten-perfektionieren"),
("mh23","Tiefenläufe","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/88-komplettes-angriffstraining-tiefenlauf"),
("mh24","Tiefenläufe","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/96-mit-tiefenlaeufe-gegnerische-abwehr-stressen-komplette-trainingseinheit"),
("mh25","Tiefenläufe","https://fussballtraining.li/fussballtraining/nebenschwerpunkte/107-mega-einheit-fuers-angriffsspiel-gegengleiche-laeufe"),
("mh26","Zusammenspiel Mittelfeld / Sturm","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/105-komplette-trainingseinheit-sturmspitze-im-fokus"),
("mh27","Torerfolg","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/8-torerfolg-torchancen-erspielen-und-verwerten"),
("mh28","Torerfolg","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/98-tore-durchs-zentrum-erzielen-trainingseinheit-in-einem-feld"),
("mh29","Torerfolg","https://fussballtraining.li/fussballtraining/hauptschwerpunkte/99-torchancen-gegen-kompakte-gegner-vorbereiten"),
]
CLOSING="https://fussballtraining.li/fussballtraining/73-das-abschlussspiel-im-fussballtraining"

def clean(t): return re.sub(r"\s+"," ",t or "").strip()
def imgurl(img,base):
    for k in ("data-src","data-lazy-src","src"):
        v=img.get(k)
        if v and not v.startswith("data:"): return urljoin(base,v)
    ss=img.get("srcset","")
    return urljoin(base,ss.split(",")[0].strip().split(" ")[0]) if ss else ""

def focus(theme):
    t=theme.lower()
    if "1 gegen 1" in t:return "1 gegen 1"
    if any(x in t for x in ["torerfolg","90-grad","rücken","klatsch"]):return "Torschuss"
    if any(x in t for x in ["ballzirkulation","spielaufbau","zusammenspiel"]):return "Passen & Ballkontrolle"
    return "Spielformen"

def category(label,order,total,text):
    t=(label+" "+text).lower()
    if order==1 or any(x in t for x in ["warm-up","warm up","einstimmung","aktivierung"]):return "Aufwärmen"
    if any(x in t for x in ["koordination","athletik","lauf-abc","lauf abc"]) and order<=2:return "Vielseitigkeit"
    if "abschlussspiel" in t:return "Ausklang"
    if order==total:return "Fussball spielen"
    return "Fussball spielen lernen"

def extract(uid,theme,url):
    r=requests.get(url,headers={"User-Agent":UA},timeout=45);r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser");h1=soup.find("h1")
    title=clean(h1.get_text(" ",strip=True) if h1 else theme)
    container=soup.body
    if h1:
        for p in h1.parents:
            cls=" ".join(p.get("class",[])) if getattr(p,"attrs",None) else ""
            if getattr(p,"name",None) in ("article","main") or (re.search(r"(item-page|article|content)",cls,re.I) and len(p.get_text(" ",strip=True))>800):
                container=p;break
    events=[]
    for tag in container.find_all(["img","p","h2","h3","h4","li"]):
        if tag.name=="img":
            src=imgurl(tag,url);alt=clean(tag.get("alt",""))
            if src:events.append(("img",{"src":src,"alt":alt}))
        else:
            txt=clean(tag.get_text(" ",strip=True))
            if txt:events.append(("text",txt))
    marks=[i for i,(k,v) in enumerate(events) if k=="text" and re.search(r"Organisation\s*(?:&|und)\s*Ablauf",v,re.I)]
    exercises=[]
    for pos,idx in enumerate(marks):
        nxt=marks[pos+1] if pos+1<len(marks) else len(events)
        marker=events[idx][1]
        mm=re.search(r"Organisation\s*(?:&|und)\s*Ablauf\s*(?:\(([^)]*)\))?",marker,re.I)
        stage=clean(mm.group(1) if mm and mm.group(1) else re.sub(r"Organisation\s*(?:&|und)\s*Ablauf","",marker,flags=re.I))
        image="";alt=""
        for j in range(idx-1,-1,-1):
            if events[j][0]=="img":
                a=events[j][1]["alt"];s=events[j][1]["src"]
                if not re.search(r"(Martin Hasenpflug|Viererkette bei|Pin It|Bücher|Cover|logo)",a,re.I):
                    image=s;alt=a;break
        seg=[v for k,v in events[idx:nxt] if k=="text"]
        fields={"Organisation & Ablauf":[],"Spieleranzahl":[],"Wettbewerb":[],"Variation":[],"Tipp":[]};cur="Organisation & Ablauf"
        for s in seg:
            if re.search(r"Organisation\s*(?:&|und)\s*Ablauf",s,re.I):
                s=re.sub(r"^.*?Organisation\s*(?:&|und)\s*Ablauf\s*(?:\([^)]*\))?\s*","",s,flags=re.I)
                if s:fields[cur].append(s)
                continue
            hit=None
            for key in ("Spieleranzahl","Wettbewerb","Variation","Tipp"):
                if re.match(rf"^{key}\s*:",s,re.I):
                    hit=key;s=re.sub(rf"^{key}\s*:\s*","",s,flags=re.I);break
            if hit:cur=hit
            if s:fields[cur].append(s)
        full=" ".join(sum(fields.values(),[]))
        cat=category(stage,pos+1,len(marks),full)
        sections=[[k,clean(" ".join(fields[k]))] for k in fields if clean(" ".join(fields[k]))]
        mats=[];low=full.lower()
        for kw,lab in [("ball","Bälle"),("hütchen","Hütchen"),("stange","Stangen"),("leibchen","Leibchen"),("minitor","Minitore"),("großtor","Gross-/Fussballtore"),("leiter","Koordinationsleiter")]:
            if kw in low and lab not in mats:mats.append(lab)
        ex={"id":f"{uid}-ex{pos+1:02d}","title":alt if len(alt)>3 else (stage or f"{title} – Übung {pos+1}"),"category":cat,"duration":15,"duration_note":"App-Planungswert; Quelle nennt keine feste Minutenangabe pro Übung.","field":"Feld","environment":"field","fcneTrainingPlaces":"Feld","focus":focus(theme),"intro":clean(" ".join(fields["Organisation & Ablauf"]))[:420],"sections":sections,"source_provider":"MH / fussballtraining.li","source_label":"Martin Hasenpflug – Gratisbuch Fußballtraining","source_url":url,"source_note":"Originalübung aus dem kostenlosen Trainingsbuch.","fcneBranch":"mh","age":"Quelle: ab C-Jugend; für E/F bei Bedarf vereinfachen","players":clean(" ".join(fields["Spieleranzahl"])) or "variabel","level":"ab C-Jugend laut Quelle","materials":mats,"coaching":[x.strip() for x in re.split(r"(?<=[.!?])\s+",clean(" ".join(fields["Tipp"]))) if x.strip()][:8],"image":image,"images":[image] if image else [],"mhUnitId":uid,"mhUnitTitle":title,"mhTheme":theme,"mhOrder":pos+1,"mhStage":stage or f"Übung {pos+1}"}
        exercises.append(ex)
    intro=""
    if h1:
        ps=[]
        for tag in h1.find_all_next(["p","h2","h3"]):
            txt=clean(tag.get_text(" ",strip=True))
            if re.search(r"Organisation\s*(?:&|und)\s*Ablauf",txt,re.I):break
            if txt:ps.append(txt)
            if len(" ".join(ps))>900:break
        intro=clean(" ".join(ps))[:1200]
    return {"id":uid,"theme":theme,"title":title,"url":url,"intro":intro,"focus":focus(theme),"exercise_count":len(exercises),"exercises":exercises}

# Scrape and validate MH source
units=[];exs=[]
for uid,theme,url in UNITS:
    u=extract(uid,theme,url);units.append({k:v for k,v in u.items() if k!="exercises"});exs.extend(u["exercises"])
byunit={}
for e in exs:byunit.setdefault(e["mhUnitId"],[]).append(e)
for u in units:u["exercise_ids"]=[e["id"] for e in sorted(byunit.get(u["id"],[]),key=lambda x:x["mhOrder"])];u["exercise_count"]=len(u["exercise_ids"])
closing_page=extract("mh-closing","Abschlussspiel",CLOSING)
closing=(closing_page["exercises"] or [{}])[0]
closing.update({"id":"mh-closing-generic","title":"MH Abschlussspiel","category":"Ausklang","duration":15,"field":"Feld","environment":"field","fcneTrainingPlaces":"Feld","focus":"Spielformen","fcneBranch":"mh","source_provider":"MH / fussballtraining.li","source_label":"Martin Hasenpflug – Das Abschlussspiel im Fußballtraining","source_url":CLOSING,"mhUnitId":"mh-closing","mhUnitTitle":"Das Abschlussspiel im Fußballtraining","mhTheme":"Abschlussspiel","mhOrder":99,"mhStage":"Abschlussspiel","mhGenericClosing":True})
if len(units)!=29 or len(exs)!=129: raise SystemExit(f"MH validation failed: units={len(units)} exercises={len(exs)}")
img_count=sum(bool(e.get("image")) for e in exs)
print(f"MH scrape: {len(units)} units, {len(exs)} exercises, {img_count} image URLs")
missing_imgs=[e for e in exs if not e.get("image")]
if missing_imgs:
    print("MISSING_IMAGES:")
    for e in missing_imgs:
        print(e["id"],"|",e["title"],"|",e["source_url"])
if img_count<128: raise SystemExit(f"MH image validation failed: only {img_count} image URLs")
MHFILE.write_text(json.dumps({"source":"https://fussballtraining.li/publikationen/die-neuen/gratisbuch-fussballtraining","units":units,"exercises":exs,"closing":closing},ensure_ascii=False,separators=(",",":")),encoding="utf-8")

# Mark the 177 user-confirmed Easy2Coach records directly in the embedded dataset.
html=INDEX.read_text(encoding="utf-8")
m=re.search(r'const E2C=(\[.*?\]);\n\s*function escSvg',html,re.S)
if not m: raise SystemExit("E2C dataset not found")
e2c=json.loads(m.group(1))
if len(e2c)!=177: raise SystemExit(f"E2C validation failed: {len(e2c)}")
hall={55,56,57,*range(61,103)}
for e in e2c:
    n=int(e["id"].split("-")[1]);mode="hall" if n in hall else "field"
    e["fcneConfirmedMode"]=mode;e["environment"]=mode;e["fcneTrainingPlaces"]="Halle" if mode=="hall" else "Feld"
if sum(e["fcneConfirmedMode"]=="field" for e in e2c)!=132 or sum(e["fcneConfirmedMode"]=="hall" for e in e2c)!=45:raise SystemExit("E2C split validation failed")
html=html[:m.start(1)]+json.dumps(e2c,ensure_ascii=False,separators=(",",":"))+html[m.end(1):]

# Remove previous production layer if this workflow is ever re-run.
html=re.sub(r'<style id="fcne-v243-prod-css">.*?</style>\s*<script id="fcne-v243-prod">.*?</script>\s*<script>window\.FCNE_APP_VERSION=.*?</script>\s*','',html,flags=re.S)

css=r'''<style id="fcne-v243-prod-css">
.fcne-branch-mh{border-color:#d8c9ef!important;background:linear-gradient(145deg,#f8f3ff,#fff)!important}.fcne-branch-mh .ep-icon{background:#efe5ff!important}
.fcne-mh-head{background:linear-gradient(145deg,#f7f1ff,#fff);border:1px solid #dfd1f2;border-radius:18px;padding:15px;margin-bottom:13px}.fcne-mh-head h2{margin:5px 0 4px;color:#4d2878}.fcne-mh-head p{margin:0;color:#6c6276;font-size:12px;line-height:1.5}.fcne-mh-pill{display:inline-flex;padding:5px 9px;border-radius:999px;background:#efe5ff;color:#5b2f87;font-size:10px;font-weight:900}
.fcne-mh-note{margin:10px 0 14px;padding:11px 12px;background:#fff7e8;border:1px solid #f0ddb4;border-radius:13px;font-size:11px;line-height:1.45;color:#6a5730}.fcne-mh-unit-list{display:grid;gap:10px;margin-top:12px}.fcne-mh-unit-card{width:100%;border:1px solid #e4d9f0;background:#fff;border-radius:16px;padding:13px;text-align:left;display:flex;align-items:center;gap:12px}.fcne-mh-unit-card .num{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;background:#f0e7fb;color:#5b2f87;font-weight:900}.fcne-mh-unit-card .copy{flex:1;min-width:0}.fcne-mh-unit-card b{display:block;font-size:14px}.fcne-mh-unit-card small{display:block;color:#758079;font-size:10px;margin-top:4px}.fcne-mh-filters{display:grid;grid-template-columns:1.25fr .9fr;gap:8px;margin-top:10px}.fcne-mh-filters input,.fcne-mh-filters select{width:100%;box-sizing:border-box;border:1px solid #dde4df;border-radius:11px;padding:10px;background:#fff}
.mh-unit-intro{background:#f8f5fb;border:1px solid #e7ddf0;border-radius:15px;padding:13px;margin:12px 0;font-size:12px;line-height:1.55}.mh-unit-exercises{display:grid;gap:13px;margin-top:12px}.mh-unit-ex{border:1px solid #dfe7e2;border-radius:17px;background:#fff;overflow:hidden}.mh-unit-ex img{display:block;width:100%;max-height:280px;object-fit:contain;background:#f4f6f5}.mh-unit-ex-copy{padding:12px}.mh-unit-ex-copy .stage{font-size:10px;font-weight:900;color:#64378e;background:#f0e7fb;border-radius:999px;padding:4px 7px;display:inline-block}.mh-unit-ex-copy h3{font-size:15px;margin:7px 0 5px}.mh-open-ex{width:100%;border:0;border-radius:11px;background:#166b43;color:#fff;padding:10px;margin-top:9px;font-weight:900}.mh-source-link{display:block;text-decoration:none;text-align:center;background:#f0e7fb;color:#542a7e;border-radius:12px;padding:11px;font-weight:900;margin:14px 0}
@media(max-width:560px){.fcne-mh-filters{grid-template-columns:1fr}.mh-unit-ex img{max-height:230px}}
</style>'''

js=r'''<script id="fcne-v243-prod">
(function(){
'use strict';
window.FCNE_APP_VERSION='2.43 MH-LIBRARY';
let MH=null,MH_LOADING=null;
const esc=v=>typeof escapeHtml==='function'?escapeHtml(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
function confirmedMode(e){if(!e)return null;if(e.fcneConfirmedMode==='field'||e.fcneConfirmedMode==='hall')return e.fcneConfirmedMode;if(!/^e2c-\d{4}$/.test(String(e.id||''))){if(e.environment==='field'||e.environment==='hall')return e.environment;if(e.fcneTrainingPlaces==='Feld')return 'field';if(e.fcneTrainingPlaces==='Halle')return 'hall'}return null}
window.fcneConfirmedExerciseMode=confirmedMode;window.fcneIsHallExercise=e=>confirmedMode(e)==='hall';window.fcneIsFieldExercise=e=>confirmedMode(e)==='field';
const oldBranch=window.fcneExerciseBranch;window.fcneExerciseBranch=e=>e?.fcneBranch==='mh'?'mh':(typeof oldBranch==='function'?oldBranch(e):(e?.fcneBranch||'sfv'));
const oldPool=window.fcneBranchPool;window.fcneBranchPool=function(branch){const b=branch??window.FCNE_ACTIVE_BRANCH??'sfv';if(b==='mh')return DATA.filter(e=>window.fcneExerciseBranch(e)==='mh');return typeof oldPool==='function'?oldPool.apply(this,arguments):DATA.filter(e=>window.fcneExerciseBranch(e)===b)};
window.fcneEasyModePool=function(mode){const m=mode==='hall'?'hall':'field';return DATA.filter(e=>window.fcneExerciseBranch(e)==='easy2coach'&&confirmedMode(e)===m&&e.id!=='fcne-halle-6v6-tw')};
const oldSwap=window.fcneApplySwap;window.fcneApplySwap=function(phase,id){const e=DATA.find(x=>x.id===id);if(typeof draft!=='undefined'&&draft?.sourceBranch==='easy2coach'){const m=draft.environment==='hall'?'hall':'field';if(confirmedMode(e)!==m){alert('BLOCKIERT: Falscher Trainingsort für dieses Training.');return}}return typeof oldSwap==='function'?oldSwap.apply(this,arguments):undefined};

async function loadMH(){
 if(MH)return MH;if(MH_LOADING)return MH_LOADING;
 MH_LOADING=fetch('./mh_library.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('MH '+r.status);return r.json()}).then(d=>{if(d.units?.length!==29||d.exercises?.length!==129)throw new Error('MH-Datensatz unvollständig');MH=d;[...d.exercises,d.closing].forEach(e=>{if(e&&!DATA.some(x=>x.id===e.id))DATA.push(e)});return d}).catch(err=>{MH_LOADING=null;alert('MH-Bibliothek konnte nicht geladen werden: '+err.message);throw err});return MH_LOADING
}
window.fcneLoadMH=loadMH;
function hidePanels(){['epSFV','epAuto','epTopics','epBranch','epLibrary'].forEach(id=>document.getElementById(id)?.classList.remove('open'));const main=document.getElementById('epMain');if(main)main.style.display='none'}
function head(title,sub){const h=document.querySelector('#eplanOverlay .ep-head>div');if(h)h.innerHTML='<b>'+esc(title)+'</b><div style="font-size:12px;color:#718078">'+esc(sub)+'</div>'}
const oldHome=window.eplanHome;window.eplanHome=function(){if(typeof oldHome==='function')oldHome();const main=document.getElementById('epMain');if(!main)return;main.style.display='block';if(!document.getElementById('fcneMhBranchCard')){const card=document.createElement('button');card.id='fcneMhBranchCard';card.className='ep-card fcne-branch-card fcne-branch-mh';card.onclick=()=>window.fcneOpenBranch('mh');card.innerHTML='<span class="ep-icon">🟣</span><span class="fcne-branch-label">Zweig 3</span><b>MH / fussballtraining.li</b><small>29 komplette Trainingseinheiten + 129 Einzelübungen mit Originalgrafiken.</small>';main.appendChild(card)}head('Training planen','E-Junioren · 3 getrennte Bibliotheken')};
const oldOpen=window.fcneOpenBranch;window.fcneOpenBranch=function(branch){if(branch!=='mh')return oldOpen?.apply(this,arguments);return openMH()};
async function openMH(){await loadMH();window.FCNE_ACTIVE_BRANCH='mh';window.FCNE_EASY_MODE=null;hidePanels();const box=document.getElementById('epBranch');if(!box)return;box.classList.add('open');head('MH / fussballtraining.li','29 komplette Einheiten · 129 Einzelübungen');box.innerHTML='<div class="fcne-mh-head"><span class="fcne-mh-pill">🟣 MARTIN HASENPFLUG</span><h2>MH / fussballtraining.li</h2><p>Eigener Trainingszweig mit kompletten Original-Einheiten und separat nutzbaren Einzelübungen.</p></div><div class="fcne-mh-note"><b>Altersstufe:</b> Die Quelle empfiehlt die Inhalte ab C-Jugend. Für E/F kann der Trainer Regeln, Feldgrösse und Komplexität vereinfachen.</div><button class="fcne-action-card" onclick="fcneMHUnits()"><span class="action-ico">📘</span><span><b>29 komplette Trainingseinheiten</b><small>Originalaufbau Schritt für Schritt.</small></span><span class="go">›</span></button><button class="fcne-action-card" onclick="fcneBranchCompose()"><span class="action-ico">🧩</span><span><b>Training zusammenstellen</b><small>MH-Einzelübungen selbst kombinieren.</small></span><span class="go">›</span></button><button class="fcne-action-card" onclick="fcneBranchGenerate()"><span class="action-ico">✨</span><span><b>Training generieren</b><small>Nach MH-Schwerpunkt.</small></span><span class="go">›</span></button><button class="fcne-action-card" onclick="fcneBranchLibrary()"><span class="action-ico">📚</span><span><b>Übungssammlung</b><small>129 Originalübungen durchsuchen.</small></span><span class="go">›</span></button><button class="ep-btn fcne-backline" onclick="eplanHome()">‹ Zurück</button>'}

window.fcneMHUnits=async function(){await loadMH();hidePanels();const b=document.getElementById('epLibrary');b.classList.add('open');head('Komplette Trainingseinheiten','MH · 29 Einheiten');const themes=[...new Set(MH.units.map(u=>u.theme))].sort((a,b)=>a.localeCompare(b,'de'));b.innerHTML='<div class="fcne-mh-head"><span class="fcne-mh-pill">📘 29 EINHEITEN</span><h2>Komplette Trainings</h2></div><div class="fcne-mh-filters"><input id="mhUnitSearch" placeholder="Training suchen …" oninput="fcneRenderMHUnits()"><select id="mhUnitTheme" onchange="fcneRenderMHUnits()"><option>Alle Schwerpunkte</option>'+themes.map(t=>'<option>'+esc(t)+'</option>').join('')+'</select></div><div id="mhUnitCount" class="fcne-library-count"></div><div id="mhUnitList" class="fcne-mh-unit-list"></div><button class="ep-btn fcne-backline" onclick="fcneOpenBranch(\'mh\')">‹ Zurück zu MH</button>';fcneRenderMHUnits()};
window.fcneRenderMHUnits=function(){const q=(document.getElementById('mhUnitSearch')?.value||'').toLowerCase(),th=document.getElementById('mhUnitTheme')?.value||'Alle Schwerpunkte';const rows=MH.units.filter(u=>(th==='Alle Schwerpunkte'||u.theme===th)&&(!q||[u.title,u.theme,u.intro].join(' ').toLowerCase().includes(q)));document.getElementById('mhUnitCount').textContent=rows.length+' Trainingseinheiten gefunden';document.getElementById('mhUnitList').innerHTML=rows.map(u=>'<button class="fcne-mh-unit-card" onclick="fcneOpenMHUnit(\''+u.id+'\')"><span class="num">'+String(Number(u.id.slice(2))).padStart(2,'0')+'</span><span class="copy"><b>'+esc(u.title)+'</b><small>'+esc(u.theme)+' · '+u.exercise_count+' Originalübungen</small></span><span>›</span></button>').join('')};
function unitOverlay(){let n=document.getElementById('mhUnitOverlay');if(!n){n=document.createElement('section');n.id='mhUnitOverlay';n.className='exercise-detail';document.body.appendChild(n)}return n}
window.fcneCloseMHUnit=()=>{document.getElementById('mhUnitOverlay')?.classList.remove('open');document.body.style.overflow=''};
window.fcneOpenMHExerciseFromUnit=id=>{fcneCloseMHUnit();const e=DATA.find(x=>x.id===id);if(e)openExercise(DATA.indexOf(e))};
window.fcneOpenMHUnit=async function(id){await loadMH();const u=MH.units.find(x=>x.id===id);if(!u)return;const xs=DATA.filter(e=>e.fcneBranch==='mh'&&e.mhUnitId===id).sort((a,b)=>(a.mhOrder||0)-(b.mhOrder||0));const shown=xs.some(e=>e.category==='Ausklang'||/abschlussspiel/i.test(e.title||''))?xs:[...xs,MH.closing];const n=unitOverlay();n.innerHTML='<div class="detail-header"><button class="round-back" onclick="fcneCloseMHUnit()">‹</button><div class="detail-title"><strong>'+esc(u.title)+'</strong><small>MH · '+esc(u.theme)+'</small></div></div><div class="detail-content"><div class="mh-unit-intro">'+esc(u.intro||'Komplette Trainingseinheit')+'</div><div class="mh-unit-exercises">'+shown.map((e,k)=>'<div class="mh-unit-ex">'+(e.image?'<img src="'+esc(e.image)+'" alt="'+esc(e.title)+'" onclick="openZoom(this.src)">':'')+'<div class="mh-unit-ex-copy"><span class="stage">'+(k+1)+' · '+esc(e.mhStage||e.category)+'</span><h3>'+esc(e.title)+'</h3><button class="mh-open-ex" onclick="fcneOpenMHExerciseFromUnit(\''+e.id+'\')">Übung im Detail öffnen</button></div></div>').join('')+'</div><a class="mh-source-link" href="'+esc(u.url)+'" target="_blank">↗ Originaleinheit öffnen</a></div>';n.classList.add('open');document.body.style.overflow='hidden'};

const oldCompose=window.fcneBranchCompose;window.fcneBranchCompose=async function(){if((window.FCNE_ACTIVE_BRANCH||'sfv')!=='mh')return oldCompose?.apply(this,arguments);await loadMH();eplanClose?.();const start=window.__fcneOriginalStartWizard||window.startWizard;if(typeof start==='function'){start();draft.sourceBranch='mh';draft.environment='field';draft.notes=(draft.notes?draft.notes+' · ':'')+'Zweig: MH / fussballtraining.li';renderWizard?.()}};
const oldLib=window.fcneBranchLibrary;window.fcneBranchLibrary=async function(){if((window.FCNE_ACTIVE_BRANCH||'sfv')!=='mh')return oldLib?.apply(this,arguments);await loadMH();hidePanels();const b=document.getElementById('epLibrary');b.classList.add('open');head('Übungssammlung','MH · 129 Übungen');const themes=[...new Set(MH.units.map(u=>u.theme))].sort((a,b)=>a.localeCompare(b,'de'));b.innerHTML='<div class="fcne-mh-head"><span class="fcne-mh-pill">📚 129 ORIGINALÜBUNGEN</span><h2>MH-Übungssammlung</h2></div><div class="fcne-mh-filters"><input id="mhLibSearch" placeholder="Übung suchen …" oninput="fcneRenderMHLibrary()"><select id="mhLibTheme" onchange="fcneRenderMHLibrary()"><option>Alle Schwerpunkte</option>'+themes.map(t=>'<option>'+esc(t)+'</option>').join('')+'</select></div><div id="mhLibCount"></div><div id="mhLibList" class="fcne-library-list"></div><button class="ep-btn fcne-backline" onclick="fcneOpenBranch(\'mh\')">‹ Zurück zu MH</button>';fcneRenderMHLibrary()};
window.fcneRenderMHLibrary=function(){const q=(document.getElementById('mhLibSearch')?.value||'').toLowerCase(),th=document.getElementById('mhLibTheme')?.value||'Alle Schwerpunkte';const rows=DATA.filter(e=>e.fcneBranch==='mh'&&!e.mhGenericClosing&&(th==='Alle Schwerpunkte'||e.mhTheme===th)&&(!q||[e.title,e.mhStage,e.mhTheme,e.intro].concat((e.sections||[]).flat()).join(' ').toLowerCase().includes(q)));document.getElementById('mhLibCount').textContent=rows.length+' Übungen gefunden';document.getElementById('mhLibList').innerHTML=rows.map(e=>'<button class="fcne-lib-card" onclick="eplanClose();openExercise('+DATA.indexOf(e)+')">'+(e.image?'<img src="'+esc(e.image)+'" alt="">':'')+'<span><small class="fcne-source-pill">MH · '+esc(e.mhTheme)+'</small><b>'+esc(e.title)+'</b><small>'+esc(e.category)+' · '+esc(e.players||'variabel')+'</small></span><span class="arrow">›</span></button>').join('')};

const oldGen=window.fcneBranchGenerate;window.fcneBranchGenerate=async function(){if((window.FCNE_ACTIVE_BRANCH||'sfv')!=='mh')return oldGen?.apply(this,arguments);await loadMH();hidePanels();const b=document.getElementById('epAuto');b.classList.add('open');head('Training generieren','MH / fussballtraining.li');const themes=[...new Set(MH.units.map(u=>u.theme))].sort((a,b)=>a.localeCompare(b,'de'));b.innerHTML='<div class="fcne-mh-head"><span class="fcne-mh-pill">✨ MH GENERATOR</span><h2>Training nach MH-Schwerpunkt</h2></div><div class="fcne-auto-form"><label>Schwerpunkt</label><select id="mhGenTheme"><option value="Alle">Alle</option>'+themes.map(t=>'<option>'+esc(t)+'</option>').join('')+'</select><div class="fcne-auto-grid"><div><label>Dauer</label><select id="mhGenDuration"><option>60</option><option selected>75</option><option>90</option></select></div><div><label>Spieler</label><input id="mhGenPlayers" type="number" value="12" min="4" max="30"></div></div><button class="fcne-primary" onclick="fcneMHGenerate()">✨ MH-Training generieren</button></div><button class="ep-btn fcne-backline" onclick="fcneOpenBranch(\'mh\')">‹ Zurück zu MH</button>'};
window.fcneMHGenerate=function(){const th=document.getElementById('mhGenTheme')?.value||'Alle',target=Number(document.getElementById('mhGenDuration')?.value)||75,players=Number(document.getElementById('mhGenPlayers')?.value)||12;const units=MH.units.filter(u=>th==='Alle'||u.theme===th),u=units[Math.floor(Math.random()*units.length)];if(!u)return;const unitEx=DATA.filter(e=>e.fcneBranch==='mh'&&e.mhUnitId===u.id).sort((a,b)=>(a.mhOrder||0)-(b.mhOrder||0)),all=DATA.filter(e=>e.fcneBranch==='mh'&&!e.mhGenericClosing),sel={},used=new Set();function pick(ph){let a=unitEx.filter(e=>e.category===ph&&!used.has(e.id));if(!a.length)a=all.filter(e=>e.mhTheme===u.theme&&e.category===ph&&!used.has(e.id));if(!a.length)a=all.filter(e=>e.category===ph&&!used.has(e.id));const e=ph==='Fussball spielen'?a[a.length-1]:a[0];if(e)used.add(e.id);return e}PHASES.forEach(ph=>{const e=ph==='Ausklang'?(unitEx.find(x=>x.category==='Ausklang')||MH.closing):pick(ph);if(e)sel[ph]=e.id});draft={name:'MH – '+u.title,target,players,focus:u.theme,date:'',notes:'MH / fussballtraining.li · '+u.title,customDurations:{},selections:sel,sourceBranch:'mh',environment:'field',mhUnitId:u.id,mhUnitTitle:u.title};eplanClose?.();showScreen?.('wizard');if(typeof STEPS!=='undefined')wizardStep=STEPS.length-1;renderWizard?.()};

const oldOpenEx=window.openExercise;window.openExercise=function(i){const e=DATA[i];if(e?.fcneBranch!=='mh')return oldOpenEx?.apply(this,arguments);let n=document.getElementById('detail-'+i);if(!n){n=document.createElement('section');n.id='detail-'+i;n.className='exercise-detail';document.body.appendChild(n)}const sections=(e.sections||[]).map(s=>'<div class="sp-section"><h4>'+esc(s[0])+'</h4><p>'+esc(s[1])+'</p></div>').join('');n.innerHTML='<div class="detail-header"><button class="round-back" onclick="closeExercise()">‹</button><div class="detail-title"><strong>'+esc(e.title)+'</strong><small>MH / fussballtraining.li · '+esc(e.mhTheme||'')+'</small></div></div><div class="detail-content">'+(e.image?'<img class="detail-hero" src="'+esc(e.image)+'" onclick="openZoom(this.src)">':'')+'<div class="fcne-mh-note"><b>Quelle:</b> Originalübung von Martin Hasenpflug. Für E/F bei Bedarf vereinfachen.</div>'+sections+'<div class="detail-actions"><button class="primary" onclick="selectFromDetail(\''+e.id+'\')">✓ Für Training wählen</button></div><a class="mh-source-link" href="'+esc(e.source_url)+'" target="_blank">↗ Original öffnen</a></div>';n.classList.add('open');document.body.style.overflow='hidden'};

document.querySelectorAll('.app-version').forEach(el=>{if(/Version/i.test(el.textContent||''))el.textContent='Version 2.43 · MH Bibliothek · Build 2026.11.15'});
setTimeout(()=>window.eplanHome?.(),0);
})();
</script>
<script>window.FCNE_APP_VERSION='2.43 MH-LIBRARY';</script>'''

html=html.replace("</body>",css+"\n"+js+"\n</body>")
INDEX.write_text(html,encoding="utf-8")

sw=SW.read_text(encoding="utf-8")
sw=re.sub(r"const CACHE='[^']+';","const CACHE='fcne-training-v2.43-mh-library-20261115';",sw,count=1)
sw=sw.replace("const APP_SHELL=['./','./index.html','./manifest.webmanifest'];","const APP_SHELL=['./','./index.html','./manifest.webmanifest','./mh_library.json'];")
SW.write_text(sw,encoding="utf-8")

print(f"OK: 29 MH units, 129 MH exercises, {sum(bool(e.get('image')) for e in exs)} images; E2C 132 field / 45 hall")
