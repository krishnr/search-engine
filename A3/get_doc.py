# MSCI 541 Assignment 3
# Krishn Ramesh - 20521942

import sys
import os
import gzip
import re

def get_doc_length(metadata_folder, doc_id, docno_to_id):
    date_regex = "LA(\d\d)(\d\d)(\d\d)"
    match = re.search(date_regex, doc_id)
    if match and match.lastindex > 2:
        month = match.group(1)
        day = match.group(2)
        year = match.group(3)
        date = year + "-" + month + "-" + day

    doc_id = docno_to_id[doc_id]

    # finding the raw document using date and doc_id
    doc_file = metadata_folder+ "/docs/" + date + "/" + str(doc_id) + ".txt.gz"
    with gzip.open(doc_file, 'r') as doc:
        doc_content = str(doc.read())

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

    tokens = tokenize(text, headline, graphic)

    doc_length = len(tokens)
    return doc_length

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
    headline_tokens = re.split(r"[^a-zA-Z0-9]", headline)
    graphic_tokens = re.split(r"[^a-zA-Z0-9]", graphic)

    tokens = text_tokens # + headline_tokens + graphic_tokens

    return tokens