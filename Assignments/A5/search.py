import pickle
import re
from collections import OrderedDict,defaultdict
from itertools import islice
from math import log
from datetime import datetime
from get_doc import get_doc_text
from bs4 import BeautifulSoup as bs
import zipfile

k1 = 1.2
b = 0.75
k2 = 7

INDEX_FOLDER = zipfile.ZipFile('index.zip', 'r')

print("Loading index into memory...")

# loading the metadata dictionary pickle
with INDEX_FOLDER.open('index/pickles/metadata_dict.p', 'r') as handle:
    metadata_dict = pickle.load(handle)

with INDEX_FOLDER.open('index/pickles/metadata_dict.p', 'r') as handle:
    metadata_dict = pickle.load(handle)

# loading the id_to_docno dictionary pickle
with INDEX_FOLDER.open('index/pickles/id_to_docno.p', 'r') as handle:
    id_to_docno = pickle.load(handle)

# loading the docno_to_id dictionary pickle
with INDEX_FOLDER.open('index/pickles/docno_to_id.p', 'r') as handle:
    docno_to_id = pickle.load(handle)

# loading the postings dictionary pickle
with INDEX_FOLDER.open('index/pickles/postings.p', 'r') as handle:
    postings = pickle.load(handle)

# loading the term_to_termid dictionary pickle
with INDEX_FOLDER.open('index/pickles/term_to_termid.p', 'r') as handle:
    term_to_termid = pickle.load(handle)

def bm25(freq, doc_length, query_freq, n, avdl, N):

    K = k1 * ( (1-b) + b * (doc_length/avdl) )

    return ((k1 + 1)*freq) / (K+freq) * (k2+1)*query_freq/(k2+query_freq) * log((N - n + 0.5)/(n + 0.5))

def tokenize(text):
    tokens = []

    # removing tags
    TAG_RE = re.compile(r'<[^>]+>')
    text = TAG_RE.sub('', text)

    # downcasing
    text = text.lower()

    # extracting tokens
    text_tokens = re.split(r"[^a-zA-Z0-9]", text)
    text_tokens = list(filter(None, text_tokens))

    tokens = text_tokens

    return tokens

def get_snippet(query_tokens, text):
    """
    First block: (?<!\w\.\w.) : this pattern searches in a negative feedback loop (?<!) for all words (\w) followed by fullstop (\.) , followed by other words (\.)

    Second block: (?<![A-Z][a-z]\.): this pattern searches in a negative feedback loop for anything starting with uppercase alphabets ([A-Z]), followed by lower case alphabets ([a-z]) till a dot (\.) is found.

    Third block: (?<=\.|\?): this pattern searches in a feedback loop of dot (\.) OR question mark (\?)
    """
    sentence_regex = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"
    sentences = re.split(sentence_regex, text)
    
    sent_scores = list(zip(sentences, [0] * len(sentences)))
    for i, s in enumerate(sent_scores):
        sentence, score = s
        if i == 0 or i == 1:
            I = 2 - i
        else:
            I = 0
        
        query_matches = []
        k = 0
        contig_terms = 0
        for token in tokenize(sentence):
            if contig_terms > k:
                k = contig_terms
                
            if token in query_tokens:
                contig_terms += 1
                query_matches.append(token)
            else:
                contig_terms = 0
        c = len(query_matches)
        d = len(set(query_matches))
        score = 2*I + 3*c + 5*d + 4*k
        sent_scores[i] = (score, sentence)

    ranked_sentences = sorted(sent_scores, reverse=True)
    snippet = ""
    for i, s in enumerate(ranked_sentences):
        if len(snippet) > 250 or i > 2:
            break
        score, sentence = s
        if score > 0:
            snippet += sentence

    return snippet

def strip_tags(text, isFullDoc=False):
    if isFullDoc:
        text = bs(text, "html5lib").get_text().strip()
        return text
        
    text = bs(text, "html5lib").get_text().replace('\n', ' ').strip()
    return ' '.join(text.split())
    
def main():
    query = input("Enter a query: ")

    start_time = datetime.now()

    query_tokens = tokenize(query)

    N = len(metadata_dict)
    total_length = 0
    for _, doc_dict in metadata_dict.items():
        total_length += doc_dict['doc_length']
    avdl = total_length/N

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

    ranked_doc_ids = sorted(scores, key=scores.get, reverse=True)[:10]
    ranked_metadata = [(metadata_dict[x]['date'], metadata_dict[x]['headline'], metadata_dict[x]['docno']) for x in ranked_doc_ids]
    ranks = [i+1 for i,_ in enumerate(ranked_doc_ids)]
    ranked_doc_text = []

    for i, doc_id in enumerate(ranked_doc_ids):
        text, full_doc = get_doc_text(INDEX_FOLDER, id_to_docno[doc_id], docno_to_id)
        ranked_doc_text.append((text, full_doc))
        snippet = get_snippet(query_tokens, text)
        rank = ranks[i]
        date, headline, docno = ranked_metadata[i]
        
        headline = strip_tags(headline)
        snippet = strip_tags(snippet)

        if not headline:
            headline = snippet[:50] + "..."

        print(str(rank) + ".", headline, "(" + date + ")")
        print(snippet, "(" + docno + ")", end='\n\n\n')
    
    time_taken = datetime.now().timestamp() - start_time.timestamp()
    print("Retrieval took %.2f seconds." % time_taken)

    user_input = ""
    while user_input not in ["N", "n", "new", "new query"]:
        user_input = input('Type in the number of a document to view or type "N" for "new query" or "Q" for "quit": ')
        
        if user_input in ["q", "quit"]:
            exit()
        
        if user_input.isdigit() and int(user_input) < 11:
            idx = int(user_input) - 1
            text, full_doc = ranked_doc_text[idx]
            full_doc = strip_tags(full_doc, isFullDoc=True)
            print(full_doc)
    
    main()

if __name__== "__main__":
    main()