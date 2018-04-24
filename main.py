from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog1@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def valid_entry(string):
    if string == '':
        return False
    else:
        return True


@app.route('/')
def index():
    return redirect('/blog')



@app.route('/blog', methods=['POST', 'GET'])

def blog_listing():

    blog_id=request.args.get('id')

    #if method = 'GET' ??
    #changed filter by to get line 43
    if blog_id:
        blog_entry = Blog.query.get(blog_id)
        return render_template("post.html", blog_entry=blog_entry)
    
    else:
        blog_entries = Blog.query.all()
        return render_template("blog.html", blog_entries=blog_entries)


@app.route('/newpost', methods=['POST', 'GET'])

def post_entry():

    title = ''
    body = ''

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

            blog_entry = Blog(title, body)
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