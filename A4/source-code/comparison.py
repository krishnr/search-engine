# MSCI 541 Assignment 3
# Krishn Ramesh - 20521942

import argparse
from parsers import QrelsParser, ResultsParser
import sys
import os
from math import log
from math import exp
import csv
from get_doc import get_doc_length
import pickle

# Author: Krishn Ramesh based on code by Nimesh Ghelani & Mark D. Smucker

parser = argparse.ArgumentParser(description='todo: insert description')
parser.add_argument('--qrel', required=True, help='Path to qrel')
parser.add_argument('--results', required=True, help='Path to folder containing results')
parser.add_argument('--file1', required=False, help='Name of first results file to compare')
parser.add_argument('--file2', required=False, help='Name of second results file to compare')

def main():
    cli = parser.parse_args()
    qrel = QrelsParser(cli.qrel).parse()
    results_folder = cli.results
    file1 = cli.file1
    file2 = cli.file2

    query_ids = sorted(qrel.get_query_ids())

    run_means = {}
    run_results = {}

    metadata_folder_1 = "../A2/index"
    metadata_folder_2 = "stem-index"

    # loading the docno_to_id dictionary pickle
    with open(metadata_folder_1 + '/pickles/docno_to_id.p', 'rb') as handle:
        docno_to_id_1 = pickle.load(handle)
    with open(metadata_folder_2 + '/pickles/docno_to_id.p', 'rb') as handle:
        docno_to_id_2 = pickle.load(handle)

    if file1 or file2:
        files = []
    else:
        files = os.listdir(results_folder)

    if file1:
        files.append(file1)
    if file2:
        files.append(file2)

    for filename in files:
        print("Parsing %s" % filename)
        path = filename
        run_means[filename] = {}
        try:
            if filename == file1:
                results = ResultsParser(path, docno_to_id_1).parse()
            elif filename == file2:
                results = ResultsParser(path, docno_to_id_2).parse()
        except ResultsParser.ResultsParseError as e:
            print(e.args[0])
            run_means[filename]['ndcg_at_1000'] = "bad format"
            run_means[filename]['ndcg_at_10'] = "bad format"
            run_means[filename]['avg_precision'] = "bad format"
            run_means[filename]['precision_at_10'] = "bad format"
            run_means[filename]['TBG'] = "bad format"
            continue

        run_results[filename] = {}

        topic_avg_precisions = []
        topic_precisions_at_10 = []
        topic_ndcg_at_10 = []
        topic_ndcg_at_1000 = []
        topic_TBG = []
        topic_ids = []

        for query_id in query_ids:
            query_result = results[1].get_result(query_id)
            
            if query_result is None:
                sys.stderr.write('%s has no results in %s\n' % (query_id, filename))
                topic_ndcg_at_1000.append(0)
                topic_ndcg_at_10.append(0)
                topic_precisions_at_10.append(0)
                topic_avg_precisions.append(0)
                topic_TBG.append(0)
                topic_ids.append(query_id)
                continue
            
            query_result = sorted(query_result)

            num_relevant = len(qrel.query_2_reldoc_nos[query_id])
            query_relevance = []
            sum_precision = 0
            relevant_so_far = 0
            precision_at_10 = 0
            dcg = 0
            idcg = 0
            Ts = 4.4
            Tk = 0
            TBG = 0
            for i, result in enumerate(query_result):
                rank = i+1
                relevance = qrel.get_relevance(query_id, result.doc_id)
                query_relevance.append(relevance)
                
                if relevance > 0:
                    relevant_so_far += 1
                    sum_precision += relevant_so_far/rank
                
                if rank <= num_relevant:
                    idcg += 1/log(rank+1,2)
                dcg += relevance/log(rank+1,2)
                
                TBG += gk(relevance) * D(Tk)

                if filename == file1:
                    doc_length = get_doc_length(metadata_folder_1, result.doc_id, docno_to_id_1)
                elif filename == file2:
                    doc_length = get_doc_length(metadata_folder_2, result.doc_id, docno_to_id_2)
                Tk += Ts + Td(doc_length)*prob(relevance)

                if rank == 10:
                    precision_at_10 = relevant_so_far/rank
                    ndcg_cut_10 = dcg / idcg
                if rank == 1000 or rank == len(query_result):
                    ndcg_cut_1000 = dcg / idcg
                    
            topic_ndcg_at_1000.append(ndcg_cut_1000)
            topic_ndcg_at_10.append(ndcg_cut_10)
            topic_precisions_at_10.append(precision_at_10)
            avg_precision = sum_precision/num_relevant
            topic_avg_precisions.append(avg_precision)
            topic_TBG.append(TBG)
            topic_ids.append(query_id)

        run_results[filename]['ndcg_at_1000'] = topic_ndcg_at_1000
        run_results[filename]['ndcg_at_10'] = topic_ndcg_at_10
        run_results[filename]['avg_precision'] = topic_avg_precisions
        run_results[filename]['precision_at_10'] = topic_precisions_at_10
        run_results[filename]['TBG'] = topic_TBG
        run_results[filename]['topic_ids'] = topic_ids

        run_means[filename]['ndcg_at_1000'] = '{:.3f}'.format(sum(topic_ndcg_at_1000) / len(topic_ndcg_at_1000))
        run_means[filename]['ndcg_at_10'] = '{:.3f}'.format(sum(topic_ndcg_at_10) / len(topic_ndcg_at_10))
        run_means[filename]['avg_precision'] = '{:.3f}'.format(sum(topic_avg_precisions) / len(topic_avg_precisions))
        run_means[filename]['precision_at_10'] = '{:.3f}'.format(sum(topic_precisions_at_10) / len(topic_precisions_at_10))
        run_means[filename]['TBG'] = '{:.3f}'.format(sum(topic_TBG) / len(topic_TBG))

    if file1 or file2:
        format_comparison(run_results, file1, file2, query_ids)

    format_results(run_means, run_results, files)

    with open('run_results.p', 'wb') as handle:
        pickle.dump(run_results, handle)

    with open('run_means.p', 'wb') as handle:
        pickle.dump(run_means, handle)

