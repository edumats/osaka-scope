import os

import psycopg2
from flask import Flask, flash, session, request, redirect, render_template, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"),echo=True)
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@login_required
def index():
    """ Main Page """
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logs user """

    # Forgets user id, if any
    session.clear()

    # Reached via POST method
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username is provided
        if not username:
            return apology("please type a username", 400)

        # Check if password is provided
        if not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":username}).fetchone()

        if rows is not None and check_password_hash(rows.hash, password):
            session["user_id"] = rows.id
            return redirect("/")

        flash('Wrong username or password')
        return redirect(url_for('login'))

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    # Forget cached session
    session.clear()

    # Reached via POST method
    if request.method == "POST":

        username = request.form.get("username")

        # Check if username is provided
        if not username:
            return apology("please type a username", 400)

        # Check if password is provided
        if not request.form.get("password"):
            return apology("please type a password", 400)

        # Check if password matches in confirmation field
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Check if user exists in database
        user = db.execute('SELECT username FROM users WHERE username=:username', {"username":username}).fetchone()
        if user is not None:
            return apology("user already exists", 400)

        # Create hash from password
        hash = generate_password_hash(request.form.get("password"))

        # Store new user into database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash) RETURNING id",
                            {"username":username, "hash":hash}).fetchone()
        db.commit()

        # Stores id in session
        session["user_id"] = result[0]

        # Redirect user to home page
        return redirect("/")

    # Reached route via GET
    else:
        return render_template("register.html")

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    if request.method == 'GET':
        username = request.args.get('username')
        # Query database for username
        query = db.execute('SELECT username FROM users WHERE username = :username', {"username":username}).fetchone()

        # If username is lenght > 1 and does not contain in users database, return true; otherwise, false
        if len(username) > 1 and not query:
            return jsonify(True)
        else:
            return jsonify(False)
