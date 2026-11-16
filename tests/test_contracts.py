import json
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator
from corporate_ai.pipeline import analyze, load, scenario_output, export
from corporate_ai.strategy import compare
from corporate_ai.vacancies import import_vacancies, summarize

def schema(name):return json.loads(files('corporate_ai').joinpath('schemas',name+'.schema.json').read_text(encoding='utf-8'))

def test_bundled_schemas_and_actual_outputs(tmp_path):
    d=export(tmp_path)
    for name,obj in [('portfolio.v1',d),('scenario',d['scenario']),('scenario-output',json.loads((tmp_path/'strategy.json').read_text(encoding='utf-8'))),('scenario-output',json.loads((tmp_path/'sensitivity.json').read_text(encoding='utf-8')))]:
        v=Draft202012Validator(schema(name));v.check_schema(schema(name));v.validate(obj)

def test_source_registry_wins_over_row_metadata():
    e=load('evidence');e[0].update(source_url='https://example.com/fake',company_id='fake',period='9999')
    row=analyze(e)['evidence'][0]
    authoritative=next(s for s in load('sources') if s['source_id']==e[0]['source_id'])
    assert row['source_url']==authoritative['source_url']
    assert row['company_id']=='US:SEC-CIK:0001467373' and row['period']=='2023'

def test_explicit_zero_skills_stay_known(tmp_path):
    rows=import_vacancies(Path(__file__).resolve().parents[1]/'examples/official-vacancy-snapshots.csv')
    rows[0]['skills']=[];rows[1]['skills']=None
    p=tmp_path/'jobs.json';p.write_text(json.dumps(rows),encoding='utf-8')
    imported=import_vacancies(p)
    assert imported[0]['skills']==[] and imported[1]['skills'] is None
    result=summarize(imported)[0]
    assert result['postings_with_skill_tags']==2 and result['postings_missing_skill_tags']==1
    assert result['skill_share_among_tagged_postings']['business_case']==.5
    Draft202012Validator(schema('vacancy')).validate(imported)

def test_changed_scenario_export_is_self_contained():
    s=load('scenario');s['upfront_budget']=0
    out=scenario_output(s,compare(s))
    assert out['inputs']['upfront_budget']==0 and out['source_id']==s['source_id']
    assert not out['results']['mixed']['feasible']
