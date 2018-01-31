# MSCI 541 Assignment 2
# Krishn Ramesh - 20521942

import sys
import os
import gzip
import re
import cPickle as pickle
from collections import Counter

if __name__ == "__main__":
    # Error message if incorrect number of inputs (ie. not 2 inputs)
    if len(sys.argv) != 3:
        print "Please provide 2 arguments: the location of latimes.gzip and the location for the metadata index"
        exit()

    gz_file = sys.argv[1]
    index_folder = sys.argv[2]

    # Error message if path to gz file is invalid
    if not os.path.exists(gz_file):
        print "Path to dataset is invalid!"
        exit()

    # Make directory if doesn't exist, otherwise throw error
    if not os.path.exists(index_folder):
        print "Making directory: " + index_folder
        os.makedirs(index_folder)
    else:
        print "Directory already exists!"
        exit()

# dictionary to store metadata
metadata_dict = {}

# mappings from id <=> docno
id_to_docno = {}
docno_to_id = {}

# mappings from termid <=> term
termid_to_term = {}
term_to_termid = {}

# initializing termid to 0
current_termid = 0

# initializing postings lists dict
postings = {}

# method to save the raw text of the doc
def save_doc(doc_content, date, doc_id):
    # make 'docs' folder if doesn't exist
    if not os.path.exists(index_folder + '/docs'):
        os.makedirs(index_folder + '/docs')

    # make date directory if doesn't exist
    directory = index_folder + "/docs/" + date
    if not os.path.exists(directory):
        os.makedirs(directory)

    # store raw doc with its doc_id
    filename = directory + "/" + str(doc_id) + '.txt.gz'

    # save raw text as a compressed text file
    with gzip.open(filename, 'wb') as doc_file:
        doc_file.write(doc_content)


def tokenize(text, headline='', graphic=''):
    tokens = []

    # removing tags
    TAG_RE = re.compile(r'<[^>]+>')
    text = TAG_RE.sub('', text)
    headline = TAG_RE.sub('', headline)
    graphic = TAG_RE.sub('', graphic)

    # downcasing
    text = text.lower()
    headline = headline.lower()
    graphic = graphic.lower()

    # extracting tokens
    text_tokens = re.split(r"[^a-zA-Z0-9]", text)
    text_tokens = filter(None, text_tokens)

    headline_tokens = re.split(r"[^a-zA-Z0-9]", headline)
    headline_tokens = filter(None, headline_tokens)

    graphic_tokens = re.split(r"[^a-zA-Z0-9]", graphic)
    graphic_tokens = filter(None, graphic_tokens)

    tokens = text_tokens + headline_tokens + graphic_tokens

    return tokens

def get_term_ids(tokens):
    global current_termid
    token_ids = []

    for token in tokens:
        if not token in term_to_termid:
            term_to_termid[token] = current_termid
            termid_to_term[current_termid] = token
            current_termid += 1
        
        token_ids.append(term_to_termid[token])
    
    return token_ids

def create_postings_list(doc_id, term_ids):

    term_counts = Counter(term_ids)
    
    for term_id in term_counts:
        count = term_counts[term_id]

        if not term_id in postings:
            postings[term_id] = []
        
        postings[term_id].append(doc_id)
        postings[term_id].append(count)

# method to extract doc metadata and build index
def build_index(doc_content, doc_id):
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
    
    # extracting graphic
    graphic_regex = re.compile(r"<GRAPHIC>(.+)</GRAPHIC>", re.DOTALL)
    match = re.search(graphic_regex, doc_content)
    if match and match.lastindex > 0:    
        graphic = match.group(1).strip()
    else:
        graphic = ""
        print "WARNING: GRAPHIC not found for doc_id %s" % doc_id 

    # extracting text
    text_regex = re.compile(r"<TEXT>(.+)</TEXT>", re.DOTALL)
    match = re.search(text_regex, doc_content)
    if match and match.lastindex > 0:    
        text = match.group(1).strip()
    else:
        text = ""
        print "WARNING: TEXT not found for doc_id %s" % doc_id 

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

    tokens = tokenize(text, headline, graphic)

    doc_length = len(tokens)

    term_ids = get_term_ids(tokens)

    create_postings_list(doc_id, term_ids)

    # save to metadata dictionary using doc_id as the key
    metadata_dict[doc_id] = {
        "docno": docno,
        "headline": headline,
        "date": date,
        "doc_length": doc_length
    }

    # record mapping for id <=> docno
    id_to_docno[doc_id] = docno
    docno_to_id[docno] = doc_id

    # save the raw text in the proper directory
    save_doc(doc_content, date, doc_id)

if __name__ == "__main__":
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
                build_index(doc_content, doc_id)
                doc_id += 1
                doc_content = ""

    # make pickles folder if doesn't exist
    if not os.path.exists(index_folder + '/pickles'):
        os.makedirs(index_folder + '/pickles')

    # store all dictionaries as pickles
    pickle.dump(metadata_dict, open(index_folder + '/pickles/metadata_dict.p', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(id_to_docno, open(index_folder + '/pickles/id_to_docno.p', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(docno_to_id, open(index_folder + '/pickles/docno_to_id.p', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(termid_to_term, open(index_folder + '/pickles/termid_to_term.p', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(term_to_termid, open(index_folder + '/pickles/term_to_termid.p', 'wb'), pickle.HIGHEST_PROTOCOL)
    pickle.dump(postings, open(index_folder + '/pickles/postings.p', 'wb'), pickle.HIGHEST_PROTOCOL)
