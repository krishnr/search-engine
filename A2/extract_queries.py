# code to extract queries
queries = []

with open(queries_file, 'rb') as f:
    doc_content = ""
    in_doc = False
    doc_id = 0

    # parse file line by line
    for line in f:
        # entering a new doc
        if "<top>" in line:
            in_doc = True
    
        if in_doc:
            doc_content += line
        
        # leaving a doc
        if "</top>" in line:
            in_doc = False
            
            reg = re.compile(r"<num> Number:(.+)<title>", re.DOTALL)
            match = re.search(reg, doc_content)
            if match and match.lastindex > 0:
                num = match.group(1).strip()

            reg = re.compile(r"<title>(.+)<desc>", re.DOTALL)
            match = re.search(reg, doc_content)
            if match and match.lastindex > 0:
                title = match.group(1).strip()
            
            skip_nums = ['416', '423', '437', '444', '447']

            if num not in skip_nums:
                queries.append( (num, title) )

            doc_content = ""

pickle.dump(queries, open('queries.txt', 'wb'))