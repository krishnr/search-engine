# MSCI 541 Assignment 2
# Krishn Ramesh - 20521942

import sys
import os
import re
import cPickle as pickle
from index_engine import tokenize

# Error message if incorrect number of inputs (ie. not 3 inputs)
if len(sys.argv) != 4:
    print "Please provide 3 arguments: the location of index folder, the queries file and the name of the output file"
    exit()

index_folder = sys.argv[1]
queries_file = sys.argv[2]
output_file = sys.argv[3]

# Throw error if index folder doesn't exist
if not os.path.exists(index_folder):
    print "Index directory does not exist!"
    exit()

# Throw error if query file doesn't exist
if not os.path.exists(queries_file):
    print "Queries file does not exist!"
    exit()

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

# empties output_file
open(output_file, 'w').close()

for query_tuple in queries:
    topicID = query_tuple[0]
    query = query_tuple[1]

    tokens = tokenize(query)
    
    docs = []

    # collects all the docs which contain each token in the query    
    for token in tokens:
        if token not in term_to_termid:
            docs = []
            continue
        termid = term_to_termid[token]
        postings_list = postings[termid]
        # get every even index
        docs_list = postings_list[0::2]
        docs.append(docs_list)

    if len(docs) == 0:
        continue

    # intersects all the docs which contain ALL the tokens
    doc_ids = list(set.intersection(*map(set,docs)))
    doc_nos = [id_to_docno[x] for x in doc_ids]
    ranks = [i+1 for i,_ in enumerate(doc_ids)]
    scores = [len(doc_ids)-ranks[i] for i,_ in enumerate(doc_ids)]

    # print output to file
    for i in range(0,len(doc_ids)):
        result_line = str(topicID) + " q0 " + str(doc_nos[i]) + " " + str(ranks[i]) + " " + str(scores[i]) + " krameshAND\n"
        with open(output_file, 'a') as f:
            f.write(result_line)