from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User,Post, Comment
from . import app, lm, db
from .forms import LoginForm, SignupForm, UserProfileForm, AddPostForm
from datetime import datetime  # This imports the datetime class directly


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template("index.html")

@login_required
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = AddPostForm()
    posts = Post.latest()

    if form.validate_on_submit():
        new_post = Post(
            posted_by=current_user.username,
            content=form.content.data,
            user_id=current_user.id,
            last_modified=datetime.utcnow()
        )
        new_post.save()
        flash("Post was successful", "success")
        return redirect(url_for('home'))

    return render_template("home.html", form=form, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("starting ")
    form = LoginForm()
    print("ok")
    if form.validate_on_submit():
        print("Form validated!")  # Debugging line
        user = User.query.filter_by(email=form.email.data).first()  # Fetch user by email
        if user and user.check_password(form.password.data):  # Check password
            login_user(user, form.remember_me.data)  # Log in user
            flash("Login successful")  # Success message
            return redirect(url_for('home'))  # Redirect to home
        flash("Incorrect password or email")  # Flash error message
       
        with app.app_context():
          users = User.query.limit(5).all()
          
           # Print the errors that caused validation to fail
    return render_template("login.html", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():  # Hash password
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()  # Save new user to the database
        flash("Registration successful, please log in.")
        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template("signup.html", form=form)
@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile' , methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = UserProfileForm()
    if form.validate_on_submit():
        user.email = form.email.data
        user.bio = form.bio.data
        db.session.commit()  # Ensure changes are committed to the database
        flash("Profile updated successfully")
        return redirect(url_for('home'))
    form.email.data = user.email
    form.bio.data = user.bio
    return render_template('profile.html', form=form)

@app.route('/comment/<id>', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = AddPostForm()
    post = Post.query.get_or_404(id)
    
    if form.validate_on_submit():
        new_comment = Comment(
            posted_by=current_user.username,
            content=form.content.data,
            post_id=id
        )
        new_comment.save()
        flash('Comment Added')
        return redirect(url_for('home'))
    
    return render_template('comment.html', form=form, post=post)

