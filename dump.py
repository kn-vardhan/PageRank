import sqlite3
import warnings
warnings.filterwarnings('ignore')

connection = sqlite3.connect('spider-data.sqlite')
cursor = connection.cursor()

cursor.execute('''SELECT COUNT(from_id) AS inbound, old_rank, new_rank, id, url
    FROM Pages JOIN Links ON Pages.id = Links.to_id
    WHERE html IS NOT NULL
    GROUP BY id ORDER BY inbound DESC''')

# it prints the number of inbound links to a webpage
count = 0
for row in cursor:
    if count < 50:
        print(row)
        count += 1

print(f'Total of {count} rows')
cursor.close()
