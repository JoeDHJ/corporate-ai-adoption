"""Enumerate bounded integer route mixes, meeting expected capability demand."""
from itertools import product
from math import isfinite
from datetime import date
from urllib.parse import urlparse

ROUTES=('train','redeploy','hire')

def number(value,name,minimum=0,maximum=None,integer=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or value<minimum or (maximum is not None and value>maximum) or (integer and not isinstance(value,int)):
        raise ValueError(f'{name} is outside its valid range')
    return value

def validate(s):
    if not isinstance(s,dict):raise ValueError('scenario must be an object')
    required=['horizon_months','deadline_months','annual_discount_rate','annual_value_per_capability','upfront_budget','skills','currency','price_year','source_id','source_url','retrieved_at','source_vintage','geography','unit_of_observation','period','schema_version','status']
    if any(k not in s for k in required):raise ValueError('scenario is missing required fields')
    if s['schema_version']!='portfolio.v1' or s['status']!='scenario':raise ValueError('scenario requires portfolio.v1 and scenario status')
    for k in ['source_id','retrieved_at','source_vintage','geography','unit_of_observation','period','currency']:
        if not isinstance(s[k],str) or not s[k].strip():raise ValueError(f'invalid scenario {k}')
    date.fromisoformat(s['retrieved_at'][:10])
    if s['source_url'] is not None and (not isinstance(s['source_url'],str) or urlparse(s['source_url']).scheme!='https' or not urlparse(s['source_url']).netloc):raise ValueError('scenario source_url must be HTTPS or null')
    number(s['price_year'],'price_year',1900,2100,True)
    if not isinstance(s['skills'],list):raise ValueError('skills must be a list')
    for key in ['horizon_months','deadline_months']:number(s[key],key,1,120,True)
    if s['deadline_months']>s['horizon_months']:raise ValueError('deadline exceeds horizon')
    number(s['annual_discount_rate'],'annual_discount_rate',0,1)
    number(s['annual_value_per_capability'],'annual_value_per_capability')
    number(s['upfront_budget'],'upfront_budget')
    if not s['skills']:raise ValueError('at least one skill is required')
    names=[]
    for skill in s['skills']:
        if not isinstance(skill,dict) or any(k not in skill for k in ['skill_id','demand','routes']):raise ValueError('invalid skill object')
        if not isinstance(skill['skill_id'],str) or not skill['skill_id']:raise ValueError('skill_id must be a nonempty string')
        if not isinstance(skill['routes'],dict) or any(r not in skill['routes'] for r in ROUTES):raise ValueError('all three routes are required')
        names.append(skill['skill_id']);number(skill['demand'],'demand',0,100,True)
        for route in ROUTES:
            x=skill['routes'][route]
            if not isinstance(x,dict) or any(k not in x for k in ['capacity','success_rate','ready_month','upfront_cost','annual_recurring_cost']):raise ValueError('invalid route object')
            number(x['capacity'],'capacity',0,100,True);number(x['success_rate'],'success_rate',0,1)
            number(x['ready_month'],'ready_month',0,s['horizon_months'],True)
            for key in ['upfront_cost','annual_recurring_cost']:number(x[key],key)
    if len(names)!=len(set(names)):raise ValueError('duplicate skill IDs')

def cashflows(s,skill,counts):
    months=s['horizon_months']; flows=[0.0]*(months+1); cost=[0.0]*(months+1); ready=0.0; upfront=0.0
    for route,count in zip(ROUTES,counts):
        x=skill['routes'][route]; c=count*x['upfront_cost'];upfront+=c;flows[0]-=c;cost[0]+=c
        ready+=count*x['success_rate'] if x['ready_month']<=s['deadline_months'] else 0
        for m in range(1,months+1):
            # Costs accrue for every candidate from month 1; benefits only after readiness.
            recurring=count*x['annual_recurring_cost']/12
            benefit=(count*x['success_rate']*s['annual_value_per_capability']/12 if m>x['ready_month'] else 0)
            cost[m]+=recurring;flows[m]+=benefit-recurring
    rate=s['annual_discount_rate']
    npv=sum(v/(1+rate)**(m/12) for m,v in enumerate(flows))
    pv_cost=sum(v/(1+rate)**(m/12) for m,v in enumerate(cost))
    return {'counts':dict(zip(ROUTES,counts)),'expected_ready':round(ready,6),'upfront_cost':upfront,'pv_cost':pv_cost,'npv':npv,'cashflows':flows}

def _frontier(options):
    # A route mix is dominated if another has <= upfront spend and <= PV cost.
    out=[]; best=float('inf')
    for x in sorted(options,key=lambda p:(p['upfront_cost'],p['pv_cost'])):
        if x['pv_cost']<best-1e-7:out.append(x);best=x['pv_cost']
    return out

def solve(s,allowed=ROUTES):
    validate(s)
    choices=[]
    for skill in s['skills']:
        ranges=[range(skill['routes'][r]['capacity']+1) if r in allowed and skill['routes'][r]['ready_month']<=s['deadline_months'] else range(1) for r in ROUTES]
        options=[];capacity_feasible=False
        for counts in product(*ranges):
            ready=sum(c*skill['routes'][r]['success_rate'] for c,r in zip(counts,ROUTES))
            if ready+1e-8<skill['demand']:continue
            capacity_feasible=True
            x=cashflows(s,skill,counts)
            if x['upfront_cost']<=s['upfront_budget']:options.append(x)
        if not options:
            reason=(f"Upfront budget cannot fund capability {skill['skill_id']}" if capacity_feasible else f"Insufficient eligible capacity by deadline for {skill['skill_id']}")
            return {'feasible':False,'reason':reason}
        choices.append(_frontier(options))
    best=None
    for combo in product(*choices):
        upfront=sum(x['upfront_cost'] for x in combo)
        if upfront>s['upfront_budget']+1e-8:continue
        total=sum(x['pv_cost'] for x in combo)
        if best is None or total<best[0]:best=total,combo
    if best is None:return {'feasible':False,'reason':'Upfront budget cannot fund a feasible mix'}
    combo=best[1]; flows=[sum(x['cashflows'][i] for x in combo) for i in range(s['horizon_months']+1)]
    cumulative=0.; payback=None
    for m,v in enumerate(flows):
        cumulative+=v
        if cumulative>=0 and payback is None:payback=m
    return {'feasible':True,'objective':'minimum PV incremental cost subject to expected demand and upfront budget','status':'scenario','currency':s['currency'],'price_year':s['price_year'],'horizon_months':s['horizon_months'],'upfront_cost':sum(x['upfront_cost'] for x in combo),'pv_cost':best[0],'npv':sum(x['npv'] for x in combo),'undiscounted_payback_month':payback,'cashflows':flows,'skills':[{'skill_id':skill['skill_id'],'demand':skill['demand'],**x} for skill,x in zip(s['skills'],combo)],'route_counts':{r:sum(x['counts'][r] for x in combo) for r in ROUTES}}

def compare(s):
    return {name:solve(s,allowed) for name,allowed in [('mixed',ROUTES),('training_only',('train',)),('redeployment_only',('redeploy',)),('hiring_only',('hire',))]}
