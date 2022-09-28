from flask import render_template,jsonify,request
from queryinterface_v4 import app
from metapub import PubMedFetcher
import json
from urllib.request import Request,urlopen

from .graphdb.graphdb import GraphDB,GraphDBSchema

CACHED = False

schema = GraphDBSchema.load("data/UZHBio.gsch")
gdb = GraphDB(schema,"localhost","7687","neo4j","root")

with open("data/nci_thesaurus.txt","r",encoding="utf-8") as fl:
    nci = [{"code":ln.split("\t")[0],
            "display_name":ln.split("\t")[5].split("|") if ln.split("\t")[5].split("|")[0] else [],
            "semantic_type":ln.split("\t")[7][:-1]} for ln in fl.readlines()]
nciidx = {ln["display_name"][0].replace("-","").replace(".","").replace("'",""):"NCIT:"+ln["code"]
          for ln in nci if ln["display_name"] if any([ty=="Neoplastic Process" for ty in ln["semantic_type"].split("|")])}

with open("data/UZHAbstracts.json","r",encoding="utf-8") as fl:
    pmidtitles = {res["id"].split(":")[1]:res["title"] for res in json.load(fl)["response"]["results"]}

def queryfilts(args,defaultlim=20):
    s,p,o = args.get("s","").split(","),args.get("p","").split(","),args.get("o","").split(",")
    lim = args.get("limit",str(defaultlim))
    stypes,rtypes,otypes = args.get("stypes","").split(","),args.get("rtypes","").split(","),args.get("otypes","").split(",")
    pmid = args.get("pmid","")
    wherestr = "where " if any(map(bool,[s[0],p[0],o[0],stypes[0],rtypes[0],otypes[0],pmid])) else ""
    if pmid:
        wherestr += "s.PMID = '%s' and " % pmid
    if s[0]:
        wherestr += "(" + " or ".join(["n.Name = '%s'"%sty for sty in s]) + ") and "
    if p[0]:
        wherestr += "(" + " or ".join(["type(r) = '%s'"%pty for pty in p]) + ") and "
    if o[0]:
        wherestr += "(" + " or ".join(["m.Name = '%s'"%oty for oty in o]) + ") and "
    if stypes[0]:
        wherestr += "(" + " or ".join(["n:%s"%sty for sty in stypes]) + ") and "
    if otypes[0]:
        wherestr += "(" + " or ".join(["m:%s"%oty for oty in otypes]) + ") and "
    if rtypes[0]:
        wherestr += "(" + " or ".join(["r:%s"%rty for rty in rtypes]) + ")"
    if wherestr[-5:] == " and ":
        wherestr = wherestr[:-5]
    return wherestr,lim

def gettriples(args):
    wherestr,lim = queryfilts(args)
    trips = [{k:(res[k] if k in res else pmidtitles[res["s.PMID"]]) for k in list(res)+["title"]}
             for res in gdb.runcommand("match (n)<-[:INSTANCE_OF]-(s)-[r]->(o)-[:INSTANCE_OF]->(m)\n%s\nreturn s,labels(n),s.PMID,r,r.FullString,type(r),o,labels(m),n,m\nlimit %s"%(wherestr,lim))]
    #print(trips[0])
    rtrips = [{k:(res[k] if k in res else pmidtitles[res["s.PMID"]]) for k in list(res)+["title"]}
              for res in gdb.runcommand("match (n)<-[:INSTANCE_OF]-(s)<-[r]-(o)-[:INSTANCE_OF]->(m)\n%s\nreturn s,labels(n),s.PMID,r,r.FullString,type(r),o,labels(m),n,m\nlimit %s"%(wherestr,lim))]
    #print(rtrips[0])
    atrips = []
    for trip in trips:
        if not any([trip["n"]["Name"]==atrip["n"]["Name"] and trip["type(r)"]==atrip["type(r)"] and trip["m"]["Name"]==atrip["m"]["Name"] for atrip in atrips]):
            #number_of_citations = find(trip['s.PMID'])
            #trip['citedby'] = number_of_citations
            atrips.append(trip)
    for trip in rtrips:
        if not any([trip["m"]["Name"]==atrip["n"]["Name"] and trip["type(r)"]==atrip["type(r)"] and trip["n"]["Name"]==atrip["m"]["Name"] for atrip in atrips]):
            trip["labels(n)"],trip["labels(m)"] = trip["labels(m)"],trip["labels(n)"]
            trip["s"],trip["o"] = trip["o"],trip["s"]
            trip["m"],trip["n"] = trip["n"],trip["m"]
            atrips.append(trip)
    resp = jsonify({"triples":atrips})
    resp.headers.add('Access-Control-Allow-Origin','*')
    return resp

