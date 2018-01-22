# MSCI 541 Assignment 1
# Krishn Ramesh - 20521942

import sys
import os
import pickle
import gzip

if len(sys.argv) != 4:
    print "Please provide 3 arguments: the location of the metadata index, the string 'docno' or 'id', and the internal integer id or the DOCNO"
    exit()

metadata_folder = sys.argv[1]
id_type = sys.argv[2]
doc_id = sys.argv[3]

metadata_file = metadata_folder + '/metadata_dict.p'

if not os.path.exists(metadata_file):
    print "Path to metadata is invalid!"

with open(metadata_file, 'rb') as handle:
    metadata_dict = pickle.load(handle)

with open(metadata_folder + '/pickles/id_to_docno.p', 'rb') as handle:
    id_to_docno = pickle.load(handle)

with open(metadata_folder + '/pickles/docno_to_id.p', 'rb') as handle:
    docno_to_id = pickle.load(handle)

if id_type.lower() == "docno":
    doc_id = docno_to_id[doc_id]
elif id_type.lower() != "id":
    print "ERROR: Argument 2 must be one of 'docno' or 'id'"
    exit()

metadata = metadata_dict[int(doc_id)]
docno = metadata['docno']
date = metadata['date']
headline = metadata['headline']

doc_file = metadata_folder+ "/docs/" + date + "/" + str(doc_id) + ".txt.gz"
with gzip.open(doc_file, 'rb') as doc:
    raw_text = doc.read()

print "docno: " + docno
print "internal id: " + str(doc_id)
print "date: " + date
print "headline: " + headline
print "raw text: "
print raw_text