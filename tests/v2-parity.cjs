const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const {workflow2,reliable2,workloadDemand2}=require('../src/corporate_ai/web/v2.js');
const source=JSON.parse(fs.readFileSync('src/corporate_ai/data/scenario.json')),base=JSON.parse(fs.readFileSync('src/corporate_ai/data/workflow.json'));
for(const [volume,realization,budget,q] of [[60000,.5,400000,.9],[0,0,400000,.9],[60000,0,400000,.8],[60000,.5,0,.95],[60000,.2,700000,.9]]){
  const s=structuredClone(source),w=structuredClone(base);s.upfront_budget=budget;Object.assign(w,{monthly_volume:volume,realization_rate:realization,confidence:q});
  const py=JSON.parse(cp.execFileSync(process.env.PYTHON||'python',['-c','import json,sys; from corporate_ai.workflow import workflow_case; x=json.load(sys.stdin); print(json.dumps(workflow_case(x[0],x[1])))'],{input:JSON.stringify([s,w]),encoding:'utf8'})),js=workflow2(s,w);
  assert.equal(js.recommended_scale,py.recommended_scale);
  for(let i=0;i<3;i++){const a=js.options[i],b=py.options[i];assert.equal(a.staffing.feasible,b.staffing.feasible);if(b.staffing.feasible){assert.deepEqual(a.staffing.route_counts,b.staffing.route_counts);for(const k of ['npv','pv_total_cost','pv_realized_value','break_even_realization'])if(b[k]!==null)assert.ok(Math.abs(a[k]-b[k])<1e-6,k);}}
}
assert.throws(()=>workflow2(source,{...base,confidence:NaN}));
assert.throws(()=>workflow2(source,{...base,tasks:[]}));
assert.throws(()=>workflow2(source,{...base,currency:'EUR'}));
assert.throws(()=>workflow2({...source,retrieved_at:'not-a-date'},base));
assert.throws(()=>workflow2(source,{...base,source_id:null}));
assert.equal(workloadDemand2(3000,.28,7),2);
const z=workflow2(source,{...base,hour_value:0});assert.equal(z.recommended_scale,0);assert.equal(z.options[0].break_even_realization,null);
for(const value of [.5,0])for(const option of workflow2(source,{...base,realization_rate:value}).options){assert.ok(!('npv' in option.staffing));for(const sk of option.staffing.skills||[])assert.ok(!('npv' in sk)&&!('cashflows' in sk));}
const {rankEvidence2}=require('../src/corporate_ai/web/v2.js'),bank=JSON.parse(fs.readFileSync('src/corporate_ai/data/bank-case.json')),pack=JSON.parse(fs.readFileSync('src/corporate_ai/data/research-benchmark.json'));
for(const t of pack.tasks)assert.equal(rankEvidence2(bank.reviewed.filter(r=>r.source_id===t.source_id),t.query)[0].evidence_id,t.expected_evidence_id);
console.log('V2 Python/browser parity: 5 workload, value, budget and reliability cases passed.');
