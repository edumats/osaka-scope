import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# database engine object from SQLAlchemy that manages connections to the database
# DATABASE_URL is an environment variable that indicates where the database lives
engine = create_engine("postgres://ciyhgcghdmlvvk:ff972a3b363002679b9a33dca4a0fcc5caf8b4095f03727de998c5f1dd58989a@ec2-54-221-201-212.compute-1.amazonaws.com:5432/ddsqmt6fvh3id5")

# create a 'scoped session' that ensures different users' interactions with the database are kept separate
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@login_required
def index():
    """Show graph"""

    """ Requests sensor data from database """
    data = db.execute('SELECT * FROM sensor_data').fetchall()
    if not data:
        return apology("Error retrieving sensor data", 400)

    return render_template("index.html", data=data)

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    if request.method == 'GET':
        username = request.args.get('username')
        # Query database for username
        query = db.execute('SELECT username FROM users WHERE username = :username', username=username)

        # If username is lenght > 1 and does not contain in users database, return true; otherwise, false
        if len(username) > 1 and not query:
            return jsonify(True)
        else:
            return jsonify(False)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        user = db.execute('SELECT username FROM users WHERE username=:username', username=request.form.get("username"))
        if user:
            return apology('user already exists', 400)

        hash = generate_password_hash(request.form.get("password"))

        # Query database for username
        result = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
                            username=request.form.get("username"), hash=hash)
        if not result:
            return apology("user already exists", 200)

        # Stores id returned by INSERT
        session["user_id"] = result

        # Redirect user to home page
        flash("Registration successful")
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    '''Manages users settings'''
    if request.method == 'POST':
        password = request.form.get("password")
        if not password:
            flash('You must provide the current password')
            return redirect("/settings")

        password_new = request.form.get("password_new")
        if not password_new:
            flash('You must provide the new password')
            return redirect("/settings")

        # Query database
        rows = db.execute("SELECT * FROM users WHERE id = :id",
                          id=session["user_id"])
        print(rows)
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid password", 403)

        # Hash new password
        hash = generate_password_hash(request.form.get("password_new"))

        # Update password
        update = db.execute('UPDATE users SET hash = :hash WHERE id = :id', hash=hash, id=session["user_id"])
        if update:
            # Redirect user to home page
            flash("Password have successfully changed")
            return redirect(url_for('index.html'))
        else:
            flash("Error updating password")
            return redirect(url_for('index.html'))
    else:
        return render_template('settings.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