def find(pmid):
    url = 'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=' + pmid
    with urlopen(url) as response:
        response_html = str(response.read())
        number_of_citations = response_html.split('<div class="results-amount">')[1]
        number_of_citations = number_of_citations.split('<span class="value">')[1]
        number_of_citations = int(number_of_citations.split('</span>')[0])
    print("This citation {} has been cited by {}" .format(pmid, number_of_citations))
    return number_of_citations

def findCitedIds(i, pmid):
    citationUrl = 'https://pubmed.ncbi.nlm.nih.gov/?size=200&linkname=pubmed_pubmed_citedin&from_uid='
    with urlopen(citationUrl+pmid+'&page='+str(i)) as response:
        response_html = str(response.read())
        paper_ids = response_html.split('data-chunk-ids=')[1]
        paper_ids = paper_ids.split('<div class="title first">')[0]
        paper_ids = paper_ids.split('"')[1].split('"')[0]
        paper_ids = paper_ids.split(',')
        paper_ids = [int(i) for i in paper_ids]
    return paper_ids


@app.route('/citedby')
def findCitations():
    pmid = request.args.get('pmid')
    url = 'https://pubmed.ncbi.nlm.nih.gov/?size=200&linkname=pubmed_pubmed_citedin&from_uid=' + pmid
    with urlopen(url) as response:
        response_html = str(response.read())
        number_of_citations = response_html.split('<div class="results-amount">')[1]
        number_of_citations = number_of_citations.split('<span class="value">')[1]
        number_of_citations = int(number_of_citations.split('</span>')[0])
        count = number_of_citations
        i = 1
        total_ids = []
        while (count > 0):
            paper_ids = findCitedIds(i, pmid)
            total_ids += paper_ids
            count -= 200
            i += 1

    total_ids = [int(i) for i in total_ids]
    print('This paper has been cited:', number_of_citations, 'times')
    resp = jsonify({"citedby": number_of_citations, "paper_ids": total_ids})
    resp.headers.add('Access-Control-Allow-Origin','*')
    return resp

@app.route('/article_abstract')
def findAbstract():
    pmid = request.args.get('pmid')
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(pmid)
    abstract = article.abstract
    title = article.title
    resp = jsonify({"pmid": pmid, "title": title, "abstract": abstract})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp
    

@app.route('/cnvmatches')
def cnvtrips():
    ctypes = request.args.get("ctypes","")
    bands = request.args.get("bands","").split(",")
    if bands[0]:
        bands = set(bands)
        for band in list(bands):
            if "p" in band:
                bands.add(band.split("p")[0]+"p")
            elif "q" in band:
                bands.add(band.split("q")[0]+"q")
            if "." in band:
                bands.add(band.split(".")[0])
        bands = [bnd.replace(".","") for bnd in bands] + [bnd.replace(".","").upper() for bnd in bands]
    else:
        bands = []
    return gettriples({"o":ctypes,"stypes":"CytogenicBand","otypes":"NeoplasticProcess","s":(",".join(list(bands)) if bands else "")})

@app.route('/triples')
def further():
    return gettriples(request.args)

