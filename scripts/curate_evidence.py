"""Persist the actual assistant rubric review of selected source spans.
These are not independent human labels or a random/held-out sample.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'src/corporate_ai/data'
C=json.loads((ROOT/'data/raw/candidates.json').read_text(encoding='utf-8'))
# Entries: candidate index, reviewed class, scope, source-specific reasoning.
REVIEW={
'ACN-2023':[(9,'planned','internal','Future doubling of the AI talent pool; the target is not an attained workforce stock.'),(10,'hiring_innovation','internal','Appointments, a center of excellence and workforce training are people/innovation actions.'),(21,'hiring_innovation','internal','Completed foundational training is reported, with an approximate participant count.')],
'ACN-2024':[(7,'hiring_innovation','internal','Investment in people and skills, without a specific completed operational workflow.'),(8,'hiring_innovation','internal','Reported training hours and year-on-year change describe capability investment.'),(9,'hiring_innovation','internal','Reported Data & AI practitioner stock is distinct from the future 80,000-person target.')],
'ADBE-2023':[(0,'promotional','customer_or_product','Broad statement about empowering creators, with no named operational release in this span.'),(6,'deployment','customer_or_product','AI features are described as natively integrated into named creative applications; co-pilot is a product role, not a trial.'),(21,'deployment','customer_or_product','Paid product plans include the AI features; plans here means subscriptions, not future investment.')],
'ADBE-2024':[(0,'promotional','customer_or_product','Broad responsible-AI statement does not establish a completed deployment.'),(4,'deployment','customer_or_product','Named applications already contain integrated AI features.'),(32,'pilot','customer_or_product','The portfolio includes an explicitly public-beta video model. Mixed maturity is retained as pilot for this span.')],
'BAC-2023':[(3,'deployment','internal','The bank states that it uses AI in its own customer service operation.'),(4,'pilot','internal','The bank explicitly says it is piloting AI in its own coding.'),(6,'hiring_innovation','internal','The claim concerns the issuer patent portfolio, not a deployed operating workflow.')],
'BAC-2024':[(0,'promotional','internal','General investment and talent language lacks a named action or quantified people investment.'),(2,'deployment','internal','Tools including AI are offered within the bank financial centers and contact centers.'),(4,'risk','unspecified','Technological change is described as heightening risks; this is not adoption evidence.')],
'CSCO-2023':[(2,'deployment','customer_or_product','Completed launches of customer-facing AI technologies are stated.'),(6,'pilot','customer_or_product','The issuer explicitly describes piloting a technical capability.'),(22,'risk','unspecified','The statement warns that ethical and legal issues may not be identified or resolved.')],
'CSCO-2024':[(3,'promotional','customer_or_product','A superlative product description alone does not specify operational availability or customer use.'),(12,'deployment','internal','The issuer states use of AI in its own service and customer-experience operation.'),(26,'planned','internal','Explicit future personnel and resource investment is an intention.')],
'CRM-2023':[(0,'promotional','customer_or_product','A product-platform list does not describe a specific completed AI use.'),(1,'deployment','customer_or_product','The service offering includes customer-facing AI chatbots resolving routine issues.'),(15,'risk','unspecified','Potential computing-cost increase is a risk, not evidence of an actual pilot.')],
'CRM-2024':[(1,'deployment','customer_or_product','An existing AI-powered platform is described as connecting customer data and teams.'),(40,'risk','unspecified','A conditional warning about costs does not establish use or testing.'),(48,'hiring_innovation','internal','The issuer explicitly links investment in AI resources to a reported R&D headcount increase.')],
'GOOGL-2023':[(2,'deployment','customer_or_product','The issuer says AI has been made available in its products and services.'),(10,'planned','customer_or_product','An aim to build advanced AI states a strategic intention.'),(28,'pilot','customer_or_product','The issuer explicitly says it is experimenting with AI-linked advertising.')],
'GOOGL-2024':[(1,'hiring_innovation','internal','Centralization of AI R&D is an organizational innovation action.'),(3,'deployment','customer_or_product','AI is described as already available in products and services.'),(8,'planned','customer_or_product','The statement sets out what the issuer aims to build.')],
'IBM-2023':[(1,'deployment','customer_or_product','Clients are reported to be using the watsonx platform in specified workflows.'),(4,'deployment','internal','The issuer reports scaling AI to improve its own productivity.'),(31,'planned','unspecified','A future commitment to train learners is not completed training or employee hiring.')],
'IBM-2024':[(16,'deployment','customer_or_product','Two completed customer-facing launches are reported.'),(21,'deployment','internal','The issuer equips its own consultants with AI tools.'),(26,'deployment','internal','The issuer explicitly says it has adopted AI automation.')],
'JPM-2023':[(4,'deployment','internal','Predictive AI use cases in production are explicitly reported; risk is a business function in this sentence.'),(5,'pilot','internal','Exploration of GenAI in company workflows is stated.'),(8,'planned','internal','The statement anticipates a future potential workforce effect; it does not report realized augmentation.')],
'JPM-2024':[(0,'promotional','unspecified','An external ranking is not a specific deployment statement.'),(5,'deployment','internal','Engineers are reported to be seeing productivity from AI coding tools; the magnitude is management-reported, not independently identified.'),(7,'deployment','internal','A completed employee rollout of LLM Suite is explicitly reported.')],
'MSFT-2023':[(0,'promotional','unspecified','A predicted general transformation does not describe an operational deployment.'),(7,'planned','internal','The issuer states it will invest to extend its AI lead.'),(26,'deployment','internal','The issuer describes its own support agents using Copilot.')],
'MSFT-2024':[(5,'deployment','customer_or_product','Named enterprise customers are reported to use the vendor product.'),(110,'hiring_innovation','unspecified','A completed grant challenge and learning-resource offer describe skills investment, not employee adoption.'),(137,'risk','internal','The statement concerns potential cost and margin consequences of current investment.')],
'NVDA-2023':[(0,'promotional','customer_or_product','A broad description of platform scope does not establish internal operational use.'),(3,'deployment','customer_or_product','Cloud and internet companies are stated to use the issuer platforms.'),(26,'hiring_innovation','customer_or_product','Demonstrations of driving capability are product innovation; pilot refers to a vehicle control role.')],
'NVDA-2024':[(22,'deployment','customer_or_product','The issuer reports launching DGX Cloud; model training is a product workload, not worker training.'),(28,'hiring_innovation','customer_or_product','Vehicle demonstrations establish innovation activity, not a workforce trial.'),(34,'planned','customer_or_product','The issuer states it will continue adding AI features to its architecture.')],
}
rows=[]
for sid,entries in REVIEW.items():
    for i,(idx,label,scope,reason) in enumerate(entries,1):
        x=next(r for r in C if r['source_id']==sid and r['candidate_id']==idx)
        prefixes={('IBM-2023',4):'InfrastructureConsultingSoftware ',('NVDA-2023',3):'4 Table of Contents ',('GOOGL-2023',10):'Deliver the Most Advanced, Safe, and Responsible AI ',('GOOGL-2024',8):'Deliver the Most Advanced, Safe, and Responsible AI ',('BAC-2024',0):'Innovating for the future '}
        prefix=prefixes.get((sid,idx),'')
        if prefix:
            assert x['excerpt'].startswith(prefix)
            x={**x,'excerpt':x['excerpt'][len(prefix):],'start_char':x['start_char']+len(prefix)}
        if sid=='JPM-2024' and idx==0:
            text=x['excerpt'].split(' #1 IN CUSTOMER SATISFACTION')[0]
            x={**x,'excerpt':text,'end_char':x['start_char']+len(text)}
        if sid=='BAC-2024' and idx==2:
            # Preserve a contiguous span while dropping the parser's split at "U.S.".
            text=x['excerpt'].split(', and have expanded')[0]
            x={**x,'excerpt':text,'end_char':x['start_char']+len(text)}
        rows.append({k:x[k] for k in ['source_id','excerpt','page','start_char','end_char']}|dict(evidence_id=f'{sid}-E{i}',review_label=label,review_scope=scope,review_reason=reason,locator=(f"PDF physical page {x['page']}" if sid not in ['CRM-2023','CRM-2024','GOOGL-2023','GOOGL-2024','MSFT-2023','MSFT-2024','NVDA-2023','NVDA-2024'] else f"HTML normalized character {x['start_char']}"),reviewer='AI assistant rubric review',reviewed_at='2026-11-16'))
for r in rows:
    d=json.loads((ROOT/'data/raw'/(r['source_id']+'.json')).read_text(encoding='utf-8'))
    assert d['pages'][r['page']-1][r['start_char']:r['end_char']]==r['excerpt'],r['evidence_id']
for sid in REVIEW:
    assert sum(len(x['excerpt'].split()) for x in rows if x['source_id']==sid)<=200,sid
(DATA/'evidence.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
# Publish access metadata and sizes, while keeping complete copyrighted documents local.
sources=json.loads((DATA/'sources.json').read_text(encoding='utf-8'))
for s in sources:
    d=json.loads((ROOT/'data/raw'/(s['source_id']+'.json')).read_text(encoding='utf-8'))
    s.update(retrieved_at=d['retrieved_at'],bytes=d['bytes'],parsed_pages=len(d['pages']),source_format='pdf' if len(d['pages'])>1 else 'html',source_native_id=s['source_id'],parser='pypdf/BeautifulSoup normalized whitespace; exact offsets retained')
(DATA/'sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(f'{len(rows)} reviewed spans across {len(sources)} reports; all exact source spans matched.')
