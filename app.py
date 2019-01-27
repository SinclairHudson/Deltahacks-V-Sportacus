from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, session
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:%q3a$%q3a$@localhost/Sportacus'
app.config['SECRET_KEY'] = '123456789'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'
#app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'

app.debug = True
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    points = db.Column(db.String(255), unique=False)
    email = db.Column(db.String(255), unique=True)
    contact = db.Column(db.String(255), unique=False)
    bio = db.Column(db.String(255), unique=False)
    interests = db.Column(db.String(255), unique=False)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def score(str1, str2):
    lst1 = str(str1).split(", ")
    lst2 = str(str2).split(", ")
    count = 0
    for i in lst1:
        for j in lst2:
            if i==j:
                count+=1
    return {count: str2}



@app.route('/')
def index():
    try:
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        return render_template('welcome.html', user=user)
    except:
        return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile/<email>')
@login_required
def profile(email):
    user = User.query.filter_by(email=email).first()
    return render_template('viewprofile.html', user=user)

@app.route('/editprofile/<email>')
@login_required
def editprofile(email):
    user = User.query.filter_by(email=email).first()
    return render_template('editprofile.html', user=user)

@app.route('/potentialmatches/<email>')
@login_required
def potentialmatches(email):
    #with app.app_context():
        user = User.query.filter_by(email=email).first()

        currentuser2 = User.query.filter_by(id=1).first()
        currenthigh = 0
        allUser = User.query.filter(User.id != user.id).all()
        allScore = [score(user.interests, row.interests) for row in allUser]
        print(allScore)
        scores = []
        scores.extend(list(row.keys()) for row in allScore)
        print(scores)
        answer = max(scores)[0]
        print(answer)
        #matchString = [row[answer] for row in allScore if answer in row]
        matchedString = None
        matchedUser = None
        for row in allScore:
            if answer in row:
                matchedString = row[answer]

        if matchedString is not None:
            matchedUser = User.query.filter_by(interests=matchedString).first()
            return render_template('potentialmatches.html', user=matchedUser)

        else:

            return " user not found    "

        # for x in range(3):
        #     user2 = User.query.filter_by(id=x+1).first()
        #     print(user2)
        #     if score(user.interests, user2.interests) > currenthigh:
        #         if user != user2:
        #             currenthigh = score(user.interests, user2.interests)
        #             currentuser2 = user2
        #         else:
        #             continue
        #     else:
        #         continue




@app.route('/post_user', methods=['POST'])
def post_user():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    user.username = request.form['username']
    user.email = request.form['email']
    user.contact = request.form['contact']
    user.bio = request.form['bio']
    user.interests = request.form['interests']
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()