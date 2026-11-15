from pathlib import Path
text=Path("index.html").read_text(encoding="utf-8")

def extract_function(name):
    needle="function "+name+"("
    pos=text.find(needle)
    if pos<0:
        print(name+": NOT FOUND"); return
    start=text.find("{",pos)
    depth=0; quote=None; esc=False; template=False
    for i in range(start,len(text)):
        ch=text[i]
        if quote:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==quote: quote=None
            continue
        if ch in ("'",'"','`'):
            quote=ch; continue
        if ch=="{": depth+=1
        elif ch=="}":
            depth-=1
            if depth==0:
                print("\n### "+name+"\n"+text[pos:i+1]+"\n")
                return
    print(name+": unterminated")

for n in ["validateStep","wizardNext","wizardBack","chooseExercise"]:
    extract_function(n)

# Also print next button markup and initial wizard state variables.
for needle in ['id="nextBtn"','let wizardStep','const STEPS','let draft=']:
    p=text.find(needle)
    print("\n### "+needle)
    print(text[max(0,p-500):p+1200] if p>=0 else "NOT FOUND")
