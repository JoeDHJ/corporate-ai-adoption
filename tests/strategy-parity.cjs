const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process');
const {compare}=require('../src/corporate_ai/web/app.js');
const source=JSON.parse(fs.readFileSync('src/corporate_ai/data/scenario.json','utf8'));
for(const [success,budget,delay] of [[.8,400000,3],[.5,400000,3],[.95,400000,3],[.8,0,3],[.8,700000,8]]){
  const s=structuredClone(source);s.upfront_budget=budget;for(const k of s.skills){k.routes.train.success_rate=success;k.routes.hire.ready_month=delay;}
  const py=JSON.parse(cp.execFileSync(process.env.PYTHON||'python',['-c','import sys,json; from corporate_ai.strategy import compare; print(json.dumps(compare(json.load(sys.stdin))))'],{input:JSON.stringify(s),encoding:'utf8'})),js=compare(s);
  for(const name of Object.keys(py)){
    assert.equal(js[name].feasible,py[name].feasible,name);
    if(py[name].feasible){assert.deepEqual(js[name].route_counts,py[name].route_counts);for(const key of ['upfront_cost','pv_cost','npv'])assert.ok(Math.abs(js[name][key]-py[name][key])<1e-6,key);assert.equal(js[name].undiscounted_payback_month,py[name].undiscounted_payback_month);}
  }
}
console.log('Python/browser solver parity passed: 5 scenarios x 4 policies.');
const {evidenceCsv}=require('../src/corporate_ai/web/app.js');
const evidence=JSON.parse(fs.readFileSync('src/corporate_ai/data/evidence.json','utf8'));
const selected=evidence.filter(r=>r.source_id==='JPM-2024').map(r=>({...r,company:'JPM',period:'2024'}));
assert.equal(evidenceCsv(selected).split('\r\n').length,4);
const quoted=evidenceCsv([{evidence_id:'=INJECTION()',excerpt:'A "quote", and\na newline'}]);
assert.ok(quoted.includes("'=INJECTION()"));assert.ok(quoted.includes('""quote""'));
console.log('Filtered CSV serialization and spreadsheet-cell safety passed.');
