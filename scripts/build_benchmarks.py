"""Pinned official facts, transcribed from the cited table/report and checked in review."""
import json
from pathlib import Path

DATA=Path(__file__).resolve().parents[1]/'src/corporate_ai/data'
def save(name,value):(DATA/(name+'.json')).write_text(json.dumps(value,indent=2),encoding='utf-8')

bls='https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm'
records=[]
for soc,name,base,future,growth,openings,wage in [
    ('15-2051','Data scientists',275.6,371.0,34.6,24.8,120230),
    ('15-1252','Software developers',1717.8,1892.6,10.2,95.3,135980),
    ('15-1212','Information security analysts',192.9,233.4,21.0,14.1,129180),
    ('15-2031','Operations research analysts',113.1,126.6,11.9,7.5,88940),
    ('13-1111','Management analysts',1077.1,1186.3,10.1,94.1,101860),
    ('43-4051','Customer service representatives',2666.0,2524.1,-5.3,289.5,44770)]:
    records.append(dict(source_id='BLS-EMP-2025-35',source_url=bls,retrieved_at='2026-11-16',source_vintage='2025-2035 table accessed 2026-11-16',geography='US',unit_of_observation='SOC occupation',period='2025/2035',currency='USD',price_year=2025,schema_version='portfolio.v1',status='estimated',occupation_id='SOC2018:'+soc,source_native_id=soc,taxonomy='SOC',taxonomy_version='2018',occupation=name,employment_2025_thousands=base,employment_2035_thousands=future,projected_growth_percent=growth,annual_openings_thousands=openings,median_annual_wage_2025=wage,measurement_note='2025 employment and wage are published estimates; 2035 levels, growth and annual openings are BLS projections, not vacancies observed at sampled firms.'))
save('labor',records)

workforce=[]
for year,total,ops,rd,sales,admin in [(2023,221000,89000,72000,45000,15000),(2024,228000,86000,81000,45000,16000)]:
    for function,value in [('Operations',ops),('Research and development',rd),('Sales and marketing',sales),('General and administration',admin)]:
        workforce.append(dict(source_id=f'MSFT-{year}',source_url=f'https://www.microsoft.com/investor/reports/ar{str(year)[2:]}/index.html',retrieved_at='2026-11-16',source_vintage=f'FY{year}',geography='Global consolidated',unit_of_observation='company function employment stock',period=f'{year}-06-30',currency=None,price_year=None,schema_version='portfolio.v1',status='observed',company_id='US:SEC-CIK:0000789019',function=function,employees=value,total_employees=total,locator='Human Capital Resources',note='Rounded full-time employee counts disclosed by Microsoft; functions are not occupations, skills or vacancy counts.'))
save('workforce',workforce)

jobs=[
dict(job_id='10594978',employer='Amazon',title='Economist, Prime Video Science',source_url='https://www.amazon.jobs/en/jobs/10594978/economist-prime-video-science-prime-video-science',requirements=['Evaluate AI systems with benchmarks','Design experiments and analyze model outputs','Communicate evidence to business leaders'],skills=['evaluation','quantitative_analysis','communication'],artifacts=['evaluation.json','executive-brief.md','methodology.md'],limits='This project demonstrates descriptive measurement and evaluation; it does not demonstrate a causal experiment.'),
dict(job_id='R00289515',employer='Accenture',title='AI & Data Strategy — Manager',source_url='https://www.accenture.com/us-en/careers/jobdetails?id=R00289515_en',requirements=['Assess AI opportunities and peer benchmarks','Build quantitative business cases','Develop roadmaps and executive presentations'],skills=['ai_strategy','business_case','roadmap'],artifacts=['executive-report.md','strategy.json','management-presentation.md'],limits='Public evidence and a consulting scenario; no paid client or enterprise implementation claim.'),
dict(job_id='R00354757',employer='Accenture',title='Talent & Workforce Industry & Process Advisor Manager, Banking',source_url='https://www.accenture.com/us-en/careers/jobdetails?id=R00354757_en',requirements=['Model workforce scenarios and acquisition costs','Connect skills-based mobility to operating decisions','Translate labor-market evidence into an executable roadmap'],skills=['workforce_modeling','business_case','roadmap','communication'],artifacts=['strategy.json','labor.json','roadmap.md'],limits='Does not establish a representative vacancy sample, people management experience or vendor platform certification.')]
for j in jobs:j.update(source_id='JD-'+j['job_id'],company_id='US:SEC-CIK:'+('0001018724' if j['employer']=='Amazon' else '0001467373'),source_native_id=j['job_id'],source_vintage='Page accessed 2026-11-16; posting date not stated',retrieved_at='2026-11-16',geography='Employer-listed location; role requirements only',unit_of_observation='selected job description',period='2026-11-16',currency=None,price_year=None,schema_version='portfolio.v1',status='observed',skill_coding_status='estimated',skill_taxonomy='corporate-ai-role-tags',skill_taxonomy_version='1.0')
save('jobs',jobs)

skills=[]
for sid,label,demand,tc,rc,hc in [('evaluation','AI evaluation and controls',8,8,3,12),('workflow','Workflow and domain integration',12,12,5,16),('data','Data engineering and governance',6,4,2,10)]:
    routes={
      'train':dict(capacity=tc,success_rate=.8,ready_month=4,upfront_cost=9000,annual_recurring_cost=12000),
      'redeploy':dict(capacity=rc,success_rate=.9,ready_month=2,upfront_cost=5000,annual_recurring_cost=42000),
      'hire':dict(capacity=hc,success_rate=1.,ready_month=3,upfront_cost=24000,annual_recurring_cost=150000)}
    skills.append(dict(skill_id=sid,label=label,taxonomy='corporate-ai-capabilities',taxonomy_version='1.0',demand=demand,routes=routes))
save('scenario',dict(schema_version='portfolio.v1',source_id='SCENARIO-BANK-01',source_url=None,retrieved_at='2026-11-16',source_vintage='Scenario v1',geography='US hypothetical business unit',unit_of_observation='incremental productive capability equivalent',period='36 months from decision',currency='USD',price_year=2026,status='scenario',name='Bank operations AI capability build',horizon_months=36,deadline_months=6,annual_discount_rate=.08,annual_value_per_capability=180000,upfront_budget=400000,skills=skills,assumptions=['Fictional 200-person bank operations unit; not a client or a staffing estimate for JPMorgan/BAC.','Demand represents distinct, non-overlapping capability assignments. Candidate pools are disjoint across skills and routes.','Upfront training cost is $5,000 instruction plus 80 learning hours at $50 per hour; redeployment $5,000; recruiting and onboarding $24,000.','Annual recurring costs are incremental pay/license uplift ($12,000 training), backfill/opportunity cost ($42,000 redeployment), and fully loaded new-hire cost ($150,000). Existing base payroll is common to the decision and excluded.','Recurring costs apply to every candidate from month 1, including unsuccessful candidates. Benefits accrue only to expected successful capability after readiness. No salvage value, tax or inflation.','Success rates represent expected attainment, not guaranteed headcount. No attrition after attainment; no claim about displacement or headcount reduction.','Annual value is modeled gross incremental operating contribution per successful capability; it is neither estimated from filings nor a BLS wage.']))
