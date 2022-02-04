import json

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy import create_engine, select
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Query
import logging
from resources import *

logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///database.db', echo=True, future=True)
logger.info(f'{engine.engine} established at {engine.dialect}')

Base = declarative_base()

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


class Info(Base):
    __tablename__ = 'info'

    name = Column(String)
    url = Column(String, primary_key=True)
    nPage = Column(Integer)
    nThread = Column(Integer)
    nPost = Column(Integer)
    nMember = Column(Integer)


class Thread(Base):
    __tablename__ = 'thread'

    title = Column(String)
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    first_post_id = Column(Integer, ForeignKey('post.id'), unique=True)
    create_time = Column(DateTime)
    author = Column(String, ForeignKey('user.id'))

    # relationship
    firstPost = relationship('Post', foreign_keys=[first_post_id])
    posts = relationship('Post', backref='thread', foreign_keys='Post.thread_id')
    comments = relationship('Comment', backref='thread', foreign_keys='Comment.thread_id')
    # authors=relationship('User',backref='threads',secondary=thread_user)


class Post(Base):
    __tablename__ = 'post'

    thread_id = Column(Integer, ForeignKey('thread.id'))
    id = Column(Integer, primary_key=True)
    post_no = Column(Integer)
    author = Column(String, ForeignKey('user.id'))
    create_time = Column(DateTime)
    content = Column(Text)

    comments = relationship('Comment', backref='post', foreign_keys='Comment.post_id')

    # thread = relationship('Thread', backref='posts',foreign_keys=[thread_id])
    # authors=relationship('User',backref='posts',secondary=post_user)


class Comment(Base):
    __tablename__ = 'comment'

    thread_id = Column(Integer, ForeignKey('thread.id'))
    post_id = Column(Integer, ForeignKey('post.id'))
    id = Column(Integer, primary_key=True)
    author = Column(String, ForeignKey('user.id'))
    create_time = Column(DateTime)
    content = Column(Text)
    comment_to = Column(String, ForeignKey('user.id'))

    # authors=relationship('User',backref='comments',secondary=comment_user)


class User(Base):
    __tablename__ = 'user'

    name = Column(String)
    nickname = Column(String)
    id = Column(String, primary_key=True)

    threads = relationship('Thread', foreign_keys='Thread.author')
    posts = relationship('Post', foreign_keys='Post.author')
    comments = relationship('Comment', foreign_keys='Comment.author')

    # threads=relationship('Thread',secondary=thread_user)


Base.metadata.create_all(engine)

# global session
Session = sessionmaker(bind=engine, autocommit=False, future=True)
session = Session()
select=select

def insertOrUpdate(cls, rows: dict | list[dict], updateStrategy: str = 'null') -> int:
    """

    Args:
        cls:
        dataList:
        updateStrategy: strategy on deplicate primary key
            all: update all columns regardless any situation
            not_null: update columns not null or empty with new value and leave`
            null: update empty or null column to new value and leave not null value unchanged
            never: don't update any column

    Returns:
        influenced row number
    """

    def all(newRow, oldRow):
        return newRow

    def not_null(newRow, oldRow):
        mergeDict = {}
        newDict = newRow.__dict__
        oldDict = oldRow.__dict__
        for i in header:
            mergeDict[i] = newDict[i] if oldDict[i] and oldDict[i] != '' else None
        merge = cls(**mergeDict)
        return merge

    def null(newRow, oldRow):
        mergeDict = {}
        newDict = newRow.__dict__
        oldDict = oldRow.__dict__
        for i in header:
            mergeDict[i] = newDict[i] if not oldDict[i] or oldDict[i] == '' else oldDict[i]
        merge = cls(**mergeDict)
        return merge

    def never(newRow, oldRow):
        return oldRow

    _dataList: list[dict] = []
    if isinstance(rows, dict):
        _dataList.append(rows)
    if isinstance(rows, list):
        _dataList += rows

    updateStrategy: str = updateStrategy.lower()
    strategies = {
        'all': all,
        'not_null': not_null,
        'null': null,
        'never': never
    }
    merge = strategies.get(updateStrategy, null)

    schemaName: str = cls.__tablename__
    header: list = sql_schema[schemaName][0].keys()
    cnt = 0

    for d in _dataList:
        newRow = cls(**d)
        stmt = select(cls).where(cls.id == d['id'])
        """
        method          no result               one result      many results
        one()           NoResultFound error     (obj,)          MultipleResultsFound error
        one_or_none()   None                    (obj,)          MultipleResultsFound error
        scalar()        None                    obj             obj
        first()         None                    (obj,)          (obj,)
        all()           []                      [(obj,)]        [(obj,)]
        """
        existingRow = session.execute(stmt).scalar()
        if existingRow:
            # if updateStrategy == ''
            newRow = merge(newRow, existingRow)
            session.delete(existingRow)
            # existing row not counted in
            cnt -= 1
        session.add(newRow)
        session.commit()
        cnt += 1
    return cnt
