# no major modules required here
# just working with the database stored in the sqlite3
import sqlite3
import sys

connection = sqlite3.connect('spider-data.sqlite')
cursor = connection.cursor()

# choosing those ids that send out page ranks
# in pages in the SSC that have in-out links
# and ids that receive page ranks
from_ids = []
to_ids = []
web_links = []

cursor.execute('SELECT DISTINCT from_id FROM Links')
for row in cursor:
    from_ids.append(row[0])

cursor.execute('SELECT DISTINCT from_id, to_id FROM Links')
for row in cursor:
    from_id = row[0]
    to_id = row[1]

    if from_id == to_id:
        continue
    if from_id not in from_ids:
        continue
    if to_id not in to_ids:
        continue

    # adding all the rows having in-out page links at one place
    web_links.append(row)

    if to_id not in to_ids:
        to_ids.append(to_id)

# getting the latest page ranks for strongly connected component
# the above term is from graph theory
old_ranks = {}
for key in from_ids:
    cursor.execute('SELECT new_rank FROM Pages WHERE id=?', (key,))
    row_data = cursor.fetchone()
    old_ranks[key] = row_data[0]

# asking for number of iterations to perform for the ranks
number = input("Enter the number of iterations: ")
count = 1
if len(number) > 0:
    count = int(number)

if len(old_ranks) < 1:
    sys.exit("No data to perform page ranking\nTerminating the program")

# page ranks in memory to make it faster in terms of execution
for i in range(count):
    print(old_ranks.items[:5])
    new_ranks = {}
    overall_count = 0.0

    for key, old_rank in old_ranks.items():
        overall_count += old_rank
        new_ranks[key] = 0.0
    print(f'Total count -> {overall_count}')

    # number of outbound links and send the page ranks down each
    for key, old_rank in old_ranks.items():
        give_ids = []
        for (from_id, to_id) in web_links:
            if from_id != key:
                continue
            print(f'Linking: {from_id} -> {to_id}')

            if to_id not in to_ids:
                continue

            give_ids.append(to_id)


