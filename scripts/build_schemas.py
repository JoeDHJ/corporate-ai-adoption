"""Create portable JSON Schemas for the public portfolio contract."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'src/corporate_ai/schemas';P.mkdir(exist_ok=True)
common=['source_id','source_url','retrieved_at','source_vintage','geography','unit_of_observation','period','currency','price_year','schema_version','status']
metadata={'type':'object','required':common,'properties':{k:{'type':'string','minLength':1} for k in common}}
metadata['properties'].update(source_url={'type':['string','null']},currency={'type':['string','null']},price_year={'type':['integer','null']},schema_version={'const':'portfolio.v1'},status={'enum':['observed','estimated','scenario']})
route={'type':'object','required':['capacity','success_rate','ready_month','upfront_cost','annual_recurring_cost'],'properties':{'capacity':{'type':'integer','minimum':0,'maximum':100},'success_rate':{'type':'number','minimum':0,'maximum':1},'ready_month':{'type':'integer','minimum':0,'maximum':120},'upfront_cost':{'type':'number','minimum':0},'annual_recurring_cost':{'type':'number','minimum':0}}}
skill={'type':'object','required':['skill_id','demand','routes'],'properties':{'skill_id':{'type':'string','minLength':1},'demand':{'type':'integer','minimum':0,'maximum':100},'routes':{'type':'object','required':['train','redeploy','hire'],'properties':{r:{'$ref':'#/$defs/route'} for r in ['train','redeploy','hire']}}}}
scenario={'allOf':[{'$ref':'#/$defs/metadata'}],'type':'object','required':['horizon_months','deadline_months','annual_discount_rate','annual_value_per_capability','upfront_budget','skills'],'properties':{'status':{'const':'scenario'},'horizon_months':{'type':'integer','minimum':1,'maximum':120},'deadline_months':{'type':'integer','minimum':1,'maximum':120},'annual_discount_rate':{'type':'number','minimum':0,'maximum':1},'annual_value_per_capability':{'type':'number','minimum':0},'upfront_budget':{'type':'number','minimum':0},'skills':{'type':'array','minItems':1,'items':{'$ref':'#/$defs/skill'}}}}
defs={'metadata':metadata,'route':route,'skill':skill,'scenario':scenario}
vacancy={'type':'array','minItems':1,'items':{'type':'object','required':['source_id','source_url','retrieved_at','source_vintage','geography','period','company_id','job_id','title'],'properties':{k:{'type':'string','minLength':1} for k in ['source_id','retrieved_at','source_vintage','geography','company_id','job_id','title']}}}
vacancy['items']['properties'].update(source_url={'type':'string','pattern':'^https://'},period={'type':'string','format':'date'},skills={'anyOf':[{'type':'null'},{'type':'string'},{'type':'array','uniqueItems':True,'items':{'type':'string','minLength':1}}]},skill_taxonomy={'type':'string','minLength':1},skill_taxonomy_version={'type':'string','minLength':1})
portfolio={'type':'object','required':['schema_version','version','as_of','sources','evidence','company_periods','evaluation','labor','workforce','jobs','scenario','strategies','summary']}
props={'schema_version':{'const':'portfolio.v1'},'version':{'type':'string'},'as_of':{'type':'string','format':'date'}}
for name in ['sources','company_periods','labor','workforce']:
    props[name]={'type':'array','items':{'$ref':'#/$defs/metadata'}}
props['evidence']={'type':'array','minItems':1,'items':{'allOf':[{'$ref':'#/$defs/metadata'}],'required':['evidence_id','review_label','review_scope','company_id','excerpt']}}
props['evidence']['items']['properties']={'review_label':{'enum':['deployment','pilot','planned','hiring_innovation','promotional','risk','none']},'review_scope':{'enum':['internal','customer_or_product','unspecified']}}
props['scenario']={'$ref':'#/$defs/scenario'}
props['jobs']={'type':'array','items':{'allOf':[{'$ref':'#/$defs/metadata'}],'required':['company_id','source_native_id','skill_coding_status'],'properties':{'skill_coding_status':{'const':'estimated'}}}}
portfolio['properties']=props
output={'allOf':[{'$ref':'#/$defs/metadata'}],'type':'object','required':['inputs','results'],'properties':{'status':{'const':'scenario'},'inputs':{'$ref':'#/$defs/scenario'},'results':{'type':'object'}}}
for name,schema in [('scenario',scenario),('vacancy',vacancy),('portfolio.v1',portfolio),('scenario-output',output)]:
    doc={'$schema':'https://json-schema.org/draft/2020-12/schema','title':name+' contract',**schema,'$defs':defs}
    (P/(name+'.schema.json')).write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
print('Saved four public JSON Schemas.')
