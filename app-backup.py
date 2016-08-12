from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.secret_key = "secret key"

app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb://login:Password1@ds153765.mlab.com:53765/mongologinexample'

mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as' + session['username']

    return render_template('index.html')

@app.route('/login')
def login():
    return ''

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'], bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'
    return render_template('register.html')







if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host='0.0.0.0')

