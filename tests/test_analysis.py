import subprocess
from copy import deepcopy
import pytest
from corporate_ai.classify import classify, evaluate
from corporate_ai.pipeline import analyze, dashboard, load, validate_evidence
from corporate_ai.strategy import cashflows, solve, validate

@pytest.mark.parametrize('text,label',[
('Our employees are using AI tools.','deployment'),('We are piloting AI in coding.','pilot'),
('We plan to invest in AI.','planned'),('We hired AI talent.','hiring_innovation'),
('AI has transformative potential.','promotional'),('AI introduces material risks.','risk'),
('We do not use AI.','risk'),('A statement without the keyword.','none'),
('Creative Cloud paid plans include AI-powered features.','deployment')])
def test_taxonomy_edges(text,label):assert classify(text)['label']==label

def test_exact_scenario_cashflows():
    s=load('scenario');s.update(horizon_months=12,deadline_months=6,annual_discount_rate=0,annual_value_per_capability=1200)
    k=deepcopy(s['skills'][0])
    for r in k['routes'].values():r.update(capacity=0,upfront_cost=0,annual_recurring_cost=0)
    k['routes']['train'].update(capacity=2,success_rate=.5,ready_month=2,upfront_cost=10,annual_recurring_cost=12)
    k['demand']=1;s['skills']=[k]
    result=solve(s)
    assert result['route_counts']==dict(train=2,redeploy=0,hire=0)
    assert result['upfront_cost']==20
    assert result['pv_cost']==44  # upfront 20 + two candidates * annual cost 12
    assert result['npv']==956  # 10 productive months * 100 less cost 44
    assert result['cashflows'][:4]==[-20,-2,-2,98]
    assert result['undiscounted_payback_month']==3

def test_discount_timing():
    s=load('scenario');r=cashflows(s,s['skills'][0],(0,0,1))
    expected=-24000+sum((-12500+(15000 if m>3 else 0))/(1.08**(m/12)) for m in range(1,37))
    assert r['npv']==pytest.approx(expected)

def test_optimizer_against_explicit_choices():
    s=load('scenario');s['skills']=s['skills'][:1];s['skills'][0]['demand']=2;s['upfront_budget']=30000
    for r in s['skills'][0]['routes'].values():r['capacity']=2
    candidates=[]
    for a in range(3):
        for b in range(3):
            for c in range(3):
                if .8*a+.9*b+c>=2 and 9000*a+5000*b+24000*c<=30000:
                    pv=9000*a+5000*b+24000*c+sum((1000*a+3500*b+12500*c)/1.08**(m/12) for m in range(1,37))
                    candidates.append(pv)
    assert solve(s)['pv_cost']==pytest.approx(min(candidates))

def test_constraints_and_zero_demand():
    s=load('scenario');s['upfront_budget']=0
    assert not solve(s)['feasible']
    s=load('scenario')
    for k in s['skills']:k['demand']=0
    r=solve(s);assert r['upfront_cost']==r['pv_cost']==r['npv']==0
    assert r['route_counts']==dict(train=0,redeploy=0,hire=0)
    s=load('scenario');s['deadline_months']=1
    assert not solve(s)['feasible']

@pytest.mark.parametrize('key,value',[('horizon_months',0),('deadline_months',40),('upfront_budget',-1),('annual_discount_rate',float('nan')),('annual_value_per_capability',True),('skills',[])])
def test_invalid_scenarios(key,value):
    s=load('scenario');s[key]=value
    with pytest.raises(ValueError):validate(s)

def test_invalid_nested():
    s=load('scenario');del s['skills'][0]['routes']['train']
    with pytest.raises(ValueError):validate(s)
    with pytest.raises(ValueError):validate({})
    s=load('scenario');s['skills'][0]['routes']['train']['success_rate']=1.1
    with pytest.raises(ValueError):validate(s)

def test_provenance_and_denominators():
    d=analyze()
    assert len(d['sources'])==20 and len(d['evidence'])==60
    assert {s['period'] for s in d['sources']}=={'2023','2024'}
    assert sum(d['summary']['review_labels'].values())==60
    assert d['evaluation']['keyword_baseline']['correct']==23
    assert sum(sum(v.values()) for v in d['evaluation']['context_rules']['confusion'].values())==60
    assert all(s['reviewed_spans']==3 for s in d['company_periods'])
    assert all(s['bytes']>10000 and s['retrieved_at']=='2026-11-16' for s in d['sources'])
    assert all(k in d['evidence'][0] for k in ['source_id','source_url','source_vintage','geography','unit_of_observation','status','schema_version'])
    for period in ['2023-06-30','2024-06-30']:
        rows=[r for r in d['workforce'] if r['period']==period]
        assert sum(r['employees'] for r in rows)==rows[0]['total_employees']

def test_evidence_errors():
    with pytest.raises(ValueError):evaluate([])
    with pytest.raises(ValueError):validate_evidence([],load('sources'))
    e=load('evidence');e[0]['source_id']='unknown'
    with pytest.raises(ValueError):validate_evidence(e,load('sources'))
    e=load('evidence');e.append(e[0])
    with pytest.raises(ValueError):validate_evidence(e,load('sources'))

def test_html_source_escaping(tmp_path):
    d=analyze();d['evidence'][0]['excerpt']='</script><script>alert(1)</script>'
    p=tmp_path/'index.html';dashboard(d,p);text=p.read_text(encoding='utf-8')
    assert '</script><script>alert(1)' not in text and '__DATA__' not in text
    assert 'https://cdn.' not in text

def test_cli_malformed_input(tmp_path):
    p=tmp_path/'bad.json';p.write_text('{broken',encoding='utf-8')
    r=subprocess.run(['corporate-ai','scenario','--input',str(p)],capture_output=True,text=True)
    assert r.returncode==2 and 'Input error:' in r.stderr
