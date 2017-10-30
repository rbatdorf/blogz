from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abc123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_list', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:

            session['username'] = username
            flash("Logged in")

            return redirect('/newentry')

        else:
            if not user:
                flash('Username does not exist', 'error')
            else:
                flash('Password incorrect', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TO DO - validate user's data
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Logged in")

            # TO DO - Remember user is logged in

            return redirect ('/')
        
        else:
            # TO Do - better response
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route("/newentry")
def newentry():
    return render_template('blogentry.html')

@app.route("/newentry", methods=['POST'])
def validation():

    author = User.query.filter_by(username=session['username']).first()

    title = request.form['title']
    blog = request.form['body']

    title_error = ''
    blog_error = ''

    #title
    if len(title)== 0:
        title_error = 'Blog entry must have a title'

    #blog
    if len(blog)==0:
        blog_error = 'Blog entry must contain text'

    if not title_error and not blog_error:
        
        if request.method == 'POST':
        
            blog_title = request.form['title']
            blog = request.form['body']
            new_blog_entry = Blog(blog_title, blog)
            db.session.add(new_blog_entry)
            db.session.commit()

            blog_id = str(new_blog_entry.id)

            #return redirect('/blog') - ORIGINAL
            return redirect("/blog?id=" + blog_id)

    else:
        return render_template('blogentry.html', title_error=title_error, blog_error=blog_error, title=title, blog=blog)

@app.route('/blog', methods=['POST', 'GET'])
def blog_list():
    
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('individualblog.html', blog=blog)
    
    else:

        blog_entries = Blog.query.all()
        return render_template('blog.html',title="Blogz", blog_entries=blog_entries)

@app.route('/', methods=['POST', 'GET'])
def index():

    blog_entries = Blog.query.filter_by(author=author).all()
    return render_template('index.html',title="Blogz", blog_entries=blog_entries)
#@app.route("/signup")
#def register():
#    username = request.args.get('username')
#    return render_template('signup_message.html', username=username)

if __name__ == '__main__':
    app.run()