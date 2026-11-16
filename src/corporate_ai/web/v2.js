'use strict';
const R2=['train','redeploy','hire'];
const pmfCache2=new Map();
function workloadDemand2(volume,minutes,hours){const x=volume*minutes/60/hours;if(!Number.isFinite(x)||x<0||x>100+1e-8)throw Error('Derived workload FTE must be between 0 and 100.');return Math.max(0,Math.ceil(x-1e-12*Math.max(1,Math.abs(x))));}
function rankEvidence2(rows,query){const terms=query.toLowerCase().match(/[a-z0-9]+/g)||[];if(!terms.length)return rows.slice();return rows.map((r,i)=>({r,i,score:terms.reduce((n,t)=>n+r.excerpt.toLowerCase().split(t).length-1,0)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.i-b.i).map(x=>x.r);}
function risk2(s,sk,counts){
  const ps=R2.map(r=>sk.routes[r].ready_month<=s.deadline_months?sk.routes[r].success_rate:0),key=JSON.stringify([counts,ps]);
  let pmf=pmfCache2.get(key);
  if(!pmf){pmf=[1];counts.forEach((n,i)=>{for(let j=0;j<n;j++){const next=Array(pmf.length+1).fill(0);pmf.forEach((v,k)=>{next[k]+=v*(1-ps[i]);next[k+1]+=v*ps[i];});pmf=next;}});if(pmfCache2.size>8192)pmfCache2.clear();pmfCache2.set(key,pmf);}
  return {probability_meeting_demand:Math.min(1,pmf.slice(sk.demand).reduce((a,b)=>a+b,0)),expected_shortfall:pmf.reduce((a,v,k)=>a+Math.max(0,sk.demand-k)*v,0)};
}
function reliable2(s,q){
  const floor=1-(1-q)/s.skills.length,choices=[];
  for(const sk of s.skills){
    const caps=R2.map(r=>sk.routes[r].ready_month<=s.deadline_months?sk.routes[r].capacity:0),opts=[];
    for(let a=0;a<=caps[0];a++)for(let b=0;b<=caps[1];b++)for(let c=0;c<=caps[2];c++){
      const counts=[a,b,c],up=R2.reduce((v,r,i)=>v+counts[i]*sk.routes[r].upfront_cost,0);
      if(up>s.upfront_budget+1e-8||risk2(s,sk,counts).probability_meeting_demand+1e-12<floor)continue;
      opts.push(flow(s,sk,counts));
    }
    if(!opts.length)return {feasible:false,confidence_target:q,reason:'No route mix meets allocated reliability and cash constraints for '+sk.skill_id};
    opts.sort((a,b)=>a.upfront_cost-b.upfront_cost||a.pv_cost-b.pv_cost);let best=Infinity;const front=[];
    for(const x of opts)if(x.pv_cost<best-1e-7){front.push(x);best=x.pv_cost;}choices.push(front);
  }
  let best=null,cost=Infinity;
  function visit(i,combo,pv,up){if(up>s.upfront_budget+1e-8)return;if(i===choices.length){if(pv<cost){cost=pv;best=combo.slice();}return;}for(const x of choices[i])visit(i+1,[...combo,x],pv+x.pv_cost,up+x.upfront_cost);}
  visit(0,[],0,0);if(!best)return {feasible:false,confidence_target:q,reason:'Shared upfront budget cannot fund a reliable plan'};
  const risks=best.map((x,i)=>risk2(s,s.skills[i],R2.map(r=>x.counts[r])));
  return {feasible:true,confidence_target:q,per_skill_probability_floor:floor,status:'scenario',
    upfront_cost:best.reduce((v,x)=>v+x.upfront_cost,0),pv_cost:cost,npv:best.reduce((v,x)=>v+x.npv,0),
    skills:best.map((x,i)=>({skill_id:s.skills[i].skill_id,demand:s.skills[i].demand,...x})),
    route_counts:Object.fromEntries(R2.map(r=>[r,best.reduce((v,x)=>v+x.counts[r],0)])),
    joint_probability_independent:risks.reduce((v,x)=>v*x.probability_meeting_demand,1),
    joint_probability_lower_bound:Math.max(0,1-risks.reduce((v,x)=>v+1-x.probability_meeting_demand,0)),
    skill_risks:risks,expected_total_shortfall:risks.reduce((v,x)=>v+x.expected_shortfall,0)};
}
function workflowPlan2(s,q,monthlyValue,launchFloor){
  if(monthlyValue<=0)return reliable2(s,q);
  const floor=1-(1-q)/s.skills.length,pools=[];
  for(const sk of s.skills){
    const caps=R2.map(r=>sk.routes[r].ready_month<=s.deadline_months?sk.routes[r].capacity:0),opts=[];
    for(let a=0;a<=caps[0];a++)for(let b=0;b<=caps[1];b++)for(let c=0;c<=caps[2];c++){
      const counts=[a,b,c],up=R2.reduce((v,r,i)=>v+counts[i]*sk.routes[r].upfront_cost,0);if(up>s.upfront_budget+1e-8)continue;
      const p=risk2(s,sk,counts).probability_meeting_demand;if(p+1e-12<floor)continue;
      const launch=Math.max(launchFloor,...R2.filter((r,i)=>counts[i]).map(r=>sk.routes[r].ready_month));
      opts.push({...flow(s,sk,counts),probability:p,launch});
    }
    opts.sort((a,b)=>a.upfront_cost-b.upfront_cost||a.pv_cost-b.pv_cost);const front=[];
    for(const x of opts)if(!front.some(y=>y.pv_cost<=x.pv_cost+1e-7&&y.probability>=x.probability-1e-12&&y.launch<=x.launch))front.push(x);
    if(!front.length)return {feasible:false,reason:'No route mix meets allocated reliability and cash constraints for '+sk.skill_id};pools.push(front);
  }
  const factors=Array(s.horizon_months+1).fill(0);for(let m=0;m<=s.horizon_months;m++)for(let t=m+1;t<=s.horizon_months;t++)factors[m]+=1/(1+s.annual_discount_rate)**(t/12);
  let best=null,bestNpv=-Infinity;
  function visit(i,combo,up,cost,p,launch){if(up>s.upfront_budget+1e-8)return;if(i===pools.length){const npv=monthlyValue*p*factors[launch]-cost;if(npv>bestNpv+1e-7){bestNpv=npv;best=combo.slice();}return;}for(const x of pools[i])visit(i+1,[...combo,x],up+x.upfront_cost,cost+x.pv_cost,p*x.probability,Math.max(launch,x.launch));}
  visit(0,[],0,0,1,launchFloor);if(!best)return {feasible:false,reason:'Shared upfront budget cannot fund a reliable plan'};
  const risks=best.map((x,i)=>risk2(s,s.skills[i],R2.map(r=>x.counts[r])));
  return {feasible:true,status:'scenario',confidence_target:q,per_skill_probability_floor:floor,
    objective:'Maximum workflow NPV within equal per-skill failure-budget allocation; joint comparison of cost, readiness and reliability',
    upfront_cost:best.reduce((v,x)=>v+x.upfront_cost,0),pv_cost:best.reduce((v,x)=>v+x.pv_cost,0),
    skills:best.map((x,i)=>({skill_id:s.skills[i].skill_id,demand:s.skills[i].demand,...x})),route_counts:Object.fromEntries(R2.map(r=>[r,best.reduce((v,x)=>v+x.counts[r],0)])),
    skill_risks:risks,joint_probability_independent:risks.reduce((v,x)=>v*x.probability_meeting_demand,1),joint_probability_lower_bound:Math.max(0,1-risks.reduce((v,x)=>v+1-x.probability_meeting_demand,0)),expected_total_shortfall:risks.reduce((v,x)=>v+x.expected_shortfall,0)};
}
function validateCase2(s,w){
  const num=(x,name,min=0,max=Infinity,integer=false)=>{if(typeof x!=='number'||!Number.isFinite(x)||x<min||x>max||(integer&&!Number.isInteger(x)))throw Error('Invalid '+name);};
  if(!s||!w||typeof s!=='object'||typeof w!=='object')throw Error('Import requires scenario and workflow objects.');
  for(const k of ['source_id','retrieved_at','source_vintage','geography','unit_of_observation','period','currency'])if(typeof s[k]!=='string'||!s[k].trim())throw Error('Missing scenario '+k);
  if(s.schema_version!=='portfolio.v1'||s.status!=='scenario')throw Error('Use portfolio.v1 with scenario status.');
  for(const k of ['source_id','retrieved_at','source_vintage','geography','unit_of_observation','period','currency'])if(typeof w[k]!=='string'||!w[k].trim())throw Error('Missing workflow '+k);
  if(w.schema_version!=='portfolio.v1'||w.status!=='scenario'||!('source_url' in w)||(w.source_url!==null&&!(typeof w.source_url==='string'&&/^https:\/\/[^/]+/.test(w.source_url))))throw Error('Invalid workflow provenance.');
  const wd=w.retrieved_at.slice(0,10),wv=new Date(wd+'T00:00:00Z');if(!/^\d{4}-\d{2}-\d{2}$/.test(wd)||Number.isNaN(wv.getTime())||wv.toISOString().slice(0,10)!==wd)throw Error('Invalid workflow retrieval date.');
  const datePart=typeof s.retrieved_at==='string'?s.retrieved_at.slice(0,10):'',dateValue=new Date(datePart+'T00:00:00Z');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(datePart)||Number.isNaN(dateValue.getTime())||dateValue.toISOString().slice(0,10)!==datePart)throw Error('Invalid retrieved_at date.');
  if(s.currency!=='USD'||s.price_year!==2026||w.currency!==s.currency||w.price_year!==s.price_year)throw Error('Browser workflow cases require matching USD and 2026 price year.');
  if(s.source_url!==null&&!(typeof s.source_url==='string'&&/^https:\/\/[^/]+/.test(s.source_url)))throw Error('Invalid source URL.');
  num(s.price_year,'price year',1900,2100,true);num(s.horizon_months,'horizon',1,120,true);num(s.deadline_months,'deadline',1,s.horizon_months,true);
  num(s.annual_discount_rate,'discount rate',0,1);num(s.upfront_budget,'budget');num(s.annual_value_per_capability,'capability value');
  if(!Array.isArray(s.skills)||s.skills.length<1||s.skills.length>3)throw Error('Browser cases support 1–3 skills.');
  if(new Set(s.skills.map(x=>x.skill_id)).size!==s.skills.length)throw Error('Duplicate skills.');
  for(const sk of s.skills){if(typeof sk.skill_id!=='string'||!sk.skill_id)throw Error('Missing skill ID.');num(sk.demand,'demand',0,100,true);for(const r of R2){const x=sk.routes?.[r];if(!x)throw Error('All routes required.');num(x.capacity,'browser route capacity (max 30)',0,30,true);num(x.success_rate,'success',0,1);num(x.ready_month,'readiness',0,s.horizon_months,true);num(x.upfront_cost,'upfront cost');num(x.annual_recurring_cost,'recurring cost');}}
  for(const k of ['monthly_volume','baseline_minutes','assisted_minutes','rework_probability','rework_minutes','productive_hours_month','hour_value','realization_rate','integration_cost','annual_platform_cost','launch_month','confidence'])num(w[k],k,0,['rework_probability','realization_rate','confidence'].includes(k)?1:Infinity,k==='launch_month');
  if(w.productive_hours_month<=0||w.launch_month>s.horizon_months)throw Error('Check productive hours and launch month.');
  if(!Array.isArray(w.tasks)||w.tasks.length!==s.skills.length||new Set(w.tasks.map(x=>x.skill_id)).size!==w.tasks.length||w.tasks.some(t=>!s.skills.some(sk=>sk.skill_id===t.skill_id)))throw Error('Tasks must match skills exactly.');
  for(const t of w.tasks)num(t.minutes_per_item,'task minutes');
  for(const f of [.25,.5,1])for(const t of w.tasks)workloadDemand2(w.monthly_volume*f,t.minutes_per_item,w.productive_hours_month);
}
function workflow2(s,w){
  validateCase2(s,w);const options=[];
  for(const fraction of [.25,.5,1]){
    const trial=structuredClone(s),volume=w.monthly_volume*fraction,fixed=w.integration_cost*fraction;
    trial.upfront_budget=Math.max(0,s.upfront_budget-fixed);
    for(const sk of trial.skills)sk.demand=workloadDemand2(volume,w.tasks.find(t=>t.skill_id===sk.skill_id).minutes_per_item,w.productive_hours_month);
    const human=w.assisted_minutes+w.tasks.reduce((v,t)=>v+t.minutes_per_item,0)+w.rework_probability*w.rework_minutes,saved=volume*(w.baseline_minutes-human)/60;
    const plan=fixed<=s.upfront_budget?workflowPlan2(trial,w.confidence,saved*w.hour_value*w.realization_rate,w.launch_month):{feasible:false,reason:'Integration alone exceeds total upfront budget'};
    if(plan.feasible){delete plan.npv;delete plan.cashflows;plan.skills=plan.skills.map(x=>Object.fromEntries(Object.entries(x).filter(([k])=>!['npv','cashflows'].includes(k))));}
    const row={scale:fraction,monthly_volume:volume,staffing_inputs:trial,staffing:plan};
    if(plan.feasible){
      const delays=plan.skills.flatMap((x,i)=>R2.filter(r=>x.counts[r]).map(r=>trial.skills[i].routes[r].ready_month));
      const launch=Math.max(w.launch_month,...delays),reliability=plan.joint_probability_independent;
      let platform=0,factor=0;for(let m=1;m<=s.horizon_months;m++){const disc=(1+s.annual_discount_rate)**(m/12);platform+=w.annual_platform_cost*fraction/12/disc;if(m>launch)factor+=1/disc;}
      const costs=plan.pv_cost+fixed+platform,value=saved*w.hour_value*w.realization_rate*reliability*factor;
      Object.assign(row,{human_minutes_after:human,monthly_capacity_hours:saved,annual_capacity_fte:saved/w.productive_hours_month,launch_month:launch,pv_total_cost:costs,pv_realized_value:value,npv:value-costs,break_even_realization:saved*w.hour_value*reliability*factor>0?costs/(saved*w.hour_value*reliability*factor):null,upfront_with_integration:plan.upfront_cost+fixed});
    }options.push(row);
  }
  const feasible=options.filter(x=>x.staffing.feasible&&x.npv>0).sort((a,b)=>b.npv-a.npv);
  return {inputs:w,options,no_action_npv:0,recommended_scale:feasible[0]?.scale||0,decision:feasible.length?'Proceed to quality-gated pilot at the selected scale':'Defer investment; no tested feasible scale beats no action'};
}
if(typeof module!=='undefined'){
  // Node tests use the same cash-flow function as the legacy browser solver.
  global.flow=require('./app.js').flow;
  module.exports={risk2,reliable2,workflow2,workflowPlan2,validateCase2,workloadDemand2,rankEvidence2};
}
if(typeof document!=='undefined'){
const V=JSON.parse(document.getElementById('case-data').textContent),v=id=>document.getElementById(id),
e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
cash=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n),pct=n=>(n*100).toFixed(1)+'%';
function dl(name,obj,type='application/json'){const u=URL.createObjectURL(new Blob([typeof obj==='string'?obj:JSON.stringify(obj,null,2)],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),10000);v('download-status').textContent='Prepared '+name+' for download.';}
const bank=V.bank_case,mean=V.reliability.expected_coverage_plan,robust=V.reliability.allocated_policy_curve.find(x=>x.confidence_target===.9);
v('metrics').innerHTML=[['39.3%','Joint attainment · mean-coverage staffing¹'],['92.9%','Joint attainment · 90% allocated policy¹'],['50%','Workflow scale selected in the base case²'],[String(bank.sources.length),'Bank annual reports · FY2023–FY2025']].map(([a,b])=>'<div class="metric"><strong>'+a+'</strong><span>'+b+'</span></div>').join('');
v('label-chart').innerHTML='<div class="comparison-row"><span>Mean-coverage plan</span><strong>'+pct(mean.joint_probability_independent)+'</strong><div class="bar-bg"><div class="bar-fill gray" style="width:'+mean.joint_probability_independent*100+'%"></div></div><small>'+cash(mean.pv_cost)+' personnel PV cost</small></div><div class="comparison-row"><span>90% allocated-reliability policy</span><strong>'+pct(robust.joint_probability_independent)+'</strong><div class="bar-bg"><div class="bar-fill" style="width:'+robust.joint_probability_independent*100+'%"></div></div><small>'+cash(robust.pv_cost)+' personnel PV cost</small></div><p class="fine">¹ Conditional Bernoulli assumptions. The conservative joint lower bound for the 90% policy is '+pct(robust.joint_probability_lower_bound)+'. These are staffing scenarios, not measured employee probabilities.</p>';
v('decision-summary').innerHTML='<p><strong>50% scale · '+cash(V.workflow.options[1].npv)+' modeled NPV</strong><br>Full scale exceeds the combined staffing and integration cash cap.²</p>';
v('brief-export').onclick=()=>dl('corporate-ai-v2-decision-brief.md',brief2(V.scenario,V.workflow_inputs,V.workflow),'text/markdown');
function brief2(s,w,result){return '# Corporate AI Adoption — Decision Brief\n\nHaojian Dui · Public research case and explicit workforce scenario · v2.0.0\n\n'+bank.sources.length+' parsed bank reports in FY2023–FY2025; BAC FY2025 full-PDF collection failed. Internal use, customer products, rollout reach and active users are different measurements. Wells Fargo use and risk language coexist in a single disclosure.\n\nDecision: '+result.decision+'. Selected scale '+pct(result.recommended_scale)+'.\n\n'+result.options.map(r=>'Scale '+pct(r.scale)+': '+(r.staffing.feasible?'NPV '+cash(r.npv)+', upfront including integration '+cash(r.upfront_with_integration)+', joint conditional attainment '+pct(r.staffing.joint_probability_independent):r.staffing.reason)).join('\n')+'\n\nMonthly volume '+w.monthly_volume+'; baseline minutes '+w.baseline_minutes+'; realization '+pct(w.realization_rate)+'; total upfront cash cap '+cash(s.upfront_budget)+'. Workload, costs, success and value are scenario assumptions. Released capacity is not observed cash savings. Validate quality, task time, eligible skill pools and capacity monetization before investment.\n\nCode, sources and reproduction: https://github.com/JoeDHJ/corporate-ai-adoption\n';}
function matrix(){v('bank-matrix').innerHTML='<div class="tablewrap"><table class="matrix"><thead><tr><th>Reviewed internal-use evidence</th>'+['2023','2024','2025'].map(y=>'<th>FY'+y+'</th>').join('')+'</tr></thead><tbody>'+bank.coverage.target_banks.map(c=>'<tr><th>'+e(c)+'</th>'+bank.coverage.periods.map(y=>{const r=bank.company_periods.find(x=>x.company===c&&x.period===y);return '<td><button class="matrix-cell '+(!r?'missing':r.internal_use_evidence_ids.length?'found':'unknown')+'" data-bank="'+c+'" data-period="'+y+'">'+(!r?'Collection failed':r.internal_use_evidence_ids.length?'Use disclosed':'Unknown from review')+(r?.reviewed_risk_flag?'<small>Risk also reviewed</small>':'')+'</button></td>';}).join('')+'</tr>').join('')+'</tbody></table></div>';v('bank-matrix').querySelectorAll('button').forEach(b=>b.onclick=()=>{v('bank-company').value=b.dataset.bank;v('bank-period').value=b.dataset.period;renderBank();v('bank-results').scrollIntoView({behavior:'smooth',block:'start'});});}
for(const c of bank.coverage.target_banks)v('bank-company').insertAdjacentHTML('beforeend','<option>'+c+'</option>');
function bankRows(){const rows=bank.reviewed.filter(r=>(!v('bank-company').value||r.company===v('bank-company').value)&&(!v('bank-period').value||r.period===v('bank-period').value)&&(!v('bank-stage').value||r.review_axes.stages.includes(v('bank-stage').value)));const query=v('bank-query').value.trim();return query.startsWith('BANK-')?rows.filter(r=>r.evidence_id===query):rankEvidence2(rows,query);}
function renderBank(){const rows=bankRows();v('bank-count').textContent=rows.length+' reviewed spans. Full candidate inventory: '+bank.candidate_locations.length+' locations. Missing matches leave adoption unknown.';v('bank-results').innerHTML=rows.map(r=>'<article class="card evidence"><div class="evidence-title"><strong>'+e(r.company)+' · FY'+r.period+'</strong><span class="pill">'+e(r.review_label)+'</span></div><blockquote>'+e(r.excerpt)+'</blockquote><p>'+e(r.review_reason)+'</p><div class="axis-tags">'+[...r.review_axes.actors,...r.review_axes.stages,r.review_axes.technology,...(r.review_axes.risk?['risk also stated']:[])].map(a=>'<span class="tag">'+e(a.replaceAll('_',' '))+'</span>').join('')+'</div><p class="fine">'+e(r.evidence_id)+' · '+e(r.locator)+'<br>Exact event date: unknown. Assistant reference coding.</p><a target="_blank" rel="noopener" href="'+e(r.source_url)+'#page='+r.page+'">Check official report ↗</a></article>').join('')||'<article class="card empty">No reviewed span matches. BAC FY2025 collection failed; other empty results remain unknown.</article>';}
['bank-company','bank-period','bank-stage','bank-query'].forEach(id=>v(id).oninput=renderBank);matrix();renderBank();
for(const t of V.research_benchmark.tasks)v('task-preset').insertAdjacentHTML('beforeend','<option value="'+e(t.task_id)+'">'+e(t.task_id)+'</option>');
v('task-preset').onchange=()=>{const t=V.research_benchmark.tasks.find(x=>x.task_id===v('task-preset').value);if(!t)return;const source=bank.sources.find(s=>s.source_id===t.source_id);v('bank-company').value=source.company;v('bank-period').value=source.period;v('bank-stage').value='';v('bank-query').value=t.query;renderBank();};
v('bank-export').onclick=()=>dl('bank-evidence-filtered.json',{schema_version:'portfolio.v1',filters:{company:v('bank-company').value,period:v('bank-period').value,stage:v('bank-stage').value,query:v('bank-query').value},records:bankRows(),coverage:bank.coverage});
v('bank-source-list').innerHTML=bank.inventory.map(r=>'<tr><td>'+e(r.source_id)+'</td><td>'+r.pages_parsed+'</td><td>'+r.ai_lexicon_hits+'</td><td>'+r.eligible_sentence_candidates+'</td></tr>').join('');
const ev=bank.evaluation;v('grouped-evaluation').innerHTML='<table><thead><tr><th>Company holdout method</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead><tbody>'+Object.entries(ev.company_holdout).map(([name,r])=>'<tr><td>'+e(name.replaceAll('_',' '))+'</td><td>'+pct(r.precision)+'</td><td>'+pct(r.recall)+'</td><td>'+r.f1.toFixed(3)+'</td></tr>').join('')+'</tbody></table><p class="fine">'+ev.company_holdout.keyword.n+' selected assistant-reference rows. Rules were already developed against part of this material; their score remains a development diagnostic. TF-IDF training excludes the held-out company. FY2025 temporal check has only '+ev.time_holdout.tfidf_centroid.n+' rows. No independent human validation.</p>';
v('axis-evaluation').innerHTML='<table><thead><tr><th>Independent reference axis</th><th>Exact agreement</th></tr></thead><tbody>'+Object.entries(bank.axis_diagnostic).map(([k,x])=>'<tr><td>'+e(k)+'</td><td>'+x.exact_matches+' / '+x.n+'</td></tr>').join('')+'</tbody></table><p class="fine">'+e(bank.axis_reference_note)+'</p><details><summary>Inspect axis disagreements</summary>'+Object.entries(bank.axis_diagnostic).map(([k,x])=>'<h3>'+e(k)+'</h3>'+x.errors.map(r=>'<p>'+e(r.evidence_id)+': rule '+e(JSON.stringify(r.automatic))+'; reference '+e(JSON.stringify(r.reference))+'</p>').join('')).join('')+'</details>';
v('vacancy-case').innerHTML='<p>'+V.bank_vacancies.length+' readable Citi snapshots from '+V.vacancy_coverage.attempted_pages+' attempted official pages. Targeted AI-role search; no hiring trend or employer comparison.</p><div class="grid three">'+V.bank_vacancies.map(j=>'<div class="job"><h3>'+e(j.title)+'</h3><p>'+e(j.geography)+'</p><p>'+j.skills.map(e).join(' · ')+'</p><p class="fine">'+e(j.job_id)+' · '+e(j.seniority)+'<br>Base pay: '+(j.annual_base_pay_range?j.annual_base_pay_range.map(cash).join('–')+' USD':'not available / not parsed')+'</p><a href="'+e(j.source_url)+'" target="_blank" rel="noopener">Official role ↗</a></div>').join('')+'</div>';
v('risk-curve').innerHTML='<table><thead><tr><th>Allocated target</th><th>Conditional joint</th><th>Personnel PV cost</th><th>Train / move / hire</th></tr></thead><tbody>'+V.reliability.allocated_policy_curve.map(r=>'<tr><td>'+pct(r.confidence_target)+'</td><td>'+(r.feasible?pct(r.joint_probability_independent):'Infeasible')+'</td><td>'+(r.feasible?cash(r.pv_cost):'—')+'</td><td>'+(r.feasible?R2.map(k=>r.route_counts[k]).join(' / '):'Cash or capacity constraint')+'</td></tr>').join('')+'</tbody></table><p class="fine">Minimum cost within equal per-skill failure-budget allocations; not the globally efficient joint chance-constraint frontier. Common-shock stress: a 10% all-pools failure event would reduce the base 90% policy product probability to '+pct(.9*robust.joint_probability_independent)+'. This is an assumption stress, not an estimate.</p>';
let activeS=structuredClone(V.scenario),activeW=structuredClone(V.workflow_inputs),activeResult=V.workflow,dirty=false;
function controls(){v('case-volume').value=activeW.monthly_volume;v('case-realization').value=activeW.realization_rate*100;v('case-confidence').value=activeW.confidence;v('case-budget').value=activeS.upfront_budget;v('case-status').textContent='Current case: '+activeW.name;}
function drawCase(){
  v('case-export').disabled=false;v('case-brief').disabled=false;dirty=false;
  const result=activeResult;v('workflow-result').innerHTML='<div class="scenario-note"><strong>'+e(result.decision)+'</strong><br>Selected scale: '+pct(result.recommended_scale)+' · no-action NPV: $0</div><div class="scale-grid">'+result.options.map(r=>'<article class="scale-option '+(r.scale===result.recommended_scale?'selected':'')+'"><span class="eyebrow">'+pct(r.scale)+' SCALE</span><h2>'+(r.staffing.feasible?cash(r.npv):'Infeasible')+'</h2><p>'+(r.staffing.feasible?'Modeled 36-month NPV':'Under the current cash, capacity and reliability limits')+'</p>'+(r.staffing.feasible?'<p>'+cash(r.upfront_with_integration)+' upfront incl. integration<br>'+cash(r.pv_total_cost)+' total PV cost<br>'+pct(r.staffing.joint_probability_independent)+' joint conditional attainment</p><p>'+R2.map(k=>r.staffing.route_counts[k]+' '+k).join(' · ')+'</p><p>Break-even realization '+(r.break_even_realization===null?'unavailable':pct(r.break_even_realization))+'</p>':'<p>'+e(r.staffing.reason)+'</p>')+'</article>').join('')+'</div><p class="fine">Value is counted once per workflow, conditional on all skill requirements being met. Costs include training time, pay uplift, backfill, hires, platform operations and integration. Base payroll is common to alternatives. No observed employee time or cash saving is claimed.</p>';
  v('task-model').innerHTML='<table><thead><tr><th>Specialist task</th><th>Minutes / item</th><th>Monthly hours · full scale</th><th>Required FTE¹</th></tr></thead><tbody>'+activeW.tasks.map(t=>'<tr><td>'+e(t.label||t.skill_id)+'</td><td>'+t.minutes_per_item+'</td><td>'+(activeW.monthly_volume*t.minutes_per_item/60).toLocaleString()+'</td><td>'+workloadDemand2(activeW.monthly_volume,t.minutes_per_item,activeW.productive_hours_month)+'</td></tr>').join('')+'</tbody></table><p class="fine">¹ Monthly task hours ÷ '+activeW.productive_hours_month+' productive hours per person; round each distinct skill up. Assisted execution '+activeW.assisted_minutes+' minutes; expected rework '+(activeW.rework_probability*activeW.rework_minutes).toFixed(1)+' minutes; baseline '+activeW.baseline_minutes+' minutes. All task inputs are assumptions awaiting measurement.</p>';
  v('case-status').textContent='Calculated from the displayed inputs. Export includes all route and workflow assumptions.';
}
['case-volume','case-realization','case-confidence','case-budget'].forEach(id=>v(id).oninput=()=>{dirty=true;v('case-export').disabled=true;v('case-brief').disabled=true;v('case-status').textContent='Inputs changed. Recalculate to update the decision and exports.';});
v('case-run').onclick=()=>{try{const s=structuredClone(activeS),w=structuredClone(activeW);for(const id of ['case-volume','case-realization','case-budget'])if(!v(id).value.trim())throw Error('Enter all inputs; zero is allowed.');w.monthly_volume=Number(v('case-volume').value);w.realization_rate=Number(v('case-realization').value)/100;w.confidence=Number(v('case-confidence').value);s.upfront_budget=Number(v('case-budget').value);const result=workflow2(s,w);activeS=s;activeW=w;activeResult=result;drawCase();}catch(err){v('case-status').textContent=err.message;v('case-export').disabled=true;v('case-brief').disabled=true;}};
v('case-reset').onclick=()=>{activeS=structuredClone(V.scenario);activeW=structuredClone(V.workflow_inputs);activeResult=V.workflow;controls();drawCase();};
v('case-export').onclick=()=>dl('workflow-case.json',{schema_version:'portfolio.v1',version:'2.0.0',scenario:activeS,workflow:activeW,results:activeResult});
v('case-brief').onclick=()=>dl('workflow-decision-brief.md',brief2(activeS,activeW,activeResult),'text/markdown');
v('case-import').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>1000000)throw Error('Use a JSON case smaller than 1 MB.');const x=JSON.parse(await file.text());validateCase2(x.scenario,x.workflow);const result=workflow2(x.scenario,x.workflow);activeS=x.scenario;activeW=x.workflow;activeResult=result;controls();drawCase();v('case-status').textContent='Imported and calculated '+file.name+'.';}catch(err){v('case-status').textContent='Import failed: '+err.message;}event.target.value='';};
controls();drawCase();
v('research-results').innerHTML='<div class="numbers"><div><strong>'+V.research_benchmark.top_one_matches+'/'+V.research_benchmark.n+'</strong><span>Fixed task reference matches</span></div><div><strong>'+V.research_benchmark.locator_matches+'/'+V.research_benchmark.n+'</strong><span>Exact original-source locators</span></div><div><strong>0</strong><span>Human-study participants</span></div></div><p>'+e(V.research_benchmark.scope)+'</p>';
v('presentation-slides').innerHTML=[['The question','Which evidence warrants an AI workflow investment?','Bank disclosures → tasks → skills → route mix → reliability → value.'],['The measurement','Use and risk coexist.','WFC FY2024 states current use inside a risk discussion. An exclusive risk label discards that information. Read the original beside the coding.'],['The public evidence',bank.sources.length+' reports; 4 banks; 3 fiscal periods.','BAC FY2025 collection failed. C FY2023 has reviewed risk language and unknown internal adoption. FY2024 Citi rollout reach and FY2025 JPM CIB active users have different denominators.'],['The workforce constraint',pct(mean.joint_probability_independent)+' joint attainment under mean coverage.','Adding reliable reserve capacity raises 36-month personnel PV cost from '+cash(mean.pv_cost)+' to '+cash(robust.pv_cost)+'. Conditional assumptions, not estimated success probabilities.'],['The economic choice','Choose 50% scale in the base scenario.','Model value once per workflow; reserve integration cash; compare no action and 25%, 50%, 100% scale. Base 50% NPV '+cash(V.workflow.options[1].npv)+'.'],['The sensitivity','Realization is the decision threshold.','Base 50% break-even realization '+pct(V.workflow.options[1].break_even_realization)+'. At 0% realization no action wins. Skill attainment and task quality require actual measurement.'],['The implementation','Gate investment with measured evidence.','Day 30: process owner maps task time and data access. Day 60: training owner tests attainment. Day 90: finance and controls owners check quality and capacity monetization.'],['The contribution','Inspect the analysis and reproduce the decision.','Source locators, independent measurement axes, grouped classifier diagnostics, exact reliability arithmetic, workflow investment model, offline application and auditable exports. No client or independent human-validation claim.']].map(([tag,title,body],i)=>'<article class="deck-slide"><span class="eyebrow">'+String(i+1).padStart(2,'0')+' / '+tag.toUpperCase()+'</span><h2>'+e(title)+'</h2><p>'+e(body)+'</p><small>Haojian Dui · Corporate AI Adoption · v2.0.0</small></article>').join('');
v('print-deck').onclick=()=>window.print();
}
