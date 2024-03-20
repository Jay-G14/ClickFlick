import json
from flask import Flask, render_template_string, send_from_directory, request, redirect, url_for, session, render_template,jsonify,send_file,Response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt 
import datetime
import pickle
import psycopg2
from werkzeug.utils import secure_filename
import re
from flask import flash
import time
from moviepy.editor import ImageSequenceClip, AudioFileClip,concatenate_audioclips
import io
import zipfile
import base64
import numpy as np
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.transitions import fadein, slide_in
from moviepy.video.compositing.concatenate import concatenate_videoclips

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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=300)  # Token expires in 30 minutes
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

db_config = {
}

music_files = [
    {"name": "sample1.mp3", "path": "/home/jayant/iss/course-project-group-51-clickflick-main/sample1.mp3"},
    {"name": "temp_music.mp3", "path": "/home/jayant/iss/course-project-group-51-clickflick-main/temp_music.mp3"}
]

# Establish database connection
def get_db_connection():
    return  psycopg2.connect(os.environ["DATABASE_URL"])

# Initialize database
def init_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Create User_Details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            )
        """)

        # Create Images table
        cursor.execute("""CREATE TABLE IF NOT EXISTS image_details (
            image_id SERIAL PRIMARY KEY NOT NULL,
            username VARCHAR(255),
            name VARCHAR(500) NOT NULL,
            size INT NOT NULL,
            extension VARCHAR(100),
            img bytea,
            include BOOLEAN DEFAULT FALSE,
            transition INT,
            duration INT
        )
        """)

        # Create Music table
        cursor.execute("""CREATE TABLE IF NOT EXISTS music_details (
            music_id SERIAL PRIMARY KEY,
            music_name VARCHAR(255) NOT NULL,
            music_data bytea NOT NULL
        )
        """)
        
        # Insert predefined music files into the database if the music_details table is empty
        cursor.execute("SELECT COUNT(*) FROM music_details")
        count = cursor.fetchone()['COUNT(*)']
        if count == 0:
            for music_file in music_files:
                with open(music_file['path'], 'rb') as f:
                    music_data = f.read()
                    cursor.execute("INSERT INTO music_details (music_name, music_data) VALUES (%s, %s)",
                                   (music_file['name'], music_data))

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
    if 'user_email' in session:
        return 'Welcome back, ' + session['user_email'] + '!'
    else:
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
            cursor.execute("INSERT INTO users ( name, email, password) VALUES ( %s, %s, %s)",
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
            print(user) 

            if check_password_hash(user[3], password):
                    #Store the user email and name in the session
                    session['user_email'] = email
                    session['user_name'] = user[1]
                    return render_template('main.html', user_name=user[1], user_email=email)
            

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

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        files = request.files.getlist('file')

        # Get username from session
        user_email = verify_jwt_token(session.get('token'))
        if not user_email:
            return 'Invalid or expired session. Please log in again.', 401

        user_data = get_user_data(user_email)
        if not user_data:
            return 'User data not found.', 404

        username = user_data['name']  # Assuming the username is stored in the 'name' field

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
                INSERT INTO image_details (username, name, size, extension, img, include, transition, duration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, file_name, file_size, file_extension, file_data, False, 1, 3))
        
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
    

@app.route('/downloadimages')
def downloadimages():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Retrieve image data from the database
        cursor.execute("SELECT img FROM image_details ORDER BY image_id")
        image_records = cursor.fetchall()

        cursor.close()
        connection.close()

        if not image_records:
            return 'No images found in the database'

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for idx, image_record in enumerate(image_records):
                image_data = io.BytesIO(image_record[5])
                zip_file.writestr(f'image_{idx}.jpg', image_data.getvalue())

        # Serve the zip file to the user
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, mimetype='application/zip', download_name='images.zip')

    except Exception as e:
        print(f'Error occurred during image retrieval: {e}')
        return 'An error occurred during image retrieval', 500


@app.route('/displayimages')
def displayimages():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Retrieve image data from the database
        cursor.execute("SELECT img FROM image_details ORDER BY image_id")
        image_records = cursor.fetchall()

        cursor.close()
        connection.close()

        if not image_records:
            return 'No images found in the database'

        # Convert image data to base64 format for embedding in HTML
        images = []
        for image_record in image_records:
            image_data = image_record[5]
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            images.append(image_base64)

        # Render the template with the images
        return render_template('display_images.html', images=images)

    except Exception as e:
        print(f'Error occurred during image retrieval: {e}')
        return 'An error occurred during image retrieval', 500
    
    

@app.route('/downloadmovie')
def downloadmovie():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        user_email = verify_jwt_token(session.get('token'))
        if not user_email:
            return 'Invalid or expired session. Please log in again.', 401

        user_data = get_user_data(user_email)
        if not user_data:
            return 'User data not found.', 404

        username = user_data[1]

        # Retrieve image data from the database
        cursor.execute("SELECT img FROM image_details WHERE username= %s name=ORDER BY image_id")
        image_records = cursor.fetchall()

        cursor.close()
        connection.close()

        if not image_records:
            return 'No images found in the database'

        # Extract image data from database records and create a sequence of frames
        frames = []
        # Determine the target size for resizing
        target_size = (640, 480)  # Example target size, adjust as needed
        for image_record in image_records:
            # Convert BytesIO object to PIL Image
            image_data = io.BytesIO(image_record[5])
            pil_image = Image.open(image_data)

            # Resize the image to the target size
            resized_image = pil_image.resize(target_size)

            # Convert resized image to RGB mode
            resized_image = resized_image.convert('RGB')

            # Convert PIL Image to NumPy array
            numpy_array = np.array(resized_image)

            # Append the frame to the list of frames
            frames.append(numpy_array)

        # Create a movie clip from the frames using MoviePy
        clip = ImageSequenceClip(frames, fps=5)

        # Save the movie to a temporary location
        output_path = 'output.mp4'
        clip.write_videofile(output_path, codec='libx264')

        # Serve the movie file to the user
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f'Error occurred during movie creation: {e}')
        return 'An error occurred during movie creation', 500


@app.route('/displaymovie/highsize', methods=['GET', 'POST'])
def displaymoviehighsize():
    if request.method == 'POST':
        try:
            selected_size = request.form.get('size')  # Get selected size from form submission

            # print("meow")
            # Connect to the database to retrieve preloaded music files
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT music_id, music_name FROM music_details")
            music_files = cursor.fetchall()
            cursor.close()

            # Connect to the database to retrieve uploaded image files
            cursor = connection.cursor()
            user_email = verify_jwt_token(session.get('token'))
            if not user_email:
                return 'Invalid or expired session. Please log in again.', 401
            

            # Get user data
            user_data = get_user_data(user_email)
            if not user_data:
                return 'User data not found.', 404

            username = user_data['name']  # Assuming the username is stored in the 'name' field

            # Retrieve image data from the database for the logged-in user
            cursor.execute("SELECT image_id, img, include FROM image_details WHERE username = %s ORDER BY image_id", (username,))
            image_files = cursor.fetchall()
            cursor.close()
            connection.close()

            # Convert image data to base64 format for embedding in HTML
            images = []
            for image_record in image_files:
                # print(image)
                image_data = image_record[5]
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                images.append({'image_id': image_record[0], 'data': image_base64, 'include': image_record[6]})

            return render_template('display_movie_highsize.html', music_files=music_files, images=images)

        except Exception as e:
            print(f'Error occurred during movie 12 display: {e}')
            return 'An error occurred during movie 12display', 500

    else:  # If request method is GET
        try:
            # Connect to the database to retrieve preloaded music files
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT music_id, music_name FROM music_details")
            music_files = cursor.fetchall()
            cursor.close()

            # Connect to the database to retrieve uploaded image files
            cursor = connection.cursor()
            user_email = verify_jwt_token(session.get('token'))
            if not user_email:
                return 'Invalid or expired session. Please log in again.', 401

            # Get user data
            user_data = get_user_data(user_email)
            if not user_data:
                return 'User data not found.', 404

            username = user_data['name']  # Assuming the username is stored in the 'name' field

            # Retrieve image data from the database for the logged-in user
            cursor.execute("SELECT image_id, img, include FROM image_details WHERE username = %s ORDER BY image_id", (username,))
            image_files = cursor.fetchall()
            cursor.close()
            connection.close()

            # Convert image data to base64 format for embedding in HTML
            images = []
            # print(image_files[0])

            for image_record in image_files:
                image_data = image_record[1]
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                images.append({'image_id': image_record[0], 'data': image_base64, 'include': image_record[2]})

            return render_template('display_movie_highsize.html', music_files=music_files, images=images)

        except Exception as e:
            print(f'Error occurred during movie 23 display: {e}')
            return 'An error occurred during movie 23 display', 500
    

@app.route('/toggle_include', methods=['POST'])
def toggle_include():
    try:
        image_id = request.form.get('image_id')
        include = request.form.get('include')
        duration = request.form.get('duration')
        transition = request.form.get('transition')

        # Convert include value to a boolean
        include = include.lower() == 'true'

        # Update include, duration, and transition fields in the database for the specified image ID
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("UPDATE image_details SET include = %s, duration = %s, transition = %s WHERE image_id = %s", (include, duration, transition, image_id))
        connection.commit()

        cursor.close()
        connection.close()

        # Debug print statements
        print(f"Toggle for image ID {image_id} was successful.")
        print(f"New include value for image ID {image_id}: {include}")
        print(f"New duration for image ID {image_id}: {duration}")
        print(f"New transition for image ID {image_id}: {transition}")

        # Return success response along with the updated values
        return jsonify({'success': True, 'include': include, 'duration': duration, 'transition': transition}), 200
    except Exception as e:
        # Debug print statement for error
        print(f"Error occurred during toggle: {e}")

        # Return error response if an exception occurs
        return jsonify({'success': False, 'error': str(e)}), 500
    



# import os
# from flask import request

from moviepy.video.fx import all as vfx

@app.route('/displaymovie', methods=['POST'])
def displaymovie():
    try:
        # Handle POST request
        # Retrieve necessary data from the form
        selected_music = request.form.get('music')
        selected_quality = request.form.get('quality')

        # Connect to the database and retrieve image records
        connection = get_db_connection()
        cursor = connection.cursor()

        user_email = verify_jwt_token(session.get('token'))
        if not user_email:
            return 'Invalid or expired session. Please log in again.', 401

        # Get user data
        user_data = get_user_data(user_email)
        if not user_data:
            return 'User data not found.', 404

        username = user_data['name']  # Assuming the username is stored in the 'name' field

        # Retrieve image data from the database including duration and transition type
        cursor.execute("SELECT img, duration, transition FROM image_details WHERE username = %s AND include = TRUE ORDER BY image_id", (username,))
        image_records = cursor.fetchall()

        if not image_records:
            return 'No images found in the database'

        # Create a temporary file to store the music data
        temp_music_file = 'temp_music.mp3'

        # Retrieve selected music data from the database
        cursor.execute("SELECT music_data FROM music_details WHERE music_id = %s", (selected_music,))
        music_record = cursor.fetchone()

        if not music_record:
            return 'Selected music not found', 404

        # Write music data to the temporary file
        with open(temp_music_file, 'wb') as f:
            f.write(music_record[0])

        # Load the temporary file as an audio clip
        music_clip = AudioFileClip(temp_music_file)
        audio_duration = music_clip.duration

        total_duration = 0
        total_transition_duration = 0
        clips = []
        # Determine the target size for resizing based on selected quality
        if selected_quality == 'low':
            target_size = (480, 360)  # Low quality resolution
        else:
            target_size = (2560, 1920)  # High quality resolution

        # Iterate through image records to create clips and apply transitions
        for image_record in image_records:
            # Convert image data to PIL Image
            image_data = io.BytesIO(image_record[0])
            pil_image = Image.open(image_data)

            # Resize the image to the target size
            resized_image = pil_image.resize(target_size)

            # Convert resized image to RGB mode
            resized_image = resized_image.convert('RGB')

            # Convert PIL Image to NumPy array
            numpy_array = np.array(resized_image)

            # Create an ImageClip from the NumPy array with specified duration
            duration = image_record[1]

            # Include transition duration in the total duration
            transition_duration = 2  # Assuming all transitions have a duration of 2 seconds
            total_duration += duration
            # total_transition_duration += transition_duration

            # Create clip from image and apply transition
            clip = ImageSequenceClip([numpy_array], durations=[duration])

            transition_type = image_record[2]
            if transition_type == 1:  # Fade
                # Apply fade-in transition with a duration of 2 seconds
                clip = clip.crossfadein(2)
            elif transition_type == 2:  # Slide from right
                # Apply slide-in transition from right with a duration of 2 seconds
                clip = clip.fx(vfx.slide_in, duration=2, side='right')
            elif transition_type == 3:  # Slide from left
                # Apply slide-in transition from left with a duration of 2 seconds
                clip = clip.fx(vfx.slide_in, duration=2, side='left')
            # Add more conditions for other transition types

            # Add the clip to the list
            clips.append(clip)


        while audio_duration < total_duration:
            music_clip = concatenate_audioclips([music_clip, music_clip])
            audio_duration *= 2  # Update music duration after concatenation

        # Trim music clip if its duration exceeds total_duration
        if audio_duration > total_duration:
            music_clip = music_clip.subclip(0, total_duration)

        # Concatenate the clips to create the final movie
        final_clip = concatenate_videoclips(clips)
        final_clip = final_clip.set_audio(music_clip)

        # Set the frames per second (fps) for the final clip
        final_clip.fps = 24  # Adjust the value as needed

        # Save the movie to a temporary location
        output_path = 'output.mp4'
        final_clip.write_videofile(output_path, codec='libx264')

        # Serve the movie file to the user
        return send_file(output_path, as_attachment=False)

    except Exception as e:
        print(f'Error occurred during 1 movie creation: {e}')
        return 'An error occurred during 1 movie creation', 500


if __name__ == "__main__":
    app.run(debug=True)


