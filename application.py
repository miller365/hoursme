from flask import Flask,render_template, request, session,url_for,redirect
from timeLogger import TimeLogger
from datetime import date
import datetime

app = Flask(__name__)
app.secret_key = 'hellokljlkjkl'

seleniumSesssion={}


@app.route("/", methods=['GET',])
def home(errors=""):
    errors = request.args.get('errors',None)
    messages  = request.args.get('messages',None)

    return render_template("login.html", errors = errors, messages = messages)
@app.route("/login",methods=['POST'])
def login():
    print(f"Selenium Session@login1:{seleniumSesssion}")
    session["user"] = request.form['user']
    if session["user"] in seleniumSesssion:
        session["errors"] = ["You are already Logged in, Can only login on one device"]
        return redirect(url_for('home',errors=session["errors"],user =session["user"]))
    seleniumSesssion[session["user"]] = TimeLogger()
    seleniumSesssion[session["user"]].user = session["user"]
    seleniumSesssion[session["user"]].passw = request.form['pass']
    session["errors"] = None
    print(session)
    loginSuccess = seleniumSesssion[session["user"]].webLogin()
    if loginSuccess:    
        jobs = seleniumSesssion[session["user"]].showJobs()
        print(f"Selenium Session@login2:{seleniumSesssion}")
        return render_template("submitHours.html",jobs = jobs,user =session["user"])
    session["errors"] = ["Wrong Password Please try again"]
    seleniumSesssion.pop(session["user"],None)
    session.pop('user', None)
    return redirect(url_for('home',errors=session["errors"]))
@app.route("/done", methods=['POST'])
def done():
    print(f"SeleniumSession@Done trying to submit{seleniumSesssion}")
    try:
        seleniumSesssion[session["user"]].selectJob(int(request.form['workplace'])+1)
    except KeyError:
        print("The user is no longer present")
        return redirect(url_for('home'))
    date = request.form["day"].split("-")
    dateP = datetime.date(int(date[0]),int(date[1]),int(date[2]))
    try:
        seleniumSesssion[session["user"]].selectMonth(dateP.month)
        seleniumSesssion[session["user"]].goToDay(dateP)
        seleniumSesssion[session["user"]].enterHours(request.form['hours'])
        seleniumSesssion[session["user"]].close()
        seleniumSesssion.pop(session["user"],None)
        session.pop('user', None)
        return redirect(url_for('home',messages="hours logged succesfully"))
    except:
        print("something went wrong")
        seleniumSesssion.pop(session["user"],None)
        return redirect(url_for('home',errors=['Did not find TimeSheet']))
