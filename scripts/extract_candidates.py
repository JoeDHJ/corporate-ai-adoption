"""Create a local review queue of short, contiguous AI evidence spans."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from corporate_ai.classify import AI,classify

ROOT=Path(__file__).resolve().parents[1]
def main():
    candidates=[]
    for file in sorted((ROOT/'data/raw').glob('*.json')):
        if file.stem=='collection-log':continue
        d=json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(d,dict) or 'pages' not in d:continue
        seen=set(); doc=[]
        for page,text in enumerate(d['pages'],1):
            for m in re.finditer(r'[^.!?]+[.!?]',text):
                sentence=m.group().strip()
                if not AI.search(sentence) or not 8<=len(sentence.split())<=65 or sentence in seen:continue
                seen.add(sentence)
                row=dict(source_id=d['source_id'],candidate_id=len(doc),excerpt=sentence,page=page,start_char=m.start()+len(m.group())-len(m.group().lstrip()),end_char=m.end(),**classify(sentence))
                doc.append(row)
        candidates.extend(doc)
    (ROOT/'data/raw/candidates.json').write_text(json.dumps(candidates,indent=2,ensure_ascii=False),encoding='utf-8')
    for sid in sorted({x['source_id'] for x in candidates}):
        rows=[x for x in candidates if x['source_id']==sid]
        print('\n'+sid)
        # Early report spans plus first few people/pilot/internal signals.
        chosen=rows[:6]+[x for x in rows[6:] if x['scope']=='internal' or x['label'] in ['pilot','planned','hiring_innovation']][:6]
        for x in chosen:print(x['candidate_id'],x['label'],x['scope'],f"p{x['page']}",x['excerpt'])
if __name__=='__main__':main()
