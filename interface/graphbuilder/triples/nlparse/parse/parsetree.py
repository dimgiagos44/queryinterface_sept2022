from nltk import Tree as nltkTree

from ..tree.tree import Tree

class PhraseTree(Tree):
    def __init__(self,root):
        Tree.__init__(self,root)
        
    @staticmethod
    def fromparser(response,i,tokens):
        ts = response.get("allParseTrees","# Parse\n"+response["parse"])
        nltkt = nltkTree.fromstring(("\n".join(ts.split("# Parse")[i+1].split("\n")[1:])).replace("\xa0",""))
        root = PhraseTree.Node(nltkt.label())
        q = [(nltkt,root)]
        while q:
            cnltkt,ct = q.pop()
            for c in cnltkt:
                if type(c) == str:
                    tstr = c.split("_")[0]
                    n = PhraseTree.LeafNode([token for token in tokens if token.word == tstr][0])
                else:
                    n = PhraseTree.Node(c.label())
                    q.append((c,n))
                ct.addchild(n)
        return PhraseTree(root).fold().phrasemerge()
    
    def rate(self):
        fragn,xn = 0,0
        for n in self.dfs():
            if not n.isleaf():
                if n.label == "FRAG":
                    fragn += 1;
                elif n.label == "X":
                    xn += 1;
        return fragn + (2*xn)
    
    def fold(self):
        while 1:
            for p,c in self.parentchildpairs():
                if c.isleaf():
                    continue
                if len(p.children) == 1 and p.label == c.label:
                    #p.label += "|"+c.label
                    p.children = c.children
            else:
                break
        return self
    
    def phrasemerge(self):
        while 1:
            for p in self.bfs():
                if len(p.children) == 1 and p.children[0].isleaf():
                    continue
                fnd = False
                while 1:
                    for c1,c2 in p.childpairs(unique=True):
                        if (c1.isleaf() or c1.children[0].isleaf()) or (c2.isleaf() or c2.children[0].isleaf()):
                            continue
                        if c1.label == c2.label:
                            c1.children += c2.children
                            p.removechild(c2)
                            fnd = True
                            break
                    else:
                        break
                if fnd:
                    break
            else:
                break
        return self
    
    def copy(self):
        return PhraseTree(self.root.copy())
    
    def __eq__(self,other):
        return self.root == other.root
    
    def __ne__(self,other):
        return not (self == other)
    
    def shalloweq(self,other):
        return self.root.shalloweq(other.root)
                
    def __str__(self):
        return self.root.tformat(0)
    
    def __repr__(self):
        return str(self)
    
    class Node(Tree.Node):
        def __init__(self,label,children=None):
            Tree.Node.__init__(self,children)
            self.label = label
            
        def isleaf(self):
            return False
        
        def copy(self):
            return PhraseTree.Node(self.label[:],[child.copy() for child in self.children])
        
        def splitas(self,label=None):
            nt = PhraseTree(self)
            if label:
                nt.root.label = label
            return nt
        
        def tformat(self,level):
            return "%s%s\n%s" % (" "*level,self.label,"".join([c.tformat(level+4) for c in self.children]))
        
        def shalloweq(self,other):
            if type(self) != type(other):
                return False
            return (self.label == other.label and
                    len(self.children) == len(other.children) and
                    all([c.shalloweq(oc) for c,oc in zip(self.children,other.children)]))
        
        def __eq__(self,other):
            if type(self) != type(other):
                return False
            return (self.label == other.label and
                    len(self.children) == len(other.children) and
                    all([c==oc for c,oc in zip(self.children,other.children)]))
        
        def __ne__(self,other):
            return not (self == other)
        
        def __str__(self):
            return self.label
        
        def __repr__(self):
            return str(self)
        
    class LeafNode(Tree.Node):
        def __init__(self,token):
            Tree.Node.__init__(self,None)
            self.token = token
            
        def isleaf(self):
            return True
        
        def copy(self):
            return PhraseTree.LeafNode(self.token.copy())
        
        def tformat(self,level):
            return (" "*level)+self.token.word+"\n"
        
        def shalloweq(self,other):
            if type(self) != type(other):
                return False
            return self.token.word.lower() == other.token.word.lower()
        
        def __eq__(self,other):
            if type(self) != type(other):
                return False
            return self.token == other.token

        def __ne__(self,other):
            return not (self == other)
        
        def __str__(self):
            return self.token.word
        
        def __repr__(self):
            return str(self)
    
