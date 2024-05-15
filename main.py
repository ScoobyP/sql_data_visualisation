import mysql.connector

try:
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='AlphaLamdaPPsHMcGregorMG42',
        port='3306',
        database = 'cricket'
    )
    my_cursor = mydb.cursor()
    print('Connection Established')
except:
    print('Connection Error')

# creating database on the db server
#my_cursor.execute('''
#CREATE DATABASE cricket
#''')
#mydb.commit()

# creating table inside the database
# my_cursor.execute('''
 #CREATE TABLE exp (
# id INTEGER PRIMARY KEY,
# code VARCHAR(10),
# city VARCHAR(10)
#
# ''')
mydb.commit()
