import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

server = os.environ.get("SERVER")
database = os.environ.get("DATABASE")
username = os.environ.get("USER")
password = os.environ.get("PASSWORD")

try:
  # Connect to Azure SQL Database
  connection = pymssql.connect(server=server, user=username, password=password, database=database)
  
  title = "Test1"
  content = "Test1"
  email = "Test1"
  
  cursor = connection.cursor()

  # SQL query to insert data
  sql_insert_query = """
  INSERT INTO entries (title, content, email, date)
  VALUES (%s, %s, %s, GETDATE())
  """
  entry_data = (title, content, email)

  # Execute the query
  cursor.execute(sql_insert_query, entry_data)
  connection.commit()
  print("Entry inserted successfully.")
  
  # Create a cursor to execute SQL queries
#   cursor = connection.cursor()
  
#   cursor.execute("SELECT * FROM users")
#   rows = cursor.fetchall()
  
#   for row in rows:
#     print(row)
    
except pymssql.Error as e:
  print("Error", e)

# finally:
#   if connection:
#     connection.close()



finally:
    # Close the cursor and connection if they exist
    if 'cursor' in locals():
        cursor.close()        
    if connection:            
        connection.close()
        print("MySQL connection is closed")