import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required

app = Flask(__name__)

db = SQL("sqlite:///run.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    # TODO: display current runs

    # get first name to display
    sql_name = db.execute("SELECT first_name FROM users WHERE id = ?", session["user_id"])
    first_name = sql_name[0]["first_name"]
    
    runs = db.execute("SELECT distance, pace, day, time_of_day, notes FROM runs WHERE user_id = ?", session["user_id"])
    # print(runs)

    return render_template("index.html", name=first_name, runs=runs)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_run():

    # visiting the page to fill out the form
    if request.method == "GET":
        # lists of days and time increments
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        times = ["12am-2am", "2am-4am", "4am-6am", "6am-8am", "8am-10am", "10am-12pm", "12pm-2pm", "2pm-4pm", "4pm-6pm", "6pm-8pm", "8pm-10pm", "10pm-12am"]
        
        # render form template
        return render_template("add.html", days=days, times=times)
    
    # POST request

    # get form inputs
    distance = request.form.get("distance")
    pace_mins = request.form.get("pace_mins")
    pace_secs = request.form.get("pace_secs")
    day = request.form.get("day")
    time = request.form.get("time")
    notes = request.form.get("notes")
    pace_full = str(pace_mins) + ":" + str(pace_secs)
    
    # check that the user actually selected a proper entry from the dropdown
    # as opposed to the default
    if not day:
        return apology("Day not selected from dropdown")
    if not time:
        return apology("Time not selected from dropdown")
    
    # insert entry into runs table
    db.execute("INSERT INTO runs (user_id, distance, pace, day, time_of_day, notes) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], distance, pace_full, day, time, notes)

    # redirect back to index page
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # if our request method is GET, then the user must have navigated to the register page.
    # We just want to display the register options
    if request.method == 'GET':
        return render_template("register.html")

    # if we didn't return anything there, then it must be a POST request.

    # get the username, password, and password confirmation from the form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm = request.form.get("confirmation")
    strava = request.form.get("strava")

    # check that the required text boxes were actually filled in
    # this is redundant now that we've added the "required" tag in HTML
    # but we're keeping the if statements anyways
    if not first_name:
        return apology("First name not entered")
    if not last_name:
        return apology("Last name not entered")
    if not email:
        return apology("Email not entered")
    if not password:
        return apology("No password")
    if not confirm:
        return apology("No password confirmation")

    # Check if password and confirmation match
    if password != confirm:
        return apology("Password and confirmation do not match")

    # check that password is at least 10 characters
    # if len(password) < 10:
    #     return apology("Password is less than 10 characters")

    # # check that password has at least one lowercase letter
    # if not any(char.islower() for char in password):
    #     return apology("Password does not contain a lowercase letter")

    # # check that password has at least one uppercase letter
    # if not any(char.isupper() for char in password):
    #     return apology("Password does not contain an uppercase letter")

    # # check that password has at least one number
    # if not any(char.isdigit() for char in password):
    #     return apology("Password does not contain a number")

    # # check that password has at least one special character
    # special_chars = ["!", "@", "#", "$", "%", "&", "^", "*"]
    # if not any(char in special_chars for char in password):
    #     return apology("Password does not contain a special character")

    # if we have made it here, then everything in the registration form is valid

    # get hashed version of the password, going with default method and salt length
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    # check that username does not already exist
    if len(db.execute("SELECT email FROM users WHERE email == ?", email)) == 0:
        # SQL insert statement is slightly different based on whether
        #   or not the user gave their Strava id
        if not strava:
            db.execute("INSERT INTO users (first_name, last_name, email, hash) VALUES (?, ?, ?, ?)", first_name, last_name, email, hashed_pw)
        else:
            db.execute("INSERT INTO users (first_name, last_name, email, hash, strava) VALUES (?, ?, ?, ?, ?)", first_name, last_name, email, hashed_pw, strava)
        return redirect("/")

    # if we get here, that means the username already existed.
    return apology("Email already exists, please choose another")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")