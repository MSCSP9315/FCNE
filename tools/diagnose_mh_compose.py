from pathlib import Path
import re
text=Path("index.html").read_text(encoding="utf-8")
terms=["fcneBranchCompose","__fcneOriginalStartWizard","startWizard","fcneBranchPool","sourceBranch='mh'","sourceBranch=\"mh\""]
for term in terms:
    print("\n###",term)
    for m in re.finditer(re.escape(term),text):
        a=max(0,m.start()-900);b=min(len(text),m.end()+1800)
        print(text[a:b].replace("\n"," ")[:3200])
        print("\n---")
