import json
from flask import Flask, render_template_string, send_from_directory, request, redirect, url_for, session, render_template,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt 
import datetime
import pickle
import pymysql
from werkzeug.utils import secure_filename
import re
from flask import flash
import time

app = Flask(__name__)

app.config['SECRET_KEY'] = 'qeervrvpnmakswplrj562mcrorl104k5n'  # Replace with a strong secret key
app.config['SESSION_COOKIE_PERMANENT'] = True  # Enable persistent cookies

import os

if not os.path.exists('users.txt'):
    with open('users.txt', 'w'):
        pass

def generate_jwt_token(email):
    payload = {
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')  # Use encode function from jwt module
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])  # Use decode function from jwt module
        return payload['email']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
def get_user_data(user_email):
    with open('users.txt', 'r') as infile:
        users = infile.readlines()
        for user_json in users:
            user_data = json.loads(user_json)
            if user_data['email'] == user_email:
                return user_data
    return None
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database configuration
db_config = {
    "host": "localhost",    
    "user": "newuser",
    "password": "issPr()ject1",
    "db": "clickflick",
}



# Establish database connection
def get_db_connection():
    return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config)

# Initialize database
def init_db(): # Redirect to the login failure page
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Create User_Details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            )
        """)

        # Create Images table
        cursor.execute("""CREATE TABLE IF NOT EXISTS image_details (
            image_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
            username VARCHAR(255) ,
            name VARCHAR(500) NOT NULL,
            size INT NOT NULL,
            extension VARCHAR(100),
            img LONGBLOB
        );
        """)

        connection.commit()

        cursor.close()
        connection.close()
        
        print("Database and tables initialization successful.")

    except Exception as e:
        print(f"An error occurred during database initialization: {e}")

# Initialize database when the app starts
init_db()
    

@app.route('/main')
def main():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_email = verify_jwt_token(token)
    if not user_email:
        return redirect(url_for('login'))

    user_data = get_user_data(user_email)
    if user_data:
        user_name = user_data['name']
        user_email = user_data['email']
        return render_template('main.html', user_name=user_name, user_email=user_email)
    else:
        return 'User data not found.'


@app.route('/hardcode')
def hardcode():
    return render_template('hardcore.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/t2mp4')
def t2mp4():
    video_path = 't2.mp4'
    directory = 'templates' 
    return send_from_directory(directory, video_path)
    
@app.route('/')  #home page route
def home():
    # if 'user_email' in session:
    #     return 'Welcome back, ' + session['user_email'] + '!'
    # else:
    return redirect(url_for('login'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password
        }
        if not is_valid_email(email):
            flash('Invalid email format. Please enter a valid email address.', 'error')
            
            
            return render_template('register.html')

            
        try:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Open a connection to the database
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert user data into the database
            cursor.execute("INSERT INTO users ( username, email, password) VALUES ( %s, %s, %s)",
                           (name, email, hashed_password))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            with open('users.txt', 'r') as infile:
                users = infile.readlines()
                for user_json in users:
                    existing_user_data = json.loads(user_json)
                    if existing_user_data['email'] == email:
                        return 'Email already registered.'
                    

            with open('users.txt', 'a') as outfile:
                json.dump(user_data, outfile)
                outfile.write('\n')

            # Generate JWT token upon successful registration
            token = generate_jwt_token(email)
            session['token'] = token

            
            return 'registration success'
        

        except FileNotFoundError:
            return 'Error: users.txt not found.'
        except Exception as e:
            return f"An error occurred: {e}", 500



    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email=='admin' and password=='admin':
            return redirect(url_for('admin'))
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(user['password'], password):
                    #Store the user email and name in the session
                    session['user_email'] = email
                    session['user_name'] = user['username']
                    return redirect(url_for('main')) # Redirect to the main page after successful login
            

            return 'Invalid credentials. Please try again.'

        except Exception as e:
            return f"An error occurred: {e}", 500
       
            
    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/user/<user_email>', methods=['GET']) #goes to login page and checks for user email
def get_user(user_email):
    with open('users.txt', 'r') as infile:
        users = infile.readlines()
        for user_json in users:
            user_data = json.loads(user_json)
            if user_data['email'] == user_email:
                return f"User details: {user_data}"
        return 'User not found.'
    
@app.route('/logout')
def logout():
    session.pop('user_email', None)  # Clear the session
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        files = request.files.getlist('file')

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Handle each uploaded file
        for file in files:
            if file.filename == '':
                return 'No selected file', 400

            # Read file contents
            file_data = file.read()

            # Extract file properties
            file_name = file.filename
            file_size = len(file_data)
            file_extension = os.path.splitext(file_name)[1]

            # Insert file data into the database as BLOB
            cursor.execute("""
                INSERT INTO image_details (username, name, size, extension, img)
                VALUES (%s, %s, %s, %s, %s)
            """, ('username_placeholder', file_name, file_size, file_extension, file_data))
        
        # Commit changes to the database and close connection
        connection.commit()
        cursor.close()
        connection.close()

        return 'Files uploaded and saved successfully', 200
    except Exception as e:
        print(f'Error occurred during file upload and database insertion: {e}')
        return 'An error occurred during file upload and database insertion', 500



@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/admin')
def admin():
    users_data = []
    with open('users.txt', 'r') as file:
        for line in file:
            user = json.loads(line)
            users_data.append({'name': user['name'], 'email': user['email']})
    return render_template('admin.html', users=users_data)

def is_valid_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):
        return True
    else:
        return False
