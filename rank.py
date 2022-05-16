# no major modules required here
# just working with the database stored in the sqlite3
import sqlite3
import sys
import warnings
warnings.filterwarnings('ignore')

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
    if to_id not in from_ids:
        continue
        
    # adding all the rows having in-out page links at one place
    web_links.append(row)
    if to_id not in to_ids:
        to_ids.append(to_id)

# getting the latest page ranks for stringly connected components
# the above term is from graph theory
old_ranks = {}
for key in from_ids:
    cursor.execute('SELECT new_rank FROM Pages WHERE id = ?', (key,))
    row = cursor.fetchone()
    old_ranks[key] = row[0]

# asking for number of iterations to perform for the ranks
number = input('Enter the number of iterations: ')
count = 1
if len(number) > 0:
    count = int(number)

if len(old_ranks) < 1:
    sys.exit("No data to perform page ranking\nTerminating the program")

# page ranks in memory to make it faster in terms of execution
for i in range(count):
    next_ranks = {}
    overall_count = 0.0
    for key, old_rank in old_ranks.items():
        overall_count = overall_count + old_rank
        next_ranks[key] = 0.0
    print(f'Total count -> {overall_count}')

    # number of outbound links and send the page ranks down each
    for key, old_rank in old_ranks.items():
        give_ids = []
        for from_id, to_id in web_links:
            if from_id != key:
                continue
            print(f'Linking: {from_id} -> {to_id}')

            if to_id not in to_ids:
                continue
            give_ids.append(to_id)
        if len(give_ids) < 1:
            continue
        amount = old_rank / len(give_ids)
#        print(f'{key} -> {old_rank}; {amount} -> {give_ids}')

        for id in give_ids:
            next_ranks[id] = next_ranks[id] + amount

    new_count = 0
    for key, next_rank in next_ranks.items():
        new_count = new_count + next_rank
    remove = (overall_count - new_count) / len(next_ranks)

    for key in next_ranks:
        next_ranks[key] = next_ranks[key] + remove

    new_count = 0
    for (key, next_rank) in list(next_ranks.items()):
        new_count = new_count + next_rank

    # computing the per paga average change from old rank to new rank
    # to indicate the convergence of algorithm
    # finds the stability of the page
    # the more changes -> the less stable the page
    difference = 0
    for key, old_rank in old_ranks.items():
        new_rank = next_ranks[key]
        diff = abs(old_rank - new_rank)
        difference = difference + diff

    average = difference / len(old_ranks)
    print(f'The average difference in page ranks: {i + 1} -> {average}')

    # rotating -> making new ranks to old ranks
    # and running the loop again
    old_ranks = next_ranks

# updating the database with the ranks
cursor.execute('UPDATE Pages SET old_rank=new_rank')
for id, new_rank in next_ranks.items():
    cursor.execute('UPDATE Pages SET new_rank=? WHERE id=?', (new_rank, id))
connection.commit()
cursor.close()
