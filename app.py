import csv
import logging
from flask import Flask, request, flash, url_for, redirect, render_template
# wrote the following two lines by breaking up one
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

# xcode-select --install
# git clone https://github.com/carlosherbozo/nba-project.git
# git init
# git add instance/ templates/ app.py data.csv README.md students.sqlite3
# git commit -am "blah"

logging.basicConfig(level=logging.DEBUG)  # for debugging

app = Flask(__name__)  # shortcut for application's module or package
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'  # filename for db
app.config['SECRET_KEY'] = "random string"  # if using sessions https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions

db = SQLAlchemy(app)

class students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200)) 
    pin = db.Column(db.String(10))

    def __init__(self, name, city, addr, pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin

        
@event.listens_for(students.__table__, 'after_create')
def create_departments(*args, **kwargs):
    with open('Team.csv', newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(reader):
            if i == 0:
                continue

            student = students(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            logging.debug("Team {}, {}, {}, {}, {}, {}, {}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            db.session.add(student)
            db.session.commit()


@app.route('/')
def show_all():
    return render_template('show_all.html', students = students.query.all() )

@app.route('/new', methods = ['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['city'] or not request.form['addr']:
            flash('Please enter all the fields', 'error')
        else:
            student = students(request.form['name'], request.form['city'], request.form['addr'], request.form['pin'])
        
            db.session.add(student)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')

# added the following line
with app.app_context():
    if __name__ == '__main__':
        db.create_all()
        app.run(debug = True)