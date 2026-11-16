"""Build the bank case from local official texts and explicit assistant review.

All candidate locations are inventoried. Only short reviewed spans are published.
Absence of a reviewed deployment is unknown, not a negative adoption observation.
"""
from datetime import datetime, timezone
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from corporate_ai.measurement import BANK_AI,axes,bank_summary
from corporate_ai.benchmark import benchmark
from corporate_ai.vacancies import import_vacancies,summarize
DATA=ROOT/'src/corporate_ai/data'

# Indexes use the complete 8–80-word candidate queue, including duplicate spans.
# Explicit actors/stages are an assistant reference judgment, never human labels.
REV={
 'BAC-2023':[(6,'deployment',['internal','customer'],['deployed'],False,'Customer-service operation uses Erica.'),(7,'pilot',['internal'],['pilot'],False,'Explicit coding pilot; not a scaled rollout.')],
 'BAC-2024':[(0,'deployment',['customer'],['deployed'],False,'CashPro Chat use is customer-facing; inquiry share is issuer-reported.'),(6,'deployment',['internal'],['deployed'],False,'Training tools are offered in financial and contact centers.')],
 'C-2023':[(0,'risk',['unspecified'],[],True,'Competitive risk does not establish deployment.'),(1,'risk',['unspecified'],[],True,'Conditional control warning; no completed use stated.')],
 'C-2024':[(1,'deployment',['internal'],['deployed'],False,'Completed platform rollout, issuer reports colleague reach.'),(3,'planned',['internal'],['planned'],False,'Workforce ambition is not an attained outcome.')],
 'C-2025':[(6,'deployment',['internal'],['deployed'],False,'Internal coding use; reported capacity is not independently measured cash saving.'),(7,'deployment',['internal','customer'],['deployed'],False,'Named service and trade-confirmation workflows are in use.')],
 'JPM-2023':[(6,'deployment',['internal'],['deployed'],False,'Predictive AI production use; not a claim of GenAI scale.'),(7,'pilot',['internal'],['pilot'],False,'GenAI potential is being explored.')],
 'JPM-2024':[(7,'deployment',['internal'],['deployed'],False,'Completed LLM Suite launch; reach is access, not active use.')],
 'JPM-2025':[],
 'WFC-2023':[(0,'deployment',['customer'],['deployed'],False,'Fargo is a customer-facing release.'),(3,'deployment',['internal','customer'],['deployed'],True,'Explicit current use and uncertainty coexist in the same statement.')],
 'WFC-2024':[(1,'deployment',['internal','customer'],['deployed'],True,'Repeated use-plus-risk disclosure is not a new adoption event.')],
 'WFC-2025':[(2,'deployment',['internal','customer'],['deployed'],False,'Established models across risk, marketing and customer assistant.'),(6,'deployment',['internal'],['deployed'],False,'Microsoft Copilot tools have been deployed internally for GenAI experience; this span does not establish agentic deployment.')]
}

def save(name,x):(DATA/(name+'.json')).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

