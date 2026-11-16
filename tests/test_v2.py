from copy import deepcopy
from itertools import product
from math import comb
import json
from pathlib import Path
import pytest
from corporate_ai.pipeline import load,analyze
from corporate_ai.reliability import distribution,attainment,solve_reliable,risk_case
from corporate_ai.workflow import workflow_case
from corporate_ai.measurement import axes
from corporate_ai.benchmark import centroid_predict,score

def test_binomial_and_failure_not_equal_to_mean():
    pmf=distribution((8,0,0),(.8,.9,1))
    assert sum(pmf)==pytest.approx(1)
    assert pmf[6]==pytest.approx(comb(8,6)*.8**6*.2**2)
    r=risk_case(load('scenario'))
    assert r['expected_coverage_plan']['joint_probability_independent']==pytest.approx(.3929537773045703)
    p=next(x for x in r['allocated_policy_curve'] if x['confidence_target']==.9)
    assert p['joint_probability_lower_bound']>=.9
    assert p['joint_probability_independent']==pytest.approx(.9285613554664082)
    assert p['route_counts']=={'train':23,'redeploy':10,'hire':5}

def test_reliable_cost_against_tiny_exhaustive_enumeration():
    s=load('scenario');s['skills']=s['skills'][:2];s['upfront_budget']=100000
    for sk in s['skills']:
        sk['demand']=1
        for r in sk['routes'].values():r['capacity']=2
    q=.8;p=solve_reliable(s,q)
    from corporate_ai.strategy import cashflows
    pools=[]
    for sk in s['skills']:
        pools.append([cashflows(s,sk,c) for c in product(range(3),repeat=3) if attainment(s,sk,c)['probability_meeting_demand']>=.9-1e-12])
    feasible=[sum(x['pv_cost'] for x in combo) for combo in product(*pools) if sum(x['upfront_cost'] for x in combo)<=s['upfront_budget']]
    assert p['pv_cost']==pytest.approx(min(feasible))

def test_readiness_zero_and_no_action():
    s=load('scenario');w=load('workflow');w['monthly_volume']=0
    r=workflow_case(s,w)
    assert r['recommended_scale']==0
    assert all(x['staffing']['feasible'] for x in r['options'])
    w=load('workflow');w['realization_rate']=0
    assert workflow_case(s,w)['recommended_scale']==0
    s['upfront_budget']=0
    assert not any(x['staffing']['feasible'] for x in workflow_case(s,w)['options'])

def test_integrated_cash_budget_and_value_counted_once():
    s=load('scenario');w=load('workflow');r=workflow_case(s,w)
    assert r['recommended_scale']==.5
    full=r['options'][-1];assert not full['staffing']['feasible']
    half=r['options'][1];assert half['npv']==pytest.approx(1907703.9595496643)
    assert [x['demand'] for x in half['staffing_inputs']['skills']]==[4,6,3]
    assert half['upfront_with_integration']<=s['upfront_budget']
    # Changing legacy per-capability value cannot change workflow-level investment value.
    s['annual_value_per_capability']=999999
    assert workflow_case(s,w)['options'][1]['npv']==pytest.approx(half['npv'])

@pytest.mark.parametrize('key,value',[('productive_hours_month',0),('confidence',1.1),('monthly_volume',float('nan')),('launch_month',37)])
def test_bad_workflow_inputs(key,value):
    w=load('workflow');w[key]=value
    with pytest.raises(ValueError):workflow_case(load('scenario'),w)

def test_use_risk_and_company_name_negative():
    a=axes('We also use artificial intelligence to automate business decisions, but there is no assurance of accurate outcomes.')
    assert 'deployed' in a['stages'] and a['risk']
    assert axes('Bank of America increased net income.')['technology']=='none'
    assert axes('Wells Fargo increased its dividend.')['technology']=='none'

def test_source_and_snapshot_integrity():
    b=load('bank-case');assert len(b['sources'])==11 and len(b['candidate_locations'])==288
    assert len(b['reviewed'])==30
    assert {s['fiscal_year_end'][-5:] for s in b['sources']}=={'12-31'}
    assert b['coverage']['missing_reports'][0]['source_id']=='BAC-2025'
    jobs=load('bank-vacancies');assert len(jobs)==5
    assert len({(j['company_id'],j['job_id'],j['period']) for j in jobs})==5
    assert any(j['annual_base_pay_range'] is None for j in jobs)
    assert load('vacancy-coverage')['retrieved_pages']==5

