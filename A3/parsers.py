from Qrels import Qrels, Judgement
from Results import Results, Result

# Author: Nimesh Ghelani based on code by Mark D. Smucker

class ResultsParser:
    class ResultsParseError(Exception):
        pass

    def __init__(self, filename, docno_list):
        self.filename = filename
        self.docno_list = docno_list

    def parse(self):
        global_run_id = None
        history = set()
        results = Results()
        with open(self.filename) as f:
            for line in f:
                line_components = line.strip().split()
                if len(line_components) != 6:
                    raise ResultsParser.ResultsParseError('lines in %s do not have exactly 6 columns' % self.filename)

                query_id, _, doc_id, rank, score, run_id = line_components
                try:
                    rank = int(rank)
                    score = float(score)
                except ValueError:
                    raise ResultsParser.ResultsParseError('Error parsing rank or score in %s' % self.filename)

                if doc_id not in self.docno_list:
                    raise ResultsParser.ResultsParseError('Docno %s does not exist for query %s in %s' % (doc_id, query_id, self.filename))

                if global_run_id is None:
                    global_run_id = run_id
                elif global_run_id != run_id:
                    raise ResultsParser.ResultsParseError('Mismatching runIDs in %s' % self.filename)

                key = query_id + doc_id
                if key in history:
                    raise ResultsParser.ResultsParseError('Duplicate query_id, doc_id in %s' % self.filename)
                history.add(key)

                results.add_result(query_id, Result(doc_id, score, rank))

        return global_run_id, results


class QrelsParser:
    class QrelsParseError(Exception):
        pass

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        qrels = Qrels()
        with open(self.filename) as f:
            for line in f:
                line_components = line.strip().split()
                if len(line_components) != 4:
                    raise QrelsParser.QrelsParseError("Line should have 4 columns")
                query_id, _, doc_id, relevance = line_components
                relevance = int(relevance)
                qrels.add_judgement(Judgement(query_id, doc_id, relevance))
        return qrels

