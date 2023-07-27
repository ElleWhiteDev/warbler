import os
import re

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from functools import wraps

from forms import UserAddForm, LoginForm, MessageForm, EditUserForm, ChangePasswordForm
from models import db, connect_db, User, Message, Follows

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

app.app_context().push()
connect_db(app)


def require_login(func):
    """Check user is logged in"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if CURR_USER_KEY not in session:
            flash('You must be logged in to view this page!', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    print(form.errors)

    if form.validate_on_submit():
        try:
            profile_img_file = request.files.get('profile_img')
            profile_img_url = request.form.get('profile_img_url')
            profile_img = User.profile_img.default.arg

            if profile_img_file and profile_img_file.filename != '':
                profile_img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_img_file.filename))
                profile_img = url_for('static', filename='uploads/' + profile_img_file.filename)
            elif profile_img_url:
                if not re.search(r'(.jpg|.png|.svg)$', profile_img_url):
                    flash("Invalid URL! Please provide a URL that ends with .jpg, .png, or .svg", 'danger')
                    return render_template('users/signup.html', form=form)
                profile_img = profile_img_url

            user = User.signup(
                username=form.username.data.strip(),
                password=form.password.data,
                email=form.email.data.strip(),
                profile_img=profile_img,
            )

            db.session.add(user)
            db.session.commit()

        except IntegrityError as e:
            if "users_email_key" in str(e.orig):
                flash("Email already taken", 'danger')
            elif "users_username_key" in str(e.orig):
                flash("Username already taken", 'danger')
            else:
                flash("An error occurred. Please try again.", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect(url_for('homepage'))

    else:
        return render_template('users/signup.html', form=form)




@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('homepage'))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash('Successfully logged out', 'success')
    return redirect(url_for('login'))


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
@require_login
def show_following(user_id):
    """Show list of people this user is following."""

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
@require_login
def users_followers(user_id):
    """Show list of followers of this user."""

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
@require_login
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(url_for('show_following', user_id=g.user.id))


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
@require_login
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(url_for('show_following', user_id=g.user.id))


@app.route('/users//profile', methods=["GET", "POST"])
@require_login
def profile():
    """Update profile for current user."""

    user = g.user
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            images = ['profile_img', 'header_img']
            for img in images:
                img_file = request.files.get(img)
                img_url = request.form.get(f'{img}_url')

                if img_file and img_file.filename != '':
                    img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename))
                    setattr(user, img, url_for('static', filename='uploads/' + img_file.filename))
                elif img_url:
                    if not re.search(r'(.jpg|.png|.svg)$', img_url):
                        flash(f"Invalid URL for {img}! Please provide a URL that ends with .jpg, .png, or .svg", 'danger')
                        return render_template('users/edit.html', form=form, user=user)
                    setattr(user, img, img_url)

                user.email = form.email.data
                user.bio = form.bio.data
                user.location = request.form.get('location')

                if form.password.data:
                    user.password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')

            db.session.commit()
            flash("Profile Updated", 'success')
            return redirect(url_for('users_show', user_id=user.id))
        else:
            flash("Wrong password, please try again.", "danger")

    return render_template('users/edit.html', form=form, user=user)

@app.route('/change_password', methods=['GET', 'POST'])
@require_login
def change_password():
    """Change user password"""
    
    user = g.user
    form = ChangePasswordForm()

    if form.validate_on_submit():
        try:
            user.change_password(form.current_password.data, form.new_password.data, form.confirm.data)
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('users_show', user_id=user.id))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('change_password.html', form=form)
    return render_template('users/change_password.html', form=form)



@app.route('/users/delete', methods=["POST"])
@require_login
def delete_user():
    """Delete user."""

    do_logout()

    db.session.delete(g.user)
    db.session.commit()
    flash("Account Deleted", 'success')

    return redirect(url_for('signup'))


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for('homepage'))

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(url_for('users_show', user_id=g.user.id))

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
@require_login
def messages_destroy(message_id):
    """Delete a message."""

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(url_for('users_show', user_id=g.user.id))


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        user = g.user

        following_ids = db.session.query(Follows.user_being_followed_id).filter(Follows.user_following_id == user.id).all()
        following_ids_list = [id for id, in following_ids]

        following_ids_list.append(user.id)

        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids_list))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
