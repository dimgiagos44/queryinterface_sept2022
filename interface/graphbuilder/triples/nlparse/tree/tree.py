import collections

class Tree:
    def __init__(self,root):
        self.root = root
        
    def dfs(self):
        yield from self.root.dfs()
        
    def bfs(self):
        yield from self.root.bfs()
            
    def leaves(self):
        return self.root.leaves()
    
    def copy(self):
        return Tree(self.root.copy())
    
    def filterall(self,f):
        self.root.filterall(f)
        
    def parentchildpairs(self):
        for n in self.bfs():
            for c in n.children:
                yield n,c
                
    def parentchildpairsdfs(self):
        for n in self.dfs():
            for c in n.children:
                yield n,c
                        
    class Node:
        def __init__(self,children):
            self.children = [] if not children else children
            
        def addchild(self,child):
            self.children.append(child)
            
        def removechild(self,child):
            for i,c in enumerate(self.children):
                if c is child:
                    del self.children[i]
                    return
            
        def copy(self):
            return Tree.Node([child.copy() for child in self.children])
            
        def isleaf(self):
            return bool(self.children)
        
        def dfs(self):
            for c in self.children:
                yield from c.dfs()
            yield self
            
        def bfs(self):
            q = collections.deque([self])
            while q:
                curr = q.popleft()
                yield curr
                q.extend(curr.children)
                
        def childpairs(self,unique=False):
            return [(c1,c2) for c1 in self.children for c2 in self.children if (not unique) or c1 is not c2]
        
        def filterchildren(self,f):
            return [child for child in self.children if f(child)]
        
        def filterall(self,f):
            self.children = self.filterchildren(f)
            for c in self.children:
                c.filterall(f)
        
        def sortchildren(self,key):
            self.children = sorted(self.children,key=key)
            
        def leaves(self):
            return [n for n in self.dfs() if n.isleaf()]