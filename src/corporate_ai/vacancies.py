"""Import permitted vacancy snapshots without inventing historical coverage."""
from collections import Counter
from datetime import date
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

REQUIRED=('source_id','source_url','retrieved_at','source_vintage','geography','period','company_id','job_id','title')
def import_vacancies(path):
    path=Path(path)
    if path.suffix.lower()=='.json':rows=json.loads(path.read_text(encoding='utf-8'))
    elif path.suffix.lower()=='.csv':
        with path.open(newline='',encoding='utf-8-sig') as stream:rows=list(csv.DictReader(stream))
    else:raise ValueError('vacancy input must be CSV or JSON')
    if not isinstance(rows,list) or not rows:raise ValueError('vacancy snapshot must be a nonempty list')
    seen=set();out=[]
    for i,r in enumerate(rows,1):
        if not isinstance(r,dict) or any(not isinstance(r.get(k),str) or not r[k].strip() for k in REQUIRED):raise ValueError(f'vacancy row {i}: missing metadata')
        date.fromisoformat(r['period']);date.fromisoformat(r['retrieved_at'][:10])
        if urlparse(r['source_url']).scheme!='https' or not urlparse(r['source_url']).netloc:raise ValueError('vacancy source must be an HTTPS URL')
        key=(r['company_id'],r['job_id'],r['period'])
        if key in seen:raise ValueError('duplicate company/job/snapshot period')
        seen.add(key)
        skills=r.get('skills')
        if isinstance(skills,str):skills=[s.strip() for s in skills.split(';') if s.strip()] or None
        if skills is not None and (not isinstance(skills,list) or any(not isinstance(s,str) or not s.strip() for s in skills)):raise ValueError('skills must be a list, semicolon-delimited string, or null')
        if skills is not None and any(not isinstance(r.get(k),str) or not r[k].strip() for k in ['skill_taxonomy','skill_taxonomy_version']):raise ValueError('skill tags require taxonomy and version')
        out.append({**r,'skills':sorted(set(skills)) if skills is not None else None,'schema_version':'portfolio.v1','unit_of_observation':'selected public vacancy snapshot','currency':None,'price_year':None,'status':'observed','skill_coding_status':'estimated'})
    return out

def summarize(rows):
    taxonomies={(r.get('skill_taxonomy'),r.get('skill_taxonomy_version')) for r in rows if r['skills'] is not None}
    if len(taxonomies)>1:raise ValueError('skill shares require one taxonomy and version; summarize coding systems separately')
    summaries=[]
    for period in sorted({r['period'] for r in rows}):
        sample=[r for r in rows if r['period']==period];known=[r for r in sample if r['skills'] is not None]
        counts=Counter(s for r in known for s in r['skills'])
        summaries.append({'period':period,'observed_selected_postings':len(sample),'postings_with_skill_tags':len(known),'postings_missing_skill_tags':len(sample)-len(known),'skill_counts':dict(counts),'skill_share_among_tagged_postings':{s:n/len(known) for s,n in counts.items()},'coverage':'Selected snapshots; external labor demand, not employee stock. Compare periods only after verifying stable employer/source coverage.'})
    return summaries
