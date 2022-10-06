import collections

from .triple import Triple
from ..nlparse.parse.parsetree import DependencyTree

class TripleTree(DependencyTree):
    def __init__(self,root,ruleset):
        DependencyTree.__init__(self,root)
        self.ruleset = ruleset
        
    @staticmethod
    def fromdeptree(deptree,ruleset):
        return TripleTree(TripleTree.Node.fromdepnode(deptree.root),ruleset)
        
    def copy(self):
        return TripleTree(self.root.copy(),self.ruleset)
    
    def __eq__(self,other):
        return self.root == other.root
    
    def __ne__(self,other):
        return not (self == other)
    
    def tokens(self,f=lambda x:True):
        return [n.token.word for n in self.sortednodes(f)]
    
    def postokens(self,f=lambda x:True):
        return [(n.token.word,n.token.pos) for n in self.sortednodes(f)]
    
    def parentchildtriples(self):
        for n in self.bfs():
            for cp in n.childpairs():
                yield n,cp
                
    def isverbal(self):
        return self.root.isverbal()
    
    def isnomial(self):
        return self.root.isnomial()
                
    def objscoresort(self):
        q = collections.deque([self.root])##############################################################use bfs()
        while q:
            curr = q.popleft()
            curr.sortchildren(lambda c,rs=self.ruleset:rs.objscore(c))
            q.extend(curr.children)
                    
    def basetriples(self,sent):
        ts,done = [],[]
        self.objscoresort()
        for p,(c1,c2) in self.parentchildtriples():
            if self.ruleset.isobjnode(c1) and self.ruleset.issubjnode(c2):
                if self.ruleset.isobjnode(c1,True):
                    if any([self.ruleset.isobjnode(oc1) and self.ruleset.issubjnode(oc2) for oc1 in c1.children for oc2 in c1.children]):
                        continue
                subjt = c2.splitas(self.ruleset)
                objt = c1.splitas(self.ruleset)
                predt = p.prunecopy(self.ruleset,{c1.dep,c2.dep},exclude=True)#################exlude multi nmod
                if self.ruleset.objswap(c1):
                    objt,predt = predt,objt
                if (subjt.root.token,predt.root.token) not in done and predt.isverbal():
                    done.append((subjt.root.token,predt.root.token))
                    ts.append(Triple(self.ruleset,sent,SubjectTree.fromtripletree(subjt,self.ruleset),
                                     PredicateTree.fromtripletree(predt,self.ruleset),
                                     ObjectTree.fromtripletree(objt,self.ruleset)))
        return ts
    
    def removeclauses(self):
        for n in self.bfs():
            for c in n.children[:]:
                if self.ruleset.isclausenode(c) or self.ruleset.iscomponentnode(c):
                    n.removechild(c)
                    
    def subjectcopy(self):
        for n,(c1,c2) in self.parentchildtriples():
            if (n.isverbal() and self.ruleset.issubjnode(c1) and c2.dep == "conj" and c2.isverbal() and
                #not any([self.ruleset.issubjnode(c1c2) and self.ruleset.isobjnode(c2c2) for c1c2 in c2.children for c2c2 in c2.children])):
                not any([self.ruleset.issubjnode(cc2) for cc2 in c2.children])):
                c2.addchild(c1.copy())
                
    def classifysubjects(self):
        for p,c in self.parentchildpairs():
            if self.ruleset.isclausenode(p) and self.ruleset.issubjnode(c) and c.posmatch("W"):
                c.dep = "whsubj"
            if self.ruleset.isobjnode(c) and c.posmatch("W"):
                c.dep = "whapp"
            if self.ruleset.iscomponentnode(p) and self.ruleset.issubjnode(c) and c.posmatch("PRP"):
                c.dep = "prpsubj"
            #if c.posmatch("T"):
            #    c.dep = 
            
    def splitsubjects(self):
        trees = [self.copy()]
        for p,c in trees[0].parentchildpairs():
            if c.isverbal() and c.dep == "conj":
                p.removechild(c)
        for p,c in self.parentchildpairs():
            if c.isverbal() and c.dep == "conj":
                trees.append(c.splitas(self.ruleset,"ROOT"))
        return trees
            
    def anaphoraresolve(self):
        trees = [self]
        for p,c in self.parentchildpairs():
            if self.ruleset.isclausenode(c):
                clausetree = c.splitas(self.ruleset,"ROOT")
                for i,cc in enumerate(clausetree.root.children):
                    if cc.dep == "whsubj":
                        clausetree.root.children[i] = p.copy()
                        clausetree.root.children[i].dep = "nsubj"
                        clausetree.root.children[i].children = clausetree.root.children[i].filterchildrendeps(set(self.ruleset.clauserules.keys())|{"case"},exclude=True)
                        break
                trees.append(clausetree)
            if self.ruleset.iscomponentnode(c):
                componenttree = c.splitas(self.ruleset,"ROOT")
                for i,cc in enumerate(componenttree.root.children):
                    if cc.dep == "prpsubj":
                        for sc in p.children:
                            if self.ruleset.issubjnode(sc):
                                componenttree.root.children[i] = sc.copy()
                                break
                        else:
                            cc.dep = "nsubj"
                        break
                trees.append(componenttree)
        return trees
    
    def conjunctionsplit(self):#######################################################deduplicate case and det etc
        trees = [self.copy()]
        trees[0].filteralldeps({"conj","cc"},exclude=True)
        while 1:
            tree = self.copy()
            for (p,c),(op,oc) in zip(tree.parentchildpairs(),self.parentchildpairs()):
                if not p.isverbal() and c.dep == "conj" and c.posmatch("N"):
                    #op = self.findnode(p.dep,p.token)
                    p.token = c.token
                    p.children = p.filterchildrendeps({"compound","conj","cc","nummod","amod","appos","dep"},exclude=True) + c.children
                    trees.append(tree)
                    #for oc in op.children:
                    #    if oc == c:
                    #        op.removechild(oc)
                    op.removechild(oc)
                    break
            else:
                break
        #for tree in trees:
        #    tree.filteralldeps({"conj","cc"},exclude=True)
        return trees
                
    class Node(DependencyTree.Node):
        def __init__(self,token,dep,children=None):
            DependencyTree.Node.__init__(self,token,dep,children)
            
        def copy(self):
            return TripleTree.Node(self.token.copy(),self.dep[:],[child.copy() for child in self.children])
        
        def __eq__(self,other):
            return (self.dep == other.dep and self.token == other.token and
                    len(self.children) == len(other.children) and
                    all([c1==c2 for c1,c2 in zip(self.children,other.children)]))
        
        def __ne__(self,other):
            return not (self == other)
            
        @staticmethod
        def fromdepnode(depnode):
            return TripleTree.Node(depnode.token.copy(),depnode.dep[:],
                                   [TripleTree.Node.fromdepnode(c) for c in depnode.children])
            
        def splitas(self,ruleset,dep=None):
            nt = TripleTree(self.copy(),ruleset)
            if dep:
                nt.root.dep = dep[:]
            return nt

        def prunecopy(self,ruleset,filtdeps,exclude=False,dep=None):
            nt = self.splitas(ruleset,dep)
            nt.root.children = nt.root.filterchildrendeps(filtdeps,exclude)
            return nt
        
        def isverbal(self):
            return self.posmatch("V")
        
        def isnomial(self):
            return self.posmatch("N")
        
