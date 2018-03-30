import pickle

index_folder = 'index'
# loading the term_to_termid dictionary pickle
with open(index_folder + '/pickles/termid_to_term.p', 'rb') as handle:
    termid_to_term = pickle.load(handle)

# loading the docno_to_id dictionary pickle
with open(index_folder + '/pickles/id_to_docno.p', 'rb') as handle:
    id_to_docno = pickle.load(handle)

print(len(termid_to_term))
print(len(id_to_docno))

# loading the postings dictionary pickle
with open(index_folder + '/pickles/postings.p', 'rb') as handle:
    postings = pickle.load(handle)

length = 0
for k,v in postings.items():
    length += len(v)
print(length)
