import sqlite3
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
import warnings
warnings.filterwarnings('ignore')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# if database doesn't exist, it creates one
connection = sqlite3.connect('spider-data.sqlite')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER, old_rank REAL, new_rank REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER, UNIQUE(from_id, to_id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

cursor.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
row_data = cursor.fetchone()

if row_data is not None:
    print("Restarting the current crawl.  Delete spider-date.sqlite to start the crawl afresh.")
else:
    start_url = input("Enter web url or enter: ")
    # using the default website - My Portfolio
    if len(start_url) < 1:
        start_url = 'https://kn-vardhan/github.io/Portfolio/'
    if start_url.endswith('/'):
        start_url = start_url[:-1]
        
    web = start_url
    
    if start_url.endswith('.htm') or start_url.endswith('.html'):
        position = start_url.rfind('/')
        web = start_url[:position]

    if len(web) > 1:
        cursor.execute('INSERT OR IGNORE INTO Webs (url) VALUES ( ? )', (web,))
        cursor.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (start_url,))
        connection.commit()

# now fetching the current websites
cursor.execute('''SELECT url FROM Webs''')
websites = list()
for row in cursor:
    websites.append(str(row[0]))

print(websites)

counts = 0
while True:
    if counts < 1:
        number = input('How many pages: ')
        if len(number) < 1:
            break
        counts = int(number)
    counts = counts - 1

    cursor.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
    try:
        row_data = cursor.fetchone()
        # print row_data
        from_id = row_data[0]
        url = row_data[1]
    except:
        print('No new html pages to be retrieved.')
        counts = 0
        break

    # printing the form id and the url we are working with
    print(f'current url: {from_id} -> {url}')

    # while retrieving a page, there shouldn't be any links from it...
    cursor.execute('DELETE from Links WHERE from_id=?', (from_id,))
    try:
        # instead of decoding, we use BeautifulSoup-compensates for the UTF-8
        document = urlopen(url, context=ctx)
        html = document.read()
        
        if document.getcode() != 200:
            print(f'Page Error at {document.getcode()}')
            cursor.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url))

        if 'text/html' != document.info().get_content_type():
            print("Ignore non text/html page")
            cursor.execute('DELETE FROM Pages WHERE url=?', (url,))
            connection.commit()
            continue

        print('(' + str(len(html)) + ')')

        # finally, parsing the html webpage
        soup = BeautifulSoup(html, "html.parser")
        
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except:
        # if we get an error=-1, then we won;t retrieve that page again
        # due to various blow ups or faults while retrieving/parsing
        print("Unknown Error: Unable to retrieve the webpage")
        cursor.execute('UPDATE Pages SET error=-1 WHERE url=?', (url,))
        connection.commit()
        continue

    cursor.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (url,))
    cursor.execute('UPDATE Pages SET html=? WHERE url=?', (memoryview(html), url))
    connection.commit()

    # Retrieve all the anchor tags
    tags = soup('a')
    new_count = 0
    for tag in tags:
        href = tag.get('href', None)
        if href is None:
            continue
        # Resolve relative references like href="/contact"
        up_parse = urlparse(href)
        if len(up_parse.scheme) < 1:
            href = urljoin(url, href)
        i_position = href.find('#')
        if i_position > 1:
            href = href[:i_position]
        if href.endswith('.png') or href.endswith('.jpg') or href.endswith('jpeg') or href.endswith('.gif'):
            continue
        if href.endswith('/'):
            href = href[:-1]
        print(href)
        if len(href) < 1:
            continue

        # checking if the url is in any of the already visited webpages
        visited = False
        for web in websites:
            if href.startswith(web):
                visited = True
                break
        if not visited:
            continue

        cursor.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (href,))
        new_count = new_count + 1
        connection.commit()

        cursor.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', (href,))
        try:
            row_data = cursor.fetchone()
            to_id = row_data[0]
        except:
            print('Unable to retrieve the id')
            continue

        print(f'{from_id} -> {to_id}')
        cursor.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', (from_id, to_id))

    print(new_count)

cursor.close()