def main():
    sources=json.loads((DATA/'bank-sources.json').read_text(encoding='utf-8'));legacy=json.loads((DATA/'evidence.json').read_text(encoding='utf-8'))
    candidates=[];inventory=[];reviewed=[]
    for source in sources:
        d=json.loads((ROOT/'data/raw'/(source['source_id']+'.json')).read_text(encoding='utf-8'));doc=[];negative=[];term_count=0
        for page,text in enumerate(d['pages'],1):
            term_count+=len(list(BANK_AI.finditer(text)))
            for m in re.finditer(r'[^.!?]+[.!?]',text):
                sentence=m.group().strip();start=m.start()+len(m.group())-len(m.group().lstrip())
                row={'source_id':source['source_id'],'excerpt':sentence,'page':page,'start_char':start,'end_char':m.end()}
                if BANK_AI.search(sentence) and 8<=len(sentence.split())<=80:
                    doc.append({**row,'candidate_id':len(doc),'automatic_axes':axes(sentence)})
                elif not BANK_AI.search(sentence) and 12<=len(sentence.split())<=24 and re.search(r'\b(?:net income|revenue|dividend|interest rates|capital|employees)\b',sentence,re.I):negative.append(row)
        candidates.extend(doc)
        inventory.append({'source_id':source['source_id'],'pages_parsed':len(d['pages']),'pages_with_text':sum(bool(t) for t in d['pages']),
            'ai_lexicon_hits':term_count,'eligible_sentence_candidates':len(doc),'scanned_characters':sum(map(len,d['pages'])),
            'eligibility':'Sentence-like punctuation spans, 8–80 words, bank AI lexicon. Length/lexicon limits and PDF layout can miss relevant context; not exhaustive adoption coding.'})
        entries=REV.get(source['source_id'],[])
        if source['source_id']=='JPM-2025':
            matches=[x for x in doc if '65,000' in x['excerpt'] and 'LLM Suite' in x['excerpt']]
            if matches:entries=[(matches[0]['candidate_id'],'deployment',['internal'],['deployed'],False,'CIB active users; not comparable to FY2024 firmwide access count.')]
        for idx,label,actors,stages,risk,reason in entries:
            row=doc[idx];reviewed.append({**row,**source,'evidence_id':'BANK-'+source['source_id']+'-'+str(idx),
                'status':'estimated','review_label':label,'review_scope':'internal' if 'internal' in actors else 'customer_or_product' if 'customer' in actors else 'unspecified',
                'review_reason':reason,'review_axes':{**axes(row['excerpt']),'actors':actors,'stages':stages or ['not_established'],'risk':risk},
                'event_date':None,'event_time_note':'Disclosure fiscal label retained; exact event date not established by this span.',
                'locator':f"physical PDF p{row['page']}; normalized chars {row['start_char']}–{row['end_char']}",
                'review_process':'Single AI assistant reference coding, 2026-11-16'})
        if negative:
            row=negative[0];reviewed.append({**row,**source,'evidence_id':'BANK-'+source['source_id']+'-NEG','status':'estimated',
                'review_label':'none','review_scope':'unspecified','review_reason':'Ordinary financial disclosure; no AI use claim in this span.',
                'review_axes':axes(row['excerpt']),'event_date':None,'event_time_note':'Not an adoption observation.',
                'locator':f"physical PDF p{row['page']}; normalized chars {row['start_char']}–{row['end_char']}",'review_process':'Single AI assistant reference coding, 2026-11-16'})
    registry={s['source_id']:s for s in json.loads((DATA/'sources.json').read_text(encoding='utf-8'))}
    evaluation_rows=[{**r,'company':registry[r['source_id']]['company'],'period':registry[r['source_id']]['period']} for r in legacy]
    seen={' '.join(r['excerpt'].lower().split()) for r in evaluation_rows}
    for r in reviewed:
        key=' '.join(r['excerpt'].lower().split())
        if key not in seen:evaluation_rows.append(r);seen.add(key)
    # Keep complete queues local; public inventory exposes all locations, no full-text redistribution.
    (ROOT/'data/raw/bank-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False),encoding='utf-8')
    locations=[{k:v for k,v in r.items() if k!='excerpt'} for r in candidates]
    axis_diagnostic={}
    for axis in ['actors','stages','risk']:
        matches=lambda a,b:sorted(a)==sorted(b) if isinstance(a,list) else a==b
        errors=[{'evidence_id':r['evidence_id'],'automatic':axes(r['excerpt'])[axis],'reference':r['review_axes'][axis]}
                for r in reviewed if not matches(axes(r['excerpt'])[axis],r['review_axes'][axis])]
        axis_diagnostic[axis]={'n':len(reviewed),'exact_matches':len(reviewed)-len(errors),'errors':errors}
    save('bank-case',{'schema_version':'portfolio.v1','as_of':'2026-11-16','status':'estimated','sources':sources,
        'source_id':'BANK-COHORT-V2','source_url':None,'retrieved_at':'2026-11-16','source_vintage':'Annual reports FY2023–FY2025',
        'geography':'Global consolidated US-listed banking groups','unit_of_observation':'selected annual-report statement','period':'FY2023–FY2025','currency':None,'price_year':None,
        'coverage':{'target_banks':['JPM','BAC','C','WFC'],'periods':['2023','2024','2025'],'complete_reports':len(sources),
        'missing_reports':[{'source_id':'BAC-2025','collection_status':'fetch_failure','reason':'Official PDF download incomplete from SEC; issuer CDN returned HTTP 403. Unknown, not no adoption.',
                            'source_url':'https://www.sec.gov/Archives/edgar/data/70858/000007085826000209/bofaannualreport2025.pdf'}],
        'selection':'Four large US-listed bank groups with public annual reports; purposive and conditional on access. Goldman Sachs expansion attempted but official CDN returned 403; excluded from this release cohort, not assigned a negative outcome.'},
        'reviewed':reviewed,'candidate_locations':locations,'inventory':inventory,'company_periods':bank_summary(sources,reviewed,inventory),
        'evaluation':benchmark(evaluation_rows),'evaluation_row_ids':[r['evidence_id'] for r in evaluation_rows],
        'axis_diagnostic':axis_diagnostic,'axis_reference_note':'Actors, stages and risk have assistant reference judgments. Technology, people-investment and numeric-claim fields are rule-derived, not independently labeled reference outcomes. These diagnostics reuse development material.',
        'measurement_note':'Independent actor, stage, technology, people and risk axes. Reviewed excerpts establish statements only; candidate hits do not estimate adoption prevalence. Repeated disclosures do not establish new events.'})
    print('Bank case:',len(sources),'reports',len(candidates),'candidate locations',len(reviewed),'review spans',len(evaluation_rows),'diagnostic rows')
    jobs=json.loads((ROOT/'data/raw/bank-job-collection.json').read_text(encoding='utf-8'));snapshots=[]
    tags={'evaluation':r'evaluat|testing|validation|monitoring','workflow':r'workflow|stakeholder|business process|business objectives|integration',
        'data':r'data pipeline|data engineering|data quality|governance|data management','python':r'\bPython\b','retrieval':r'\bRAG\b|retrieval.augmented','production':r'production|MLOps|CI/CD|deployment'}
    for j in jobs:
        if j['collection_status']!='retrieved':continue
        t=j['text'];desc=t.split('Responsibilities:',1)[-1].split('Job Family Group:',1)[0]
        jobid=re.search(r'Job Req Id:\s*(\d+)',t).group(1)
        loc=re.search(r'Location\(s\):\s*(.*?)\s*Job Type:',t)
        pay=re.search(r'Primary Location Full Time Salary Range:\s*([\d$,.]+)\s*-\s*([\d$,.]+)',t)
        snapshots.append({'source_id':'CITI-JOB-'+jobid,'source_url':j['source_url'],'retrieved_at':j['retrieved_at'],
            'source_vintage':'Official vacancy page snapshot 2026-11-16','period':'2026-11-16','company_id':'US:SEC-CIK:0000831001','company':'C',
            'job_id':jobid,'source_native_url_id':j['native_url_id'],'title':j['title'],'geography':loc.group(1) if loc else 'See official page',
            'seniority':'Senior Vice President' if 'Senior Vice President' in j['title'] else 'Vice President' if 'Vice President' in j['title'] else 'Not standardized',
            'skills':[tag for tag,p in tags.items() if re.search(p,desc,re.I)],'skill_taxonomy':'corporate-ai-capabilities','skill_taxonomy_version':'2.0',
            'annual_base_pay_range':[float(x.replace('$','').replace(',','')) for x in pay.groups()] if pay else None,
            'pay_currency':'USD' if pay else None,'pay_note':'Primary-location advertised base range; not total compensation; null means no parsed range.',
            'collection_status':'retrieved','requirement_summary':'Rule-coded capability requirements from the official job description; verify the role and seniority on the linked page.'})
    save('bank-vacancies',snapshots)
    parsed=import_vacancies(DATA/'bank-vacancies.json')
    save('bank-vacancies',parsed)
    save('vacancy-coverage',{'schema_version':'portfolio.v1','source_id':'BANK-VACANCY-COLLECTION-V2','source_url':None,'retrieved_at':'2026-11-16','source_vintage':'Official job pages accessed 2026-11-16',
        'geography':'Selected Citi and JPMorgan official career sites','unit_of_observation':'attempted vacancy-page collection','period':'2026-11-16','currency':None,'price_year':None,'status':'estimated',
        'snapshot_date':'2026-11-16','attempted_pages':len(jobs),'retrieved_pages':len(parsed),'records':[
        {k:j.get(k) for k in ['company','source_url','native_url_id','retrieved_at','collection_status','error']} for j in jobs],
        'summary':summarize(parsed),'selection':'Targeted AI-role searches on official Citi and JPMorgan sites. Only readable Citi pages are in the analytical sample; no bank comparison, hiring growth or skill-population inference.'})

if __name__=='__main__':main()
