"""Grouped out-of-sample diagnostic against assistant reference labels, not validation."""
from collections import Counter
from math import log,sqrt
import re
from time import perf_counter
from .classify import baseline,classify

def tokens(text):return re.findall(r'[a-z]{2,}',text.lower())

def centroid_predict(train,test):
    docs=[Counter(tokens(r['excerpt'])) for r in train]
    df=Counter(k for d in docs for k in d);idf={k:log((1+len(docs))/(1+n))+1 for k,n in df.items()}
    def vector(text):
        c=Counter(tokens(text));v={k:(1+log(n))*idf[k] for k,n in c.items() if k in idf}
        norm=sqrt(sum(x*x for x in v.values())) or 1
        return {k:x/norm for k,x in v.items()}
    centers={False:Counter(),True:Counter()}
    for r in train:centers[r['review_label']=='deployment'].update(vector(r['excerpt']))
    for y,v in centers.items():
        norm=sqrt(sum(x*x for x in v.values())) or 1
        centers[y]={k:x/norm for k,x in v.items()}
    predictions=[]
    for r in test:
        v=vector(r['excerpt']);scores={y:sum(x*center.get(k,0) for k,x in v.items()) for y,center in centers.items()}
        predictions.append(scores[True]>scores[False])
    return predictions

def score(rows,pred):
    y=[r['review_label']=='deployment' for r in rows]
    tp=sum(a and b for a,b in zip(y,pred));fp=sum(not a and b for a,b in zip(y,pred));fn=sum(a and not b for a,b in zip(y,pred))
    return {'n':len(y),'reference_deployments':sum(y),'true_positive':tp,'false_positive':fp,'false_negative':fn,
        'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None,
        'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,
        'accuracy':sum(a==b for a,b in zip(y,pred))/len(y) if y else None}

def benchmark(rows):
    start=perf_counter();tests=[];predictions=[];folds=[]
    for company in sorted({r['company'] for r in rows}):
        test=[r for r in rows if r['company']==company];train=[r for r in rows if r['company']!=company]
        p=centroid_predict(train,test);tests.extend(test);predictions.extend(p)
        folds.append({'held_out_company':company,'train_n':len(train),'test_n':len(test)})
    grouped={'tfidf_centroid':score(tests,predictions),
             'keyword':score(tests,[baseline(r['excerpt'])=='deployment' for r in tests]),
             'context_rules':score(tests,[classify(r['excerpt'])['label']=='deployment' for r in tests])}
    train=[r for r in rows if int(r['period'])<2025];test=[r for r in rows if r['period']=='2025']
    train_text={' '.join(r['excerpt'].lower().split()) for r in train}
    train_features={tuple(sorted(Counter(tokens(r['excerpt'])).items())) for r in train}
    temporal=[r for r in test if tuple(sorted(Counter(tokens(r['excerpt'])).items())) not in train_features]
    return {'target':'Binary statement deployment, including customer products; not firm internal adoption',
        'reference_status':'Single-assistant rubric labels; selected diagnostic set, no human validity claim',
        'company_holdout':grouped,'folds':folds,'time_holdout':{'train_periods':'2023–2024','test_period':'2025',
        'train_n':len(train),'excluded_exact_repeated_test_spans':sum(' '.join(r['excerpt'].lower().split()) in train_text for r in test),
        'excluded_feature_identical_test_spans':len(test)-len(temporal),
        'tfidf_centroid':score(temporal,centroid_predict(train,temporal))},
        'method':'TF-IDF cosine nearest class centroid; vocabulary, IDF and centroids fitted on training rows only. No hyperparameter search.',
        'elapsed_seconds':perf_counter()-start,
        'errors':[{'evidence_id':r['evidence_id'],'company':r['company'],'reference':r['review_label'],'predicted_deployment':p}
                  for r,p in zip(tests,predictions) if (r['review_label']=='deployment')!=p]}
