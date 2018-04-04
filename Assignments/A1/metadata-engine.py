# MSCI 541 Assignment 1
# Krishn Ramesh - 20521942

import sys
import os
import gzip
import re
import pickle

# Error message if incorrect number of inputs (ie. not 2 inputs)
if len(sys.argv) != 3:
    print "Please provide 2 arguments: the location of latimes.gzip and the location for the metadata index"
    exit()

gz_file = sys.argv[1]
metadata_folder = sys.argv[2]

# Error message if path to gz file is invalid
if not os.path.exists(gz_file):
    print "Path to dataset is invalid!"
    exit()

# Make directory if doesn't exist, otherwise throw error
if not os.path.exists(metadata_folder):
    print "Making directory: " + metadata_folder
    os.makedirs(metadata_folder)
else:
    print "Directory already exists!"
    exit()

# dictionary to store metadata
metadata_dict = {}

# mappings from id <=> docno
id_to_docno = {}
docno_to_id = {}

# method to save the raw text of the doc
def save_doc(doc_content, date, doc_id):
    # make 'docs' folder if doesn't exist
    if not os.path.exists(metadata_folder + '/docs'):
        os.makedirs(metadata_folder + '/docs')

    # make date directory if doesn't exist
    directory = metadata_folder + "/docs/" + date
    if not os.path.exists(directory):
        os.makedirs(directory)

    # store raw doc with its doc_id
    filename = directory + "/" + str(doc_id) + '.txt.gz'

    # save raw text as a compressed text file
    with gzip.open(filename, 'wb') as doc_file:
        doc_file.write(doc_content)

# method to extract doc metadata
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

    # save to metadata dictionary using doc_id as the key
    metadata_dict[doc_id] = {
        "docno": docno,
        "headline": headline,
        "date": date
    }

    # record mapping for id <=> docno
    id_to_docno[doc_id] = docno
    docno_to_id[docno] = doc_id

    # save the raw text in the proper directory
    save_doc(doc_content, date, doc_id)

# iterating through file
with gzip.open(gz_file, 'rb') as f:
    doc_content = ""
    in_doc = False
    doc_id = 0

    # parse gz file line by line
    for line in f:
        # entering a new doc
        if "<DOC>" in line:
            in_doc = True
    
        if in_doc:
            doc_content += line
        
        # leaving a doc
        if "</DOC>" in line:
            in_doc = False
            extract_metadata(doc_content, doc_id)
            doc_id += 1
            doc_content = ""

# make pickles folder if doesn't exist
if not os.path.exists(metadata_folder + '/pickles'):
    os.makedirs(metadata_folder + '/pickles')

# store all dictionaries as pickles
pickle.dump(metadata_dict, open(metadata_folder + '/metadata_dict.p', 'wb'))
pickle.dump(id_to_docno, open(metadata_folder + '/pickles/id_to_docno.p', 'wb'))
pickle.dump(docno_to_id, open(metadata_folder + '/pickles/docno_to_id.p', 'wb'))