import os
import csv
import pandas as pd
from scipy.stats import ttest_rel as ttest
import pickle
from scipy import stats

csv_file = open(os.path.join('mean_results_table.csv'), 'r')
df = pd.read_csv(csv_file)
df = df[df['Run Name'].isin(['msmuckerAND', 'student1'])]

mean_measures = ['Mean Average Precision','Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
measures = ['avg_precision', 'precision_at_10', 'ndcg_at_10', 'ndcg_at_1000', 'TBG']

with open('q6_run_results.p', 'rb') as handle:
    run_results = pickle.load(handle)

results = {}

csv_columns = ['Effectiveness Measure', 'msmuckerAND score', 'student1 score', 'Relative Percent Improvement', 'p-value']
with open(os.path.join('q6_stats_table.csv'), 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

for i, mean_measure in enumerate(mean_measures):
    measure = measures[i]
    df[mean_measure] = df[mean_measure].apply(pd.to_numeric)
    student1_score, msmuckerAND_score = df[mean_measure].values
    percent_change = (student1_score - msmuckerAND_score)/msmuckerAND_score
    
    student1_scores = run_results['student1.results'][measure]
    msmuckerAND_scores = run_results['msmuckerAND.results'][measure]
    topic_ids = run_results['msmuckerAND.results']['topic_ids']

    for i, (x,y) in enumerate(zip(msmuckerAND_scores, student1_scores)):
        if x > y:
            print('msmuckerAND has a better %s than student1 for topic %s' % (measure, topic_ids[i]))

    t, pval = ttest(student1_scores, msmuckerAND_scores)
    
    with open(os.path.join('q6_stats_table.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        data = {}
        data['Effectiveness Measure'] = mean_measure
        data['msmuckerAND score'] = '{:.3f}'.format(msmuckerAND_score)
        data['student1 score'] = '{:.3f}'.format(student1_score)
        data['Relative Percent Improvement'] = '{:.3f}'.format(percent_change * 100) + '%'
        data['p-value'] = '{:.3f}'.format(pval)
        writer.writerow(data)