class SubjectTree(TripleTree):
    def __init__(self,root,ruleset):
        TripleTree.__init__(self,root,ruleset)
        
    @staticmethod
    def fromtripletree(tripletree,ruleset):
        return SubjectTree(SubjectTree.Node.fromtriplenode(tripletree.root),ruleset)
        
    def copy(self):
        return SubjectTree(self.root.copy(),self.ruleset)
    
    def prunebranches(self):
        for n in self.bfs():
            for c in n.children[:]:
                if not self.ruleset.issubjbranch(c):
                    n.removechild(c)
    
    class Node(TripleTree.Node):
        def __init__(self,token,dep,children=None):
            TripleTree.Node.__init__(self,token,dep,children)
            
        @staticmethod
        def fromtriplenode(triplenode):
            return SubjectTree.Node(triplenode.token.copy(),triplenode.dep[:],
                                   [SubjectTree.Node.fromtriplenode(c) for c in triplenode.children])
        
        def copy(self):
            return SubjectTree.Node(self.token.copy(),self.dep[:],[child.copy() for child in self.children])

class PredicateTree(TripleTree):
    def __init__(self,root,ruleset):
        TripleTree.__init__(self,root,ruleset)
        
    @staticmethod
    def fromtripletree(tripletree,ruleset):
        return PredicateTree(PredicateTree.Node.fromtriplenode(tripletree.root),ruleset)
        
    def copy(self):
        return PredicateTree(self.root.copy(),self.ruleset)
    
    def prunebranches(self):
        for n in self.bfs():
            for c in n.children[:]:
                if not self.ruleset.ispredbranch(c):
                    n.removechild(c)
    
    class Node(TripleTree.Node):
        def __init__(self,token,dep,children=None):
            TripleTree.Node.__init__(self,token,dep,children)
            
        @staticmethod
        def fromtriplenode(triplenode):
            return PredicateTree.Node(triplenode.token.copy(),triplenode.dep[:],
                                      [PredicateTree.Node.fromtriplenode(c) for c in triplenode.children])
        
        def copy(self):
            return PredicateTree.Node(self.token.copy(),self.dep[:],[child.copy() for child in self.children])
        
class ObjectTree(TripleTree):
    def __init__(self,root,ruleset):
        TripleTree.__init__(self,root,ruleset)
        for n in self.dfs():
            if n.dep == "mark" and n.token.word.lower() == "that":
                n.dep = "thatmark"
        
    @staticmethod
    def fromtripletree(tripletree,ruleset):
        return ObjectTree(ObjectTree.Node.fromtriplenode(tripletree.root),ruleset)
        
    def copy(self):
        return ObjectTree(self.root.copy(),self.ruleset)
    
    def exchangenodes(self,predtree):
        for child in self.root.children:
            if self.ruleset.hasobjexchange(child):
                predtree.root.addchild(child)
                self.root.removechild(child)
        for child in predtree.root.children:
            if self.ruleset.haspredexchange(child):
                self.root.addchild(child)
                predtree.root.removechild(child)
                
    def prunebranches(self):
        for n in self.bfs():
            for c in n.children[:]:
                if not self.ruleset.isobjbranch(c):
                    n.removechild(c)
    
    class Node(TripleTree.Node):
        def __init__(self,token,dep,children=None):
            TripleTree.Node.__init__(self,token,dep,children)
            
        @staticmethod
        def fromtriplenode(triplenode):
            return ObjectTree.Node(triplenode.token.copy(),triplenode.dep[:],
                                   [ObjectTree.Node.fromtriplenode(c) for c in triplenode.children])
        
        def copy(self):
            return ObjectTree.Node(self.token.copy(),self.dep[:],[child.copy() for child in self.children])