class TextCleaner:
    def __init__(self):
        self.remterms = ["Purpose","Methods","Conclusions","Materials","Objective",
                        "Results","Conclusion","Methodology","<label>","</label>"]

    def cleantext(self,text):
        ntext = text
        for term in self.remterms:
            if term+":" in ntext:
                ntext = ntext.replace(term+":"," ")
            else:
                ntext = ntext.replace(term," ")
                ntext = ntext.replace(term.upper()," ")
        ntoks = []
        for tok in ntext.split():
            if ("." in tok and tok[:1] != "." and tok[-1:] != "."
                and not set(tok)&set("0123456789") and len([1 for c in tok if c == "."]) == 1):
                ntoks.extend(tok.split("."))
            else:
                ntoks.append(tok)
        return " ".join(ntoks)