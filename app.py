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

@app.route('/questions', methods=['GET', 'POST'])
def questions1():
    # Establish database connection
    que = mongo.db.questions
    if request.method == 'GET':
        question_id = '1'
        question_record = que.find_one({'id': question_id})
        return render_template("quiz.html",
                               question_text=question_record['Q'],
                               question_number=question_id)
    else:
        question_id = request.form.get('qnum', '')
        submitted_answer = request.form.get('answer', '')
        question_record = que.find_one({'id': question_id})
        actual_answer = str(question_record['answer']).strip()

        if actual_answer != submitted_answer:
            flash('Wrong answer... Come on dude this is simple')
            return render_template("quiz.html",
                                   question_text=question_record['Q'],
                                   question_number=question_id)
        else:
            next_record_id = str(int(question_id) + 1)
            next_question_record = que.find_one({'id': next_record_id})
            return render_template("quiz.html",
                                   question_text=next_question_record['Q'],
                                   question_number=next_record_id)
    return redirect(url_for('success.html'))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host='0.0.0.0')
