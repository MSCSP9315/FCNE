from pathlib import Path
import re
text=Path("index.html").read_text(encoding="utf-8")
for term in ["function wizardNext","function validateStep","function renderWizard","fcneBranchPool()","wizardStep++","id=\"wizardBody\"","Weiter"]:
    print("\n###",term)
    for m in re.finditer(re.escape(term),text):
        a=max(0,m.start()-1800);b=min(len(text),m.end()+4200)
        print(text[a:b].replace("\n"," ")[:6500])
        print("\n---")
