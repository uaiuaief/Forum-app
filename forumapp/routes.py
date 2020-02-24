from datetime import datetime
from flask import url_for, render_template, redirect, abort, flash, session, request
from flask_login import login_user, current_user, logout_user, login_required
from forumapp import app, db, login_manager
from forumapp.utils import delete_recursively, sanitize_html, render_quote
from .models.forms import LoginForm, RegistrationForm, ThreadForm, CategoryForm, SubCategoryForm, ThreadReplyForm
from .models.models import User, Post, Thread, Category, SubCategory
from sqlalchemy import desc


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/home')
def home():
    ct = Category.query.all()
    return render_template('home.html', categories=ct)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username.ilike(form.username.data)).first()
        password_is_correct = form.password.data == user.password
        if password_is_correct:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Password Incorrect')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/<string:category_title>/<int:sub_category_id>/threads')
def threads(category_title, sub_category_id):
    ct = Category.query.filter_by(title=category_title).first()
    sub = SubCategory.query.filter_by(id=sub_category_id).first()
    category_threads = Thread.query.filter_by(parent_id=sub_category_id)\
        .join(Post, Thread.id == Post.thread_id).order_by(desc(Post.pub_date))

    variables = {
        'threads': category_threads,
        'sub_category_id': sub_category_id,
        'category_title': ct.title,
        'sub_category': sub,
        'len': len
    }

    return render_template('sub_categories.html', **variables)

    # return render_template('sub_categories.html',
    #                        threads=category_threads, sub_category_id=sub_category_id,
    #                        category_title=ct.title, sub_category=sub, len=len)


