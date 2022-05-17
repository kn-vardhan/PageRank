# PageRank
 
Implementation of the page rank algorithm

> PageRank is an algorithm used by Google Search to rank web pages in their search engine results.

Using Python modules, BeautifulSoup (a Python package to parse HTML and XML pages) and sqlite. The webpages were ranked based on the number of in-bound and out-bound links. 

Steps to work it out
- Requirements - Python version 3.8, install SQLite browser in your PC
- Open terminal or CommandPrompt
- run the spider.py file using '**python3 spider.py**'
- Enter the url you would like to parse and find the page rank associated to that url. E.g. https://iith.ac.in/
- Give input of number of pages you would like to scrape. E.g. _How many pages: 50_
- Next up, run the rank.py file with '**python3 rank.py**'
- Enter the number of iterations to perform for finding the rank. The higher the number, the more stable the rank would be. E.g. 1000
- Next up, run the dump.py file with '**python3 dump.py**'. This program returns the number of html pages retrieved; the maximum number of nodes possible in the pagerank.
- Next up, run the json.py file with '**python3 json.py**'
- Enter the number of nodes you wish to have in the graph. E.g. _How many nodes? X_
- Your pagerank graph is ready. Open the **force.html** page in your browser to view the visualization

> To reset all the ranks of webpages, run '**python3 reset.py**'.
> To find the pagerank of new webpage, delete the _spider-data.sqlite_ file and follow the above steps with a new url
