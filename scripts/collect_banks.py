"""Pinned bank annual reports; retain complete normalized text locally only."""
import concurrent.futures
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from collect_reports import fetch, RAW

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'src/corporate_ai/data/bank-sources.json'
BANKS = {'JPM': ('JPMorgan Chase', '0000019617'), 'BAC': ('Bank of America', '0000070858'),
         'C': ('Citigroup', '0000831001'),
         'WFC': ('Wells Fargo', '0000072971')}

def main():
    legacy = json.loads((ROOT/'src/corporate_ai/data/sources.json').read_text())
    sources = [s for s in legacy if s['company'] in ['JPM', 'BAC']]
    sources.append({**next(s for s in sources if s['company']=='JPM'), 'source_id':'JPM-2025',
                    'source_url':'https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/annualreport-2025.pdf', 'period':'2025', 'source_vintage':'FY2025'})
    sources.append({**next(s for s in sources if s['company']=='BAC'), 'source_id':'BAC-2025',
                    'source_url':'https://d1io3yog0oux5.cloudfront.net/_c88539a6717957514910928c75e7c025/bankofamerica/db/867/10497/annual_report/BAC%2B2025%2BAnnual%2BReport.pdf', 'period':'2025', 'source_vintage':'FY2025'})
    for company in ['C','WFC']:
        for year in [2023,2024,2025]:
            if company=='C':
                url=(f'https://www.citigroup.com/rcs/citigpa/storage/public/Annual_Report/{year}/citi-{year}-annual-report.pdf' if year==2025 else ('https://www.citigroup.com/rcs/citigpa/storage/public/Citi-2023-Annual-Report.pdf' if year==2023 else f'https://www.citigroup.com/rcs/citigpa/storage/public/citi-{year}-annual-report.pdf'))
            elif company=='WFC':
                url=f'https://www.wellsfargo.com/assets/pdf/about/investor-relations/annual-reports/{year}-annual-report.pdf'
            sources.append(dict(source_id=f'{company}-{year}',company=company,company_name=BANKS[company][0],
                company_id='US:SEC-CIK:'+BANKS[company][1],industry='Banking',source_url=url,
                source_vintage=f'FY{year}',period=str(year),geography='Global consolidated; US-listed issuer',
                unit_of_observation='company annual report',status='observed',schema_version='portfolio.v1',
                currency=None,price_year=None,access='Official public annual report',redistribution='Short excerpts only; issuer rights retained',
                source_format='pdf',source_native_id=f'{company}-{year}'))
    errors=[]; results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(fetch,s):s for s in sources}
        for future in concurrent.futures.as_completed(jobs):
            s=jobs[future]
            try:
                d=future.result()
                results.append({**s,**{k:d[k] for k in ['retrieved_at','bytes']},'parsed_pages':len(d['pages']),
                    'source_native_id':s['source_id'],
                    'fiscal_year_end':s['period']+'-12-31','document_scope':'Annual report including shareholder narrative',
                    'parser':'pypdf normalized whitespace; physical page and exact character offsets'})
            except Exception as e:errors.append({'source_id':s['source_id'],'error':str(e)})
    DEST.write_text(json.dumps(sorted(results,key=lambda r:(r['company'],r['period'])),indent=2)+'\n')
    (RAW/'bank-collection-log.json').write_text(json.dumps(errors,indent=2))
    print(json.dumps({'reports':len(results),'errors':errors},indent=2),flush=True)
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
