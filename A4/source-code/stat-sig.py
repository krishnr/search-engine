import os
import csv
import pandas as pd
from scipy.stats import ttest_rel as ttest
import pickle
from scipy import stats

csv_file = open(os.path.join('mean_results_table.csv'), 'r')
df = pd.read_csv(csv_file)
df = df[df['Run Name'].isin(['kramesh-hw4-bm25-stem', 'kramesh-hw4-bm25-baseline'])]

mean_measures = ['Mean Average Precision','Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
measures = ['avg_precision', 'precision_at_10', 'ndcg_at_10', 'ndcg_at_1000', 'TBG']

with open('run_results.p', 'rb') as handle:
    run_results = pickle.load(handle)

results = {}

csv_columns = ['Effectiveness Measure', 'stem score', 'baseline score', 'Relative Percent Improvement', 'p-value']
with open(os.path.join('stats_table.csv'), 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

for i, mean_measure in enumerate(mean_measures):
    measure = measures[i]
    df[mean_measure] = df[mean_measure].apply(pd.to_numeric)
    baseline_score, stem_score = df[mean_measure].values
    percent_change = (stem_score - baseline_score)/baseline_score
    
    baseline_scores = run_results['kramesh-hw4-bm25-baseline.txt'][measure]
    stem_scores = run_results['kramesh-hw4-bm25-stem.txt'][measure]
    topic_ids = run_results['kramesh-hw4-bm25-stem.txt']['topic_ids']

    for i, (x,y) in enumerate(zip(stem_scores, baseline_scores)):
        if x > y:
            print('stem has a better %s than baseline for topic %s' % (measure, topic_ids[i]))

    t, pval = ttest(baseline_scores, stem_scores)
    
    with open(os.path.join('stats_table.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        data = {}
        data['Effectiveness Measure'] = mean_measure
        data['stem score'] = '{:.3f}'.format(stem_score)
        data['baseline score'] = '{:.3f}'.format(baseline_score)
        data['Relative Percent Improvement'] = '{:.3f}'.format(percent_change * 100) + '%'
        data['p-value'] = '{:.3f}'.format(pval)
        writer.writerow(data)
