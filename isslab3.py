import json
from flask import Flask, render_template_string, send_from_directory, request, redirect, url_for, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'qeervrvpnmakswplrj562mcrorl104k5n'  # Replace with a strong secret key
app.config['SESSION_COOKIE_PERMANENT'] = True  # Enable persistent cookies
import os

if not os.path.exists('users.txt'):
    with open('users.txt', 'w'):
        pass

@app.route('/main')
def main():
    return render_template('main.html')

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
@app.route('/register', methods=['GET', 'POST']) #home page redirects to register which accepts get and post requests, hashes password and also checks for duplicate email
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
        with open('users.txt', 'r') as infile:
            users = infile.readlines()
            for user_json in users:
                existing_user_data = json.loads(user_json)
                if existing_user_data['email'] == email:
                    return 'Email already registered.'

        with open('users.txt', 'a') as outfile:
            json.dump(user_data, outfile)
            outfile.write('\n')
        return 'Registration successful.'

    register_form_html = """
    
         <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Form Animation CSS | Codehal</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>

<body>

    <div class="login-light"></div>
    <div class="login-box">
        <form action="/login" method="post">
            <input type="checkbox" class="input-check" id="input-check">
            <label for="input-check" class="toggle">
                <span class="text off">off</span>
                <span class="text on">on</span>
            </label>
            <div class="light"></div>

            <h2>Register</h2>
            <div class="input-box">
                <span class="icon">
                    <ion-icon name="lock-closed"></ion-icon>
                </span>
                <input type="text" name="name" required>
                <label>Name</label>
                <div class="input-line"></div>
            </div>
            <div class="input-box">
                <span class="icon">
                    <ion-icon name="mail"></ion-icon>
                </span>
                <input type="text" name="email" required>
                <label>Email</label>
                <div class="input-line"></div>
            </div>
            <div class="input-box">
                <span class="icon">
                    <ion-icon name="lock-closed"></ion-icon>
                </span>
                <input type="password" name="password" required>
                <label>Password</label>
                <div class="input-line"></div>
            </div>
            
            <div class="remember-forgot">
                <label><input type="checkbox"> Remember me</label>
                <a href="#">Forgot Password?</a>
            </div>
            <input type="submit" value="Register">
            
        </form>
    </div>


    <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
</body>

</html>


    """
    return render_template_string(register_form_html)

@app.route('/login', methods=['GET', 'POST']) #login page accepts get and post requests, compares hash of password
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'admin' and password == 'admin':
            return redirect(url_for('admin'))
        if email=="user" and password=="1234":
            return redirect(url_for('hardcode'))
        with open('users.txt', 'r') as infile:
            users = infile.readlines()
            for user_json in users:
                user_data = json.loads(user_json)
                if user_data['email'] == email:
                    if check_password_hash(user_data['password'], password):
                        #session['user_email'] = email
                        return redirect(url_for('main'))
                    else:
                        return 'Password is incorrect.'
            return 'User not found.'

    login_form_html = """
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Form Animation CSS | Codehal</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>

<body>

    <div class="login-light"></div>
    <div class="login-box">
        <form action="/login" method="post">
            <input type="checkbox" class="input-check" id="input-check">
            <label for="input-check" class="toggle">
                <span class="text off">off</span>
                <span class="text on">on</span>
            </label>
            <div class="light"></div>

            <h2>Login</h2>
            <div class="input-box">
                <span class="icon">
                    <ion-icon name="mail"></ion-icon>
                </span>
                <input type="text" name="email" required>
                <label>Email</label>
                <div class="input-line"></div>
            </div>
            <div class="input-box">
                <span class="icon">
                    <ion-icon name="lock-closed"></ion-icon>
                </span>
                <input type="password" name="password" required>
                <label>Password</label>
                <div class="input-line"></div>
            </div>
            <div class="remember-forgot">
                <label><input type="checkbox"> Remember me</label>
                <a href="#">Forgot Password?</a>
            </div>
            <input type="submit" value="Login">
            <div class="register-link">
                <p>Don't have an account? <a href="/register">Register</a>.</p></center>
            </div>
        </form>
    </div>


    <script type="module" src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule src="https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js"></script>
</body>

</html>

    """
    return render_template_string(login_form_html)

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

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/admin')
def admin():
    with open('users.txt', 'r') as file:
        data = file.read()
    return data


