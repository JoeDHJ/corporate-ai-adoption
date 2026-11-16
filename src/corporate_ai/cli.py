import argparse
import json
from importlib.resources import files
from pathlib import Path
import sys
from .classify import classify
from .pipeline import analyze, dashboard, export, load, write_json, scenario_output
from .strategy import compare
from .vacancies import import_vacancies, summarize

def main(argv=None):
    parser=argparse.ArgumentParser(description='Corporate AI Adoption — reproducible public evidence and workforce scenarios')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('demo',help='export public case and a standalone offline dashboard');p.add_argument('--out',default='output')
    p=sub.add_parser('analyze',help='export portfolio.v1 outputs');p.add_argument('--out',default='output')
    p=sub.add_parser('classify',help='classify a supplied text span');p.add_argument('text')
    p=sub.add_parser('scenario',help='solve a JSON scenario');p.add_argument('--input',type=Path);p.add_argument('--out',type=Path)
    p=sub.add_parser('workflow',help='compare workload-derived investment scales and no action');p.add_argument('--input',type=Path,help='JSON with scenario and workflow objects');p.add_argument('--out',type=Path)
    p=sub.add_parser('reliability',help='compare conditional staffing reliability policies');p.add_argument('--input',type=Path,help='scenario JSON');p.add_argument('--out',type=Path)
    p=sub.add_parser('import-vacancies',help='validate permitted public vacancy snapshots');p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('schema',help='print a bundled JSON Schema');p.add_argument('name',choices=['scenario','vacancy','portfolio.v1','scenario-output','workflow-case'])
    args=parser.parse_args(argv)
    try:
        if args.command in ['demo','analyze']:
            data=export(args.out)
            if args.command=='demo':
                dashboard(data,Path(args.out)/'index.html')
                dashboard(data,Path(args.out)/'presentation.html',initial_tab='presentation')
            print(json.dumps({'version':data['version'],'bank_reports':len(data['bank_case']['sources']),
                'bank_candidate_locations':len(data['bank_case']['candidate_locations']),'bank_reviewed_spans':len(data['bank_case']['reviewed']),
                'selected_workflow_scale':data['workflow']['recommended_scale'],'legacy_context':data['summary']},indent=2))
        elif args.command=='classify':print(json.dumps(classify(args.text),indent=2))
        elif args.command=='schema':print(files('corporate_ai').joinpath('schemas',args.name+'.schema.json').read_text(encoding='utf-8'))
        elif args.command=='import-vacancies':
            rows=import_vacancies(args.input);write_json(args.out,{'schema_version':'portfolio.v1','records':rows,'summary':summarize(rows)})
            print(f'Imported {len(rows)} selected public vacancy snapshots.')
        elif args.command in ['workflow','reliability']:
            from .workflow import workflow_case
            from .reliability import risk_case
            if args.command=='workflow':
                x=json.loads(args.input.read_text(encoding='utf-8')) if args.input else {'scenario':load('scenario'),'workflow':load('workflow')}
                result={'schema_version':'portfolio.v1','version':'2.0.0',**x,'results':workflow_case(x['scenario'],x['workflow'])}
            else:
                s=json.loads(args.input.read_text(encoding='utf-8')) if args.input else load('scenario')
                result=scenario_output(s,risk_case(s))
            if args.out:write_json(args.out,result)
            else:print(json.dumps(result,indent=2))
        else:
            s=json.loads(args.input.read_text(encoding='utf-8')) if args.input else load('scenario')
            result=scenario_output(s,compare(s))
            if args.out:write_json(args.out,result)
            else:print(json.dumps(result,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(f'Input error: {exc}',file=sys.stderr);return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
