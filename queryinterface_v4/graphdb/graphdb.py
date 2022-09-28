import json,glob
from neo4j import GraphDatabase

class GraphDB:
    def __init__(self,schema,hostname,port,username,password):
        self.schema = schema
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.driver = None
    
    def connect(self):
        self.driver = GraphDatabase.driver("bolt://"+self.hostname+":"+str(int(self.port)),
                                           auth=(self.username,self.password))
        
    def runcommand(self,command,results=True):
        if not self.driver:
            self.connect()
        with self.driver.session() as sn:
            if not results:
                sn.run(command)
            else:
                return [result.data() for result in sn.run(command)]
    
    def erasegraph(self):
        self.runcommand("MATCH (n) DETACH DELETE n",results=False)
        
class GraphDBSchema:
    def __init__(self,name,categories):
        self.name = name
        self.categories = categories
        self.index = self._buildindex()
        self.catindex = {category.label for category in categories}
        
    @staticmethod
    def buildfromontologies(name,ontpath):
        categories = []
        for flname in glob.glob(ontpath+"/*"):
            categories.append(GraphDBCategory.fromontologyfile(flname))
        return GraphDBSchema(name,categories)
    
    def _buildindex(self):
        index = {}
        for category in self.categories:
            for k in category.index:
                if k not in index:
                    index[k] = set()
                index[k].add(category.label)
        return index
    
    def save(self,outpath):
        with open(outpath+"/"+self.name+".gsch","w",encoding="utf-8") as fl:
            json.dump({"name":self.name,"categories":[category._tojson() for category in self.categories]},fl)
            
    def lookupname(self,name):
        return self.index.get(name.upper(),set())
        
    def hascategory(self,cname):
        return cname in self.catindex

    @staticmethod
    def load(flname):
        with open(flname,"r",encoding="utf-8") as fl:
            jdict = json.load(fl)
            return GraphDBSchema(jdict["name"],[GraphDBCategory._fromjson(cjdict) for cjdict in jdict["categories"]])
        
class GraphDBCategory:
    def __init__(self,label,members):
        self.label = label
        self.members = members
        self.index = self._buildindex(members)
        
    @staticmethod
    def fromontologyfile(flname):
        with open(flname,"r",encoding="utf-8") as fl:
            ontology = json.load(fl)
        return GraphDBCategory(ontology["label"],
                               {entity["name"]:GraphDBCategory.Member(entity["name"],entity["synonyms"])
                                for entity in ontology["entities"]})
    
    def _tojson(self):
        return {"label":self.label,"members":[{"entity":self.members[k].entity,"synonyms":self.members[k].synonyms}
                                              for k in self.members]}
    
    def _buildindex(self,members):
        index = {}
        for entity in self.members:
            index[entity.upper()] = entity
            for synonym in self.members[entity].synonyms:
                index[synonym.upper()] = entity
        return index
    
    @staticmethod
    def _fromjson(jdict):
        return GraphDBCategory(jdict["label"],{member["entity"]:GraphDBCategory.Member(member["entity"],member["synonyms"])
                                               for member in jdict["members"]})
    
    class Member:
        def __init__(self,entity,synonyms):
            self.entity = entity
            self.synonyms = synonyms
