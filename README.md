# RUNMATE
CS50 Final Project 2022

Varun Suraj and Kevin Wang

## Abstract

RunMate is a web-based application that essentially matches users who are interested in finding a new partner (or partners) to run with. Users register for an account, and can subsequently “Add Runs” (as many as they desire) to be put in the database, and RunMate will then provide a list of matched users based on the criteria in what the user inputted in “Add Runs”. The matching is made based on several criteria, including if there are common times of availability (date and the time of the day). 

## Setting Up RunMate
	
The GitHub repository is located at https://github.com/vsuraj156/RunMate.

Open a terminal window and run ‘git clone https://github.com/vsuraj156/RunMate.git’, then cd to the new directory by running ‘cd RunMate’

There are some packages that have to be installed in order to run the program; these can be installed using pip.

CS50 (for SQL): ‘pip install cs50’
Flask: ‘pip install flask’
Flask-Session: ‘pip install flask-session’
Werkzeug (for password hashing): ‘pip install Werkzeug’
DateTime: ‘pip install DateTime’

Once these packages are installed, run ‘flask run’. The command line window will tell you what server port the code is running on; copy that link and paste it into a web browser. If ‘flask run’ fails to work, please make sure that there are no other programs running, as another program might be taking up the same server port on your computer.

## Using RunMate

### Registering an Account and Logging In

When you, the user, navigate to the link that ‘flask run’ gives you, you should be directed to the /login route of the website. If you have previously created an account, you can simply enter your email and password to log into the website. If you have not created an account yet (or would like to make another account), click the “Register” tab. This new page will prompt you for your first and last name, email, and password (as well as a confirmation password). All of these fields are required, and the website will not allow you to submit without each of these fields being filled out. An error message will also be displayed if the two passwords (password and confirmation) do not match. If the user successfully registers, the website will redirect back to the login page; here, you can log in with your newly created account.

### Index

Once you log in, you are directed to the index page of the website. This page serves to show the user the runs they have currently entered into the system (more on how to add runs in the next section). If you have just made your account, then this page will display a table with no entries. If you have already added runs, they will populate on this index page; the information displayed will be the date of the proposed run, the time of day (the two hour range in which you would like to run), your proposed distance and pace, and any additional notes you would like to give as a supplement (note that this is not all the information available to enter when adding a run).

### Add Run

Navigating to the “Add Run” page will display a form for users to propose runs. If the user has no runs registered to their account, a warning message will appear at the top of the page in yellow stating that the user must submit a run before being able to match with other runners. The information that must be submitted is the date (the website will not allow you to submit a date in the past) and time of day that the user wants to run, as well as the proposed distance (in miles) and pace (two input boxes, one for minutes and one for seconds). There are also two optional text boxes. The first is for any additional notes that the user would like to submit; if there is any clarifying information about the run that the user wants others to know, that can be submitted. In addition, another optional text box is a share link for OnTheGoMap.com. This website allows users to plot runs on a map and see what the exact distance for the run would be; users can get a share link from that site and enter it into the second optional text box (more on where that link is used in the Match section of this Readme). Once the form is complete, the user can click the blue “Add Run” at the bottom of the page; this will redirect the user back to the index page, where they should be able to see the newly created run in the table.

### Delete Run

Users can also delete a run they no longer want to go on. If the user clicks the “Delete Run” tab at the top of their screen, they will be directed to the delete page, which consists of a dropdown form. The dropdown contains each run that the user has submitted (the displayed information is the date of the run and two-hour block of time that was submitted as the time of the run). If the user selects a run and clicks the blue “Delete” button, they will be redirected to the index page; the selected run should no longer be there.

### Match

Finally, we come to the core functionality of the website: the matching page. Firstly, it is worth noting that if a user tries to go to the Match page without having any runs submitted, they will automatically be redirected to the Add page and will be prompted to submit a run. If the user does have a run submitted, the Match page will display any proposed run submitted by another user that will take place at the same date and two-hour block of time, as well as a similar distance and pace (+/- 1.5 miles for distance, +/- 1 minute for pace). Any run that matches will display in the table on the page (if there are no matches, this table will remain empty); the information in the table itself is the name of the other runner, and the other runner’s proposed day, time, distance, and pace. Clicking on any of the entries will open a pop-up window with further information about the other runner’s submission. The information in the table will appear, as well as information from the optional Add fields like notes and an embedded map that shows a proposed route and exact distance of route (map would have been created previously by the other runner on OnTheGoMap.com).