def format_results(run_means, run_results, files):
    csv_columns = ['Run Name','Mean Average Precision','Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
    with open(os.path.join('mean_results_table.csv'), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for filename in run_means:
            data = {}
            data['Run Name'] = filename.split('.')[0]
            data['Mean NDCG@1000'] = run_means[filename]['ndcg_at_1000']
            data['Mean NDCG@10'] = run_means[filename]['ndcg_at_10']
            data['Mean Average Precision'] = run_means[filename]['avg_precision']
            data['Mean P@10'] = run_means[filename]['precision_at_10']
            data['Mean TBG'] = run_means[filename]['TBG']
            writer.writerow(data)
    
    mean_measures = ['Average Precision','P@10', 'NDCG@10', 'NDCG@1000', 'TBG']
    measures = ['avg_precision', 'precision_at_10', 'ndcg_at_10', 'ndcg_at_1000', 'TBG']
    header = ['Run Name', 'Query ID'] + mean_measures
    
    with open(os.path.join('full_results_table.csv'), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        data = {}
        for f in files:
            if f not in run_results:
                continue
            data['Run Name'] = f
            query_ids = run_results[f]['topic_ids']
            for query_id in query_ids:
                data['Query ID'] = query_id
                for j,measure in enumerate(mean_measures):
                    idx = run_results[f]['topic_ids'].index(query_id)
                    scores = run_results[f][measures[j]]
                    data[measure] = '{:.3f}'.format(scores[idx])
                writer.writerow(data)

def format_comparison(run_results, file1, file2, query_ids):
    files_to_compare = []
    bad_run = [True, True]
    mean_measures = ['MAP','Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
    measures = ['avg_precision', 'precision_at_10', 'ndcg_at_10', 'ndcg_at_1000', 'TBG']
    header = ['Query ID']
    if file1:
        files_to_compare.append(file1)
        for measure in mean_measures:
                run = file1.split('.')[0]
                header.append(run + ' ' + measure)
        if file1 in run_results:
            bad_run[0] = False

    if file2:
        files_to_compare.append(file2)
        for measure in mean_measures:
                run = file2.split('.')[0]
                header.append(run + ' ' + measure)
        if file2 in run_results:
            bad_run[1] = False
    
    with open(os.path.join('comparison_table.csv'), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        data = {}

        for query_id in query_ids:
            data['Query ID'] = query_id
            for i,file in enumerate(files_to_compare):
                run = file.split('.')[0]
                for j,measure in enumerate(mean_measures):
                    if bad_run[i]:
                        data[run + ' ' + measure] = "bad format"
                    else:
                        idx = run_results[file]['topic_ids'].index(query_id)
                        scores = run_results[file][measures[j]]
                        data[run + ' ' + measure] = '{:.3f}'.format(scores[idx])
            writer.writerow(data)


def prob(relevance):
    if relevance == 1:
        return 0.64
    elif relevance == 0:
        return 0.39

def Td(doc_length):
    return 0.018 * doc_length + 7.8

def gk(relevance):
    if relevance:
        return prob(1)*0.77
    return 0

def D(t):
    h = 224
    return exp(-t*log(2)/h)

if __name__ == '__main__':
    main()