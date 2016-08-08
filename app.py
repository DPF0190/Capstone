from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from wtforms import Form, TextField, validators, PasswordField
from passlib.hash import sha256_crypt
from flask.ext.pymongo import PyMongo

app = Flask(__name__)

app.secret_key = "secret key"

app.config['MONGO_DBNAME'] = 'myquiz'
app.config['MONGO_URI'] = 'mongodb://quiz:Yankees7@ds145315.mlab.com:45315/myqyuiz'

mongo = PyMongo(app)

# from pymongo import MongoClient
# client = MongoClient()
# quiz = client.mydb.quiz



#from dbconnection import connection

# create the application object

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap



# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    # return "Hello, World!"  # return a string
    return render_template('index.html')


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Repeat Password')



@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

    except Exception as e:
        return(str(e))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were just logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    # question = quiz.find_one({'Q1': 1})
    # return render_template('questions.html', question=question)
    addition = mongo.db.addition
    q1 = addition.find_one({"Q1": "what is 1+2?"})
    return q1

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out')
    return redirect(url_for('welcome'))


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

