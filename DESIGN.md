# RUNMATE
CS50 Final Project 2022

Varun Suraj and Kevin Wang

### Structure of SQL Database

Our SQL Database consists of two tables.

The first is ‘users’, which contains account information for each user. This information comes directly from the Register form, and contains a first_name, last_name, email, and hash (password), as well as an auto incrementing integer ID to easily identify each distinct user.

The second table is ‘runs’, which stores all runs submitted by all users. Information comes from the Add Runs form; the table contains a unique run_id for each run, a user_id that corresponds to the id in users of the currently logged in user, the distance and pace of the run, the date and time of day of the run, and (optionally) additional notes for the run and a map_link that can contain an OnTheGoMap share link. 

### Register and Login

The functionality of Register and Login are fairly straightforward, as they for the most part are identical to the corresponding functions in the Finance problem set. In Register, navigating to the page sends a GET request that simply returns an HTML template, while submitting the form on the page sends a POST request. In the processing of this POST request, the code retrieves the form responses, makes checks to ensure that every field was filled in (these checks are also made directly in the HTML by specifying that every entry field is required, along with requiring that the email actually fit with an email format), that the password and its confirmation matched, and that the email address entered has not already been taken by another user. Through an INSERT SQL statement, the form entries are inserted into the users table (a hashed version of the password is inserted rather than the actual password).

Login also has GET and POST request functionality; GET requests return the HTML template for the login form (email and password fields are marked as required within the HTML), while the POST request retrieves the responses of this form. Using a SELECT statement, any account that is associated with the entered email is retrieved (note that this can never be more than 1 account given that Register prevents any account from being registered that uses an email already associated with an account). The password is checked against the hashed version of the password in the database; if there’s a match there, then the user is logged in and redirected to the index page.

### Index

The Index page uses two SQL queries; the first is a simple SELECT query to ‘users’ to get the first name of the user currently logged in, and the second is a SELECT query to ‘runs’ to get all runs associated with the user logged in (this uses the condition WHERE user_id = the user id stored in the current session of the application). The name of the user is displayed at the top of the screen, and all proposed runs of the current user are displayed in the table (this is accomplished through a Jinja loop through the list of dictionaries that the second SELECT query returns). The current date is also displayed on the screen; this is obtained using the Python datetime library.

### Add Run

Add uses GET and POST, the GET being for displaying the form and the POST being for processing form responses. In the HTML template, key features worth noting are that all entries except for notes and the map link are marked as required in the tags, and that the date selector has a minimum value set at the current date to prevent users from proposing a run in the past. The POST request section of the code retrieves the responses from the form, ensures that the date and time were actually selected and not simply on the default values (which are still submittable but will appear with a value of None), and runs an INSERT statement to put the run into ‘runs’.

### Delete Run

Again, a GET request to display the form and a POST request to process the form responses. The HTML template utilizes Jinja loops to loop through all of the current user’s runs (retrieved through a SELECT statement) and displays identifying information about them in a dropdown. The POST gets the run_id of the selected run (while ensuring that a run was actually selected) and, through DELETE FROM runs WHERE run_id = the selected run, removes the selected run from the ‘runs’ table.

### Match

The core functionality is also the most complex. We first SELECT all runs (essentially the information that was inputted in the Add Runs page) for the user that was logged in (storing it in user_runs). If the user hasn’t yet inputted any runs (when the length of the previous select statement is 0), we redirect them to the Add Runs page, which then displays an error message. Assuming that the user has already inputted runs, we continue down the code. For each entry, we first split the pace at the colon mark, to separate the minutes and seconds. We convert the pace into purely the number of seconds by casting the minutes and seconds from strings to ints, then multiplying the number of minutes by 60 and adding it to the number of seconds. We then repeat the same process for every run from users other than the user currently logged in (by first SELECTING all runs where the user_id is not equal to the user_id of the logged in user, storing it inside other_runs). The same conversion of the pace occurs afterwards. We then create an empty list of dictionaries called available_users that stores all the matches. We iterate through the other_runs as the outer loop, then iterate through inner_runs as the inner loop. For each entry in other_runs that matches the date and time availability of a run in user_runs and where the user_run’s distance is within +- 1.5 miles and pace is within +- 60 seconds of other_run, that entry in other_run is appended to available_users. Then, for each entry in available_users, we add the name and email address of the matched user by SELECTING all fields from the users table (essentially the information collected when registering for a new account), storing these inside the available_users list as well. We then convert the pace inside the available_users table back into minutes: seconds format. We then render the match.html template, passing in the available_users table, where we use Jinja to iterate through each entry in available_users, displaying each in a separate row.
