"""Fetch the pinned official reports. Raw reports stay local and ignored by git."""
import concurrent.futures
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import urllib.request
import ssl
import truststore
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
REGISTRY = ROOT / 'src/corporate_ai/data/sources.json'

def normalize(text):
    return re.sub(r'\s+', ' ', text.replace('\u00ad', '').replace('\u200b', '')).strip()

def fetch(source):
    sid = source['source_id']
    cached = RAW / (sid + '.json')
    if cached.exists():
        previous=json.loads(cached.read_text(encoding='utf-8'))
        if previous['source_url']==source['source_url']:return previous
    req = urllib.request.Request(source['source_url'], headers={'User-Agent':'Haojian Dui public research dui@szu.edu.cn'})
    with urllib.request.urlopen(req, timeout=60, context=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)) as response:
        raw = response.read()
        final_url = response.url
    if raw[:4] == b'%PDF':
        pages = [normalize(p.extract_text()) for p in PdfReader(io.BytesIO(raw)).pages]
    else:
        soup = BeautifulSoup(raw, 'html.parser')
        for tag in soup(['script','style','ix:header']): tag.decompose()
        pages = [normalize(soup.get_text(' ', strip=True))]
    if sum(map(len,pages)) < 5000:
        raise ValueError(f'{sid}: report text too short')
    result = {**source, 'retrieved_at':datetime.now(timezone.utc).isoformat(), 'bytes':len(raw), 'resolved_url':final_url, 'pages':pages}
    cached.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    print(f'{sid}: {len(pages)} pages / {len(raw)} bytes',flush=True)
    return result

def main():
    RAW.mkdir(parents=True,exist_ok=True)
    sources=json.loads(REGISTRY.read_text(encoding='utf-8'))
    results=[]; errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(fetch,s):s for s in sources}
        for future in concurrent.futures.as_completed(jobs):
            try:results.append(future.result())
            except Exception as exc:errors.append({'source_id':jobs[future]['source_id'],'error':str(exc)});print(errors[-1],flush=True)
    (RAW/'collection-log.json').write_text(json.dumps({'success':[r['source_id'] for r in results],'errors':errors},indent=2),encoding='utf-8')
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
