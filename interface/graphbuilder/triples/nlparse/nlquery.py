import itertools

import nltk
from nltk.tokenize import sent_tokenize as sentsplit, word_tokenize as tokenise

from .parse.parse import ParserRequest,Parse

PARSE_MODS = ["pretagged","imperative","firstlower"]

class NLQuery:    
    def __init__(self,text,parses):
        self.text = text
        self.parses = parses
        
    @staticmethod
    def fromparser(text,numparses=10,port=10000):
        parses = []
        for i in range(len(PARSE_MODS)+1):
            for ks in itertools.combinations(PARSE_MODS,i):
                qtext = NLQuery.QueryText(text,**{k:True for k in ks})
                request = ParserRequest(pretagged="pretagged" in ks,numparses=numparses,port=port)
                response = request.run(qtext.text)
                for i in range(numparses):
                    parse = Parse.fromparser(text,response,i,ks)
                    for oparse in parses:
                        if parse.tree.shalloweq(oparse.tree):
                            break
                    else:
                        parses.append(parse)
        return NLQuery(text,sorted(parses,key=lambda x:x.rating))
    
    def __str__(self):
        return "Query: '%s'\nParses:\n%s" % (self.text,"\n###\n".join(["# %d\n%s" % (i,str(parse))
                                                                       for i,parse in enumerate(self.parses)]))  
    
    def __repr__(self):
        return str(self)

    class QueryText:
        def __init__(self,text,**kwargs):
            self.text = text.replace("_"," ")
            if kwargs.get("imperative",False) and kwargs.get("pretagged",False):
                self._prependpronoun()
            if kwargs.get("firstlower",False):
                self._lowerfirst()
            if kwargs.get("pretagged",False):
                self._tagquery(remfirst=kwargs.get("imperative",False))

        def _tagquery(self,remfirst=False):
            tokens = ["%s_%s" % (t,p) for t,p in nltk.pos_tag(tokenise(sentsplit(self.text)[0]))]
            if remfirst:
                tokens = tokens[1:]
            tokentext = " ".join(tokens)
            tokentext = tokentext.replace("(_(","-LRB-_-LRB-")
            tokentext = tokentext.replace(")_)","-RRB-_-RRB-")
            self.text = tokentext

        def _lowerfirst(self):
             self.text = self.text[0].lower() + self.text[1:]

        def _prependpronoun(self):
            self._lowerfirst()
            self.text = "They " + self.text
        
        def __str__(self):
            return self.text
        
        def __repr__(self):
            return str(self)
