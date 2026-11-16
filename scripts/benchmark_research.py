"""Execute a small, reproducible public-excerpt retrieval and citation task pack.

Elapsed time is machine runtime only. Tasks and relevance references are assistant
authored and fixed, not user-study measurements or an unseen external benchmark.
"""
from datetime import datetime,timezone
import json,math,re,sys,time,platform
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'src/corporate_ai/data'
sys.path.insert(0,str(ROOT/'src'))
from corporate_ai.retrieval import rank_evidence
TASKS=[
 ('citi-2024-rollout','C-2024','colleagues platforms launched','BANK-C-2024-1','Colleague reach is rollout/access, not independently observed active use.'),
 ('citi-2025-coding','C-2025','developers coding hours capacity','BANK-C-2025-6','Reported released capacity is not verified cash savings.'),
 ('jpm-2024-access','JPM-2024','LLM Suite launched colleagues','BANK-JPM-2024-7','Firmwide access population.'),
 ('wfc-use-risk','WFC-2024','business decisions operations no assurance','BANK-WFC-2024-1','Use and risk coexist; repeated disclosure is not a new event.'),
 ('bac-coding-pilot','BAC-2023','piloting programming coding','BANK-BAC-2023-7','A pilot does not establish scaled deployment.'),
 ('citi-risk','C-2023','controls governance increased risks','BANK-C-2023-1','A conditional warning does not establish use.')]

def main():
    rows=json.loads((DATA/'bank-case.json').read_text(encoding='utf-8'))['reviewed'];results=[]
    for tid,sid,query,expected,interpretation in TASKS:
        start=time.perf_counter();docs=[r for r in rows if r['source_id']==sid]
        ranked=rank_evidence(docs,query)
        selected=ranked[0];elapsed=time.perf_counter()-start
        raw=json.loads((ROOT/'data/raw'/(sid+'.json')).read_text(encoding='utf-8'))
        exact=raw['pages'][selected['page']-1][selected['start_char']:selected['end_char']]==selected['excerpt']
        results.append({'task_id':tid,'source_id':sid,'query':query,'expected_evidence_id':expected,
            'retrieved_evidence_id':selected['evidence_id'],'top_one_reference_match':selected['evidence_id']==expected,
            'exact_source_locator_match':exact,'elapsed_seconds':elapsed,'interpretation':interpretation})
    out={'source_id':'RESEARCH-TASKS-2026-11-16','source_url':None,'retrieved_at':datetime.now(timezone.utc).isoformat(),
        'source_vintage':'Fixed assistant-authored task pack v2','geography':'Local machine','unit_of_observation':'selected excerpt retrieval task',
        'period':'2026-11-16','currency':None,'price_year':None,'schema_version':'portfolio.v1','status':'estimated',
        'environment':{'python':platform.python_version(),'system':platform.system(),'processor':platform.machine()},
        'tasks':results,'top_one_matches':sum(x['top_one_reference_match'] for x in results),'locator_matches':sum(x['exact_source_locator_match'] for x in results),
        'n':len(results),'scope':'Document-filtered keyword ranking over released reviewed excerpts. Expected references and tasks by one AI assistant; not independent quality validation, full-document search, or employee productivity measurement.',
        'human_benchmark_status':'Not conducted. No participants or human time measurements.',
        'human_pilot_protocol':{'design':'Randomized task-order crossover with consenting actual analysts; common document set; independent source-quality scoring blinded to condition.',
            'outcomes':['correct fact and denominator','citation resolves to exact source','unsupported claim count','elapsed human minutes','revision minutes','failure severity'],
            'release_gate':'No unsupported material claims; all decision-driving citations correct; quality noninferior to the agreed manual baseline. Report actual participant count and uncertainty before claiming productivity gains.'}}
    (DATA/'research-benchmark.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(out['top_one_matches'],'/',out['n'],'reference matches;',out['locator_matches'],'exact locators')

if __name__=='__main__':main()
