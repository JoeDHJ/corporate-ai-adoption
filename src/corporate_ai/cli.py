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
    p=sub.add_parser('import-vacancies',help='validate permitted public vacancy snapshots');p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('schema',help='print a bundled JSON Schema');p.add_argument('name',choices=['scenario','vacancy','portfolio.v1','scenario-output'])
    args=parser.parse_args(argv)
    try:
        if args.command in ['demo','analyze']:
            data=export(args.out)
            if args.command=='demo':dashboard(data,Path(args.out)/'index.html')
            print(json.dumps(data['summary'],indent=2))
        elif args.command=='classify':print(json.dumps(classify(args.text),indent=2))
        elif args.command=='schema':print(files('corporate_ai').joinpath('schemas',args.name+'.schema.json').read_text(encoding='utf-8'))
        elif args.command=='import-vacancies':
            rows=import_vacancies(args.input);write_json(args.out,{'schema_version':'portfolio.v1','records':rows,'summary':summarize(rows)})
            print(f'Imported {len(rows)} selected public vacancy snapshots.')
        else:
            s=json.loads(args.input.read_text(encoding='utf-8')) if args.input else load('scenario')
            result=scenario_output(s,compare(s))
            if args.out:write_json(args.out,result)
            else:print(json.dumps(result,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(f'Input error: {exc}',file=sys.stderr);return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
