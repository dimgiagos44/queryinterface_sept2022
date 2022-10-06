import requests,urllib

from .parsetree import PhraseTree,DependencyTree,Token

PARSER_BASE_URL = "http://localhost:%d/?properties={%s}"
PARSER_MODEL_PATH = "parser/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
DEPPARSER_MODEL_PATH = "parser/stanford-corenlp-4.4.0-models/edu/stanford/nlp/models/parser/nndep/english_UD.gz"
OLDDEPPARSER_MODEL_PATH = "parser/stanford-corenlp-3.9.2-models/edu/stanford/nlp/models/parser/nndep/english_UD.gz"

class ParseException(Exception):
    pass
    
class ParserRequest:
    def __init__(self,pretagged=False,olddeps=False,numparses=10,port=10000):
        opts = {"outputFormat":"json","parse.kbest":str(numparses),
                "parse.model":PARSER_MODEL_PATH,
                "depparse.model":OLDDEPPARSER_MODEL_PATH if olddeps else DEPPARSER_MODEL_PATH}
        if not pretagged:
            opts["annotators"] = "parse,depparse"
        else:
            opts["annotators"] = "tokenize,ssplit,forcedpos,parse,depparse"
            opts["enforceRequirements"] = "false"
            opts["tokenize.whitespace"] = "true"
            opts["ssplit.eolonly"] = "true"
            opts["parse.tokenized"] = "true"
            opts["parse.tagSeparator"] = "_"
            opts["customAnnotatorClass.forcedpos"] = "edu.stanford.nlp.pipeline.IdentityTagger"
        self.requesturl = PARSER_BASE_URL % (port,urllib.parse.quote_plus(str(opts)[1:-1]))
    
    def run(self,text):
        r = requests.post(self.requesturl,data=text.encode("ascii",errors="ignore").decode())
        if r.status_code == 200:
            return r.json()["sentences"][0]
        else:
            raise ParseException("Parse error")

class Parse:
    def __init__(self,mods,tokens,tree,deptree):
        self.mods = mods
        self.tokens = tokens
        self.tree = tree
        self.deptree = deptree
        self.rating = tree.rate()
        
    @staticmethod
    def fromparser(text,response,i,mods):
        tokens = [Token.fromparser(token) for token in response["tokens"]]
        tree = PhraseTree.fromparser(response,i,tokens)
        deptree = DependencyTree.fromparser(response,tokens)
        return Parse(mods,tokens,tree,deptree)
        
    def __str__(self):
        return ("Rating: %f\nParse mods: %s\nTokens: %s\n"
                "Parse tree:\n%s\nDependency tree:\n%s") % (self.rating,str(self.mods),
                                                            str([(token.word,token.pos) for token in self.tokens]),
                                                            str(self.tree),str(self.deptree)) 
    
    def __repr__(self):
        return str(self)
    
