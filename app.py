from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.pymongo import PyMongo
import bcrypt

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):

    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def load_from_mongo(self):
        users = mongo.db.users
        existing_user = users.find_one({'name': self.username})
        self.pw_hash = existing_user['password']

    def get_id(self):
        return self.username


app.secret_key = "secret key"

app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb://login:Password1@ds153765.mlab.com:53765/mongologinexample'

mongo = PyMongo(app)


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



@app.route('/')
@login_required
def index():
    return 'You are logged in as' + session['username']

    #return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    print(request)
    print(request.method)
    if request.method == 'POST':

        users = mongo.db.users
        user_data = users.find_one({ 'name': request.form['username'] })
        print(user_data)

    # f logins are the sane, checks if users input username/password matches the database else returns the error message
        if user_data:
            print('form: ', request.form)
            submitted_password = request.form.get('password')
            print(submitted_password)
            print(user_data['password'])
            if check_password_hash(user_data['password'], submitted_password):
                print(user_data['name'])
                user = User(user_data['name'])
                login_user(user)
                return redirect(url_for('index'))
        return 'Invalid username/password combination'
    elif request.method == 'GET':
        return render_template('login.html')


@login_manager.user_loader
def load_user(id):
    users = mongo.db.users
    return users.find_one({ 'name': id })


@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = generate_password_hash(request.form.get('pass'))
            users.insert({'name' : request.form['username'], 'password': hashpass})
            print(request.form['username'])
            login_user(request.form['username'])
            return redirect(url_for('index'))

        return 'That username already exists!'
    return render_template('register.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host='0.0.0.0')
