"""Exact conditional attainment and conservative allocated chance constraints.

Independent Bernoulli candidates within each skill; skill independence is required
only for the reported product probability. The union bound does not require it.
"""
from functools import lru_cache
from itertools import product
from math import prod
from .strategy import ROUTES, validate, cashflows, _frontier, solve, number

@lru_cache(maxsize=8192)
def distribution(counts, probabilities):
    pmf=[1.0]
    for count,p in zip(counts, probabilities):
        for _ in range(count):
            nxt=[0.0]*(len(pmf)+1)
            for k,v in enumerate(pmf):
                nxt[k]+=v*(1-p);nxt[k+1]+=v*p
            pmf=nxt
    return tuple(pmf)

def attainment(s, skill, counts):
    ps=tuple(skill['routes'][r]['success_rate'] if skill['routes'][r]['ready_month']<=s['deadline_months'] else 0 for r in ROUTES)
    pmf=distribution(tuple(counts),ps);d=skill['demand']
    return {'probability_meeting_demand':min(1.0,sum(pmf[d:])),
            'expected_shortfall':sum(max(0,d-k)*v for k,v in enumerate(pmf))}

def attach_risk(s, plan):
    if not plan['feasible']:return plan
    risks=[attainment(s,sk,tuple(x['counts'][r] for r in ROUTES)) for sk,x in zip(s['skills'],plan['skills'])]
    return {**plan,'skill_risks':risks,
            'joint_probability_independent':prod(x['probability_meeting_demand'] for x in risks),
            'joint_probability_lower_bound':max(0,1-sum(1-x['probability_meeting_demand'] for x in risks)),
            'expected_total_shortfall':sum(x['expected_shortfall'] for x in risks)}

def solve_reliable(s, confidence=.9):
    validate(s);number(confidence,'confidence',0,1)
    threshold=1-(1-confidence)/len(s['skills']);choices=[]
    for skill in s['skills']:
        caps=[skill['routes'][r]['capacity'] if skill['routes'][r]['ready_month']<=s['deadline_months'] else 0 for r in ROUTES]
        options=[]
        for counts in product(*(range(c+1) for c in caps)):
            upfront=sum(c*skill['routes'][r]['upfront_cost'] for c,r in zip(counts,ROUTES))
            if upfront>s['upfront_budget']+1e-8:continue
            if attainment(s,skill,counts)['probability_meeting_demand']+1e-12<threshold:continue
            options.append(cashflows(s,skill,counts))
        if not options:return {'feasible':False,'confidence_target':confidence,'reason':'No route mix meets allocated reliability and cash constraints for '+skill['skill_id']}
        choices.append(_frontier(options))
    best=None
    for combo in product(*choices):
        if sum(x['upfront_cost'] for x in combo)>s['upfront_budget']+1e-8:continue
        cost=sum(x['pv_cost'] for x in combo)
        if best is None or cost<best[0]:best=(cost,combo)
    if best is None:return {'feasible':False,'confidence_target':confidence,'reason':'Shared upfront budget cannot fund a reliable plan'}
    cost,combo=best
    plan={'feasible':True,'confidence_target':confidence,'per_skill_probability_floor':threshold,
          'objective':'Minimum PV incremental staffing cost within equal per-skill failure-budget allocation; conservative, not globally optimal joint chance constraint',
          'status':'scenario','upfront_cost':sum(x['upfront_cost'] for x in combo),'pv_cost':cost,
          'npv':sum(x['npv'] for x in combo),'cashflows':[sum(x['cashflows'][m] for x in combo) for m in range(s['horizon_months']+1)],
          'skills':[{'skill_id':sk['skill_id'],'demand':sk['demand'],**x} for sk,x in zip(s['skills'],combo)],
          'route_counts':{r:sum(x['counts'][r] for x in combo) for r in ROUTES}}
    return attach_risk(s,plan)

def risk_case(s):
    return {'assumptions':['Conditional independent Bernoulli candidate attainment within each skill.',
        'Product probability additionally assumes independence across skills; the union lower bound does not.',
        'Success probabilities are assumptions, not estimates from disclosures. No post-attainment attrition.',
        'Equal allocation is a sufficient reliability constraint; the displayed cost curve is an allocated-policy curve, not the global efficient frontier.'],
        'expected_coverage_plan':attach_risk(s,solve(s)),
        'allocated_policy_curve':[solve_reliable(s,q) for q in [.5,.65,.8,.9,.95,.99]]}

def solve_workflow(s, confidence, monthly_value, launch_floor):
    """Maximize workflow NPV within the equal failure-budget policy class.

    Value is positive only after the slowest selected route is ready and the
    workflow launches. More reliable/earlier mixes can beat the cheapest mix.
    """
    validate(s);number(confidence,'confidence',0,1)
    if monthly_value<=0:
        plan=solve_reliable(s,confidence)
        if plan['feasible']:plan['objective']='Descriptive minimum-cost reliable staffing; no action dominates nonpositive workflow value'
        return plan
    floor=1-(1-confidence)/len(s['skills']);pools=[]
    for sk in s['skills']:
        caps=[sk['routes'][r]['capacity'] if sk['routes'][r]['ready_month']<=s['deadline_months'] else 0 for r in ROUTES]
        opts=[]
        for counts in product(*(range(c+1) for c in caps)):
            up=sum(c*sk['routes'][r]['upfront_cost'] for c,r in zip(counts,ROUTES))
            if up>s['upfront_budget']+1e-8:continue
            p=attainment(s,sk,counts)['probability_meeting_demand']
            if p+1e-12<floor:continue
            ready=max((sk['routes'][r]['ready_month'] for r,c in zip(ROUTES,counts) if c),default=0)
            opts.append({**cashflows(s,sk,counts),'probability':p,'launch':max(ready,launch_floor)})
        front=[]
        for x in sorted(opts,key=lambda x:(x['upfront_cost'],x['pv_cost'])):
            if any(y['pv_cost']<=x['pv_cost']+1e-7 and y['probability']>=x['probability']-1e-12 and y['launch']<=x['launch'] for y in front):continue
            front.append(x)
        if not front:return {'feasible':False,'reason':'No route mix meets allocated reliability and cash constraints for '+sk['skill_id']}
        pools.append(front)
    factors={m:sum(1/(1+s['annual_discount_rate'])**(t/12) for t in range(m+1,s['horizon_months']+1)) for m in range(s['horizon_months']+1)}
    best=None
    for combo in product(*pools):
        if sum(x['upfront_cost'] for x in combo)>s['upfront_budget']+1e-8:continue
        cost=sum(x['pv_cost'] for x in combo);p=prod(x['probability'] for x in combo);launch=max(x['launch'] for x in combo)
        npv=monthly_value*p*factors[launch]-cost
        if best is None or npv>best[0]+1e-7:best=npv,combo
    if best is None:return {'feasible':False,'reason':'Shared upfront budget cannot fund a reliable plan'}
    _,combo=best
    plan={'feasible':True,'status':'scenario','confidence_target':confidence,'per_skill_probability_floor':floor,
          'objective':'Maximum workflow NPV within equal per-skill failure-budget allocation; joint comparison of cost, readiness and reliability',
          'upfront_cost':sum(x['upfront_cost'] for x in combo),'pv_cost':sum(x['pv_cost'] for x in combo),
          'skills':[{'skill_id':sk['skill_id'],'demand':sk['demand'],**{k:v for k,v in x.items() if k not in ['npv','cashflows']}} for sk,x in zip(s['skills'],combo)],
          'route_counts':{r:sum(x['counts'][r] for x in combo) for r in ROUTES}}
    return attach_risk(s,plan)
