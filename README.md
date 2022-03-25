# Hogwarts School
Hogwarts inspired school management system made with Python and Django.
Created for educational purposes.

[Live version](https://hogwarts-school-management.herokuapp.com/)

Login details (accounts generated with populatedb command):
* login: **admin**, password: **admin**
* login: **teacher**, password: **teacher**
* login: **student**, password: **student**
* login: **parent**, password: **parent**

## Features
* Creating, editing, deleting grade categories and grades
* Displaying grades for a specific student or class and subject
* Managing lesson sessions
* Setting and submitting homeworks
* Displaying attendance summary for a specific student or class
* Creating, editing, deleting events in the calendar
* Displaying a timetable for a specific class or teacher
* Generating summary PDF files for classes
* Sending messages to other users

## Technologies
* Python 3.10
* Django 3.2
* Bootstrap 5.0
* htmx
* PostgresSQL

## Setup
1. Clone the repository
```sh
$ git clone https://github.com/rcybulski1122012/django_school.git
```
2. Create virtual environment, activate it and install dependencies
```sh
$ cd django_school
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
3. Provide required environments variables for database connection
   * `PSQL_NAME`
   * `PSQL_USER`
   * `PSQL_PASSWORD`
   * `PSQL_HOST`
   * `PSQL_PORT`

4. Run migrations. Optionally you can generate sample data
```sh
$ python manage.py migrate
$ python manage.py populatedb
```

5. That's all. Now you can run the application
```sh
$ python manage.py runserver
```
