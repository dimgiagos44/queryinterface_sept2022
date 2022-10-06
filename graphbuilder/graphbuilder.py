from graphbuilder.triples.extractor import TripleExtractor
from graphbuilder.triples.triple.triple import Triple
from graphbuilder.graphdb.graphdb import GraphDBSchema
from graphbuilder.abstractreader.textcleaner import TextCleaner
from graphbuilder.builder import GraphDBBuilder

from nltk.tokenize import sent_tokenize as sents, word_tokenize as tokens

extractor = TripleExtractor()
gdbbuilder = GraphDBBuilder(GraphDBSchema.load("data/UZHBio.gsch"))
sortedbands = sorted(gdbbuilder.gdb.schema.catindex["CytogenicBand"].index.values(),key=lambda x:(int(x.split("p")[0].split("q")[0]) if x[0] not in "XY" else (101 if x[0]=="X" else 102),float(x.split("p")[1]+"0" if "p" in x else x.split("q")[1]+"0")))
clean = TextCleaner().cleantext

def addabstract(pmid,abstract):
    cyabstract = clean(abstract)
    fnd = any([cy in cyabstract for cy in gdbbuilder.gdb.schema.catindex["CytogenicBand"].index.values()])
    cyabstokens = [tokens(sent) for sent in sents(cyabstract)]
    cys = set(gdbbuilder.gdb.schema.catindex["CytogenicBand"].index.values())
    for i,cysent in enumerate(cyabstokens):
        nsent = []
        for j,cytok in enumerate(cysent):
            if any([pt in cys for pt in [cytok[:i] for i in range(2,len(cytok)+1)]]):
                cytoks = []
                if len([1 for c in cytok if c == "p"]) > 1 or "-" in cytok or len([1 for c in cytok if c == "q"]) > 1:
                    if "-" in cytok and cytok.split("-")[0] in cys:
                        frst = sortedbands.index(cytok.split("-")[0])
                        try:
                            if cytok.split("-")[1] in cys:
                                snd = sortedbands.index(cytok.split("-")[1])
                            elif cytok.split("p")[0].split("q")[0]+cytok.split("-")[1] in cys:
                                snd = sortedbands.index(cytok.split("p")[0].split("q")[0]+cytok.split("-")[1])
                            elif cytok.split("p")[0].split("q")[0]+("p" if "p" in cytok else "q")+cytok.split("-")[1] in cys:
                                snd = sortedbands.index(cytok.split("p")[0].split("q")[0]+("p" if "p" in cytok else "q")+cytok.split("-")[1])
                            else:
                                snd = -1
                            if snd != -1:
                                if snd < frst:
                                    frst,snd = snd,frst
                                cytoks = ["CytogenicBand"+"I"+str(frst)+"I"+str(snd)]
                        except IndexError:
                            cytoks = ["CytogenicBand"+cytok.split("-")[0].replace(".","DOT")]
                    elif len([1 for c in cytok if c == "p"]) > 1:
                        tks = []
                        mn = cytok.split("p")[0]
                        for pt in cytok.split("p")[1:]:
                            tks.append(mn+"p"+pt)
                        cytoks = ["CytogenicBand"+("A".join(tks)).replace(".","DOT")]
                    elif len([1 for c in cytok if c == "q"]) > 1:
                        tks = []
                        mn = cytok.split("q")[0]
                        for pt in cytok.split("q")[1:]:
                            tks.append(mn+"q"+pt)
                        cytoks = ["CytogenicBand"+("A".join(tks)).replace(".","DOT")]            
                else:
                    cytoks = ["CytogenicBand"+cytok.replace(".","DOT")]
                nsent.extend(cytoks)
            else:
                nsent.append(cytok)
            cyabstokens[i] = nsent
    cyabstract = " ".join([" ".join(cysent) for cysent in cyabstokens])
    triples = extractor.extract(cyabstract)
    rems = []
    for k,triple in enumerate(list(triples)):
        bnds = [n for n in triple.subjecttree.dfs() if "CytogenicBand" in n.token.word]
        if len(bnds) > 1:
            for i,bnd in enumerate(bnds):
                ntriple = Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy())
                for j,bnd2 in enumerate(bnds):
                    if i != j:
                        for p,c in ntriple.subjecttree.parentchildpairs():
                            if c == bnd2:
                                p.removechild(c)
                                break
                triples.append(ntriple)
            rems.append(k)
    rems = []
    for k,triple in enumerate(list(triples)):
        bnds = [n for n in triple.objecttree.dfs() if "CytogenicBand" in n.token.word]
        if len(bnds) > 1:
            for i,bnd in enumerate(bnds):
                ntriple = Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy())
                for j,bnd2 in enumerate(bnds):
                    if i != j:
                        for p,c in ntriple.objecttree.parentchildpairs():
                            if c == bnd2:
                                p.removechild(c)
                                break
                triples.append(ntriple)
            rems.append(k)
    triples = [triple for i,triple in enumerate(triples) if i not in rems]
    for triple in list(triples):
        nw = True
        for n in triple.subjecttree.dfs():
            if "CytogenicBand" in n.token.word:
                nw = True
                if "A" in n.token.word:
                    n.token.word = n.token.word.replace("CytogenicBand","").replace("DOT",".")
                    wd = n.token.word[:]
                    for pt in wd.split("A")[1:]:
                        n.token.word = pt
                        triples.append(Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy()))
                    n.token.word = wd.split("A")[0]
                elif "I" in n.token.word:
                    n.token.word = n.token.word.replace("CytogenicBand","")
                    fst,snd = map(int,n.token.word.split("I")[1:3])
                    for i in range(fst,snd):
                        n.token.word = sortedbands[i]
                        triples.append(Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy()))
                    n.token.word = sortedbands[snd]
                else:
                    n.token.word = n.token.word.replace("CytogenicBand","").replace("DOT",".")
            if n.token.word == "-LRB-":
                n.token.word = "("
            if n.token.word == "-RRB-":
                n.token.word = ")"
            if n.token.word == "-LSB-":
                n.token.word = "["
            if n.token.word == "-RSB-":
                n.token.word = "]"
        for n in triple.objecttree.dfs():
            if "CytogenicBand" in n.token.word:
                nw = True
                if "A" in n.token.word:
                    n.token.word = n.token.word.replace("CytogenicBand","").replace("DOT",".")
                    wd = n.token.word[:]
                    for pt in wd.split("A")[1:]:
                        n.token.word = pt
                        triples.append(Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy()))
                    n.token.word = wd.split("A")[0]
                elif "I" in n.token.word:
                    n.token.word = n.token.word.replace("CytogenicBand","")
                    fst,snd = map(int,n.token.word.split("I")[1:3])
                    for i in range(fst,snd):
                        n.token.word = sortedbands[i]
                        triples.append(Triple(triple.ruleset,triple.sent,triple.subjecttree.copy(),triple.predicatetree.copy(),triple.objecttree.copy()))
                    n.token.word = sortedbands[snd]
                else:
                    n.token.word = n.token.word.replace("CytogenicBand","").replace("DOT",".")
            if n.token.word == "-LRB-":
                n.token.word = "("
            if n.token.word == "-RRB-":
                n.token.word = ")"
            if n.token.word == "-LSB-":
                n.token.word = "["
            if n.token.word == "-RSB-":
                n.token.word = "]"
    while 1:
        fnd = False
        for i,triple1 in list(enumerate(triples)):
            for triple2 in list(triples[i+1:]):
                if triple1.predicatetree.tokens() == ["is"] or triple1.predicatetree.tokens() == ["are"]:
                    if triple2.subjecttree.tokens() == triple1.objecttree.tokens():
                        fnd = True
                        triple2.subjecttree = triple1.subjecttree.copy()
            if fnd:
                triple1.predicatetree.root.token.word = "###REMOVE###"
                break
        if not fnd:
            break
    rems = []
    for i,triple in list(enumerate(triples)):
        if triple.predicatetree.root.token.word == "###REMOVE###":
            rems.append(i)
        if len([1 for n in triple.sent.parse.deptree.dfs() if n.dep == "conj"]) >= 4:
            rems.append(i)
        if any([n.dep=="dep" and n.posmatch("V") for n in triple.sent.parse.deptree.dfs()]):
            rems.append(i)
    sppairs = {(tuple(triple.subjecttree.tokens()),tuple(triple.predicatetree.tokens())):0 for triple in triples}
    for triple in triples:
        sppairs[(tuple(triple.subjecttree.tokens()),tuple(triple.predicatetree.tokens()))] += 1
    for i,triple in enumerate(triples):
        if sppairs[(tuple(triple.subjecttree.tokens()),tuple(triple.predicatetree.tokens()))] > 3:
            rems.append(i)
    for i,triple in enumerate(triples):
        np = 0
        for n in triple.objecttree.dfs():
            if n.posmatch("-L"):
                np += 1
            if n.posmatch("-R"):
                np -= 1
        if np:
            j = 200
            for n in triple.objecttree.dfs():
                if n.posmatch("-L"):
                    j = n.token.index
                    break
            while 1:
                for p,c in triple.objecttree.parentchildpairs():
                    if c.token.index >= j:
                        p.removechild(c)
                        break
                else:
                    break
            if triple.objecttree.root.token.posmatch("-L") and not triple.objecttree.root.children:
                rems.append(i)
    triples = [triple for i,triple in enumerate(triples) if i not in rems]
    for triple in list(triples):
        fnd = True
        while fnd:
            fnd = False
            for p,c in triple.subjecttree.parentchildpairs():
                if c.token.word == "," or c.token.word == "-" or c.token.word == ".":
                    p.removechild(c)
                    fnd = True
                    break
        fnd = True
        while fnd:
            fnd = False
            for p,c in triple.objecttree.parentchildpairs():
                if c.token.word == "," or c.token.word == "-" or c.token.word == ".":
                    p.removechild(c)
                    fnd = True
                    break
        if 1 or nw:
            otrips = gdbbuilder.addtriple(triple,pmid,debug=False,debugout=False)
