from run import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author')
    threads = db.relationship('Thread', backref='author')
    permission_level = db.Column(db.Integer, default=0)
    post_signature = db.Column(db.Text(200))
    profile_pic = db.Column(db.String(60), default='default.jpg')

    def __repr__(self):
        return f'User (id: {self.id}, username: {self.username})'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=True, nullable=False)
    sub_categories = db.relationship('SubCategory', backref='parent')

    def __repr__(self):
        return f'Category (title: {self.title})'


class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    threads = db.relationship('Thread', backref='parent')

    def __repr__(self):
        return f'Sub-category (title: {self.title})'


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'))

    posts = db.relationship('Post', backref='thread')

    def __repr__(self):
        return f'Thread (title: {self.title}, author: {self.author})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    edit_date = db.Column(db.DateTime, default=None)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

    def __repr__(self):
        return f'Post (title: {self.title} author: {self.author})'


