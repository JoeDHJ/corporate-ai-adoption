"""Independent axes preserve deployments inside risk and training discussions."""
import re
from .classify import AI

BANK_AI=re.compile(AI.pattern+r'|\b(?:LLM Suite|Citi Assist|Citi Stylus|Erica)\b|(?<!Wells )\bFargo\b',re.I)

def axes(text):
    t=text.lower();present=bool(BANK_AI.search(text))
    internal=bool(re.search(r'\b(?:our employees|our colleagues|our developers|within citi|inside the company|inside wells fargo|our business|our own|business decisions|our operations|our software engineers)\b',t))
    external=bool(re.search(r'\b(?:customers|clients|client|customer|erica|fargo)\b',t))
    # Actors can coexist. A risk paragraph must not erase an explicit use statement.
    actor=[x for x,b in [('internal',internal),('customer',external)] if b] if present else []
    stages=[]
    if present:
        if re.search(r'\b(?:piloting|pilot|exploring|experiment|experimenting|testing|trial)\b',t):stages.append('pilot')
        if re.search(r'\b(?:plan|planned|intend|will|expect|opportunities|potential)\b',t):stages.append('planned')
        if re.search(r'\b(?:use|using|used|launched|introduced|deployed|deploying|rolled out|embedded|integrating|have equipped|have put)\b',t):stages.append('deployed')
    return {'actors':actor or ['unspecified'],'stages':stages or ['not_established'],
        'people_investment':present and bool(re.search(r'train|reskill|upskill|talent|experts|scientists|workforce',t)),
        'risk':present and bool(re.search(r'\brisk|no assurance|inaccurate|biased|regulat|unintended|adverse|misuse',t)),
        'technology':('generative' if re.search(r'generative|genai|llm|agentic',t) else 'AI_unspecified' if present else 'none'),
        'numeric_claim':bool(re.search(r'\d',t)), 'status':'estimated'}

def bank_summary(sources,rows,inventory):
    out=[]
    for s in sources:
        reviewed=[r for r in rows if r['source_id']==s['source_id']]
        ops=[r for r in reviewed if 'internal' in r['review_axes']['actors'] and 'deployed' in r['review_axes']['stages']]
        out.append({**s,'status':'estimated','reviewed_spans':len(reviewed),
            'internal_use_evidence_ids':[r['evidence_id'] for r in ops],
            'reviewed_risk_flag':any(r['review_axes']['risk'] for r in reviewed),
            'internal_stage':'deployed_evidence' if ops else 'unknown_from_reviewed_spans',
            'inventory':next(r for r in inventory if r['source_id']==s['source_id'])})
    return out
