import os

import psycopg2
from flask import Flask, flash, session, request, redirect, render_template, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

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
    # Counts the number of views on tube
    counter = db.execute("SELECT COUNT(counter) FROM sensor_data").fetchone()

    # Returns date of last view
    lastView = db.execute("SELECT TO_CHAR(date, 'Mon dd, yyyy') date_correct FROM sensor_data ORDER BY date DESC LIMIT 1;").fetchone()

    # Returns hour of last views
    lastViewHour = db.execute("SELECT TO_CHAR(date - INTERVAL '3 hour', 'HH24:MI') date_correct FROM sensor_data ORDER BY date DESC LIMIT 1").fetchone()

    # Returns today's number of views
    todayView = db.execute("SELECT COUNT(counter) FROM sensor_data WHERE date >= NOW()::date").fetchone()

    return render_template("index.html", counter=counter[0], lastView=lastView[0], todayView=todayView[0], lastViewHour=lastViewHour[0])

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
            error = 'Please fill the username field'
            return render_template("login.html", error=error)

        # Check if password is provided
        if not password:
            error = 'Please fill the password field'
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":username}).fetchone()
        # Check if username is not present in database and if provided password is correct, if yes, logs and goes to index page
        if rows is not None and check_password_hash(rows.hash, password):
            session["user_id"] = rows.id
            return redirect(url_for('index'))

        # If username/password check fails, return error message and redirects to login
        error = 'Incorrect username or password'
        return render_template("login.html", error=error)

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
            error = 'Please fill the username field'
            return render_template("register.html", error=error)

        # Check if password is provided
        if not request.form.get("password"):
            error = 'Please fill the password field'
            return render_template("register.html", error=error)

        # Check if password matches in confirmation field
        if request.form.get("password") != request.form.get("confirmation"):
            error = 'Provided passwords do not match'
            return render_template("register.html", error=error)

        # Check if user exists in database
        user = db.execute('SELECT username FROM users WHERE username=:username', {"username":username}).fetchone()
        if user is not None:
            error = 'Username already registered'
            return render_template("register.html", error=error)

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
