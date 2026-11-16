import json
from pathlib import Path
from copy import deepcopy
import pytest
from corporate_ai.vacancies import import_vacancies, summarize
from corporate_ai.strategy import solve, validate
from corporate_ai.pipeline import load

def test_real_example_and_missing_skill_denominator(tmp_path):
    rows=import_vacancies(Path(__file__).resolve().parents[1]/'examples/official-vacancy-snapshots.csv')
    assert len(rows)==3 and summarize(rows)[0]['observed_selected_postings']==3
    rows[0]['skills']=None
    result=summarize(rows)[0]
    assert result['postings_with_skill_tags']==2 and result['postings_missing_skill_tags']==1
    assert result['skill_share_among_tagged_postings']['business_case']==1

def test_mixed_taxonomy_not_merged():
    rows=import_vacancies(Path(__file__).resolve().parents[1]/'examples/official-vacancy-snapshots.csv')
    rows[0]['skill_taxonomy_version']='2.0'
    with pytest.raises(ValueError,match='one taxonomy'):summarize(rows)

@pytest.mark.parametrize('mutation',['empty','duplicate','bad_url','bad_date','no_taxonomy','bad_skills'])
def test_reject_malformed_snapshots(tmp_path,mutation):
    rows=import_vacancies(Path(__file__).resolve().parents[1]/'examples/official-vacancy-snapshots.csv')
    if mutation=='empty':rows=[]
    elif mutation=='duplicate':rows.append(deepcopy(rows[0]))
    elif mutation=='bad_url':rows[0]['source_url']='http://example.com'
    elif mutation=='bad_date':rows[0]['period']='2026-99-99'
    elif mutation=='no_taxonomy':del rows[0]['skill_taxonomy']
    else:rows[0]['skills']=[123]
    p=tmp_path/'vacancies.json';p.write_text(json.dumps(rows),encoding='utf-8')
    with pytest.raises(ValueError):import_vacancies(p)

def test_integer_floats_fail_cleanly_and_budget_reason():
    s=load('scenario');s['skills'][0]['routes']['train']['capacity']=8.0
    with pytest.raises(ValueError):validate(s)
    s=load('scenario');s['horizon_months']=36.0
    with pytest.raises(ValueError):validate(s)
    s=load('scenario');s['upfront_budget']=0
    assert 'Upfront budget' in solve(s)['reason']
