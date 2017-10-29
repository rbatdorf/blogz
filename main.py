from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        # NEED TO ADD one for Title one for Blog?? YES

@app.route("/newentry")
def index():
    return render_template('blogentry.html')

@app.route("/newentry", methods=['POST'])
def validation():

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
        return render_template('blog.html',title="Build-a-Blog!", blog_entries=blog_entries)

#@app.route("/signup")
#def register():
#    username = request.args.get('username')
#    return render_template('signup_message.html', username=username)

if __name__ == '__main__':
    app.run()