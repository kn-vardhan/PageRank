import sqlite3
import warnings
warnings.filterwarnings('ignore')

connection = sqlite3.connect('spider-data.sqlite')
cursor = connection.cursor()

print("Creating JSON output on spider.js...")
node_count = int(input("How many nodes? "))

cursor.execute('''SELECT COUNT(from_id) AS inbound, old_rank, new_rank, id, url 
        FROM Pages JOIN Links ON Pages.id = Links.to_id
        WHERE html IS NOT NULL AND ERROR IS NULL
        GROUP BY id ORDER BY id,inbound''')

fhand = open('spider.js', 'w')
nodes = []
max_rank = None
min_rank = None
for row in cursor:
    nodes.append(row)
    rank = row[2]
    if max_rank is None or max_rank < rank:
        max_rank = rank
    if min_rank is None or min_rank > rank:
        min_rank = rank
    if len(nodes) > node_count:
        break

if max_rank == min_rank or max_rank is None or min_rank is None:
    print("Error - please run rank.py to compute page rank")
    quit()

fhand.write('spiderJson = {"nodes":[\n')
count = 0
mapping = {}
ranks = {}
for row in nodes:
    if count > 0:
        fhand.write(',\n')
    # print row
    rank = row[2]
    rank = 19 * ((rank - min_rank) / (max_rank - min_rank))
    fhand.write('{'+'"weight":'+str(row[0])+',"rank":'+str(rank)+',')
    fhand.write(' "id":'+str(row[3])+', "url":"'+row[4]+'"}')
    mapping[row[3]] = count
    ranks[row[3]] = rank
    count = count + 1
fhand.write('],\n')

cursor.execute('''SELECT DISTINCT from_id, to_id FROM Links''')
fhand.write('"links":[\n')

count = 0
for row in cursor:
    # print row
    if row[0] not in mapping or row[1] not in mapping:
        continue
    if count > 0:
        fhand.write(',\n')
    rank = ranks[row[0]]
    srank = 19 * ((rank - min_rank) / (max_rank - min_rank))
    fhand.write('{"source":' + str(mapping[row[0]]) + ',"target":' + str(mapping[row[1]]) + ',"value":3}')
    count = count + 1
fhand.write(']};')
fhand.close()
cursor.close()

print("PageRank successfully executed. open force.html in a browser for viewing the visualization")
