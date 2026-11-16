"""Selected official vacancy snapshots, not a census or historical panel."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import urllib.request
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
JOBS=[
('C','https://jobs.citi.com/job/irving/generative-ai-engineering-lead-senior-vice-president/287/102816963472'),
('C','https://jobs.citi.com/job/new-york/vice-president-generative-ai-technical-expert-data-science-and-artificial-intelligence-hybrid/287/102161054480'),
('C','https://jobs.citi.com/job/-/-/287/102161045008'),
('C','https://jobs.citi.com/job/new-york/senior-generative-ai-engineer/287/102161046336'),
('C','https://jobs.citi.com/job/-/-/287/94846498992'),
('C','https://jobs.citi.com/job/jersey-city/lead-generative-ai-python-engineer-vice-president/287/102161041056'),
('JPM','https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210780109'),
('JPM','https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210793628'),
('JPM','https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210788130'),
('JPM','https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210784217'),
('JPM','https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210803316')]
TAGS={'evaluation':r'evaluat|testing|validation|monitoring', 'workflow':r'workflow|stakeholder|business process|business objectives|integration',
      'data':r'data pipeline|data engineering|data quality|governance|data management',
      'python':r'\bPython\b','retrieval':r'\bRAG\b|retrieval.augmented','production':r'production|MLOps|CI/CD|deployment'}

def fetch_job(item):
    company,url=item;now=datetime.now(timezone.utc).isoformat();native=url.rstrip('/').split('/')[-1]
    req=urllib.request.Request(url,headers={'User-Agent':'Haojian Dui public research dui@szu.edu.cn'})
    path=ROOT/'data/raw'/f'job-{company}-{native}.json'
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    try:
        with urllib.request.urlopen(req,timeout=40) as response:raw=response.read()
        soup=BeautifulSoup(raw,'html.parser');structured=[]
        for s in soup.select('script[type="application/ld+json"]'):
            try:structured.append(json.loads(s.string or s.text))
            except json.JSONDecodeError:pass
        h=soup.find('h1');title=h.get_text(' ',strip=True) if h else None
        for x in soup(['script','style','nav','footer','header']):x.decompose()
        text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True)).strip()
        result={'company':company,'source_url':url,'retrieved_at':now,'native_url_id':native,'title':title,'text':text,'structured':structured,
                'collection_status':'retrieved' if title and len(text)>1500 else 'requires_rendered_source'}
    except Exception as e:result={'company':company,'source_url':url,'retrieved_at':now,'native_url_id':native,'collection_status':'fetch_failure','error':str(e)}
    path.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    return result

def main():
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch_job,JOBS))
    for r in rows:
        text=r.get('text','');print(r['company'],r['native_url_id'],r['collection_status'],r.get('title'),len(text))
        if r['collection_status']=='retrieved':
            print('REQ',re.findall(r'(?:Job Req Id:|Job Identification|Primary Location|Date posted|Posted on|Salary Range)[^.!?]{0,100}',text)[:6])
    (ROOT/'data/raw/bank-job-collection.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
