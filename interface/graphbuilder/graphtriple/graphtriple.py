from ..triples.triple.triple import Triple
from .graphtripletree import GraphTripleTree

class GraphTriple(Triple):
    def __init__(self,ruleset,sent,subjecttree,predicatetree,objecttree):
        Triple.__init__(self,ruleset,sent,subjecttree,predicatetree,objecttree)
        self.subject = GraphTriple.Element(subjecttree)
        self.predicate = GraphTriple.Element(predicatetree)
        self.object = GraphTriple.Element(objecttree)
        
    @staticmethod
    def fromtriple(triple):
        return GraphTriple(triple.ruleset,triple.sent,triple.subjecttree.copy(),
                           triple.predicatetree.copy(),triple.objecttree.copy())
    
    def schemamatch(self,schema):
        if self.predicate.tree.root.token.word[0] in "0123456789":
            return None
        smatch = self.subject.schemamatch(schema)
        omatch = self.object.schemamatch(schema)
        res = []
        for subjcat in smatch:
            for objcat in omatch:
                res.append(((subjcat,smatch[subjcat][0],smatch[subjcat][1],smatch[subjcat][2],
                             set(smatch[subjcat][3])-set(smatch[subjcat][2]),
                             " ".join(smatch[subjcat][4])),
                            (objcat,omatch[objcat][0],omatch[objcat][1],omatch[objcat][2],
                             set(omatch[objcat][3])-set(omatch[objcat][2]),
                             " ".join(omatch[objcat][4]))))
        ptree = self.predicate.tree.copy()
        ptree.lemmatise()
        return (res,ptree.tokens(),ptree.root.token.word,####################################################posmatch entities in schema using template sentences
                self.predicate.tree.tokens(),set(ptree.tokens())-set([ptree.root.token.word]))
    
    class Element:
        def __init__(self,tree):
            self.tree = GraphTripleTree.fromtripletree(tree)
            
        def schemamatch(self,schema):
            res,cmatches = {},{}
            for ngram,ngramtokens in self.tree.ngrams():
                cats = schema.lookupname(ngram)
                for cat in cats:
                    if cat not in cmatches:
                        cmatches[cat] = []
                    cmatches[cat].append(tuple(ngramtokens))
            fcmatches = {}
            for cat in cmatches:
                for match in cmatches[cat]:
                    if match not in fcmatches:
                        fcmatches[match] = set()
                    fcmatches[match].add(cat)
            fcmatches = {k:tuple(fcmatches[k]) for k in fcmatches}
            cmatches = {}
            for match in fcmatches:
                if fcmatches[match] not in cmatches:
                    cmatches[fcmatches[match]] = []
                cmatches[fcmatches[match]].append(match)
            for category in cmatches:
                matches = sorted(cmatches[category],key=lambda x:(-len(x),min([self.tree.heightof(t) for t in x])))
                for match in matches:######################################################if root
                    mtree = self.tree.copy()
                    mtree.mark(match)
                    ptree = self.tree.copy()
                    ptree.mark(match)
                    if not mtree.validentitymark():
                        continue
                        
                    mtree = mtree.entityroot()
                    atree = mtree.copy()
                    ftree = mtree.copy()
                    
                    mtree.entitycollapse()
                    
                    #mtree.filterall(lambda x:(x.token.word[:2] != "!#"))
                    atree.root.children = atree.root.filterchildrendeps({"nmod"})
                    for c in atree.root.children:
                        if any([n.ismarked() for n in c.dfs()]):
                            atree.root.removechild(c)
                    mtree.filteralldeps({"nsubj","nsubjpass","compound","amod"})
                    #for c in atree.root.children:
                    #    c.filteralldeps({"nsubj","nsubjpass","compound","amod","nmod"})
                    #atree.filteralldeps({"case","det"},exclude=True)#################################################################dont filter casedets in fullstring
                    #ftree.filteralldeps({"nsubj","nsubjpass","compound","amod","case","det","nmod"})
                    mtree.filterall(lambda x:not x.ismarked())
                    atree.filterall(lambda x:not x.ismarked())
                    mtree.lemmatise()
                    atree.lemmatise()
                    #ftree.lemmatise()
                    lptree = ptree.copy()
                    lptree.lemmatise()
                    res[":".join(category)] = [ptree.markedtokens(),lptree.markedtokens(),
                                     mtree.tokens(),atree.tokens(),ptree.tokens()]
                    break
            return res

