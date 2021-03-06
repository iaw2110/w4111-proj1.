#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://iaw2110:ivanrohan@34.73.21.127/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  
#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/home')
def home():
  return redirect('/')

@app.route('/another')
def another():
  cursor = g.conn.execute("SELECT A.city FROM addresses A")
  names = []
  names.append(["City"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)
  return render_template("another.html", **context)

@app.route('/another', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute("INSERT INTO addresses (ad_id, country, state_province, city) VALUES ((SELECT MAX(ad_id) + 1 FROM addresses), NULL, NULL, %(name)s)", {'name': name})
  return redirect('/another')

@app.route('/')
def index():

  cursor = g.conn.execute("SELECT P.p_name, P.t_name, S.games_played, S.goals, S.assists, S.points, S.plus_minus, S.penalty_minutes, S.minutes, S.blocks, S.hits, S.faceoff_percentage, S.goals_against, S.shots_against, S.saves, S.save_percentage FROM players P LEFT OUTER JOIN player_statistics PS ON P.p_name = PS.p_name LEFT OUTER JOIN statistics S ON S.s_id = PS.s_id")

  names = []
  names.append(["Player Name", "Team Name", "Games Played", "Goals", "Assists", "Points", "Plus/Minus", "Penalty Minutes", "Minutes on the Ice", "Blocks", "Hits", "Faceoff Percentage", "Goals Against", "Shots Against", "Saves", "Save Percentage"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/goals', methods=['POST'])
def goals():
  cursor = g.conn.execute("SELECT P.p_name, S.goals FROM players P LEFT OUTER JOIN player_statistics PS ON P.p_name = PS.p_name LEFT OUTER JOIN statistics S on S.s_id = PS.s_id GROUP BY P.p_name, S.goals ORDER BY S.goals DESC")
  names = []
  names.append(["Player Name", "Goals"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)      
  
@app.route('/plusminus', methods=['POST'])
def plusminus():
  cursor = g.conn.execute("SELECT P.p_name, S.plus_minus FROM players P LEFT OUTER JOIN player_statistics PS ON P.p_name = PS.p_name LEFT OUTER JOIN statistics S on S.s_id = PS.s_id GROUP BY P.p_name, S.plus_minus ORDER BY S.plus_minus DESC")
  names = []
  names.append(["Player Name", "Plus/Minus"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/saves', methods=['POST'])
def saves():
  cursor = g.conn.execute("SELECT P.p_name, S.saves FROM players P LEFT OUTER JOIN player_statistics PS ON P.p_name = PS.p_name LEFT OUTER JOIN statistics S on S.s_id = PS.s_id GROUP BY P.p_name, S.saves ORDER BY S.saves DESC")
  names = []
  names.append(["Player Name", "Saves"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/hometown', methods=['POST'])
def hometown():
  name = request.form['name']
  name = name + '%'
  if (name != ''):
    cursor =  g.conn.execute("SELECT P.p_name, A.city, A.country FROM players P LEFT OUTER JOIN addresses A ON P.ad_id = A.ad_id WHERE A.city LIKE %(name)s", {'name': name}) 
    names = []
    names.append(["Player Name", "City", "Country"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)

  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/conference', methods=['POST'])
def conference():
  name = request.form['name']
  name = name + '%'
  if (name != ''):
    cursor = g.conn.execute("SELECT P.p_name, C.con_name FROM players P LEFT OUTER JOIN teams T ON P.t_name = T.t_name LEFT OUTER JOIN conferences C ON T.con_name = C.con_name WHERE C.con_name LIKE %(name)s", {'name': name})
    names = []
    names.append(["Player Name", "Conference"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)

  else:
    names = []
    context = dict(data = names)
  
  return render_template("index.html", **context)

@app.route('/years', methods=['GET'])
def years():
  cursor = g.conn.execute("SELECT T.t_name, T.year_established FROM teams T ORDER BY T.year_established ASC")
  names = []
  names.append(["Team Name", "Year Established"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)
 
  return render_template("index.html", **context)

@app.route('/info', methods=['GET'])
def info():
  cursor = g.conn.execute("SELECT T.t_name, T.salary_cap, T.owner_name, C.c_name, T.number_of_wins, T.number_of_losses, T.overtime_losses, T.points, T.con_name FROM teams T LEFT OUTER JOIN coaches C ON T.t_name = C.t_name")
  names = []
  names.append(["Team Name", "Salary Cap", "Owner Name", "Coach Name", "# of Wins", "# of Losses", "# of Overtime Losses", "Points",  "Conference Name"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/team', methods=['POST'])
def team():
  name = request.form['name']
  name = name + '%'
  if (name != ''):
    cursor = g.conn.execute("SELECT T.t_name, P.p_name, P.position, P.salary, P.date_of_birth FROM players P LEFT OUTER JOIN teams T ON P.t_name = T.t_name WHERE T.t_name LIKE %(name)s", {'name': name})
    names = []
    names.append(["Team Name", "Player Name", "Position", "Salary", "Date of Birth"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)

  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/arenas', methods=['GET'])
def arenas():
  cursor = g.conn.execute("SELECT T.t_name, A.a_name, A.capacity FROM teams T LEFT OUTER JOIN arenas A ON T.a_name = A.a_name")
  names = []
  names.append(["Team Name", "Arena Name", "Arena Capacity"])
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