class DependencyTree(Tree):
    def __init__(self,root):
        Tree.__init__(self,root)
        
    @staticmethod
    def fromparser(response,tokens):
        deps = response["basicDependencies"]
        root = [dep["dependent"] for dep in deps if dep["governor"]==0][0]
        rootnode = DependencyTree.Node(tokens[root-1],"ROOT")
        q = [(root,rootnode)]
        while q:
            prev,prevnode = q.pop()
            for nxt,nxtdep in [(dep["dependent"],dep["dep"]) for dep in deps if dep["governor"]==prev]:
                nxtnode = DependencyTree.Node(tokens[nxt-1],nxtdep)
                prevnode.addchild(nxtnode)
                q.append((nxt,nxtnode))
        return DependencyTree(rootnode)
    
    def copy(self):
        return DependencyTree(self.root.copy())

    def filteralldeps(self,deps,exclude=False):
        self.root.filteralldeps(deps,exclude)
        
    def findnode(self,dep,token):
        for n in self.bfs():
            if n.dep == dep and n.token == token:
                return n
        return None
    
    def sortednodes(self,f=lambda x:True):
        return [n for n in sorted(self.dfs(),key=lambda x:x.token.index) if f(n)]

    def __str__(self):
        return self.root.tformat(0)
    
    def __repr__(self):
        return str(self)
    
    class Node(Tree.Node):
        def __init__(self,token,dep,children=None):
            Tree.Node.__init__(self,children)
            self.token = token
            self.dep = dep
            
        def copy(self):
            return DependencyTree.Node(self.token.copy(),self.dep[:],[child.copy() for child in self.children])
        
        def splitas(self,dep=None):
            nt = DependencyTree(self.copy())
            if dep:
                nt.root.dep = dep[:]
            return nt
        
        def filterchildrendeps(self,deps,exclude=False):
            return self.filterchildren((lambda c:c.dep in deps) if not exclude else (lambda c:c.dep not in deps))
        
        def filteralldeps(self,deps,exclude=False):
            self.filterall((lambda c:c.dep in deps) if not exclude else (lambda c:c.dep not in deps))
        
        def prunecopy(self,filtdeps,exclude=False,dep=None):
            nt = self.splitas(dep)
            nt.root.children = nt.root.filterchildrendeps(filtdeps,exclude)
            return nt
        
        def posmatch(self,pos):
            return self.token.posmatch(pos)
        
        def tformat(self,level):
            return "%s%s | %s %s\n%s" % (" "*level,self.dep,self.token.word,self.token.pos,
                                         "".join(c.tformat(level+4) for c in self.children))
        
        def __str__(self):
            return self.dep + " " + self.token.word
        
        def __repr__(self):
            return str(self)
    
class Token:
    def __init__(self,word,pos,index):
        self.word = word
        self.pos = pos
        self.index = index
        
    @staticmethod
    def fromparser(parsetoken):
        return Token(parsetoken["word"].replace("\xa0",""),parsetoken["pos"],parsetoken["index"]-1)
    
    def copy(self):
        return Token(self.word[:],self.pos[:],self.index)
    
    def posmatch(self,pos):
        return all([p1==p2 for p1,p2 in zip(self.pos,pos)])
    
    def __eq__(self,other):
        return self.word == other.word and self.pos == other.pos and self.index == other.index
    
    def __ne__(self,other):
        return not (self == other)
    
    def __str__(self):
        return self.word
    
    def __repr__(self):
        return str(self)
