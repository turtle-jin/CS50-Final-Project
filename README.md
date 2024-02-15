# CS50 Final Project--Student Incentive Tracker



### About the Project:

> This is my final project for Harvard CS50X course-Introduction to Computer Science.
>
>I teach high school math at an alternative school setting. I have an incentive system for my classroom to help motivate my students to learn and to encourge good behavior in the classroom: students can earn points when they complete their assignments with satisfactory grades and after gaining enough points they can exchange their points for some rewards. In the past I have been just using paper and pencil to keep track of each student's points and after a while it has become very tedius so I made this web app called Student Incentive Tracker to help relieve some of the workload for myself.

> I have used python, HTML, CSS, sqlite3, and Flask framwork for this project.

### Project Description:

I created two different sections for the this Flask framework based web application: students accounts and admin accounts.

Students can create an account for themselves and then send requests to gain points, after the requests are approved by the admin, they can then use their points to purchase some of the classroom rewards. All the points transctions can be checked and verified through the "history" tab on their account.

On admin account, I can delete and edit students' accounts on admin index page and approve or deny student's point requests on the students request page. I can also view what they have spent on their points on through the "student usage" tab.

### Project break down:

`app.py` has the following routes to make this webapp functional:
> - after_request: Ensures responses are not cached.
> - index: Render student index page.
> - request: Users can send requests for admin approval.
> - use: Uses can buy incentives with the points they have requested and approved.
> - history: To show user all the point requests and usage history.
> - register: New student can register to make a new account.
> - login: Enables students to login.
> - logout: Logs users out.
> - admin_login: Enables admin to login. Admin user is stored in a seperated SQL table.
> - admin_index: Render admin index page which shows a summary of all students accounts.
> - delete_confirm: Double check with admin user if it is the right account to delete.
> - delete: delete a student user account.
> - edit and update: Admin can edit student's points here.
> - approve_request: Render the approve_request template page
> - approved: approve selected user request
> - denied: deny selected user request

`incentive.db` contains the following SQL table and SQL view table:
> - users
> - point_transactions
> - view points

When working with SQL view tables, I realized that the view tables basically are just a long "SELECT" statement, therefore it doesn't have id numbers auto generated, I have to insert both id numbers from the users and point_transactions to the points table to be able to work with the view table as intended.

`templates` contains all the html templates used for this project

`static` contains images, and the stylesheet for this project

### How to use:

To run the web applicaation use the following commands:

```
flask run --debug
```

### Requirements:
- cs50
- Flask
- Flask-Session
- requests