@app.route('/<string:category_title>/<int:sub_category_id>/new', methods=['GET', 'POST'])
def new_thread(category_title, sub_category_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ThreadForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        author_id = current_user.id
        td = Thread(title=title, author_id=author_id, parent_id=sub_category_id)
        db.session.add(td)
        db.session.commit()

        post = Post(title=title, body=body, author_id=author_id, thread_id=td.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('threads', category_title=category_title, sub_category_id=sub_category_id))
    return render_template('new_thread.html', category_title=category_title, form=form)


@app.route('/home/new_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.permission_level < app.config['MANAGE_CATEGORY_PERMISSION_LEVEL']:
        abort(302)

    form = CategoryForm()
    if form.validate_on_submit():
        title = form.title.data
        ct = Category(title=title)
        db.session.add(ct)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('new_category.html', form=form)


@app.route('/home/<int:category_id>/new_sub_category', methods=['GET', 'POST'])
@login_required
def add_sub_category(category_id):
    if current_user.permission_level < app.config['MANAGE_SUB_CATEGORY_PERMISSION_LEVEL']:
        abort(302)

    form = SubCategoryForm()
    if form.validate_on_submit():
        title = form.title.data
        desc = form.description.data

        sub = SubCategory(title=title, desc=desc, parent_id=category_id)
        db.session.add(sub)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('new_sub_category.html', form=form)


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>/new_post', methods=['GET', 'POST'])
def new_post(category_title, sub_category_id, thread_id):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = ThreadReplyForm()
    if session.get('quote', False):
        form.body.process_data(session['quote'])
        session['quote'] = None
    if form.validate_on_submit():
        text = form.body.data
        author_id = current_user.id
        post = Post(title='Post reply', body=text, author_id=author_id, thread_id=thread_id)
        db.session.add(post)
        db.session.commit()

        variables = {
            'category_title': category_title,
            'sub_category_id': sub_category_id,
            'thread_id': thread_id
        }

        return redirect(url_for('thread', **variables))

        # return redirect(url_for('thread', category_title=category_title, sub_category_id=sub_category_id,
        #                         thread_id=thread_id))

    return render_template('new_post.html', thread_id=thread_id, form=form)


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>/quote/<int:post_id>')
def quote(category_title, sub_category_id, thread_id, post_id):
    quote_text = Post.query.filter_by(id=post_id).first().body
    session['quote'] = quote_text
    # session['quote'] = render_quote(quote_text)

    variables = {
        'category_title': category_title,
        'sub_category_id': sub_category_id,
        'thread_id': thread_id
    }

    return redirect(url_for('new_post', **variables))

    # return redirect(url_for('new_post', category_title=category_title, sub_category_id=sub_category_id,
    #                         thread_id=thread_id))


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(category_title, sub_category_id, thread_id, post_id):
    form = ThreadReplyForm()
    post = Post.query.filter_by(id=post_id).first()

    authorized_users = [post.author.username, 'admin']
    if current_user.username not in authorized_users:
        abort(302)

    if request.method == 'GET':
        form.body.process_data(post.body)
    if form.validate_on_submit():
        post.body = form.body.data
        post.edit_date = datetime.utcnow()
        db.session.commit()

        variables = {
            'category_title': category_title,
            'sub_category_id': sub_category_id,
            'thread_id': thread_id
        }

        return redirect(url_for('thread', **variables))

    return render_template('new_post.html', form=form)


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>')
def thread(category_title, sub_category_id, thread_id):
    td = Thread.query.filter_by(id=thread_id).first()
    posts = td.posts
    quote_form = ThreadReplyForm()

    variables = {
        'category_title': category_title,
        'sub_category_id': sub_category_id,
        'thread': td,
        'posts': posts,
        'sanitize_html': sanitize_html,
        'form': quote_form,
    }

    return render_template('thread.html', **variables)

    # return render_template('thread.html', category_title=category_title, sub_category_id=sub_category_id,
    #                        thread=td, posts=posts, sanitize_html=sanitize_html)


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>/delete/<int:post_id>')
def delete_post(category_title, sub_category_id, thread_id, post_id):
    post = Post.query.filter_by(id=post_id).first()
    td = post.thread

    authorized_users = [post.author.username, 'admin']
    if current_user.username not in authorized_users:
        abort(302)

    variables = {
        'category_title': category_title,
        'sub_category_id': sub_category_id
    }

    if post == td.posts[0]:
        delete_recursively(td)
        return redirect(url_for('threads', **variables))
    else:
        variables['thread_id'] = thread_id
        delete_recursively(post)
        return redirect(url_for('thread', **variables))


@app.route('/<string:category_title>/<int:sub_category_id>/threads/<int:thread_id>/remove')
@login_required
def delete_thread(category_title, sub_category_id, thread_id):
    td = Thread.query.filter_by(id=thread_id).first()

    thread_author = td.author.username
    authorized_users = [thread_author, 'admin']
    if current_user.username not in authorized_users:
        abort(302)

    delete_recursively(td)

    return redirect(url_for('threads', category_title=category_title, sub_category_id=sub_category_id))


@app.route('/home/<string:category_title>/remove')
@login_required
def delete_category(category_title):
    if current_user.permission_level < app.config['MANAGE_CATEGORY_PERMISSION_LEVEL']:
        abort(302)

    ct = Category.query.filter_by(title=category_title).first()

    delete_recursively(ct)

    return redirect(url_for('home'))


@app.route('/home/<int:category_id>/<int:sub_category_id>/remove')
@login_required
def delete_sub_category(sub_category_id, category_id):
    if current_user.permission_level < app.config['MANAGE_SUB_CATEGORY_PERMISSION_LEVEL']:
        abort(302)

    sub = SubCategory.query.filter_by(id=sub_category_id).first()

    delete_recursively(sub)

    return redirect(url_for('home'))


@app.route('/<string:username>/posts')
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(author=user).all()

    return render_template('user_posts.html', posts=posts)


@app.route('/profile/<string:username>')
def user_page(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(author=user).all()

    return render_template('profile_page.html', posts=posts)


# Javascript routes
@app.route('/ajax/quote')
def ajax_quote():
    post_id = request.args['post']
    body = Post.query.filter_by(id=post_id).first().body
    body = f'<quote>{body}</quote>\n'
    return body


@app.route('/ajax/reply', methods=['GET', 'POST'])
def ajax_reply():
    form = ThreadReplyForm()
    return form.body


@app.route('/ajax/login', methods=['POST'])
def ajax_login():
    username = request.form['user']
    password = request.form['password']
    user = User.query.filter(User.username.ilike(username)).first()
    if user:
        password_is_correct = password == user.password
        if password_is_correct:
            login_user(user)
            return redirect(url_for('home'))
    else:
        flash('Password Incorrect')
        return redirect((url_for('login')))





