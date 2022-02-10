import logging

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy import create_engine, select
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from resources import *

logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///database.db', echo=True, future=True, poolclass=NullPool)

for h in logging.getLogger('sqlalchemy.engine.Engine').handlers:logging.getLogger('sqlalchemy.engine.Engine').removeHandler(h)

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


def _str(obj):
    __header: list = sql_schema[obj.__tablename__][0].keys()
    __dict: dict = obj.__dict__
    __newDict: dict = {h: __dict.get(h, None) for h in __header}
    __str = ', '.join([f'{k} = {v}' for k, v in __newDict.items()])
    return __str


class Forum(Base):
    __tablename__ = 'forum'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    nPage = Column(Integer)
    nThread = Column(Integer)
    nPost = Column(Integer)
    nMember = Column(Integer)
    slogan = Column(String)

    # relationships
    threads = relationship('Thread', foreign_keys='Thread.forum_id', backref='forum')
    posts = relationship('Post', foreign_keys='Post.forum_id', backref='forum')
    comments = relationship('Comment', foreign_keys='Comment.forum_id', backref='forum')

    def __str__(self):
        return _str(self)

    def __repr__(self):
        return _str(self)


class Thread(Base):
    __tablename__ = 'thread'

    forum_id = Column(String, ForeignKey('forum.id'))
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
    def __str__(self):
        return _str(self)

    def __repr__(self):
        return _str(self)


class Post(Base):
    __tablename__ = 'post'

    forum_id = Column(String, ForeignKey('forum.id'))
    thread_id = Column(Integer, ForeignKey('thread.id'))
    id = Column(Integer, primary_key=True)
    post_no = Column(Integer)
    post_index = Column(Integer)
    author = Column(String, ForeignKey('user.id'))
    create_time = Column(DateTime)
    content = Column(Text)
    origin = Column(String)

    comments = relationship('Comment', backref='post', foreign_keys='Comment.post_id')

    # thread = relationship('Thread', backref='posts',foreign_keys=[thread_id])
    # authors=relationship('User',backref='posts',secondary=post_user)
    def __str__(self):
        return _str(self)

    def __repr__(self):
        return _str(self)


class Comment(Base):
    __tablename__ = 'comment'

    forum_id = Column(String, ForeignKey('forum.id'))
    thread_id = Column(Integer, ForeignKey('thread.id'))
    post_id = Column(Integer, ForeignKey('post.id'))
    id = Column(Integer, primary_key=True)
    author = Column(String, ForeignKey('user.id'))
    create_time = Column(DateTime)
    content = Column(Text)
    comment_to = Column(String, ForeignKey('user.id'))

    # authors=relationship('User',backref='comments',secondary=comment_user)
    def __str__(self):
        return _str(self)

    def __repr__(self):
        return _str(self)


class User(Base):
    __tablename__ = 'user'

    name = Column(String)
    nickname = Column(String)
    id = Column(String, primary_key=True)

    threads = relationship('Thread', foreign_keys='Thread.author')
    posts = relationship('Post', foreign_keys='Post.author')
    comments = relationship('Comment', foreign_keys='Comment.author')

    # threads=relationship('Thread',secondary=thread_user)
    def __str__(self):
        return _str(self)

    def __repr__(self):
        return _str(self)


Base.metadata.create_all(engine)

# global session
Session = sessionmaker(bind=engine, autocommit=False, future=True)
session = Session()
select = select


def insertOrUpdate(cls, rows: dict | list[dict], updateStrategy: str = 'null') -> int:
    """
    ORM wrapped insert method with deplicate update
    Args:
        cls:
        dataList:
        updateStrategy: strategy on deplicate primary key
            all: update all columns regardless any situation
            not_null: update columns not null or empty with new value and leave null unchanged
            null: update empty or null column to new value and leave not null value unchanged
            never: don't update any column

    Returns:
        influenced row number
    """

    def all(newRow, oldRow):
        return newRow

    def not_null(newRow, oldRow):
        mergeDict: dict = {}
        newDict = newRow.__dict__
        oldDict = oldRow.__dict__
        for i in header:
            mergeDict[i] = newDict[i] if oldDict[i] else None
        merge = cls(**mergeDict)
        return merge

    def null(newRow, oldRow):
        newDict = newRow.__dict__
        oldDict = oldRow.__dict__
        mergeDict: dict = {h: oldDict[h] or newDict[h] for h in header}
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
        engine.echo = False
        stmt = select(cls).where(cls.id == d['id'])
        """
        method          no result               one result      many results
        one()           NoResultFound error     (obj,)          MultipleResultsFound error
        one_or_none()   None                    (obj,)          MultipleResultsFound error
        scalar()        None                    obj             obj
        first()         None                    (obj,)          (obj,)
        all()           []                      [(obj,)]        [(obj,)]
        """
        existingRow: object = session.execute(stmt).scalar()
        engine.echo = True
        if existingRow:
            # if updateStrategy == ''
            newRow = merge(newRow=newRow, oldRow=existingRow)
            logger.debug(f'({updateStrategy})Found deplicate {existingRow=} -> {newRow}')
            session.delete(existingRow)

        session.add(newRow)
        session.commit()
        cnt += 1
    return cnt
