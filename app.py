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
    sql = db.execute("SELECT first_name FROM users WHERE id = ?", session["user_id"])
    name = sql[0]["first_name"]
    return render_template("index.html", name=name)

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
        if not strava:
            db.execute("INSERT INTO users (first_name, last_name, email, hash) VALUES (?, ?, ?, ?)", first_name, last_name, email, hashed_pw)
        else:
            db.execute("INSERT INTO users (first_name, last_name, email, hash, strava) VALUES (?, ?, ?, ?, ?)", first_name, last_name, email, hashed_pw, strava)
        return redirect("/")

    # if we get here, that means the username already existed.
    return apology("Username already exists, please choose another")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/match")
@login_required
def match():  
    # Gets the data input from the runs table for the logged-in user
    user_runs = db.execute("SELECT * FROM runs WHERE user_id = ?", session["user_id"])
    # If user hasn't yet entered any runs, redirect them to the Add Runs page
    if len(user_runs) == 0:
       return render_template("add.html") 

    for user_run in user_runs:
        # Changes the input pace from minute:second format to an int representing the number of seconds
        user_unedited_pace = user_run["pace"].split(':')
        user_run["pace"] = int(user_unedited_pace[0]) * 60 + int(user_unedited_pace[1])

    # Gets the data input from the runs table for all users except the logged-in user
    other_runs = db.execute("SELECT * FROM runs WHERE user_id != ?", session["user_id"])

    for other_run in other_runs:
        # Changes the input pace from minute:second format to an int representing the number of seconds
        other_unedited_pace = other_run["pace"].split(':')
        other_run["pace"] = int(other_unedited_pace[0]) * 60 + int(other_unedited_pace[1])


    # Matching user to other runners
    # Creates an list of dictionaries matched users with common availability times and pace within +- 1 min and distance within +- 1.5 miles
    # Creates a blank table with same headers as user_runs, which will contain list of matched users
    available_users = []

    for user_run in user_runs:
        for other_run in other_runs:
            if ((user_run["day"] == other_run["day"]) and (user_run["time_of_day"] == other_run["time_of_day"]) 
            and (user_run["distance"] >= (other_run["distance"] - 1.5) and user_run["distance"] <= (other_run["distance"] + 1.5))
            and (user_run["pace"] >= (other_run["pace"] - 60) and user_run["pace"] <= (other_run["pace"] + 60))):
                available_users.append(other_run)

    
    # For each matched user, convert their pace from seconds back to minute:seconds
    for available_user in available_users:
        name_list = db.execute("SELECT * FROM users WHERE id = ?", available_user["user_id"])
        name = name_list[0]["first_name"] + " " + name_list[0]["last_name"]
        available_user["full_name"] = name


        min = str(available_user["pace"] // 60)
        # If pace % 60 is 0, add an extra zero so the time format shows as xx:00 instead of xx:0
        sec = available_user["pace"] % 60
        if sec == 0:
            sec = str(available_user["pace"] % 60) + str(0)
        else:
            sec = str(available_user["pace"] % 60)
        
        available_user["pace"] = min + ":" + sec 
    
    # Merge the available_users table with the users table
    return render_template("match.html", available_users = available_users)