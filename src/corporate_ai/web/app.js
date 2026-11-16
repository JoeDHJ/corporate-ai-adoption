'use strict';
const ROUTES=['train','redeploy','hire'];
function flow(s,skill,counts){
  const flows=Array(s.horizon_months+1).fill(0), costs=Array(flows.length).fill(0);
  let ready=0,upfront=0;
  ROUTES.forEach((r,i)=>{const x=skill.routes[r],n=counts[i];const u=n*x.upfront_cost;upfront+=u;flows[0]-=u;costs[0]+=u;ready+=x.ready_month<=s.deadline_months?n*x.success_rate:0;
    for(let m=1;m<flows.length;m++){const cost=n*x.annual_recurring_cost/12;const benefit=m>x.ready_month?n*x.success_rate*s.annual_value_per_capability/12:0;costs[m]+=cost;flows[m]+=benefit-cost;}
  });
  const pv=a=>a.reduce((v,x,m)=>v+x/(1+s.annual_discount_rate)**(m/12),0);
  return {counts:Object.fromEntries(ROUTES.map((r,i)=>[r,counts[i]])),expected_ready:+ready.toFixed(6),upfront_cost:upfront,pv_cost:pv(costs),npv:pv(flows),cashflows:flows};
}
function solve(s,allowed=ROUTES){
  const choices=[];
  for(const skill of s.skills){
    const caps=ROUTES.map(r=>allowed.includes(r)&&skill.routes[r].ready_month<=s.deadline_months?skill.routes[r].capacity:0),opts=[];let capacityFeasible=false;
    for(let a=0;a<=caps[0];a++)for(let b=0;b<=caps[1];b++)for(let c=0;c<=caps[2];c++){
      const counts=[a,b,c],ready=ROUTES.reduce((z,r,i)=>z+counts[i]*skill.routes[r].success_rate,0);
      if(ready+1e-8<skill.demand)continue;
      capacityFeasible=true;const x=flow(s,skill,counts);if(x.upfront_cost<=s.upfront_budget)opts.push(x);
    }
    if(!opts.length)return {feasible:false,reason:(capacityFeasible?'Upfront budget cannot fund capability ':'Insufficient eligible capacity by deadline for ')+skill.skill_id};
    opts.sort((a,b)=>a.upfront_cost-b.upfront_cost||a.pv_cost-b.pv_cost);
    let best=Infinity;const frontier=[];for(const x of opts)if(x.pv_cost<best-1e-7){frontier.push(x);best=x.pv_cost;}
    choices.push(frontier);
  }
  let bestCost=Infinity,bestCombo=null;
  function visit(i,combo,cost,upfront){if(upfront>s.upfront_budget+1e-8)return;if(i===choices.length){if(cost<bestCost){bestCost=cost;bestCombo=combo.slice();}return;}for(const x of choices[i])visit(i+1,[...combo,x],cost+x.pv_cost,upfront+x.upfront_cost);}
  visit(0,[],0,0);
  if(!bestCombo)return {feasible:false,reason:'Upfront budget cannot fund a feasible mix'};
  const flows=Array(s.horizon_months+1).fill(0).map((_,m)=>bestCombo.reduce((v,x)=>v+x.cashflows[m],0));
  let total=0,payback=null;flows.forEach((x,m)=>{total+=x;if(total>=0&&payback===null)payback=m;});
  return {feasible:true,status:'scenario',upfront_cost:bestCombo.reduce((v,x)=>v+x.upfront_cost,0),pv_cost:bestCost,npv:bestCombo.reduce((v,x)=>v+x.npv,0),undiscounted_payback_month:payback,cashflows:flows,skills:bestCombo.map((x,i)=>({skill_id:s.skills[i].skill_id,demand:s.skills[i].demand,...x})),route_counts:Object.fromEntries(ROUTES.map(r=>[r,bestCombo.reduce((v,x)=>v+x.counts[r],0)]))};
}
function compare(s){return Object.fromEntries([['mixed',ROUTES],['training_only',['train']],['redeployment_only',['redeploy']],['hiring_only',['hire']]].map(([n,a])=>[n,solve(s,a)]));}
function evidenceCsv(rows){
  const fields=['evidence_id','company','period','review_label','review_scope','excerpt','source_url','locator'];
  const cell=value=>{let v=String(value??'');if(/^[=+\-@]/.test(v))v="'"+v;return '"'+v.replaceAll('"','""')+'"';};
  return [fields,...rows.map(r=>fields.map(f=>r[f]))].map(row=>row.map(cell).join(',')).join('\r\n');
}
if(typeof module!=='undefined')module.exports={flow,solve,compare,evidenceCsv};
if(typeof document!=='undefined'){
const D=JSON.parse(document.getElementById('case-data').textContent),$=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const short=n=>'$'+(n/1000000).toFixed(2)+'m';
const names={deployment:'Deployment',pilot:'Pilot / exploration',planned:'Planned',hiring_innovation:'People / innovation',promotional:'Promotional',risk:'Risk',none:'No AI evidence'};
const nice=s=>s.replaceAll('_',' ');
function download(name,value,type='application/json'){const blob=new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();$('download-status').textContent='Prepared '+name+' for download.';setTimeout(()=>URL.revokeObjectURL(url),10000);}
function tab(id){if(!$(id)||!$(id).classList.contains('panel'))id='overview';document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!==id);document.querySelectorAll('[data-tab]').forEach(b=>{b.classList.toggle('active',b.dataset.tab===id);b.setAttribute('aria-current',b.dataset.tab===id?'page':'false');});history.replaceState(null,'','#'+id);window.scrollTo(0,0);}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>tab(b.dataset.go));document.querySelector('.brand').onclick=e=>{e.preventDefault();tab('overview');};
$('metrics').innerHTML=[[D.summary.companies,'Companies · purposive peer group'],[D.summary.company_periods,'Annual-report periods'],[D.summary.reviewed_spans,'Selected, reviewed evidence spans'],[D.summary.internal_deployment_company_periods,'Periods with selected internal-use evidence']].map(([n,s])=>'<div class="metric"><strong>'+n+'</strong><span>'+s+'</span></div>').join('');
const counts=D.summary.review_labels,max=Math.max(...Object.values(counts));
$('label-chart').innerHTML=Object.entries(names).filter(([k])=>counts[k]).map(([k,v])=>'<div class="bar-row"><span>'+v+'</span><div class="bar-bg"><div class="bar-fill '+(k==='deployment'?'':'gray')+'" style="width:'+counts[k]/max*100+'%"></div></div><b>'+counts[k]+'</b></div>').join('');
const base=D.strategies.mixed;
$('decision-summary').innerHTML=base.feasible?'<p><strong>'+base.route_counts.train+' training candidates + '+base.route_counts.redeploy+' redeployments + '+base.route_counts.hire+' external hire(s)</strong><br>'+money(base.upfront_cost)+' upfront · '+short(base.pv_cost)+' 36-month PV cost</p>':'<p>Base scenario is infeasible under the stated constraints.</p>';
$('brief-export').onclick=()=>download('corporate-ai-decision-brief.md','# Corporate AI Adoption — Decision Brief\n\nTen companies, FY2023–FY2024. '+D.summary.reviewed_spans+' selected source spans. Evidence records are available in the portfolio.v1 export.\n\nThe base workforce scenario uses '+JSON.stringify(base.route_counts)+', with '+money(base.upfront_cost)+' upfront spend and '+money(base.npv)+' NPV over 36 months. Costs, success rates and value are scenario assumptions, not observed company outcomes.\n\nUse the 90/180/365-day roadmap to validate workflow quality, attainment and incremental value before scaling.\n\nAuthor: Haojian Dui\n','text/markdown');
for(const c of [...new Set(D.evidence.map(r=>r.company))].sort())$('company-filter').insertAdjacentHTML('beforeend','<option>'+esc(c)+'</option>');
for(const [k,v]of Object.entries(names))$('label-filter').insertAdjacentHTML('beforeend','<option value="'+k+'">'+v+'</option>');
function filtered(){const q=$('search').value.toLowerCase();return D.evidence.filter(r=>(!$('company-filter').value||r.company===$('company-filter').value)&&(!$('year-filter').value||r.period===$('year-filter').value)&&(!$('label-filter').value||r.review_label===$('label-filter').value)&&(!q||[r.excerpt,r.review_reason,r.company,r.review_scope].join(' ').toLowerCase().includes(q)));}
function evidence(){const rows=filtered();$('evidence-count').textContent=rows.length+' of '+D.evidence.length+' selected evidence spans. A missing match does not establish non-adoption.';$('evidence-cards').innerHTML=rows.length?rows.map(r=>'<article class="card evidence"><div class="evidence-title"><strong>'+esc(r.company)+' / FY'+r.period+'</strong><span class="pill">'+names[r.review_label]+'</span></div><blockquote>'+esc(r.excerpt)+'</blockquote><div class="tag '+(r.review_scope==='internal'?'':'blue')+'">'+esc(nice(r.review_scope))+'</div><p>'+esc(r.review_reason)+'</p><p class="fine">Context rules: '+names[r.classifier.label]+' · '+esc(r.classifier.rule)+'<br>'+esc(r.evidence_id)+' · '+esc(r.locator)+' · retrieved '+esc(r.retrieved_at)+'</p><a href="'+esc(r.source_url)+(r.source_format==='pdf'?'#page='+r.page:'')+'" target="_blank" rel="noopener">Check original source ↗</a></article>').join(''):'<div class="card empty">No evidence matches these filters. Try another company, label or search term.</div>';}
['company-filter','year-filter','label-filter','search'].forEach(id=>$(id).addEventListener('input',evidence));evidence();
$('evidence-export').onclick=()=>download('selected-evidence.csv',evidenceCsv(filtered()),'text/csv');
const functions=[...new Set(D.workforce.map(r=>r.function))];
$('workforce-chart').innerHTML='<div class="legend"><span><i class="blue"></i>FY2023</span><span><i></i>FY2024</span></div>'+functions.map(f=>{const rows=D.workforce.filter(r=>r.function===f);return '<h3>'+esc(f)+'</h3>'+rows.map((r,i)=>'<div class="bar-row"><span>'+r.employees.toLocaleString()+' people</span><div class="bar-bg"><div class="bar-fill '+(i===0?'blue':'')+'" style="width:'+r.employees/r.total_employees*200+'%"></div></div><b>'+(r.employees/r.total_employees*100).toFixed(1)+'%</b></div>').join('');}).join('');
const rd=D.workforce.filter(r=>r.function==='Research and development'),pp=(rd[1].employees/rd[1].total_employees-rd[0].employees/rd[0].total_employees)*100;
$('workforce-finding').textContent='R&D rose by '+(rd[1].employees-rd[0].employees).toLocaleString()+' people and '+pp.toFixed(2)+' percentage points of total full-time employment. The figures do not identify an AI effect.';
$('labor-chart').innerHTML=D.labor.map(r=>'<div class="bar-row"><span>'+esc(r.occupation)+'</span><div class="bar-bg"><div class="bar-fill '+(r.projected_growth_percent<0?'gray':'blue')+'" style="width:'+Math.abs(r.projected_growth_percent)/35*100+'%"></div></div><b>'+r.projected_growth_percent+'%</b></div>').join('');
$('jobs').innerHTML=D.jobs.map(j=>'<div class="job"><span class="eyebrow">'+esc(j.employer)+'</span><h3>'+esc(j.title)+'</h3><ul>'+j.requirements.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul><a href="'+esc(j.source_url)+'" target="_blank" rel="noopener">Official role '+esc(j.job_id)+' ↗</a><p class="fine">'+esc(j.limits)+'</p></div>').join('');
$('evaluation').innerHTML='<table><thead><tr><th>Method</th><th>Agreement</th><th>Macro F1*</th></tr></thead><tbody>'+Object.entries(D.evaluation).map(([k,v])=>'<tr><td>'+nice(k)+'</td><td>'+v.correct+'/'+v.n+' ('+(v.accuracy*100).toFixed(1)+'%)</td><td>'+v.macro_f1_supported_labels.toFixed(3)+'</td></tr>').join('')+'</tbody></table><p class="fine">*Mean over labels represented in the reviewed set.</p>';
$('review-note').textContent=D.summary.review_process;
$('errors').innerHTML=D.evaluation.context_rules.errors.map(e=>'<p><a href="#evidence" data-eid="'+e.evidence_id+'">'+esc(e.evidence_id)+'</a>: review '+names[e.review]+'; rule '+names[e.predicted]+'</p>').join('')||'<p>No label disagreements in this selected set.</p>';
document.querySelectorAll('[data-eid]').forEach(a=>a.onclick=e=>{e.preventDefault();const r=D.evidence.find(x=>x.evidence_id===a.dataset.eid);$('company-filter').value=r.company;$('year-filter').value=r.period;$('label-filter').value='';$('search').value='';evidence();tab('evidence');});
$('portfolio-export').onclick=()=>download('portfolio.v1.json',D);
$('sources').innerHTML=D.company_periods.map(s=>'<tr><td>'+esc(s.company_name)+'</td><td>'+esc(s.industry)+'</td><td>'+s.source_vintage+'</td><td><a href="'+esc(s.source_url)+'" target="_blank" rel="noopener">Official report ↗</a><br>'+esc(s.retrieved_at)+'</td><td>'+s.reviewed_spans+'</td></tr>').join('');
let lastScenario=structuredClone(D.scenario),lastResult=D.strategies;
function cashChart(result){if(!result.feasible){$('cashflow-chart').innerHTML='<p>No feasible plan; no cash-flow path is shown.</p>';return;}
  let sum=0;const values=result.cashflows.map(x=>sum+=x),lo=Math.min(0,...values),hi=Math.max(0,...values),w=560,h=210,p=38,y=v=>h-p-(v-lo)/Math.max(1,hi-lo)*(h-2*p),x=i=>p+i/(values.length-1)*(w-2*p),points=values.map((v,i)=>x(i)+','+y(v)).join(' ');
  $('cashflow-chart').innerHTML='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Cumulative undiscounted cash flow in USD"><line x1="'+p+'" y1="'+y(0)+'" x2="'+(w-p)+'" y2="'+y(0)+'" stroke="#c4d1cc"/><polyline points="'+points+'" fill="none" stroke="#007f79" stroke-width="3"/><text x="'+p+'" y="18" font-size="11" fill="#526773">'+money(hi)+'</text><text x="'+p+'" y="'+(h-6)+'" font-size="11" fill="#526773">Month 0 · '+money(values[0])+'</text><text text-anchor="end" x="'+(w-p)+'" y="'+(h-6)+'" font-size="11" fill="#526773">Month 36 · '+money(values.at(-1))+'</text></svg>';
}
function displayScenario(s,result){$('scenario-export').disabled=false;lastScenario=s;lastResult=result;const m=result.mixed;
  if(!m.feasible)$('scenario-result').innerHTML='<p class="warning">'+esc(m.reason)+'</p>';
  else $('scenario-result').innerHTML='<div class="numbers"><div><strong>'+money(m.upfront_cost)+'</strong><span>Upfront spend</span></div><div><strong>'+short(m.pv_cost)+'</strong><span>36-month PV cost</span></div><div><strong>'+short(m.npv)+'</strong><span>NPV · assumed value</span></div></div><div class="scenario-note">'+m.route_counts.train+' training candidates · '+m.route_counts.redeploy+' redeployments · '+m.route_counts.hire+' hire(s). Undiscounted payback: '+(m.undiscounted_payback_month===null?'not reached':m.undiscounted_payback_month+' months')+'.</div><div class="tablewrap"><table><thead><tr><th>Capability</th><th>Demand</th><th>Expected ready</th><th>Train / move / hire</th></tr></thead><tbody>'+m.skills.map(x=>'<tr><td>'+esc(s.skills.find(k=>k.skill_id===x.skill_id).label)+'</td><td>'+x.demand+'</td><td>'+x.expected_ready.toFixed(1)+'</td><td>'+ROUTES.map(r=>x.counts[r]).join(' / ')+'</td></tr>').join('')+'</tbody></table></div>';
  if(m.feasible&&m.npv<0)$('scenario-result').innerHTML+='<p class="warning">Negative NPV under the contribution assumption. Meeting the capability requirement does not by itself justify investment.</p>';
  $('scenario-result').innerHTML+='<h3>Alternative route policies</h3><table><thead><tr><th>Policy</th><th>Feasibility / PV cost</th></tr></thead><tbody>'+Object.entries(result).map(([n,r])=>'<tr><td>'+nice(n)+'</td><td>'+(r.feasible?money(r.pv_cost):'Infeasible: '+esc(r.reason))+'</td></tr>').join('')+'</tbody></table>';
  $('assumptions').innerHTML='<ul>'+s.assumptions.map(a=>'<li>'+esc(a)+'</li>').join('')+'</ul><p class="fine">Annual modeled contribution: '+money(s.annual_value_per_capability)+' per successful capability; annual discount rate: '+s.annual_discount_rate*100+'%.</p>';
  $('route-inputs').innerHTML='<div class="tablewrap"><table><thead><tr><th>Skill / route</th><th>Capacity</th><th>Success</th><th>Ready month</th><th>Upfront / annual cost</th></tr></thead><tbody>'+s.skills.flatMap(k=>ROUTES.map(r=>{const z=k.routes[r];return '<tr><td>'+esc(k.skill_id+' / '+r)+'</td><td>'+z.capacity+'</td><td>'+z.success_rate*100+'%</td><td>'+z.ready_month+'</td><td>'+money(z.upfront_cost)+' / '+money(z.annual_recurring_cost)+'</td></tr>';})).join('')+'</tbody></table></div>';cashChart(m);
}
function run(){for(const id of ['budget','hire-delay','annual-value'])if(!$(id).checkValidity()){$('scenario-export').disabled=true;$(id).reportValidity();return;}
  const s=structuredClone(D.scenario);s.upfront_budget=Number($('budget').value);s.annual_value_per_capability=Number($('annual-value').value);
  if(!$('budget').value||!$('hire-delay').value||!$('annual-value').value){$('scenario-export').disabled=true;$('scenario-result').innerHTML='<p class="warning">Enter budget, readiness and contribution values; zero is allowed.</p>';return;}
  for(const k of s.skills){k.demand=Math.round(k.demand*Number($('demand').value)/100);k.routes.train.success_rate=Number($('success').value)/100;k.routes.hire.ready_month=Number($('hire-delay').value);}
  displayScenario(s,compare(s));
}
for(const id of ['success','demand'])$(id).oninput=()=>$(id+'-value').textContent=$(id).value+'%';
$('run-scenario').onclick=run;$('reset-scenario').onclick=()=>{$('success').value=80;$('demand').value=100;$('success-value').textContent='80%';$('demand-value').textContent='100%';$('budget').value=400000;$('hire-delay').value=3;$('annual-value').value=180000;displayScenario(structuredClone(D.scenario),D.strategies);};
$('scenario-export').onclick=()=>download('workforce-scenario.json',{...Object.fromEntries(['source_id','source_url','retrieved_at','source_vintage','geography','unit_of_observation','period','currency','price_year','schema_version','status'].map(k=>[k,lastScenario[k]])),inputs:lastScenario,results:lastResult});
displayScenario(lastScenario,lastResult);tab(location.hash.slice(1)||'overview');
}
