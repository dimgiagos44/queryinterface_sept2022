import json

class Ruleset:
    def __init__(self,subjrules,objrules,clauserules,branchrules):
        self.objrules = objrules
        self.objruleidx = {rule.dep:rule for rule in objrules}
        self.subjrules = {rule.dep:rule for rule in subjrules}
        self.clauserules = {rule.dep:rule for rule in clauserules}
        self.branchrules = branchrules
        
    def isobjnode(self,node,strict=False):
        return any([rule.applies(node,strict) for rule in self.objrules])

    def objscore(self,node):
        return ([i for i,rule in enumerate(self.objrules) if rule.applies(node)] + [len(self.objrules)])[0]
    
    def objswap(self,node):
        return self.objruleidx[node.dep].swap
    
    def issubjnode(self,node):
        return node.dep in self.subjrules
    
    def isclausenode(self,node):
        return node.dep in self.clauserules and not self.clauserules[node.dep].component
    
    def iscomponentnode(self,node):
        return node.dep in self.clauserules and self.clauserules[node.dep].component
    
    def hasobjexchange(self,node):
        return self.branchrules.hasobjexchange(node.dep)
    
    def haspredexchange(self,node):
        return self.branchrules.haspredexchange(node.dep)
    
    def issubjbranch(self,node):
        return self.branchrules.issubjbranch(node.dep)
    
    def ispredbranch(self,node):
        return self.branchrules.ispredbranch(node.dep)
    
    def isobjbranch(self,node):
        return self.branchrules.isobjbranch(node.dep)
    
    @staticmethod
    def load(flname):
        with open(flname,"r",encoding="utf-8") as fl:
            rules = json.load(fl)
        return Ruleset([SubjectRule(rule["dependency"]) for rule in rules["subjectrules"]],
                       [ObjectRule(rule["dependency"],rule["swap"],rule["strict"])
                        for rule in rules["objectrules"]],
                       [ClauseRule(rule["dependency"],rule["component"]) for rule in rules["clauserules"]],
                       BranchRuleTable.fromdict(rules["branchrules"]))
        
class BranchRuleTable:
    _IDS = {"exclude":-1,
            "subject":0,
            "predicate":1,
            "object":2}
    
    def __init__(self,table,alldeps):
        self.table = table
        self.alldeps = alldeps
        
    def hasobjexchange(self,dep):
        return dep in self.alldeps and self.table[self._IDS["object"]][dep] == self._IDS["predicate"]
    
    def haspredexchange(self,dep):
        return dep in self.alldeps and self.table[self._IDS["predicate"]][dep] == self._IDS["object"]
    
    def issubjbranch(self,dep):
        return dep in self.alldeps and self.table[self._IDS["subject"]][dep] == self._IDS["subject"]
    
    def ispredbranch(self,dep):
        return dep in self.alldeps and self.table[self._IDS["predicate"]][dep] == self._IDS["predicate"]

    def isobjbranch(self,dep):
        return dep in self.alldeps and self.table[self._IDS["object"]][dep] == self._IDS["object"]
    
    @staticmethod
    def fromdict(jdict):
        alldeps = {dep for k in jdict for dep in jdict[k]}
        table = [{dep:-1 for dep in alldeps} for _ in range(3)]
        for k in jdict:
            if k in BranchRuleTable._IDS:
                for dep in jdict[k]:
                    table[BranchRuleTable._IDS[k]][dep] = BranchRuleTable._IDS[k]
            else:
                frm,to = k.split("->")
                for dep in jdict[k]:
                    table[BranchRuleTable._IDS[frm]][dep] = BranchRuleTable._IDS[to]
        return BranchRuleTable(table,alldeps)
    
class DependencyRule:
    def __init__(self,dep):
        self.dep = dep
        
    def applies(self,node):
        return node.dep == self.dep
    
class ObjectRule(DependencyRule):
    def __init__(self,dep,swap,strict):
        DependencyRule.__init__(self,dep)
        self.swap = swap
        self.strict = strict

    def applies(self,node,strict=False):
        return node.dep == self.dep and (not strict or self.strict == strict)
        
class SubjectRule(DependencyRule):
    def __init__(self,dep):
        DependencyRule.__init__(self,dep)
        
class ClauseRule(DependencyRule):
    def __init__(self,dep,component):
        DependencyRule.__init__(self,dep)
        self.component = component
