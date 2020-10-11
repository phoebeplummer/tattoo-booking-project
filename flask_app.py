#set up sql
import sqlite3
conn = sqlite3.connect("tattoo database 2.db")
cursor = conn.cursor()

#load flask framework
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('clientHome.html')

#booking request
@app.route('/bookingRequest', methods = ["GET", "POST"])
def makeBooking():
    if request.method == 'GET':
        return render_template('bookingForm.html')
    if request.method == 'POST':
        clientForm = []
        aFirstName = request.form['firstName']
        clientForm.append(aFirstName)
        aLastName = request.form['aLastName']
        clientForm.append(aLastName)
        aEmail = request.form["email"]
        clientForm.append(aEmail)
        aPhone = request.form["phone"]
        clientForm.append(aPhone)
        aArtist = request.form["artists"]
        clientForm.append(aArtist)
        aDescription = request.form["description"]
        clientForm.append(aDescription)
        aWidth = request.form["sizeWidth"]
        clientForm.append(aWidth)
        aLength = request.form["sizeLength"]
        clientForm.append(aLength)

#       area = aWidth*aLength
 #       sqlfind = " SELECT avgPrice FROM tblArtists where artistNumber = " + "'" + aArtist + "'"
#        rate = cursor.execute(sqlfind)
 #       estimate = area*rate
  #      clientForm.append(estimate)


        aMonth = request.form["month"]
        clientForm.append(aMonth)

#sql statement
        sql = """
        INSERT INTO tblClients (firstName, lastName, email, phoneNumber, artistNumber, description, sizeWidth, sizeLength, month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """

        try:
            cursor.execute(sql, clientForm)
            conn.commit()
            msg = "booking successfully requested"

        except sqlite3.Error:
            conn.rollback()
            msg = "the following error occured: ()".format(sqlite3.Error)

        finally:
            return render_template("result.html", msg=msg)
        
@app.route("/employeeLogin", methods = ["GET", "POST"])  
def employeeLogin():
    if request.method == 'GET':
        return render_template('employeeLogin.html')
    if request.method == 'POST':
        aUsername = request.form['username']
        aPassword = request.form['password']
        sql = "SELECT 'username' FROM 'tblLogin' WHERE 'username' = " + "'" + aUsername +  "'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if result == 0:
            msg = "username not recognised"
        else:
            sql = "SELECT password FROM tblLogin WHERE username = " + "'" + aUsername +  "'"
            cursor.execute(sql)
            userPassword = cursor.fetchall()
            if userPassword != aPassword:
                msg = "username and password do not match, please try again"
            else:
                msg = "you are successfully logged in"
                
    return render_template("result.html", msg=msg) 
            
          
       
