from sqlalchemy import create_engine,text


db_conn_string="mysql+pymysql://2vsfnf1qpq6udop702u1:pscale_pw_WheMMTABITKws64FffWowKKgGndvk7tNu8MMHYAB5Jp@aws.connect.psdb.cloud/bloggo"

engine=create_engine(db_conn_string,
                      connect_args={
                        "ssl": {
                          "ssl_ca": "/etc/ssl/cert.pem"
                        }
                      })
    

def signup_to_db(data):
  with engine.connect() as conn:

    result = conn.execute(
          text("select * from users where userid=:id or email=:email"),
            {"id": data['userid'],
             "email": data['email']}
    )
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
      
    if len(rows) != 0:
      return 0;
      
    else:
      query = text("INSERT INTO users (fullname, email, userid, password) VALUES (:fullname, :email, :userid, :password)")
  
      conn.execute(query, { 
                   'fullname': data['fullname'],
                   'email':data['email'],
                   'userid':data['userid'],
                   'password':data['pwd']                 
      })
      return 1;


def login_from_db(data):
  with engine.connect() as conn:
    result = conn.execute(
          text("select * from users where userid=:id and password=:pwd"),
            {"id": data['username'],
             "pwd": data['pwd']}
    )
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
      
    if len(rows) == 0:
      return None
    else:
      return (rows[0])


def all_blogs_from_db():
  with engine.connect() as conn:
    query = text("SELECT * FROM blogs ORDER BY last_update DESC LIMIT 5")
    result=conn.execute(query)
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return rows


def blog_from_db(id):
  with engine.connect() as conn:
    query = text("SELECT * FROM blogs where id=:id")
    result= conn.execute(query, { 
                 'id':id                           
    })
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return (rows[0])



def my_blogs_from_db(userid):
  with engine.connect() as conn:
    query = text("SELECT * FROM blogs where userid=:userid ORDER BY last_update desc" )
    result= conn.execute(query, { 
                 'userid':userid                           
    })
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return (rows)



def blogs_based_on_cat(cat):
  with engine.connect() as conn:
    query = text("SELECT * FROM blogs where category=:cat ORDER BY last_update desc" )
    result= conn.execute(query, { 
                 'cat':cat                           
    })
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return (rows)



def add_to_db(data):
  with engine.connect() as conn:
    query=text("INSERT  INTO blogs(userid,title,category,blog) VALUES (:userid,:title,:category,:blog)")
    if data['category']:
        category = data['category'].title()
    else:
        # Check if the value of the input element is not empty
        if data['new_category']:
            category = data['new_category'].title()
        else:
            # Set a default value for the category field
            category = 'Uncategorized'
    conn.execute(query, { 
                 'userid': data['userid'],
                 'title':data['title'].title(),
                 'category':category,
                 'blog':data['blog']                 
    })

def category_from_db():
  with engine.connect() as conn:
    query = text("SELECT category, MAX(last_update) as last_update FROM blogs GROUP BY category ORDER BY last_update DESC")
    result=conn.execute(query)
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return rows


def userid_for_add_blog(uid):
  with engine.connect() as conn:
    query = text("SELECT * FROM users where id=:id")
    result= conn.execute(query, { 
                 'id':uid                           
    })
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return (rows[0])



def all_blogs():
  with engine.connect() as conn:
    query = text("SELECT * FROM blogs ORDER BY last_update DESC")
    result=conn.execute(query)
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    return rows

def update_to_db(data,blog_id):
  with engine.connect() as conn:
    query = text("UPDATE blogs SET title=:title, category=:category, blog=:blog WHERE id=:id")
    conn.execute(query, { 
              'id': blog_id,
              'title': data['title'].title(),
              'category': data['category'].title(),
              'blog': data['blog'],

          })



def user_has_liked_blog(blog_id, user_id):
  with engine.connect() as conn:
    query = text("SELECT * FROM likes WHERE blog_id =:blog_id AND user_id =:user_id")
    result= conn.execute(query, { 
                 'blog_id':blog_id,
                 'user_id':user_id
    })
    rows = []
    rows=[dict(zip(result.keys(), row)) for row in result]
    if rows:
      return True
    else:
      return False



def update_likes_db(blog_id, user_id):
  with engine.connect() as conn:
    if user_has_liked_blog(blog_id, user_id):
    # User has already liked this blog, so remove the like.
      query = text("DELETE FROM likes WHERE user_id = :user_id AND blog_id = :blog_id")
      conn.execute(query, { 
                   'blog_id':blog_id,
                   'user_id':user_id
      })      
          
    else:
    # User has not yet liked this blog, so add the like.
      query = text("INSERT INTO likes(user_id, blog_id) VALUES (:user_id, :blog_id)")
      conn.execute(query, { 
                   'blog_id':blog_id,
                   'user_id':user_id
      })



def like_count(blog_id):
  with engine.connect() as conn:
    query = text("SELECT COUNT(*) FROM likes WHERE blog_id =:blog_id")
    result= conn.execute(query, { 
                 'blog_id':blog_id,
            })
    count = result.fetchone()[0]
    return count