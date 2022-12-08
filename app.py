import csv
import logging
from flask import Flask, request, flash, url_for, redirect, render_template, make_response
# wrote the following two lines by breaking up one
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlite3 import Cursor, connect, Row
from contextlib import closing
import sqlite3
import pandas as pd

# pip3 install flask
# pip3 install Flask_sqlalchemy
# pip3 install sqlalchemy
# xcode-select --install
# git clone https://github.com/carlosherbozo/nba-project.git
# git init
# git add instance/ templates/ app.py data.csv README.md students.sqlite3
# git commit -am "blah"

DB_URL = 'nba.sqlite3'
logging.basicConfig(level=logging.DEBUG)  # for debugging

app = Flask(__name__)  # shortcut for application's module or package
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'  # filename for db
app.config['SECRET_KEY'] = "random string"  # if using sessions https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions

db = SQLAlchemy(app)

class teams(db.Model):
    id = db.Column('team_id', db.Integer, primary_key = True)
    Team_Name = db.Column(db.String(50))
    City = db.Column(db.String(50))
    Division = db.Column(db.String(20)) 
    Head_Coach = db.Column(db.String(50))
    Year_Founded = db.Column(db.String(5))
    Number_Of_Championships = db.Column(db.String(3)) 
    Home_Stadium = db.Column(db.String(20))

    def __init__(self, Team_Name, City, Division, Head_Coach, Year_Founded, Number_Of_Championships, Home_Stadium):
        self.Team_Name = Team_Name
        self.City = City
        self.Division = Division
        self.Head_Coach = Head_Coach
        self.Year_Founded = Year_Founded
        self.Number_Of_Championships = Number_Of_Championships
        self.Home_Stadium = Home_Stadium

#BACKEND HELPERS
def execute_query(stmt_str: str, vals = None):
    try:
        with connect(DB_URL, isolation_level=None, uri=True) as connection:
            # Create row factory
            connection.row_factory = Row
            with closing(connection.cursor()) as cursor:
                if vals:
                    cursor.execute(stmt_str, vals)
                else:
                    cursor.execute(stmt_str)
                names = [description[0] for description in cursor.description]
                data = cursor.fetchall()
            return (names, data)
    except:
        return []

def player_search(input: dict):
    try:
        stmt_str = "SELECT * FROM players "
        filters = []
        vals = []
        for key in input.keys():
            if input[key] and input[key] != '':
                filters.append(f"\"{key}\" LIKE ? ")
                vals.append("%" + str(input[key]) + "%")
        if len(filters) != 0:
            stmt_str += ("WHERE " + " AND ".join(filters))
            return execute_query(stmt_str, vals)
        return execute_query(stmt_str)
    except:
        return [[], {}]

def team_search(input: dict):
    stmt_str = "SELECT Team_Name, Division, AVG(Points_per_Game) as Points_per_Game, AVG(Rebounds_per_Game) as Rebounds_per_Game, "
    stmt_str += "AVG(Assists_per_Game) as Assists_per_Game, AVG(Steals_per_Game) as Steals_per_Game, "
    stmt_str += "AVG(Blocks_per_Game) as Blocks_per_Game, AVG(Turnovers_per_Game) as Turnovers_per_Game "
    stmt_str += "FROM (teams NATURAL JOIN players) "
    try:
        filters = []
        vals = []
        for key in input.keys():
            if input[key] and input[key] != '':
                filters.append(f"\"{key}\" LIKE ? ")
                vals.append("%" + str(input[key]) + "%")
        if len(filters) != 0:
            stmt_str += ("WHERE " + " AND ".join(filters))
            stmt_str += "GROUP BY Team_Name "
            return execute_query(stmt_str, vals)
        stmt_str += "GROUP BY Team_Name "
        return execute_query(stmt_str)
    except:
        return [[], {}]


# @event.listens_for(students.__table__, 'after_create')
# def create_departments(*args, **kwargs):
#     with open('data.csv', newline='\n') as csvfile:
#         reader = csv.reader(csvfile, delimiter=',')
#         for i, row in enumerate(reader):
#             if i == 0:
#                 continue

#             student = students(row[0], row[1], row[2], row[3])
#             logging.debug("Student {}, {}, {}, {}".format(row[0], row[1], row[2], row[3]))
#             db.session.add(student)
#             db.session.commit()

@event.listens_for(teams.__table__, 'after_create')
def create_teams(*args, **kwargs):
    with open('Team.csv', newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(reader):
            if i == 0:
                continue

            team = teams(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            logging.debug("Team {}, {}, {}, {}, {}, {}, {}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            db.session.add(team)
            db.session.commit()


@app.route('/', methods = ['GET', 'POST'])
def show_all():
    data = None
    if request.method == "POST":
        query = request.form["query"]
        names, data = execute_query(query)
        return render_template('show_all.html', names=names, data=data)
    return render_template('show_all.html' , data=data)

@app.route('/teams')
def teams_all():
    return render_template('teams.html', teams = teams.query.all() )

# @app.route('/new', methods = ['GET', 'POST'])
# def new():
#     if request.method == 'POST':
#         if not request.form['name'] or not request.form['city'] or not request.form['addr']:
#             flash('Please enter all the fields', 'error')
#         else:
#             student = students(request.form['name'], request.form['city'], request.form['addr'], request.form['pin'])
        
#             db.session.add(student)
#             db.session.commit()
#             flash('Record was successfully added')
#             return redirect(url_for('show_all'))
#     return render_template('new.html')

@app.route('/searchplayers', methods = ['GET'])
def search_players():
    name = request.args.get('name')
    team = request.args.get('team')
    pos = request.args.get('pos')
    if any(item is not None for item in [name, team, pos]):
        parameters = {
            "Player_Name": name if name else '',
            "Team_Name": team if team else '',
            "Primary_Secondary_Position": pos if pos else '',
        }
        names, data = player_search(parameters)
        html = render_template('player_stats.html', names=names, data = data)
    else:
        html = render_template('player_stats.html')
    response = make_response(html)
    return response

@app.route('/teamstats', methods = ['GET'])
def team_stats():
    name = request.args.get('name')
    div = request.args.get('div')
    if any(item is not None for item in [name, div]):
        parameters = {
            "Team_Name": name if name else '',
            "Division": div if div else '',
        }
        names, data = team_search(parameters)
        html = render_template('teamstats.html', names=names, data = data)
    else:
        html = render_template('teamstats.html')
    response = make_response(html)
    return response
