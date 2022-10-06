import collections

import nltk.data
nltk.data.path.append("./nltk_data")
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

from ..triples.triple.tree import TripleTree

lemma = WordNetLemmatizer().lemmatize
wnposmap = {"N":wn.NOUN,"V":wn.VERB,"J":wn.ADJ,"R":wn.ADV}

class GraphTripleTree(TripleTree):
    def __init__(self,root):
        TripleTree.__init__(self,root,None)
        
    @staticmethod
    def fromtripletree(tripletree):
        return GraphTripleTree(GraphTripleTree.Node.fromtriplenode(tripletree.root))
        
    def copy(self):
        return GraphTripleTree(self.root.copy())
    
    def __eq__(self,other):
        return self.root == other.root
    
    def __ne__(self,other):
        return not (self == other)
    
    def ngrams(self,n=12):
        ngs,toks = set(),self.tokens()
        for i in range(n,0,-1):
            for j,t in enumerate(toks):
                ngs.add((" ".join(toks[j:j+i]),tuple(toks[j:j+i])))
        return ngs
    
    def heightof(self,token):
        q = collections.deque([(self.root,0)])
        while q:
            curr,ph = q.popleft()
            if curr.token.word == token:
                return ph
            q.extend([(child,ph+1) for child in curr.children])
        return -1
    
    def mark(self,toks):
        for n in self.bfs():
            n.mark = False
            if n.token.word in toks:
                n.mark = True
                n.entityid = toks.index(n.token.word)
                
    def validentitymark(self):
        return (any([n.ismarked() and n.isnomial() for n in self.dfs()])
                and (self.root.ismarked() or any([c.ismarked() for c in self.root.children])))
    
    def entityroot(self):
        for p,c in self.parentchildpairs():
            if c.ismarked():
                return p.splitas()
        return self
            
    def entitycollapse(self):
        for p,c in self.parentchildpairs():
            if c.ismarked():
                #p.removechild(c)
                p.children += c.children
    
    def markedtokens(self):
        return [n.token.word for n in self.sortednodes(lambda x:x.ismarked())]
    
    def lemmatise(self):
        for n in self.dfs():
            n.token.word = lemma(n.token.word,pos=wnposmap.get(n.token.pos[0],wn.NOUN))
    
    class Node(TripleTree.Node):
        def __init__(self,token,dep,mark=False,entityid=-1,children=None):
            TripleTree.Node.__init__(self,token,dep,children)
            self.mark = mark
            self.entityid = entityid
            
        def copy(self):
            return GraphTripleTree.Node(self.token.copy(),self.dep[:],self.mark,self.entityid,
                                        [child.copy() for child in self.children])
        
        def __eq__(self,other):
            return (self.dep == other.dep and self.token == other.token and
                    len(self.children) == len(other.children) and
                    self.mark == other.mark and self.entityid == other.entityid and
                    all([c1==c2 for c1,c2 in zip(self.children,other.children)]))
        
        def __ne__(self,other):
            return not (self == other)
            
        @staticmethod
        def fromtriplenode(triplenode):
            return GraphTripleTree.Node(triplenode.token.copy(),triplenode.dep[:],False,-1,
                                        [GraphTripleTree.Node.fromtriplenode(c) for c in triplenode.children])
            
        def splitas(self,dep=None):
            nt = GraphTripleTree(self.copy())
            if dep:
                nt.root.dep = dep[:]
            return nt
        
        def ismarked(self):
            return self.mark

