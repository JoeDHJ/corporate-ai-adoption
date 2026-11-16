"""Simple transparent keyword ranking shared by the CLI task benchmark."""
import re
def rank_evidence(rows,query):
    terms=re.findall(r'[a-z0-9]+',query.lower())
    if not terms:return list(rows)
    scored=[(sum(r['excerpt'].lower().count(t) for t in terms),i,r) for i,r in enumerate(rows)]
    return [r for score,_,r in sorted(scored,key=lambda x:(-x[0],x[1])) if score>0]
