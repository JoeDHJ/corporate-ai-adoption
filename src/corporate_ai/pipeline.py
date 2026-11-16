"""Offline analysis and versioned exports; only packaged public inputs are needed."""
from collections import Counter
import csv
from copy import deepcopy
from importlib.resources import files
import json
from pathlib import Path
from .classify import LABELS, classify, baseline, evaluate
from .strategy import compare

META=('source_id','source_url','retrieved_at','source_vintage','geography','unit_of_observation','period','currency','price_year','schema_version','status')

def load(name):
    return json.loads(files('corporate_ai').joinpath('data',name+'.json').read_text(encoding='utf-8'))

def validate_evidence(evidence,sources):
    if not evidence:raise ValueError('evidence must not be empty')
    ids=set(); registry={s['source_id']:s for s in sources}
    for r in evidence:
        for key in ['evidence_id','source_id','excerpt','review_label','review_scope','review_reason','locator']:
            if not isinstance(r.get(key),str) or not r[key].strip():raise ValueError(f'missing or invalid {key}')
        if r['evidence_id'] in ids:raise ValueError('duplicate evidence ID')
        ids.add(r['evidence_id'])
        if r['source_id'] not in registry:raise ValueError('unknown source ID')
        if r['review_label'] not in LABELS:raise ValueError('invalid review label')
        if r['review_scope'] not in ['internal','customer_or_product','unspecified']:raise ValueError('invalid scope')
    return evidence

def analyze(evidence=None):
    sources=load('sources'); evidence=load('evidence') if evidence is None else evidence
    validate_evidence(evidence,sources)
    registry={s['source_id']:s for s in sources}; enriched=[]
    for r in evidence:
        source=registry[r['source_id']]
        enriched.append({**r,**{k:source[k] for k in META},'company':source['company'],'company_id':source['company_id'],'industry':source['industry'],'source_format':source['source_format'],'source_status':'observed','status':'estimated','classifier':classify(r['excerpt']),'baseline_label':baseline(r['excerpt'])})
    firm_year=[]
    for source in sources:
        spans=[r for r in enriched if r['source_id']==source['source_id']]
        firm_year.append({**{k:source[k] for k in META},'status':'estimated','company':source['company'],'company_name':source['company_name'],'company_id':source['company_id'],'industry':source['industry'],'reviewed_spans':len(spans),'labels':dict(Counter(r['review_label'] for r in spans)),'internal_deployment_evidence_ids':[r['evidence_id'] for r in spans if r['review_label']=='deployment' and r['review_scope']=='internal'],'coverage_note':'Selected evidence spans, not exhaustive document coding. No matching internal deployment span means unknown adoption, not no adoption.'})
    scenario=load('scenario'); strategies=compare(scenario)
    sensitivity=[]
    for success in [.5,.65,.8,.95]:
        s=deepcopy(scenario)
        for skill in s['skills']:skill['routes']['train']['success_rate']=success
        sensitivity.append({'training_success':success,**compare(s)['mixed']})
    totals=Counter(r['review_label'] for r in enriched)
    reference=deepcopy(scenario);reference['upfront_budget']=2000000
    hiring_reference=compare(reference)['hiring_only']
    value_sensitivity=[]
    for value in [30000,60000,120000,180000]:
        s=deepcopy(scenario);s['annual_value_per_capability']=value
        value_sensitivity.append({'annual_value_per_capability':value,**compare(s)['mixed']})
    return {'schema_version':'portfolio.v1','version':'1.0.0','as_of':'2026-11-16','sources':sources,'evidence':enriched,'company_periods':firm_year,'evaluation':evaluate(evidence),'labor':load('labor'),'workforce':load('workforce'),'jobs':load('jobs'),'scenario':scenario,'strategies':strategies,'sensitivity':sensitivity,'value_sensitivity':value_sensitivity,'hiring_reference':{'budget_relaxation':2000000,'note':'Comparison only: hiring-only policy with relaxed upfront budget, not feasible under the base cash cap.','result':hiring_reference},'summary':{'companies':len({s['company'] for s in sources}),'company_periods':len(sources),'reviewed_spans':len(evidence),'review_labels':dict(totals),'internal_deployment_company_periods':sum(bool(r['internal_deployment_evidence_ids']) for r in firm_year),'review_process':'Single AI assistant applied a written rubric to actual source spans. No independent human labels or held-out validation. Baseline and rule metrics are descriptive agreement on this selected set.'}}

def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

def scenario_output(inputs,results):
    return {**{k:inputs.get(k) for k in META},'schema_version':'portfolio.v1','status':'scenario','inputs':inputs,'results':results}

def export(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True); data=analyze()
    for name,value in [('portfolio.v1',data),('evidence',data['evidence']),('company-periods',data['company_periods']),('evaluation',data['evaluation']),('labor',data['labor']),('workforce',data['workforce']),('strategy',scenario_output(data['scenario'],data['strategies'])),('sensitivity',scenario_output(data['scenario'],{'training_attainment':data['sensitivity'],'annual_value':data['value_sensitivity'],'hiring_reference':data['hiring_reference']}))]:write_json(out/(name+'.json'),value)
    with (out/'evidence.csv').open('w',newline='',encoding='utf-8') as stream:
        fields=['evidence_id','company','period','review_label','review_scope','excerpt','source_url','locator']
        writer=csv.DictWriter(stream,fields,extrasaction='ignore');writer.writeheader();writer.writerows(data['evidence'])
    return data

def dashboard(data,path):
    root=files('corporate_ai').joinpath('web')
    template=root.joinpath('index.html').read_text(encoding='utf-8')
    # Protect an inline JSON script against source text containing HTML end tags.
    encoded=json.dumps(data,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=template.replace('/*__STYLE__*/',root.joinpath('style.css').read_text(encoding='utf-8')).replace('/*__APP__*/',root.joinpath('app.js').read_text(encoding='utf-8')).replace('__DATA__',encoded)
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(html,encoding='utf-8')