@app.route("/params")
def params():
    wherestr,_ = queryfilts(request.args)
    qry = gdb.runcommand("match (n)<-[:INSTANCE_OF]-(s)-[r]-(o)-[:INSTANCE_OF]->(m)\n%s\nreturn labels(n),labels(m),n.Name,type(r),m.Name"%wherestr)
    resp = jsonify({"stypes":list({lb for res in qry for lb in res["labels(n)"]}),
                    "otypes":list({lb for res in qry for lb in res["labels(m)"]}),
                    "rtypes":list({res["type(r)"] for res in qry}),
                    "snames":list({res["n.Name"] for res in qry}),
                    "onames":list({res["m.Name"] for res in qry})})
    resp.headers.add('Access-Control-Allow-Origin','*')
    return resp

@app.route("/cancertypes")
def cancertypes():
    resp = jsonify({"cancertypes":[{"name":res["n.Name"],"id":nciidx[res["n.Name"]]} for res in gdb.runcommand("match (n:NeoplasticProcess)<-[:INSTANCE_OF]-(s)-[r]-(o)-[:INSTANCE_OF]->(m:CytogenicBand)\nreturn distinct n.Name") if res["n.Name"] in nciidx]})
    resp.headers.add('Access-Control-Allow-Origin','*')
    return resp

@app.route("/cnvplot")
def cnvplot():
    currnci = request.args.get("nci","")
    if not currnci and not CACHED:
        resp = jsonify({"plot":{"losses":[],"gains":[],"xaxis":[],"widths":[],"bands":[]}})
        resp.headers.add('Access-Control-Allow-Origin','*')
        return resp
    if CACHED:
        with open("data/cnvtest.json","r",encoding="utf-8") as fl:
            plotdata = json.load(fl)["response"]["results"][0]["intervalFrequencies"]
    else:
        try:
            req = Request("http://progenetix.org/services/intervalFrequencies/?filters=%s"%currnci,headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req) as fl:
                resp = "".join([ln.decode("utf-8") for ln in fl.readlines()])
                plotdata = json.loads(resp)["response"]["results"][0]["intervalFrequencies"]
        except Exception as e:
            print(e)
            resp = jsonify({"plot":{"losses":[],"gains":[],"xaxis":[],"widths":[],"bands":[]}})
            resp.headers.add('Access-Control-Allow-Origin','*')
            return resp
    chroms = sorted({rw["referenceName"] for rw in plotdata},key=lambda x:int(x) if x not in "XY" else (100 if x=="X" else 101))
    plotdata = sorted(plotdata,key=lambda x:(int(x["referenceName"]) if x["referenceName"] not in "XY" else (100 if x["referenceName"]=="X" else 101),x["start"]))
    chrombins = {k:sorted([rw["start"]+(rw["size"]//2) for rw in plotdata if rw["referenceName"]==k]) for k in chroms}
    chromstartendbins = {k:sorted([(rw["start"],rw["end"]) for rw in plotdata if rw["referenceName"]==k]) for k in chroms}
    allbins = []
    lst = 0
    for k in chroms:
        alle = 0
        for s,e in chromstartendbins[k]:
            allbins.append(lst+s)
            alle = e
        lst += alle
    xaxis = [(s+e)//2 for s,e in zip(allbins,(allbins[1:])+[lst])]
    widths = [(e-s) for s,e in zip(allbins,(allbins[1:])+[lst])]
    bands = []
    for rw in plotdata:
        bnds = rw["cytobands"]
        bnds = bnds.replace("p",","+rw["referenceName"]+"p")
        if bnds[0] == ",":
            bnds = bnds[1:]
        bnds = bnds.replace("q",","+rw["referenceName"]+"q")
        if bnds[0] == ",":
            bnds = bnds[1:]
        bands.append(bnds)
    plot = {"losses":[-float(rw["lossFrequency"]) for rw in plotdata],"gains":[float(rw["gainFrequency"]) for rw in plotdata],"xaxis":xaxis,"widths":widths,"bands":bands}
    resp = jsonify({"plot":plot})
    resp.headers.add('Access-Control-Allow-Origin','*')
    return resp
