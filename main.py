from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'z337kGnys&zP3BB3py'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

def valid_entry(string):
    if string == '':
        return False
    else:
        return True

def valid_password_conf(password, password_conf):
    if password == password_conf:
        return True
    else:
        return False

def valid_char_count(string):
    if len(string) >= 3:
        return True
    else:
        return False

def blogs_by_author(current_user_id):
    return Blog.query.filter_by( owner_id=current_user_id).all()


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_listing', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():

    usernames=User.query.all()
    user = User.query.filter_by(email=email).first()

    if user:
        return redirect("/blog")
    #check to see if user id exists and if it does you filter and if it doesnt do current return
    else:
        return render_template('index.html', 
                                usernames=usernames)
        



@app.route('/login', methods=['POST', 'GET'])

def login():
    
    incorrect_password_error = ''
    no_user_found_error = ''
    
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user.password != password:
            incorrect_password_error = 'incorrect password'

        if not user:
            no_user_found_error = 'this username does not exist'

        else:
            session['email'] = email
            return redirect('/newpost')

    return render_template('login.html',
                            incorrect_password_error=incorrect_password_error,
                            no_user_found_error=no_user_found_error)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    username_error = ''
    password_error = ''
    verify_password_error = ''
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()
     

        if not valid_entry(email):
            username_error = 'invalid field'
            email = ''
            
        if not valid_entry(password): 
            password_error = 'invalid field'
            
        if not valid_entry(verify):
            verify_password_error = 'invalid field'

        if email == existing_user:
            username_error = 'this username already exists'
            email = ''

        if valid_entry(password) and not valid_password_conf(password, verify):
            verify_password_error = 'passwords do not match'

        if not valid_char_count(email):
            username_error = 'invalid username'
            email = ''

        if valid_entry(password) and not valid_char_count(password):
            password_error = 'invalid password'

        if not username_error and not password_error and not verify_password_error:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/login')

        else: 
            return render_template('signup.html',
                            email=email,
                            username_error=username_error,
                            password_error=password_error,
                            verify_password_error=verify_password_error)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')



@app.route('/blog', methods=['POST', 'GET'])
    
def blog_listing():

    blog_id=request.args.get('id')
    user_id=request.args.get('userid')
    owner = User.query.filter_by(email=session['email']).first()
    print (user_id)
    if blog_id:
        blog_entry = Blog.query.get(blog_id)
        return render_template("post.html", blog_entry=blog_entry)

    if user_id:
        user_posts = User.query.filter_by(owner_id=user_id) 
        print (user_id)
        return render_template("singleUser.html",
                                user_posts = user_posts )
    
    else:
        blog_entries = Blog.query.all()
        return render_template("blog.html", blog_entries=blog_entries)

    

    # get request for dynamic user page
    # #if owner_id:
    #     == 'POST':
    #    title = request.form['entry-title']
    #    body = request.form['entry-body']
    #    blog_entry = Blog(title, body)

    #blog_entries = Blog.query.filter_by(owner=owner).all()
    #return render_template('blog.html', 
    #                        title=title,
    #                        body=body,
    #                        )


@app.route('/newpost', methods=['POST', 'GET'])

def post_entry():

    title = ''
    body = ''
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        title = request.form['entry-title']
        body = request.form['entry-body']

        title_error = ''
        body_error = ''
        
        if not valid_entry(title):
            title_error = 'not a valid title'
            title=''

        if not valid_entry(body):
            body_error = 'not a valid entry'
            body=''        

        if not title_error and not body_error:

            blog_entry = Blog(title, body, owner)
            db.session.add(blog_entry)
            db.session.commit()

            return redirect('/blog?id=' + str(blog_entry.id))
            #return redirect('/post?id='+ str(blog_entry.id))

        else:

            return render_template("newpost.html", 
                                    title=title,
                                    body=body,
                                    title_error=title_error,
                                    body_error=body_error)

    else:
        return render_template("newpost.html")



      

if __name__ == '__main__':
    app.run()