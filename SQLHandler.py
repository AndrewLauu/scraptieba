from sqlalchemy import Table,Column,String,DateTime,ForeignKey,create_engine,select
from sqlalchemy.orm import relationship,declarative_base,sessionmaker,Query
import logging

logger=logging.getLogger("main")

engine=create_engine('sqlite://',echo=True,future=True)

Base=declarative_base()

"""
thread_user=Table(
    't2u',Base.metadata,
    Column('thread_id',String,ForeignKey('thread.id'),primary_key=True),
    Column('user_id',String,ForeignKey('user.id'),primary_key=True)
        )
post_user=Table(
    'p2u',Base.metadata,
    Column('post_id',String,ForeignKey('post.id'),primary_key=True),
    Column('user_id',String,ForeignKey('user.id'),primary_key=True)
        )
comment_user=Table(
    'c2u',Base.metadata,
    Column('comment_id',String,ForeignKey('comment.id'),primary_key=True),
    Column('user_id',String,ForeignKey('user.id'),primary_key=True)
        )
"""
class Thread(Base):
    __tablename__='thread'

    title=Column(String)
    id=Column(String,primary_key=True)
    url=Column(String,unique=Ttue)
    first_post_id=Column(String,ForeignKey('post.id'))
    create_time=Column(DatetTime)
    author=Column(String,ForeignKey('user.id'))

    #relationship
    posts=relationship('Post',backref='thread')
    comments=relationship('Comment',backref='thread')
    #authors=relationship('User',backref='threads',secondary=thread_user)

class Post(Base):

    __tablename__='post'
    
    thread_id=Column(String,ForeignKey('thread.id'))
    id=Column(String,primary_key=True)
    post_no=Column(Integer)
    author=Column(String,ForeignKey('user.id'))
    create_time=Column(DatetTime)
    content=Column(LongText)

    comments=relationship('Comment',backref='post')
    #authors=relationship('User',backref='posts',secondary=post_user)
    

class Comment(Base):
    __tablename__='comment'

    thread_id=Column(String,ForeignKey('thread.id'))
    post_id=Column(String,ForeignKey('post.id'))
    id=Column(String,primary_key=True)
    author=Column(String,ForeignKey('user.id'))
    create_time=Column(DatetTime)
    content=Column(LongText)

    #authors=relationship('User',backref='comments',secondary=comment_user)

class User(Base):
    __tablename__='user'
    
    name=Column(String)
    nickname=Column(String)
    id=Column(String,primary_key=True)

    threads=relationship('Thread')
    posts=relationship('Post')
    comments=relationship('Comment')

    #threads=relationship('Thread',secondary=thread_user)

Base.metadata.create_all(engine)

session=sessionmaker(bind=engine,autocommit=False,future=True)()

Query.only_return_tuples=True

#test suit
"""
user1=User(id=1,name=1)
user2=User(id=2,name=2)

session.add_all([user1,user2])

thread1=Thread(id=1,author=1,content='user 1 thread 1')
thread2=Thread(id=2,author=2,content='user 2 thread 2')
thread3=Thread(id=3,author=2,content='user 2 thread 3')

session.add_all([thread1,thread2,thread3])

post1=Post(id=1,thread_id=1,author=1,content='user 1 thread 1 post 1')
post2=Post(id=2,thread_id=1,author=1,content='user 1 thread 1 post 2')

session.add_all([post1,post2])

comment1=Comment(id=1,thread_id=1,post_id=1,author=1,content='user 1 thread 1 post 1 comment 1')
comment2=Comment(id=2,thread_id=1,post_id=1,author=1,content='user 1 thread 1 post 1 comment 2')
session.add_all([comment1,comment2])

stmt=select(User).where(User.id==1)
a=session.execute(stmt)
print(stmt)
print(a)
"""
