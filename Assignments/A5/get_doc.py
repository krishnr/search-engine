import sys
import os
import gzip
import re

def get_doc_text(metadata_folder, docno, docno_to_id):
    date_regex = "LA(\d\d)(\d\d)(\d\d)"
    match = re.search(date_regex, docno)
    if match and match.lastindex > 2:
        month = match.group(1)
        day = match.group(2)
        year = match.group(3)
        date = year + "-" + month + "-" + day

    doc_id = docno_to_id[docno]

    # finding the raw document using date and doc_id
    doc_file = "index/docs/" + date + "/" + str(doc_id) + ".txt.gz"
    with gzip.open(metadata_folder.open(doc_file,'r'), 'r') as doc:
        doc_content = str(doc.read().decode())
    
    # extracting headline
    headline_regex = re.compile(r"<HEADLINE>(.+)</HEADLINE>", re.DOTALL)
    match = re.search(headline_regex, doc_content)
    if match and match.lastindex > 0:    
        headline = match.group(1).strip()
    else:
        headline = ""
    
    # extracting graphic
    graphic_regex = re.compile(r"<GRAPHIC>(.+)</GRAPHIC>", re.DOTALL)
    match = re.search(graphic_regex, doc_content)
    if match and match.lastindex > 0:    
        graphic = match.group(1).strip()
    else:
        graphic = ""

    # extracting text
    text_regex = re.compile(r"<TEXT>(.+)</TEXT>", re.DOTALL)
    match = re.search(text_regex, doc_content)
    if match and match.lastindex > 0:    
        text = match.group(1).strip()
    else:
        text = ""

    return (text + graphic, doc_content)