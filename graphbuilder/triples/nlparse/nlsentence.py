from .parse.parse import ParserRequest,Parse

class NLSentence:    
    def __init__(self,text,parse):
        self.text = text
        self.parse = parse
        
    @staticmethod
    def fromparser(text,port=10000):
        request = ParserRequest(pretagged=False,olddeps=True,numparses=1,port=port)
        response = request.run(text.replace("_"," "))
        return NLSentence(text,Parse.fromparser(text,response,0,{}))
        
    def __str__(self):
        return "Sentence: '%s'\nParse:\n%s" % (self.text,str(self.parse))
    
    def __repr__(self):
        return str(self)