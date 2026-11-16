import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for path in sorted((ROOT/'data/raw').glob('*.json')):
    if not re.fullmatch(r'(JPM|BAC|C|WFC)-20\d\d',path.stem):continue
    d=json.loads(path.read_text(encoding='utf-8'));out=[]
    for p,text in enumerate(d['pages'],1):
        for m in re.finditer(r'[^.!?]+[.!?]',text):
            t=m.group().strip()
            if re.search(r'\bAI\b|artificial intelligence|machine learning|LLM Suite|Citi Assist|Citi Stylus|\bErica\b|(?<!Wells )\bFargo\b',t,re.I) and 8<=len(t.split())<=80:
                out.append((len(out),p,t))
    print('\n'+path.stem+' candidates '+str(len(out)))
    for i,p,t in out[:9]:print(i,'p'+str(p),t)
