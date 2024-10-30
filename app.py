import datetime
import os
from flask import (
    Flask, 
    render_template, 
    request,
    session,
    abort,
    flash,
    redirect,
    url_for,
)
    
import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key") 

# Insert a new blog entry into the database
def insert_entry(title, content, email):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to insert data
            sql_insert_query = """
            INSERT INTO entries (title, content, email, date)
            VALUES (%s, %s, %s, NOW())
            """
            entry_data = (title, content, email)

            # Execute the query
            cursor.execute(sql_insert_query, entry_data)
            connection.commit()
            print("Entry inserted successfully.")

    except Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        # Close the cursor and connection if they exist
        if 'cursor' in locals():
            cursor.close()        
        if connection.is_connected():            
            connection.close()
            print("MySQL connection is closed")    
       
# Fetch all blog entries from the database
def fetch_entries():
    entries = []
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Define the query to retrieve data
            query = "SELECT title, content, email, date, id FROM entries ORDER BY date DESC"
            cursor.execute(query)
            
            # Fetch all rows from the result
            entries = cursor.fetchall()

    except Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        if 'cursor' in locals():
            cursor.close()        
        if connection.is_connected():            
            connection.close()
            print("MySQL connection is closed")    
    return entries

# Insert a new user into the users table
def insert_user(email, password):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to insert data
            sql_insert_query = """
            INSERT INTO users (email, password)
            VALUES (%s, %s)
            """
            user_data = (email, password)

            # Execute the query
            cursor.execute(sql_insert_query, user_data)
            connection.commit()
            print("User inserted successfully.")

    except Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        # Close the cursor and connection if they exist
        if 'cursor' in locals():
            cursor.close()        
        if connection.is_connected():            
            connection.close()
            print("MySQL connection is closed")

# Check if an email is already registered
def is_email_registered(email):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Query to check if the email exists in the users table
            query = "SELECT COUNT(*) FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            
            # Fetch the result
            result = cursor.fetchone()
            return result[0] > 0  # True if email exists, False otherwise

    except Error as e:
        print("Error while connecting to MySQL:", e)
        return False  # Assume email doesn't exist if there's an error

    finally:
        # Close the cursor and connection if they exist
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()
            
# Validate user login credential
def validate_user(email, password):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Query to check if the email and password match
            query = "SELECT password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            
            # Fetch the stored password if the email exists
            result = cursor.fetchone()
            return result and result[0] == password

    except Error as e:
        print("Error while connecting to MySQL:", e)
        return False  # Assume login fails if there's an error

    finally:
        # Close the cursor and connection if they exist
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

# Display a detailed post
def get_post_by_id(post_id):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),  # Use environment variable for host
            user=os.environ.get("MYSQL_USER", "codebind"),  # Use environment variable for user
            password=os.environ.get("MYSQL_PASSWORD"),  # Use environment variable for password
            database=os.environ.get("MYSQL_DATABASE", "ficticiousblogs")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Define the query to fetch the post by ID
            query = "SELECT title, content, email, date FROM entries WHERE id = %s"
            cursor.execute(query, (post_id,))
            
            # Fetch the result
            post = cursor.fetchone()
            return post

    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

    finally:
        # Close the cursor and connection if they exist
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()

# Sign-up route
@app.route("/signup", methods=["GET", "POST"])
def signup():
  if request.method == "POST":
    email = request.form.get("email")
    password = request.form.get("password")    
    
    if is_email_registered(email):
        flash("Email is already registered. Please log in.", "warning")
        return redirect(url_for("login"))
        
    # Proceed with registration if email is not registered
    
    # Insert user into MySQL
    insert_user(email, password)
    flash("Registration successful. Please log in.", "success")
    return redirect(url_for("login"))

  return render_template("signup.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if validate_user(email,password):
            session["email"] = email
            flash("Login successfull", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))
        
    return render_template("login.html")

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
  if "email" not in session:
      return redirect(url_for("signup"))
  
  user_email = session["email"]
  
  if request.method == "POST":
      
    title = request.form.get("title")
    content = request.form.get("content")
    
    # Insert entry into MySQL
    insert_entry(title, content, user_email)
    
  # Add entry to in-memory list
  entries = fetch_entries()
        
  return render_template("index.html", entries=entries, user_email=user_email)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("email", None)
    flash("You have been logged out", "info")
    return redirect(url_for("login"))

@app.route("/post/<int:post_id>")
def post(post_id):
    # Fetch the detailed post using the post ID    
    post = get_post_by_id(post_id)
    
    if post:
        # Render the post details in a template
        return render_template("post_detail.html", title=post[0], content=post[1], email=post[2], date=post[3])
    else:
        flash("Post not found.", "warning")
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

