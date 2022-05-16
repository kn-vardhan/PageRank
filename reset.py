# resetting all the page ranks in the database
# and starting it afresh
import sqlite3
import warnings
warnings.filterwarnings('ignore')

connection = sqlite3.connect('spider-data.sqlite')
cursor = connection.cursor()

cursor.execute('UPDATE Pages SET new_rank=1.0, old_rank=0.0')
connection.commit()

cursor.close()

print("Ranks of all pages set to 1.0")
