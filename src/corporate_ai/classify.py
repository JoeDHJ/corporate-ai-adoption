"""Interpretable span classification. Labels describe statements, not latent adoption."""
import re

LABELS = ('deployment', 'pilot', 'planned', 'hiring_innovation', 'promotional', 'risk', 'none')
AI = re.compile(r'\b(?:AI|artificial intelligence|machine learning|generative AI|copilot|watsonx|firefly)\b', re.I)

def baseline(text):
    return 'deployment' if AI.search(text) else 'none'

def classify(text):
    if not isinstance(text,str): raise ValueError('text must be a string')
    if not AI.search(text):return {'label':'none','scope':'unspecified','rule':'no AI term'}
    t=text.lower()
    # Risks do not establish use even when they contain deployment verbs.
    if re.search(r'\b(?:risks|adversely|laws|regulations|litigation|unintended|unethical|may fail|could harm|may not|not yet|do not use)\b',t):
        return {'label':'risk','scope':'unspecified','rule':'risk or negative assertion'}
    if re.search(r'\b(?:piloting|experiment|experimenting|testing|exploring|beta|trial)\b|(?<!co-)\bpilot\b',t):
        label,rule='pilot','trial or exploration cue'
    elif re.search(r'\b(?:plan to|plans to|plan on|planned|intend|intends|will invest|will need|expect to|will continue|aim to|committed to investing)\b',t):
        label,rule='planned','future commitment cue'
    elif re.search(r'\b(?:hiring|recruit|recruiting|patents|research and development|upskill|talent)\b|\b(?:training|trained)\b.{0,40}\b(?:people|workforce|workers|employees|learners)\b',t):
        label,rule='hiring_innovation','people or innovation investment cue'
    elif re.search(r'\b(?:launched|released|introduced|deployed|using|uses|use|utilize|utilizes|integrated|incorporated|powered|available|production|enabled|enables|leveraging|leverage)\b',t):
        label,rule='deployment','present use or completed release cue'
    else:label,rule='promotional','AI mention without operational action'
    if re.search(r'\b(?:our employees|our colleagues|our workforce|internally|internal operations|our own|across ibm|our developers)\b',t):scope='internal'
    elif re.search(r'\b(?:clients|customers|enterprises|businesses)\b',t):scope='customer_or_product'
    else:scope='unspecified'
    return {'label':label,'scope':scope,'rule':rule}

def evaluate(rows):
    if not rows:raise ValueError('evaluation requires at least one annotated span')
    results={}
    for name,fn in [('keyword_baseline',baseline),('context_rules',lambda t:classify(t)['label'])]:
        pairs=[(r['review_label'],fn(r['excerpt'])) for r in rows]
        confusion={a:{p:sum(y==a and pred==p for y,pred in pairs) for p in LABELS} for a in LABELS}
        supported=[l for l in LABELS if any(y==l for y,_ in pairs)]
        f1=[]
        for label in supported:
            tp=confusion[label][label]; fp=sum(y!=label and p==label for y,p in pairs); fn_=sum(y==label and p!=label for y,p in pairs)
            f1.append(2*tp/(2*tp+fp+fn_) if 2*tp+fp+fn_ else 0)
        results[name]={'n':len(pairs),'correct':sum(a==p for a,p in pairs),'accuracy':sum(a==p for a,p in pairs)/len(pairs),'macro_f1_supported_labels':sum(f1)/len(f1),'confusion':confusion,'errors':[{'evidence_id':r['evidence_id'],'review':a,'predicted':p} for r,(a,p) in zip(rows,pairs) if a!=p]}
    return results
