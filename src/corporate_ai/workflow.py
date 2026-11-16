"""Workload-derived staffing and workflow-level value; no duplicated skill benefits."""
from copy import deepcopy
from math import ceil
from datetime import date
from urllib.parse import urlparse
from .strategy import number, validate
from .reliability import solve_workflow

def workload_demand(volume,minutes,hours):
    value=volume*minutes/60/hours
    number(value,'derived workload FTE',0,100+1e-8)
    return ceil(value-1e-12*max(1,abs(value)))

def validate_workflow(w):
    if not isinstance(w,dict):raise ValueError('workflow must be an object')
    for key in ['source_id','retrieved_at','source_vintage','geography','unit_of_observation','period','currency']:
        if not isinstance(w.get(key),str) or not w[key].strip():raise ValueError('workflow missing metadata '+key)
    if w.get('schema_version')!='portfolio.v1' or w.get('status')!='scenario':raise ValueError('workflow requires portfolio.v1 and scenario status')
    if 'source_url' not in w or (w['source_url'] is not None and (not isinstance(w['source_url'],str) or urlparse(w['source_url']).scheme!='https' or not urlparse(w['source_url']).netloc)):raise ValueError('workflow source_url must be HTTPS or null')
    date.fromisoformat(w['retrieved_at'][:10]);number(w.get('price_year'),'workflow price_year',1900,2100,True)
    for key in ['monthly_volume','baseline_minutes','assisted_minutes','rework_probability','rework_minutes','productive_hours_month','hour_value','realization_rate','integration_cost','annual_platform_cost','launch_month','confidence']:
        if key not in w:raise ValueError('workflow missing '+key)
        number(w[key],key,0,1 if key in ['rework_probability','realization_rate','confidence'] else None, key=='launch_month')
    if w['productive_hours_month']<=0:raise ValueError('productive hours must be positive')
    if not isinstance(w.get('tasks'),list) or not w['tasks']:raise ValueError('workflow tasks required')
    ids=[]
    for task in w['tasks']:
        if not isinstance(task,dict) or not isinstance(task.get('skill_id'),str):raise ValueError('invalid workflow task')
        ids.append(task['skill_id']);number(task.get('minutes_per_item'),'minutes per item')
    if len(ids)!=len(set(ids)):raise ValueError('duplicate workflow skill')

def workflow_case(s,w):
    validate(s);validate_workflow(w)
    if w.get('currency')!=s['currency'] or w.get('price_year')!=s['price_year']:raise ValueError('Workflow and staffing currency and price year must match')
    if w['launch_month']>s['horizon_months']:raise ValueError('launch exceeds horizon')
    if {x['skill_id'] for x in w['tasks']}!={x['skill_id'] for x in s['skills']}:raise ValueError('workflow tasks must match scenario skills exactly')
    options=[]
    for fraction in [.25,.5,1.0]:
        trial=deepcopy(s);volume=w['monthly_volume']*fraction
        fixed=w['integration_cost']*fraction
        trial['upfront_budget']=max(0,s['upfront_budget']-fixed)
        for sk in trial['skills']:
            task=next(t for t in w['tasks'] if t['skill_id']==sk['skill_id'])
            sk['demand']=workload_demand(volume,task['minutes_per_item'],w['productive_hours_month'])
        human_after=w['assisted_minutes']+sum(t['minutes_per_item'] for t in w['tasks'])+w['rework_probability']*w['rework_minutes']
        saved=volume*(w['baseline_minutes']-human_after)/60
        plan=(solve_workflow(trial,w['confidence'],saved*w['hour_value']*w['realization_rate'],w['launch_month']) if fixed<=s['upfront_budget'] else {'feasible':False,'reason':'Integration alone exceeds total upfront budget'})
        if plan['feasible']:
            plan={k:v for k,v in plan.items() if k not in ['npv','cashflows']}
            plan['skills']=[{k:v for k,v in x.items() if k not in ['npv','cashflows']} for x in plan['skills']]
        row={'scale':fraction,'monthly_volume':volume,'staffing_inputs':trial,'staffing':plan}
        if plan['feasible']:
            launch=max(w['launch_month'],max((sk['routes'][r]['ready_month'] for sk,x in zip(trial['skills'],plan['skills']) for r,n in x['counts'].items() if n),default=0))
            # Value is capped by the joint success event: conservative all-or-nothing
            # launch; no extra benefits for redundant candidates or overlapping skills.
            reliability=plan['joint_probability_independent']
            monthly_value=saved*w['hour_value']*w['realization_rate']*reliability
            costs=plan['pv_cost']+fixed+sum(w['annual_platform_cost']*fraction/12/(1+s['annual_discount_rate'])**(m/12) for m in range(1,s['horizon_months']+1))
            value_factor=sum(1/(1+s['annual_discount_rate'])**(m/12) for m in range(launch+1,s['horizon_months']+1))
            pv_value=monthly_value*value_factor
            row.update(human_minutes_after=human_after,monthly_capacity_hours=saved,annual_capacity_fte=saved/w['productive_hours_month'],
                launch_month=launch,pv_total_cost=costs,pv_realized_value=pv_value,npv=pv_value-costs,
                break_even_realization=(costs/(saved*w['hour_value']*reliability*value_factor) if saved*w['hour_value']*reliability*value_factor>0 else None),
                upfront_with_integration=plan['upfront_cost']+fixed)
            if row['upfront_with_integration']>s['upfront_budget']+1e-8:
                row['staffing']={**plan,'feasible':False,'reason':'Integration plus staffing exceeds total upfront budget'}
        options.append(row)
    feasible=[r for r in options if r['staffing']['feasible'] and r['npv']>0]
    best=max(feasible,key=lambda r:r['npv']) if feasible else None
    return {'inputs':w,'options':options,'no_action_npv':0,'recommended_scale':best['scale'] if best else 0,
        'decision':'Proceed to quality-gated pilot at the selected scale' if best else 'Defer investment; no feasible modeled scale beats no action',
        'value_definition':'Released capacity valued at an assumed realization rate; not observed cash savings. All-or-nothing workflow launch conditional on all three skill demands; no value duplicated across skills.',
        'assumptions':['Task minutes, productive hours, value, realization, costs and success are scenario inputs.',
        'Value begins only after all selected routes are ready and launch is permitted; failed joint attainment yields no workflow value.',
        'Staffing costs include candidate costs and redeployment/backfill; platform and integration are additional.',
        'Do not add wage-based savings to incremental revenue when they monetize the same capacity.',
        'Equal workload proportions and disjoint specialist pools; no attrition, tax or salvage.']}
