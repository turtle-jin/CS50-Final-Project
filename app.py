import os
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__, static_url_path="/static")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///incentive.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# User home
@app.route("/",methods=["GET", "POST"])
@login_required
def index():

    user = db.execute("SELECT * FROM users WHERE id = (?);", session["user_id"])
    firstname = user[0]["firstname"]
    points = user[0]["points"]
    return render_template("index.html", firstname=firstname, points=points)

# request points for approval
@app.route("/request", methods=["GET", "POST"])
@login_required
def request_points():
    user = db.execute("SELECT * FROM users WHERE id = (?);", session["user_id"])
    firstname = user[0]["firstname"]
    points = user[0]["points"]

    # Create a list of dict for request choices
    choices = [
        {"option":"Complete a Mastery Test with 80% or above grade", "value":2},
        {"option":"Complete a Post Test with 60% or above grade", "value":3},
        {"option":"Complete a Post Test with 80% or above grade", "value":5},
        {"option":"Solve the Math Brain Teaser", "value":2},
        {"option":"Good behavior in the classroom", "value":1},
    ]

    if request.method == "GET":
        return render_template("request.html", firstname=firstname, points=points, choices=choices)
    else:
        # Get user input
        user_request = request.form.get("ptchoice").split('|') #use split to seperate the strings
        request_reason = user_request[0]
        request_value = int(user_request[1])

        db.execute("INSERT INTO point_transactions (user_id, transaction_description, point_change) VALUES(?, ?, ?);", session["user_id"], request_reason, request_value)

        flash("Request sent, pending approval by your teachers.")


        return redirect("/")


# Purchase items with the points
@app.route("/use", methods=["GET", "POST"])
@login_required
def use():

    user = db.execute("SELECT * FROM users WHERE id = (?);", session["user_id"])
    firstname = user[0]["firstname"]
    points = user[0]["points"]

    # Create a list of dict for point usage choices
    choices = [
        {"option":"One piece of Candy", "value":3},
        {"option":"One bag of Fruit Snacks", "value":10},
        {"option":"One bag of Chips", "value":20},
        {"option":"15 mins of Classroom Music Pass", "value":20},
        {"option":"30 mins of Classroom Music Pass", "value":30},
    ]

    if request.method == "GET":
        return render_template("use.html", firstname=firstname, points=points, choices=choices)
    else:
        purchase_request = request.form.get("purchaseOptions").split("|")
        purchase_item = purchase_request[0]
        item_value = int(purchase_request[1])

        # Flash error message when user does not have enough points
        if item_value > points:
            flash("Sorry, you don't have enough points.")

        # Proceed and complete the purchase
        else:
            new_points = points - item_value
            db.execute("UPDATE users SET points = ? WHERE id = ?", new_points, session["user_id"])
            db.execute("INSERT INTO point_transactions (user_id, transaction_description, point_change, status) VALUES(?, ?, ?, ?);", session["user_id"], purchase_item, item_value*(-1), "COMPLETE")
            flash("Transaction successful.")

        return redirect("/")


# Give users a list of point transaction history
@app.route("/history")
@login_required
def history():

    """Show incentive history, status, earning and spending"""
    user = db.execute("SELECT * FROM users WHERE id = (?);", session["user_id"])
    points = user[0]["points"]
    firstname = user[0]["firstname"]

    # retrieve point transactions from the point_transactions table
    transaction_history = db.execute("SELECT transaction_description, point_change, timestamp, status FROM point_transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", transaction_history = transaction_history, points = points, firstname = firstname)


@app.route("/student_usage")
@login_required
def student_usage():

    # Show completed transactions
    usage = db.execute("SELECT * FROM points WHERE status = (?) ORDER BY timestamp DESC", "COMPLETE")

    return  render_template("student_usage.html", usage = usage)


# Register new user account
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get user input
        firstname = request.form.get("firstname")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Generate hash password
        hashed_password = generate_password_hash(password)

        # Validate the user's input
        row = db.execute("SELECT * FROM users WHERE username=(?);", username)

        if password != confirmation:
            flash ("Passwords do not match.")
            return render_template("register.html")
        elif row:
            flash("Username already exist, please pick a different username.")
            return render_template("register.html")
        else:
            db.execute("INSERT INTO users (username, firstname, hash) VALUES (?,?,?);", username, firstname, hashed_password)
            flash("Congratulations! Your account has been successfully created, please log in.")
            return render_template("login.html")

    return render_template("register.html")


# User login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():

    session.clear()

    if request.method =="POST":
        rows = db.execute("SELECT * FROM AdminUsers WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or rows[0]["password_hash"]!="unholydk":
            flash("invalid username and/or password")
            return render_template("adminlogin.html")
        session["user_id"] = rows[0]["id"]
        return redirect("/adminindex")

    return render_template("adminlogin.html")


# Admin home page
@app.route("/adminindex", methods=["GET","POST"])
@login_required
def adminindex():

    user = db.execute("SELECT * FROM users;")

    return render_template("adminindex.html", user = user)


# Confirm to delete the user account
@app.route("/delete_confirm", methods=["POST"])
@login_required
def delete_confirm():

    # retrieve the user id from the form
    id = int(request.form.get("id"))
    row = db.execute("SELECT firstname FROM users WHERE id = (?);", id)
    delete_name = row[0]['firstname']

    return render_template("delete.html", delete_name = delete_name, id = id)


# Delete selected user account
@app.route("/delete", methods=["POST"])
@login_required
def delete():

    id = request.form.get("id")

    print(f"Received id to delete: {id}")

    db.execute("DELETE FROM users WHERE id = (?);", id)

    return redirect("/adminindex")


# Edit user account
@app.route("/edit", methods=["POST", "GET"])
@login_required
def edit():

    id = int(request.form.get("id"))
    row = db.execute("SELECT * FROM users WHERE id = (?);", id)
    edit_name = row[0]["firstname"]
    points = row[0]["points"]

    return render_template("edit.html", edit_name = edit_name, points = points, id = id)


# Update user account
@app.route("/update", methods=["POST"])
@login_required
def update():

    id = int(request.form.get("id"))
    points = request.form.get("points")

    db.execute("UPDATE users SET points = :points WHERE id = :id;",
               points = points, id=id)

    return redirect("/adminindex")


# approve user request page
@app.route("/approve_request", methods=["POST", "GET"])
@login_required
def approve_request():
    if request.method == "GET":
        user = db.execute("SELECT * FROM points WHERE status = (?) ORDER BY timestamp DESC;", "PENDING")

        return render_template("approve_request.html", user = user)


# approve selected user request
@app.route("/approved", methods=["POST"])
@login_required
def approved():

    if request.method == 'POST':
        id = int(request.form.get('id'))
        row = db.execute("SELECT * FROM points WHERE id = (?);", id)
        user_id = row[0]["user_id"]
        point_change = int(row[0]["point_change"])
        user_points_list = db.execute("SELECT points FROM users WHERE id = (?);", user_id)
        user_current_points = user_points_list[0]["points"]
        new_total = user_current_points + point_change

        #Update users and point_transactions table
        db.execute("UPDATE users SET points = (?) WHERE id = (?);", new_total, user_id)
        db.execute("UPDATE point_transactions SET status =(?) WHERE id = (?);", "APPROVED", id)

    return redirect("/approve_request")


# deny selected user request
@app.route("/denied", methods=["POST"])
@login_required
def denied():
    id = int(request.form.get('id'))
    db.execute("UPDATE point_transactions SET status =(?) WHERE id = (?);", "DENIED", id)

    return redirect("/approve_request")


# log user out
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)