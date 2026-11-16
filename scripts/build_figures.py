"""Static, exportable exhibits from actual coded data and the explicit scenario."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from corporate_ai.pipeline import analyze
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'docs/figures';out.mkdir(parents=True,exist_ok=True)
d=analyze()
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#d8dfdc','text.color':'#142f3b','axes.labelcolor':'#142f3b','xtick.color':'#526773','ytick.color':'#142f3b','figure.facecolor':'#f5f4ee','axes.facecolor':'#f5f4ee'})
fig,axs=plt.subplots(1,2,figsize=(13,5.2),gridspec_kw={'width_ratios':[1.2,1]})
labels=['Deployment','People / innovation','Planned','Promotional','Pilot / exploration','Risk']
counts=[23,11,8,8,5,5]
axs[0].barh(labels[::-1],counts[::-1],color=['#8b9ea5']*5+['#007f79'],height=.6)
axs[0].set_xlim(0,27);axs[0].set_xlabel('Selected evidence spans (n=60)')
axs[0].set_title('Public disclosure: meaning before counting',loc='left',fontweight='bold',pad=20)
for i,v in enumerate(counts[::-1]):axs[0].text(v+.35,i,str(v),va='center')
m=d['strategies']['mixed'];route=['Training candidates','Internal redeployments','External hires'];values=[m['route_counts'][r] for r in ['train','redeploy','hire']]
axs[1].barh(route[::-1],values[::-1],color='#4567a4',height=.6)
axs[1].set_xlim(0,29);axs[1].set_xlabel('Candidate decisions (scenario)')
axs[1].set_title('Bank unit: a constrained capability plan',loc='left',fontweight='bold',pad=20)
for i,v in enumerate(values[::-1]):axs[1].text(v+.35,i,str(v),va='center')
fig.suptitle('Corporate AI Adoption and Workforce Strategy',x=.02,y=.98,ha='left',fontsize=18,fontweight='bold')
fig.text(.02,.045,'Left: three reviewed spans per FY2023/FY2024 report, ten firms; purposive selection, not adoption prevalence.\nRight: fictional costs, capacities and attainment; $275,000 upfront, $2.23m PV cost over 36 months. Source: portfolio.v1.',fontsize=9,color='#526773')
fig.subplots_adjust(left=.15,right=.97,wspace=.75,top=.78,bottom=.24)
fig.savefig(out/'decision-evidence.png',dpi=170)
fig.savefig(out/'decision-evidence.svg')
print('Saved static analytical exhibits.')
