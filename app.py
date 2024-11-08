import openai
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
    
# import mysql.connector
from mysql.connector import Error
import pymssql
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    

    server = os.environ.get("SERVER")
    database = os.environ.get("DATABASE")
    username = os.environ.get("USER")
    password = os.environ.get("PASSWORD")
    port = os.environ.get("PORT", "1433")
    

    # Insert a new blog entry into the database
    def insert_entry(title, content, email):
        try:            
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database
            )

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

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)

        finally:
            # Close the cursor and connection if they exist
            if 'cursor' in locals():
                cursor.close()        
            if connection:            
                connection.close()
                print("SQL server connection is closed")    
        
    # Fetch all blog entries from the database
    def fetch_entries():
        entries = []
        try:
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database
            )

            cursor = connection.cursor()

            # Define the query to retrieve data
            query = "SELECT title, content, email, date, id FROM entries ORDER BY date DESC"
            cursor.execute(query)
            
            # Fetch all rows from the result
            entries = cursor.fetchall()

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)

        finally:
            if 'cursor' in locals():
                cursor.close()        
            if connection:            
                connection.close()
                print("SQL server connection is closed")    
        return entries

    # Insert a new user into the users table
    def insert_user(email, password):
        try:                        
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database
            )

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

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)

        finally:
            # Close the cursor and connection if they exist
            if 'cursor' in locals():
                cursor.close()        
            if connection:            
                connection.close()
                print("SQL server connection is closed")

    # Check if an email is already registered
    def is_email_registered(email):
        try:                        
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database)
            
            cursor = connection.cursor()
                
            # Query to check if the email exists in the users table
            query = "SELECT COUNT(*) FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            
            # Fetch the result
            result = cursor.fetchone()
            return result[0] > 0  # True if email exists, False otherwise

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)
            return False  # Assume email doesn't exist if there's an error

        finally:
            # Close the cursor and connection if they exist
            if 'cursor' in locals():
                cursor.close()
            if connection:
                connection.close()
                print("SQL server connection is closed")
                
    # Validate user login credential
    def validate_user(email, password):
        connection = None  # Initialize connection as None
        try:                        
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database)
            
            cursor = connection.cursor()
                
            # Query to check if the email and password match
            query = "SELECT password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            
            # Fetch the stored password if the email exists
            result = cursor.fetchone()
            return result and result[0] == password

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)
            return False  # Assume login fails if there's an error

        finally:
            # Close the cursor and connection if they exist
            if 'cursor' in locals():
                cursor.close()
            if connection is not None:
                connection.close()
                print("SQL server connection is closed")

    # Display a detailed post
    def get_post_by_id(post_id):
        try:                        
            connection = pymssql.connect(
                server=f"{server},{port}", 
                user=username, 
                password=password, 
                database=database)

            cursor = connection.cursor()

            # Define the query to fetch the post by ID
            query = "SELECT title, content, email, date FROM entries WHERE id = %s"
            cursor.execute(query, (post_id,))
            
            # Fetch the result
            post = cursor.fetchone()
            return post

        except pymssql.Error as e:
            print("Error while connecting to SQL server:", e)
            return None

        finally:
            # Close the cursor and connection if they exist
            if 'cursor' in locals():
                cursor.close()
            if connection:
                connection.close()
                print("SQL server connection is closed")
                
    def generate_content_with_openai(title):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a technical blog writer."},
                    {"role": "user", "content": f"Write a 200 word blog post based on the title: '{title}'"}
                ],
                max_tokens=800  # Adjust max tokens as needed
            )
            content = response.choices[0].message['content']
            return content
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Error generating content. Please try again."

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
        title = ""
        content = ""
        
        if request.method == "POST":    
            # Check if the generate content button was pressed       
            if request.form.get("generate_content") == "true":
                    title = request.form.get("title")
                    content = generate_content_with_openai(title)
                    entries = fetch_entries()
                    return render_template("index.html", entries=entries, user_email=user_email, content=content, title=title)        
            else:
                # Otherwise, treat it as a submission
                title = request.form.get("title")
                content = request.form.get("content")
                # Insert entry into MySQL
                insert_entry(title, content, user_email)
                flash("BLog entry submitted successfully", "success")
                
        # Fetch all entries for display
        entries = fetch_entries()
        return render_template("index.html", entries=entries, user_email=user_email)        
    
    # Logout route
    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("email", None)
        flash("You have been logged out", "info")
        return redirect(url_for("login"))

    # Posts route
    @app.route("/post/<int:post_id>")
    def post(post_id):
        if "email" not in session:
            return redirect(url_for("signup"))
    
        user_email = session["email"]
        
        # Fetch the detailed post using the post ID    
        post = get_post_by_id(post_id)
        
        if post:
            # Render the post details in a template
            return render_template("post_detail.html", title=post[0], content=post[1], email=post[2], date=post[3], user_email=user_email)
        else:
            flash("Post not found.", "warning")
            return redirect(url_for("home"))

    if __name__ == "__main__":    
        app.run(debug=True)

    return app