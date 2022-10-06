class Triple:
    def __init__(self,ruleset,sent,subjecttree,predicatetree,objecttree):
        self.ruleset = ruleset
        self.sent = sent
        self.subjecttree = subjecttree
        self.predicatetree = predicatetree
        self.objecttree = objecttree

    def exchangenodes(self):
        self.objecttree.exchangenodes(self.predicatetree)
        
    def prunebranches(self):
        self.subjecttree.prunebranches()
        self.objecttree.prunebranches()
        self.predicatetree.prunebranches()
        
    def totext(self):
        return (" ".join(self.subjecttree.tokens()),
                " ".join(self.predicatetree.tokens()),
                " ".join(self.objecttree.tokens()))
        
    def __str__(self):
        return "Subject:\n%sPredicate:\n%sObject:\n%s" % (self.subjecttree,self.predicatetree,self.objecttree)
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self,other):
        return (self.subjecttree == other.subjecttree and
                self.predicatetree == other.predicatetree and
                self.objecttree == other.objecttree)
    
    def __ne__(self,other):
        return not (self == other)
