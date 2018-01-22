# MSCI 541 Assignment 1
# Krishn Ramesh - 20521942

import sys
import os
import gzip
import re
import pickle

if len(sys.argv) != 3:
    print "Please provide 2 arguments: the location of latimes.gzip and the location for the metadata index"
    exit()

gz_file = sys.argv[1]
metadata_folder = sys.argv[2]

# "./latimes.gz"
if not os.path.exists(gz_file):
    print "Path to dataset is invalid!"

# "./metadata.txt"
if not os.path.exists(metadata_folder):
    print "Making directory: " + metadata_folder
    os.makedirs(metadata_folder)

metadata_dict = {}
id_to_docno = {}
docno_to_id = {}

def save_doc(doc_content, date, doc_id):
    if not os.path.exists(metadata_folder + '/docs'):
        os.makedirs(metadata_folder + '/docs')

    directory = metadata_folder + "/docs/" + date
    
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = directory + "/" + str(doc_id) + '.txt.gz'

    with gzip.open(filename, 'wb') as doc_file:
        doc_file.write(doc_content)

def extract_metadata(doc_content, doc_id):
    # extracting docno
    docno_regex = re.compile(r"<DOCNO>(.+)</DOCNO>", re.DOTALL)
    match = re.search(docno_regex, doc_content)
    if match and match.lastindex > 0:
        docno = match.group(1).strip()
    else:
        print "ERROR: DOCNO not found for doc_id %s" % doc_id 
        exit()
    
    # extracting headline
    headline_regex = re.compile(r"<HEADLINE>(.+)</HEADLINE>", re.DOTALL)
    match = re.search(headline_regex, doc_content)
    if match and match.lastindex > 0:    
        headline = match.group(1).strip()
    else:
        headline = ""
        print "WARNING: HEADLINE not found for doc_id %s" % doc_id 
    
    # extracting date
    date_regex = "LA(\d\d)(\d\d)(\d\d)"
    match = re.search(date_regex, docno)
    if match and match.lastindex > 2:
        month = match.group(1)
        day = match.group(2)
        year = match.group(3)
        date = year + "-" + month + "-" + day
    else:
        print "ERROR: date not parsed for doc_id %s" % doc_id

    metadata_dict[doc_id] = {
        "docno": docno,
        "headline": headline,
        "date": date
    }

    id_to_docno[doc_id] = docno
    docno_to_id[docno] = doc_id
    save_doc(doc_content, date, doc_id)

# iterating through file
with gzip.open(gz_file, 'rb') as f:
    doc_content = ""
    in_doc = False
    doc_id = 0
    for line in f:
        if "<DOC>" in line:
            in_doc = True
    
        if in_doc:
            doc_content += line
        
        if "</DOC>" in line:
            in_doc = False
            extract_metadata(doc_content, doc_id)
            doc_id += 1
            doc_content = ""

if not os.path.exists(metadata_folder + '/pickles'):
    os.makedirs(metadata_folder + '/pickles')

pickle.dump(metadata_dict, open(metadata_folder + '/metadata_dict.p', 'wb'))
pickle.dump(id_to_docno, open(metadata_folder + '/pickles/id_to_docno.p', 'wb'))
pickle.dump(docno_to_id, open(metadata_folder + '/pickles/docno_to_id.p', 'wb'))