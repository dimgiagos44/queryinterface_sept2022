from flask import render_template,jsonify,request
import json
from urllib.request import Request,urlopen
from pubmed_lookup import PubMedLookup, Publication
from metapub import PubMedFetcher



paper = '9521467'
paper2 = '12297621'
citationUrl = 'https://pubmed.ncbi.nlm.nih.gov/?size=200&linkname=pubmed_pubmed_citedin&from_uid='


with urlopen(citationUrl + paper2) as response:
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
        with urlopen(citationUrl+paper2+'&page=2') as response2:
            response2_html = str(response2.read())
            paper_ids2 = response2_html.split('data-chunk-ids=')[1]
            paper_ids2 = paper_ids2.split('<div class="title first">')[0]
            paper_ids2 = paper_ids2.split('"')[1].split('"')[0]
            paper_ids2 = paper_ids2.split(',')
            paper_ids2 = [int(i) for i in paper_ids2]
            paper_ids = paper_ids + paper_ids2
    print(paper_ids)

'''
paperUrl = 'https://pubmed.ncbi.nlm.nih.gov/' + paper2
with urlopen(paperUrl) as response:
    response_html = str(response.read())
    title = response_html.split('<title>')[1].split('</title>')[0]
    abstract = response_html.split('<div class="abstract-content selected"')[1].split('</p>')[0]
    print(title)
    print(abstract)
'''
'''
pmid = int(paper)
fetch = PubMedFetcher()
article = fetch.article_by_pmid(pmid)
abstract = article.abstract
title = article.title
'''