def test_training_groups_and_reference_scope():
    e=load('bank-case')['evaluation'];assert len(e['folds'])==12
    assert all(x['train_n']+x['test_n']==82 for x in e['folds'])
    assert e['time_holdout']['train_n']==75 and e['time_holdout']['tfidf_centroid']['n']==6
    assert e['time_holdout']['excluded_feature_identical_test_spans']==1
    assert 'Single-assistant' in e['reference_status']
    assert centroid_predict([{'excerpt':'deployed tools','review_label':'deployment'},{'excerpt':'risk to capital','review_label':'risk'}],[{'excerpt':'unseenword','review_label':'none'}])==[False]

def test_packaged_task_measurements_not_human_times():
    b=load('research-benchmark');assert b['top_one_matches']==b['locator_matches']==b['n']==6
    assert all(x['elapsed_seconds']>=0 for x in b['tasks'])
    assert b['human_benchmark_status'].startswith('Not conducted')

def test_zero_value_currency_and_rounding():
    from corporate_ai.workflow import workload_demand
    assert workload_demand(3000,.28,7)==2
    w=load('workflow');w['hour_value']=0
    r=workflow_case(load('scenario'),w)
    assert r['recommended_scale']==0
    assert all(x.get('break_even_realization') is None for x in r['options'])
    w['currency']='EUR'
    with pytest.raises(ValueError,match='currency'):workflow_case(load('scenario'),w)

def test_more_expensive_earlier_route_can_make_investment_positive():
    s=load('scenario');s.update(horizon_months=12,deadline_months=6,annual_discount_rate=0,upfront_budget=15000)
    s['skills']=s['skills'][:1];sk=s['skills'][0]
    for x in sk['routes'].values():x.update(capacity=0,annual_recurring_cost=0)
    sk['routes']['train'].update(capacity=1,success_rate=.9,ready_month=6,upfront_cost=12000)
    sk['routes']['hire'].update(capacity=1,success_rate=1,ready_month=0,upfront_cost=13000)
    w=load('workflow');w.update(monthly_volume=6000,baseline_minutes=20,assisted_minutes=0,rework_probability=0,
        productive_hours_month=100,hour_value=1,realization_rate=1,integration_cost=0,annual_platform_cost=0,launch_month=0)
    w['tasks']=[{'skill_id':sk['skill_id'],'minutes_per_item':1}]
    r=workflow_case(s,w);full=r['options'][-1]
    assert full['staffing']['route_counts']['hire']==1
    assert full['npv']==pytest.approx(9800) and r['recommended_scale']==1

def test_workflow_export_schema_and_no_legacy_benefits():
    from corporate_ai.cli import main
    from importlib.resources import files
    from jsonschema import Draft202012Validator
    schema=json.loads(files('corporate_ai').joinpath('schemas','workflow-case.schema.json').read_text(encoding='utf-8'))
    s=load('scenario');w=load('workflow')
    for value in [.5,0]:
        w['realization_rate']=value;r=workflow_case(s,w)
        Draft202012Validator(schema).validate({'schema_version':'portfolio.v1','scenario':s,'workflow':w,'results':r})
        for row in r['options']:
            plan=row['staffing']
            assert 'npv' not in plan and 'cashflows' not in plan
            for sk in plan.get('skills',[]):assert 'npv' not in sk and 'cashflows' not in sk

def test_standalone_v2_exports_retain_inputs_and_metadata(tmp_path):
    from corporate_ai.pipeline import export,META
    from importlib.resources import files
    from jsonschema import Draft202012Validator
    export(tmp_path)
    for name in ['bank-case','vacancy-coverage','reliability','workflow','research-benchmark']:
        x=json.loads((tmp_path/(name+'.json')).read_text(encoding='utf-8'))
        assert all(k in x for k in META)
    x=json.loads((tmp_path/'workflow.json').read_text(encoding='utf-8'))
    sch=json.loads(files('corporate_ai').joinpath('schemas','workflow-case.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(sch).validate(x)
    assert x['scenario']['upfront_budget']==400000 and x['workflow']['monthly_volume']==60000
    assert json.loads((tmp_path/'reliability.json').read_text(encoding='utf-8'))['inputs']['skills']

def test_workflow_provenance_required():
    w=load('workflow');del w['source_id']
    with pytest.raises(ValueError,match='metadata'):workflow_case(load('scenario'),w)
