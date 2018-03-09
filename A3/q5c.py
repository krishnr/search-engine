import os
import csv
import pandas as pd
from scipy.stats import ttest_rel as ttest
import pickle
from scipy import stats

csv_file = open(os.path.join('mean_results_table.csv'), 'r')
df = pd.read_csv(csv_file)
df = df[df['Mean TBG'] != 'bad format']

mean_measures = ['Mean Average Precision','Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
measures = ['avg_precision', 'precision_at_10', 'ndcg_at_10', 'ndcg_at_1000', 'TBG']

with open('run_results.p', 'rb') as handle:
    run_results = pickle.load(handle)

results = {}

csv_columns = ['Effectiveness Measure', 'Best Run Score', 'Second Best Run Score', 'Relative Percent Improvement', 'p-value']
with open(os.path.join('stats_table.csv'), 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

for i, mean_measure in enumerate(mean_measures):
    measure = measures[i]
    df[mean_measure] = df[mean_measure].apply(pd.to_numeric)
    top_2_df = df.nlargest(2,mean_measure)
    best_mean, second_best_mean = top_2_df[mean_measure].values
    percent_change = (best_mean - second_best_mean)/second_best_mean
    best_run, second_best_run = top_2_df["Run Name"] + ".results"
    best_run_scores = run_results[best_run][measure]
    second_best_run_scores = run_results[second_best_run][measure]
    t, pval = ttest(best_run_scores, second_best_run_scores)
    
    with open(os.path.join('stats_table.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        data = {}
        data['Effectiveness Measure'] = mean_measure
        data['Best Run Score'] = '{:.3f}'.format(best_mean)
        data['Second Best Run Score'] = '{:.3f}'.format(second_best_mean)
        data['Relative Percent Improvement'] = '{:.3f}'.format(percent_change * 100) + '%'
        data['p-value'] = '{:.3f}'.format(pval)
        writer.writerow(data)