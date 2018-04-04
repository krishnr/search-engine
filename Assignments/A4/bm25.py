import math
import pickle
import re
from PorterStemmer import PorterStemmer
from index_engine import tokenize
from index_engine import stem
from get_doc import get_doc_length
from collections import OrderedDict,defaultdict
from itertools import islice

k1 = 1.2
b = 0.75
k2 = 7

def bm25(freq, doc_length, query_freq, n, avdl, N):

    K = k1 * ( (1-b) + b * (doc_length/avdl) )

    return ((k1 + 1)*freq) / (K+freq) * (k2+1)*query_freq/(k2+query_freq) * math.log((N - n + 0.5)/(n + 0.5))

def main():
    queries_file = "queries.p"
    
    index_folder = "stem-index"
    results_file = "kramesh-hw4-bm25-stem.txt"
    end_string = " kramesh_bm25_stem\n"

    # index_folder = "../A2/index"
    # results_file = "kramesh-hw4-bm25-baseline.txt"
    # end_string = " kramesh_bm25_baseline\n"
    
    # loading the metadata dictionary pickle
    with open(index_folder + '/pickles/metadata_dict.p', 'rb') as handle:
        metadata_dict = pickle.load(handle)

    # loading the id_to_docno dictionary pickle
    with open(index_folder + '/pickles/id_to_docno.p', 'rb') as handle:
        id_to_docno = pickle.load(handle)

    # loading the docno_to_id dictionary pickle
    with open(index_folder + '/pickles/docno_to_id.p', 'rb') as handle:
        docno_to_id = pickle.load(handle)

    # loading the postings dictionary pickle
    with open(index_folder + '/pickles/postings.p', 'rb') as handle:
        postings = pickle.load(handle)

    # loading the term_to_termid dictionary pickle
    with open(index_folder + '/pickles/term_to_termid.p', 'rb') as handle:
        term_to_termid = pickle.load(handle)

    # loading the termid_to_term dictionary pickle
    with open(index_folder + '/pickles/termid_to_term.p', 'rb') as handle:
        termid_to_term = pickle.load(handle)

    with open(queries_file, 'rb') as handle:
        queries = pickle.load(handle)

    # empties results_file
    open(results_file, 'w').close()
    
    N = len(metadata_dict)
    total_length = 0
    for _, doc_dict in metadata_dict.items():
        total_length += doc_dict['doc_length']
    avdl = total_length/N

    for i,query_tuple in enumerate(queries):
        topicID = query_tuple[0]
        query = query_tuple[1]
        print(topicID)

        query_tokens = tokenize(query)
        query_tokens = stem(query_tokens)
        
        #initialize scores to 0
        scores = {}
        scores = defaultdict(lambda:0,scores)
                
        # collects all the docs which contain each token in the query    
        for token in query_tokens:
            query_freq = query_tokens.count(token)

            if token in term_to_termid:
                termid = term_to_termid[token]
                postings_list = postings[termid]
                # get every even index
                docs_list = postings_list[0::2]
                # get every odd index
                freq_list = postings_list[1::2]
                doc_len_list = [metadata_dict[x]['doc_length'] for x in docs_list]
                n = len(docs_list)
                
                for i,doc_id in enumerate(docs_list):
                    score = bm25(freq_list[i], doc_len_list[i], query_freq, n, avdl, N)
                    scores[doc_id] += score

        ranked_doc_ids = sorted(scores, key=scores.get, reverse=True)[:1000]
        ranked_scores = sorted(scores.values(), reverse=True)[:1000]
        ranked_doc_nos = [id_to_docno[x] for x in ranked_doc_ids]
        ranks = [i+1 for i,_ in enumerate(ranked_scores)]

        # print output to file
        for i in range(0,len(ranked_scores)):
            result_line = str(topicID) + " q0 " + str(ranked_doc_nos[i]) + " " + str(ranks[i]) + " " + str(ranked_scores[i]) + end_string
            with open(results_file, 'a') as f:
                f.write(result_line)

if __name__== "__main__":
  main()
