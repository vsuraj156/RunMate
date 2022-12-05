from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

app = Flask(__name__)

db = SQL("sqlite:///run.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# get current date (users shouldn't be able to select runs in the past)
cur_date = datetime.today().strftime('%Y-%m-%d')
# whether or not an error message should be displayed
error_message = False

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
    
    # get all runs for this user
    runs = db.execute("SELECT distance, pace, date, time_of_day, notes FROM runs WHERE user_id = ?", session["user_id"])

    # if there are no runs yet, set error message boolean to true
    # This will cause a warning in add to appear when the user navigates there
    global error_message
    if len(runs) == 0:
        error_message = True
    else:
        error_message = False
    
    return render_template("index.html", name=first_name, runs=runs, cur_date = cur_date)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_run():
    # visiting the page to fill out the form
    if request.method == "GET":
        # list of time increments
        times = ["12am-2am", "2am-4am", "4am-6am", "6am-8am", "8am-10am", "10am-12pm", "12pm-2pm", "2pm-4pm", "4pm-6pm", "6pm-8pm", "8pm-10pm", "10pm-12am"]
        
        # render form template
        return render_template("add.html", times=times, cur_date=cur_date, error_message = error_message)
    
    # POST request

    # get form inputs
    distance = request.form.get("distance")
    pace_mins = request.form.get("pace_mins")
    pace_secs = request.form.get("pace_secs")
    date = request.form.get("date")
    time = request.form.get("time")
    notes = request.form.get("notes")
    map_link = request.form.get("map_link")

    pace_full = str(pace_mins) + ":" + str(pace_secs)
    
    # check that the user actually selected a proper entry from the dropdown
    # as opposed to the default (even though default is not selectable, 
    #   if it is not changed from initial then the user can still click enter and it will go through
    #   so we have to check for that here)
    if not date:
        return apology("Date not selected")
    if not time:
        return apology("Time not selected from dropdown")
    
    # insert entry into runs table
    db.execute("INSERT INTO runs (user_id, distance, pace, date, time_of_day, notes, map_link) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], distance, pace_full, date, time, notes, map_link)

    # redirect back to index page
    return redirect("/")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete_run():
    # get all runs for this user
    user_runs = db.execute("SELECT * FROM runs WHERE user_id = ?", session["user_id"])

    # normal navigation to the page
    if request.method == 'GET':
        return render_template("delete.html", user_runs = user_runs)
    
    # get run id from the form
    run_id = request.form.get("delete-run")
    # default entry selected instead of actual run
    if not run_id:
        return apology("Entry not selected from dropdown")

    # delete specified run, and navigate back to index
    db.execute("DELETE FROM runs WHERE run_id = ?", run_id)
    return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
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

    # get hashed version of the password, going with default method and salt length
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    # check that username does not already exist
    if len(db.execute("SELECT email FROM users WHERE email == ?", email)) == 0:
        # SQL insert statement
        db.execute("INSERT INTO users (first_name, last_name, email, hash) VALUES (?, ?, ?, ?)", first_name, last_name, email, hashed_pw)
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


@app.route("/match")
@login_required
def match():  
    # Gets the data input from the runs table for the logged-in user
    user_runs = db.execute("SELECT * FROM runs WHERE user_id = ?", session["user_id"])
    # If user hasn't yet entered any runs, redirect them to the Add Runs page
    if len(user_runs) == 0:
        
        global error_message
        error_message = True
        return redirect("/add") 

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
            if ((user_run["date"] == other_run["date"]) and (user_run["time_of_day"] == other_run["time_of_day"]) 
            and (user_run["distance"] >= (other_run["distance"] - 1.5) and user_run["distance"] <= (other_run["distance"] + 1.5))
            and (user_run["pace"] >= (other_run["pace"] - 60) and user_run["pace"] <= (other_run["pace"] + 60))):
                available_users.append(other_run)

    
    # For each matched user, convert their pace from seconds back to minute:seconds
    for available_user in available_users:
        name_list = db.execute("SELECT * FROM users WHERE id = ?", available_user["user_id"])
        name = name_list[0]["first_name"] + " " + name_list[0]["last_name"]
        available_user["full_name"] = name

        email = name_list[0]["email"]
        available_user["email"] = email


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