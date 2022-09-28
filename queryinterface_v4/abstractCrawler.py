from flask import render_template,jsonify,request
import json
from urllib.request import Request,urlopen
from pubmed_lookup import PubMedLookup, Publication
from metapub import PubMedFetcher
from tqdm import tqdm
import sys, getopt
import csv

#crawls titles and abstracts from papers that cite the input-paper
#writes results in a csv file

def main(argv):
    
    paper_id = None
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o",["id=", "ofile="])
    except getopt.GetoptError:
        print('abstractCrawler.py -id <paper_id> -o <output_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('abstractCrawler.py -id <paper_id> -o <output_file>')
            sys.exit()
        elif opt in ("--id", '-i'):
            paper_id = arg
        elif opt in ('--ofile', '-o'):
            outputfile = str(arg)
    
    print('Looking titles, abstracts for the paper with id:', paper_id, '\nWriting output to file:', outputfile)

    citationUrl = 'https://pubmed.ncbi.nlm.nih.gov/?size=200&linkname=pubmed_pubmed_citedin&from_uid='
    with urlopen(citationUrl + paper_id) as response:
        response_html = str(response.read())
        number_of_citations = response_html.split('<div class="results-amount">')[1]
        number_of_citations = number_of_citations.split('<span class="value">')[1]
        number_of_citations = int(number_of_citations.split('</span>')[0])
        print('This paper has been cited:', number_of_citations, 'times')

        paper_ids = response_html.split('data-chunk-ids=')[1]
        paper_ids = paper_ids.split('<div class="title first">')[0]
        paper_ids = paper_ids.split('"')[1].split('"')[0]
        paper_ids = paper_ids.split(',')
        paper_ids = [int(i) for i in paper_ids]

        if number_of_citations > 200:
            with urlopen(citationUrl+paper_id+'&page=2') as response2:
                response2_html = str(response2.read())
                paper_ids2 = response2_html.split('data-chunk-ids=')[1]
                paper_ids2 = paper_ids2.split('<div class="title first">')[0]
                paper_ids2 = paper_ids2.split('"')[1].split('"')[0]
                paper_ids2 = paper_ids2.split(',')
                paper_ids2 = [int(i) for i in paper_ids2]
                paper_ids = paper_ids + paper_ids2
        #print(paper_ids)
    dict = {}
    for pmid in tqdm(paper_ids):
        pmid = int(pmid)
        fetch = PubMedFetcher()
        article = fetch.article_by_pmid(pmid)
        abstract = article.abstract
        title = article.title
        dict[pmid] = (title, abstract)
    
    if outputfile != '':
        f = open(outputfile, 'w')
        writer = csv.writer(f)
        header = ['PAPER_ID', 'TITLE', 'ABSTRACT']
        writer.writerow(header)
        for key in dict:
            line = [str(key), str(dict[key][0]), str(dict[key][1])]
            writer.writerow(line)
            line2 = ['']
            writer.writerow(line2)


if __name__ == "__main__":
    main(sys.argv[1:])