import pathlib

from nltk.tokenize import sent_tokenize as sentsplit

from .nlparse.nlsentence import NLSentence
from .triple.tree import TripleTree
from .ruleset.ruleset import Ruleset
from .nlparse.parse.parse import ParseException

class TripleExtractor:
    def __init__(self,ruleset=pathlib.Path(__file__).parent/"rules.json",expanded_context=False):
        self.ruleset = Ruleset.load(ruleset)
        self.expanded_context = expanded_context
    
    def _extractparsed(self,sents,debug=False):
        triples = []
        for sent in sents:
            tree = TripleTree.fromdeptree(sent.parse.deptree,self.ruleset)
            if debug:
                print(tree)
            tree.subjectcopy()
            tree.classifysubjects()
            trees = tree.splitsubjects()
            trees = [ntree for tree in trees for ntree in tree.anaphoraresolve()]
            ln = len(trees)
            while 1:
                trees = [ntree for tree in trees for ntree in tree.conjunctionsplit()]
                if len(trees) == ln:
                    break
                ln = len(trees)
            for tree in trees:
                if not self.expanded_context:
                    tree.removeclauses()
                if debug:
                    print(tree)
                for triple in tree.basetriples(sent):
                    triple.exchangenodes()
                    triple.prunebranches()
                    triples.append(triple)
                    if debug:
                        print(triple)
        return list({" ".join(triple.totext()):triple for triple in triples}.values())
    
    def extract(self,text):
        sents = []
        for sent in sentsplit(text):
            try:
                sents.append(NLSentence.fromparser(sent))
            except ParseException:
                print("PARSE EXCEPTION: %s"%sent)
                continue
        return self._extractparsed(sents)