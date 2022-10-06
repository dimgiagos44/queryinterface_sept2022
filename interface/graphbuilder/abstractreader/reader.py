import json

from .textcleaner import TextCleaner

class AbstractReader:
    def __init__(self,flname):
        tc = TextCleaner()
        with open(flname,"r",encoding="utf-8") as fl:
            res = json.load(fl)["response"]["results"]
            self.abs = {ent["id"].split(":")[1]:tc.cleantext(ent["abstract"]) for ent in res if "abstract" in ent}

    def abstracts(self):
        return ((pmid,self.abs[pmid]) for pmid in self.abs)