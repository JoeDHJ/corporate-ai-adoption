"""Reusable analytical exhibits; PNG and SVG only."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from corporate_ai.pipeline import analyze
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=analyze();r=d['reliability'];w=d['workflow'];OUT=ROOT/'docs/figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#b3c7c3','text.color':'#142f3b','axes.labelcolor':'#526773','xtick.color':'#526773','ytick.color':'#526773'})
fig,axs=plt.subplots(1,2,figsize=(13.5,6.5),facecolor='#f5f4ee');fig.subplots_adjust(left=.19,right=.97,top=.73,bottom=.30,wspace=.5)
fig.text(.06,.92,'A rollout is a starting point. Readiness and value decide scale.',size=17,weight='bold')
fig.text(.06,.855,'Corporate AI Adoption and Workforce Strategy · public research case · v2.0.0',size=10,color='#526773')
mean=r['expected_coverage_plan'];p90=next(x for x in r['allocated_policy_curve'] if x['confidence_target']==.9)
ax=axs[0];vals=[mean['joint_probability_independent']*100,p90['joint_probability_independent']*100]
bars=ax.barh(['Expected-coverage\nstaffing','90% allocated\nreliability'],vals,color=['#8b9ea5','#007f79'],height=.55)
ax.set_xlim(0,110);ax.set_xlabel('Conditional joint attainment (%)');ax.invert_yaxis();ax.set_title('1. Readiness needs reserve capacity',loc='left',pad=18,size=12)
for bar,value,cost in zip(bars,vals,[mean['pv_cost'],p90['pv_cost']]):
    ax.text(value+2,bar.get_y()+bar.get_height()/2,f'{value:.1f}%',va='center',size=11,weight='bold')
    ax.text(3,bar.get_y()+bar.get_height()/2,f'${cost/1e6:.2f}m personnel PV',va='center',size=9,color='white')
ax=axs[1];vals=[0,w['options'][0]['npv']/1e6,w['options'][1]['npv']/1e6]
bars=ax.bar(['No action','25% scale','50% scale'],vals,color=['#aebeba','#8b9ea5','#007f79'],width=.55)
ax.set_ylim(-.08,2.35);ax.set_ylabel('36-month workflow NPV (USD million)');ax.set_title('2. Select a feasible investment scale',loc='left',pad=18,size=12);ax.axhline(0,color='#b3c7c3',lw=.7)
for bar,value in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,value+.08,f'${value:.2f}m',ha='center',weight='bold')
ax.text(.5,.96,'100% scale: cash-constrained',transform=ax.transAxes,ha='center',va='top',size=9,color='#8b4238')
fig.text(.06,.05,'Notes: conditional Bernoulli scenarios; success, workload, costs and value are assumptions.\nLeft: original fixed skill demands. Right: workload-derived demand with integration/platform costs and value counted once.\nOptimization covers three predefined scales and equal per-skill failure-budget policies; no observed client savings.',size=9,color='#526773',linespacing=1.6)
for ext in ['png','svg']:fig.savefig(OUT/f'v2-decision.{ext}',dpi=180,facecolor=fig.get_facecolor())
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.8));feasible=[x for x in r['allocated_policy_curve'] if x['feasible']]
ax.plot([x['confidence_target']*100 for x in feasible],[x['pv_cost']/1e6 for x in feasible],marker='o',color='#007f79')
ax.set(xlabel='Allocated joint reliability target (%)',ylabel='Personnel PV cost (USD million)',title='Cost of a more demanding readiness policy')
fig.text(.12,.02,'Equal failure-budget policy class; not the globally efficient frontier.\n95% and 99% targets infeasible under base cash/capacity. Scenario, constant USD 2026.',size=9,color='#526773');fig.tight_layout(rect=(0,.12,1,1))
for ext in ['png','svg']:fig.savefig(OUT/f'v2-reliability.{ext}',dpi=180)
plt.close(fig)
print('Wrote two v2 exhibits in PNG and SVG.')
