from .graphtriple.graphtriple import GraphTriple
from graphbuilder.graphdb.graphdb import GraphDB

class GraphDBBuilder:
    def __init__(self,schema):
        self.gdb = GraphDB(schema,"localhost","7687","neo4j","test")

    def newgraph(self):
        self.gdb.runcommand("MATCH (n:SUBJECT)-[r]-(m:OBJECT) DETACH DELETE n,r,m")

    def deletefullgraph(self):
        self.gdb.erasegraph()

    def addtriple(self,triple,pmid,debug=False,debugout=False):
        gtriple = GraphTriple.fromtriple(triple)
        match = gtriple.schemamatch(self.gdb.schema)
        if not match:
            return
        matches,lpred,rpred,fpred,dpred = match
        dbgout = []
        for (subjcat,subjname,subjlname,subjdesc,subjinfo,subjfullstr),(objcat,objname,objlname,objdesc,objinfo,objfullstr) in matches:
            subjfullstr = subjfullstr.replace("( ","(").replace(" )",")")
            objfullstr = objfullstr.replace("( ","(").replace(" )",")")
            subjname,objname = " ".join(subjname)," ".join(objname)
            if not self.gdb.schema.canonicalnameof(subjname) or not self.gdb.schema.canonicalnameof(objname):
                continue
            if debugout:
                dbgout.append((subjfullstr," ".join(fpred),objfullstr,subjname,objname,subjcat,objcat))
                continue

            cmd = (("MATCH (n {Name:'%s'})\nMATCH (m {Name:'%s'})\n"%self._cypherformat(self.gdb.schema.canonicalnameof(subjname),self.gdb.schema.canonicalnameof(objname)))
                   +("MERGE (s:SUBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})"%self._cypherformat(" ".join(subjdesc)," ".join(subjinfo),subjfullstr,pmid))
                   +("-[r:%s {FullString:'%s',Descriptors:'%s'}]->"%self._cypherformat(rpred.upper()," ".join(fpred)," ".join(dpred)))
                   +("(o:OBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})\n"%self._cypherformat(" ".join(objdesc)," ".join(objinfo),objfullstr,pmid))
                   +("MERGE (n)<-[:INSTANCE_OF]-(s)\nMERGE (m)<-[:INSTANCE_OF]-(o)"))


            #cmd = (("MATCH (n {Name:'%s'})\nMATCH (m {Name:'%s'})\n"%self._cypherformat(self.gdb.schema.canonicalnameof(subjname),self.gdb.schema.canonicalnameof(objname)))
            #        +("MERGE (n)<-[:INSTANCE_OF]-(:SUBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})"%self._cypherformat(" ".join(subjdesc)," ".join(subjinfo),subjfullstr,pmid))
            #        +("-[:%s {FullString:'%s',Descriptors:'%s'}]->"%self._cypherformat(rpred.upper()," ".join(fpred)," ".join(dpred)))
            #        +("(:OBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})-[:INSTANCE_OF]->(m)"%self._cypherformat(" ".join(objdesc)," ".join(objinfo),objfullstr,pmid)))


            #cmd = (("MERGE (s:%s {Name:'%s',Synonyms:[%s]})\n" % (self._cypherformat(subjcat,self.gdb.schema.canonicalnameof(subjname),
            #                                                                         ["'%s'" % syn for syn in self.gdb.schema.synonymsof(subjname)])))
            #       + ("MERGE (o:%s {Name:'%s',Synonyms:[%s]})\n" % (self._cypherformat(objcat,self.gdb.schema.canonicalnameof(objname),
            #                                                                         ["'%s'" % syn for syn in self.gdb.schema.synonymsof(objname)])))
            #       + ("CREATE (s)<-[:INSTANCE_OF]-(:SUBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})" 
            #          % self._cypherformat(" ".join(subjdesc)," ".join(subjinfo),subjfullstr,pmid))
            #       + ("-[:%s {FullString:'%s',Descriptors:'%s'}]->" % self._cypherformat(rpred.upper()," ".join(fpred)," ".join(dpred)))
            #       + ("(:OBJECT {Descriptors:'%s',ContextTerms:'%s',FullString:'%s',PMID:'%s'})-[:INSTANCE_OF]->(o)"
            #          % self._cypherformat(" ".join(objdesc)," ".join(objinfo),objfullstr,pmid)))
            print(subjcat,subjname,rpred.upper(),objname,objcat)
            if debug:
                print(cmd)
            self.gdb.runcommand(cmd,results=False)
        if debugout:
            return dbgout
            
    def _cypherformat(self,*args):
        return tuple(arg.replace("-","").replace(".","").replace("'","") if type(arg) != list else ",".join(["'%s'" % s.replace("-","").replace(".","").replace("'","") for s in arg]) for arg in args)
