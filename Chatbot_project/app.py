from datetime import datetime
from flask import Flask, render_template, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, Email
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from main import chat
import src

from src.config import CHATBOT_NAME
app = Flask(__name__)
# User authentication database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db_user = SQLAlchemy(app)


# Chatbot information database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_chatbot = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db_user.Model, UserMixin):
    id = db_user.Column(db_user.Integer, primary_key=True)
    username = db_user.Column(db_user.String(20), nullable=False, unique=True)
    email = db_user.Column(db_user.String(120), nullable=False)  # Added email column
    password = db_user.Column(db_user.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = EmailField(validators=[
        InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# Define the Chatbot model (Table structure in the database)
class Chatbot(db_chatbot.Model):
    id = db_chatbot.Column(db_chatbot.Integer, primary_key=True)
    bot_name = db_chatbot.Column(db_chatbot.String(100), nullable=False)
    bot_description = db_chatbot.Column(db_chatbot.String(255), nullable=False)
    created_at = db_chatbot.Column(db_chatbot.DateTime, default=datetime.utcnow, nullable=False)
   

    def __repr__(self):
        return f'<Chatbot {self.bot_name}>'

@app.route('/')
def home():
    return render_template('home.html')



@app.route('/submit', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        # Extract form data
        bot_name = request.form['chatbot_name']
        bot_description = request.form['chatbot_description']
        uploaded_files = request.files.getlist('files[]')
        chatbot_dir = Path('data') / bot_name
        chatbot_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist

        for file in uploaded_files:
            if file:
                file_path = chatbot_dir / file.filename
                file.save(file_path)

        with open("src/config.py", "r") as file:
            lines = file.readlines()
        # Modify the chatbot_name assignment
        with open("src/config.py", "w") as file:
            for line in lines:
                if "CHATBOT_NAME" in line:
                     file.write(f"CHATBOT_NAME = '{bot_name}'\n") 
                else:
                    file.write(line)

      


        # Create a new Chatbot object
        new_chatbot = Chatbot(bot_name=bot_name, bot_description=bot_description)

        # Add the new chatbot to the database
        db_chatbot.session.add(new_chatbot)
        db_chatbot.session.commit()

        # Redirect to a new page after submission
        return render_template('bot.html', CHATBOT_NAME=src.config.CHATBOT_NAME)

# Route for thank-you page
@app.route('/bot')
def bot():
    return render_template('bot.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    chatbots = Chatbot.query.all()  # Retrieve all chatbots from the database
    return render_template('dashboard.html', chatbots=chatbots)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db_user.session.add(new_user)
        db_user.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/menu')
def create_bot_form():
    return render_template('menu.html')

@app.post("/predict")
def predict():
    try:
        # Extract incoming JSON data
        data = request.get_json()
        personality = data.get("personality","Friendly") 
        # Check for contents
        contents = data.get("contents", [])
    
        if not contents:
            return jsonify({"answer": "No contents provided"}), 400
        # Initialize variable for text data
        text = ""
        
        # Extract parts (only text data, no image-related processing)
        parts = contents[0].get("parts", [])
        for part in parts:
            if "text" in part:
                text = part["text"]  # Extract the text part

        # If no text is provided, return an error response
        if not text.strip():
            return jsonify({"answer": "No valid text found"}), 400

        # Generate a response using the provided text
        print("Text for response generation:", text)
        response = chat(Path('data') / src.config.CHATBOT_NAME,text,personality)  # Assuming get_response processes the text input
        # Get the response text
        answer = response.response

        # Return a structured JSON response
        result = {"answer": answer}

        return jsonify(result)

    except Exception as e:
        print("Error during prediction:", e)
        return jsonify({"answer": "An error occurred while processing your request"}), 500



if __name__ == "__main__":
    app.run(debug=True)
