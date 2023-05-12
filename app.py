from flask import Flask, render_template, redirect, request, url_for, session
from sqlalchemy import text
from database import signup_to_db, login_from_db, all_blogs_from_db, blog_from_db, add_to_db, category_from_db, userid_for_add_blog, all_blogs, update_to_db, my_blogs_from_db, blogs_based_on_cat, engine, user_has_liked_blog, update_likes_db, like_count

app = Flask(__name__)
app.secret_key = 'my_secret_key'


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route("/")
def home():
  blogs = all_blogs_from_db()
  category = category_from_db()
  return render_template('index.html', blogs=blogs, category=category)


@app.route("/signup")
def signup():
  return render_template('signup.html')


@app.route("/signup/apply", methods=['post'])
def signup_done():
  data = request.form
  val= signup_to_db(data)
  if not val:
    alert = "Email or username is already in use !!!"
    return render_template('signup.html', alert=alert)
  else:
    return render_template('signup_apply.html')


@app.route('/help')
def help():
  return render_template('contactus.html')


@app.route("/login")
def login():
  return render_template('login.html')



@app.errorhandler(404)
def error_404(e):
  return render_template('404.html')
@app.errorhandler(500)
def error_500(e):
  return render_template('500.html')



@app.route("/check_for_login", methods=['post'])
def check_for_login():
  data = request.form
  is_user = login_from_db(data)

  if not is_user:
    return render_template('index.html')

  session['is_user'] = is_user
  return redirect(url_for('login_success'))


@app.route("/dashboard")
def login_success():
  if 'is_user' not in session:
    return redirect('/login')
    
  blogs = all_blogs_from_db()
  is_user = session.get('is_user')

  return render_template('dashboard.html',
                         userid=is_user['userid'],
                         uid=is_user['id'],
                         blogs=blogs)



@app.route("/<int:blog_id>/blog/<int:uid>")
def single_blog(blog_id, uid):
  # Get the blog from the database.
  blog = blog_from_db(blog_id)
  user_has_liked= user_has_liked_blog(blog_id, uid)
  count= like_count(blog_id)
  # Check if the blog exists.
  if not blog:
    return 404
  # Render the blog template.
  return render_template('single-blog.html', blog=blog, uid=uid, user_has_liked=user_has_liked, count=count)



@app.route("/<uid>/<id>/blog")
def myBlog_logged_in(uid, id):
  blog = blog_from_db(id)
  count= like_count(id)
  return render_template('myBlog_logged_in.html', blog=blog, uid=uid, count=count)



@app.route("/<uid>/myBlogs")
def myBlogs(uid):
  if 'is_user' not in session:
    return render_template('login.html')
    
  res = userid_for_add_blog(uid)
  userid=res['userid']
  blogs = my_blogs_from_db(userid)  
  return render_template('myBlogs.html', blogs=blogs, userid= userid, uid=uid)



@app.route('/<uid>/add')
def new(uid):
  if 'is_user' not in session:
    return redirect('/login')
    
  res = userid_for_add_blog(uid)
  category = category_from_db()
  return render_template('addBlog.html', userid=res['userid'], category=category, uid=uid)



@app.route('/user/add', methods=['post'])
def create_blog():
  data = request.form
  add_to_db(data)
  uid= data['uid']
  return redirect(url_for("myBlogs", uid=uid))



@app.route("/allBlogs/<int:nav>/<int:uid>")
def allBlogs(nav, uid):
  blogs = all_blogs()
  userid = None
  if uid !=0:
    if 'is_user' not in session:
      return redirect('/login')
    res = userid_for_add_blog(uid)
    userid=res['userid']
  return render_template('allBlogs.html', blogs=blogs, nav=nav, userid= userid, uid=uid)



@app.route("/categories/<int:nav>/<int:uid>")
def categories(nav, uid):
  category = category_from_db()
  userid = None
  if uid !=0:
    if 'is_user' not in session:
      return redirect('/login')
    res = userid_for_add_blog(uid)
    userid=res['userid']
  return render_template('categories.html', category= category, nav= nav, userid= userid, uid=uid)



@app.route("/categories/<int:nav>/<int:uid>/<string:cat>")
def category_blog(nav, uid, cat):
  blogs = blogs_based_on_cat(cat)
  userid = None
  if uid !=0:
    if 'is_user' not in session:
      return redirect('/login')
    res = userid_for_add_blog(uid)
    userid=res['userid']
  return render_template('blogs_based_on_cat.html', blogs= blogs, nav= nav, userid= userid, cat= cat, uid=uid)



@app.route("/delete/<int:blog_id>/<int:uid>", methods=['POST'])
def delete_blog(blog_id, uid):
    with engine.connect() as conn:
        query = text("DELETE FROM blogs WHERE id=:blog_id")
        conn.execute(query, {'blog_id': blog_id})
    return redirect(url_for("myBlogs", uid=uid))



@app.route("/edit/<int:blog_id>/<int:uid>", methods=['POST'])
def edit_blog(blog_id, uid):
  if 'is_user' not in session:
    return redirect('/login')
  post = blog_from_db(blog_id)
  return render_template('editblog.html', post=post, uid=uid)



@app.route('/update', methods=['post'])
def update_blog():
    blog_id = request.args.get('blog_id')
    uid = request.args.get('uid')
    data = request.form
    update_to_db(data, blog_id)
    return redirect(url_for("myBlogs", uid=uid))



@app.route("/<int:blog_id>/like/<int:uid>", methods=['POST'])
def like_blog(blog_id, uid):
  # Check if the user has already liked this blog.
  update_likes_db(blog_id, uid)
  # Redirect the user back to the single-blog page.
  return redirect(url_for('single_blog', blog_id=blog_id, uid=uid))



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



@app.route('/logo')
def logo():
    if 'is_user' in session:
        return redirect('/dashboard')
    else:
        return redirect('/')



if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)