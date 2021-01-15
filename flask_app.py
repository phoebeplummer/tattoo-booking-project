import sqlite3
import hashlib, binascii, os
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('clientHome.html')

@app.route('/db')
def view():
    with sqlite3.connect('queen-bitch-db.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tblBookings")
        result = cursor.fetchall()
        return ','.join(map(str, result))

#booking request for new clients
@app.route('/booking-request', methods = ["GET", "POST"])
def requestBookingNew():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == 'GET':
       return render_template('bookingForm.html')
    if request.method == 'POST':
#add client details to tblClients
        clientDetails = []
        aFirstName = request.form['firstName']
        clientDetails.append(aFirstName)
        aSurname = request.form['surname']
        clientDetails.append(aSurname)
        aEmail = request.form["email"]
        clientDetails.append(aEmail)
        aPhone = request.form["phone"]
        clientDetails.append(aPhone)
        sqltblClients = "INSERT INTO tblClients (firstName, surname, email, phone) VALUES (?, ?, ?, ?)"
        cursor.execute(sqltblClients, clientDetails)
        conn.commit()

#add booking details to tblBookings
        bookingDetails = []
#first create unique bookingID
        aArtist = request.form["artists"]
        sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + aFirstName + "'" + "AND surname =" + "'" + aSurname + "'"
        cursor.execute(sqlClientNo)
        clientNo = (cursor.fetchone()[0])
        bookingId = aFirstName[0] + aSurname[0] + str(clientNo) + str(aArtist)
        sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
        cursor.execute(sqlCheckID)
        checkID = cursor.fetchall()
        while checkID != None:
            i = 1
            bookingId = bookingId + str(i)
            sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
            cursor.execute(sqlCheckID)
            checkID = cursor.fetchall()
            bookingDetails.append(bookingId)
            i = i + 1
#can then add rest of info from form
        bookingDetails.append(int(clientNo))
        bookingDetails.append(int(aArtist))
        aDescription = request.form['description']
        bookingDetails.append(aDescription)
        aPlacement = request.form['placement']
        bookingDetails.append(aPlacement)
        aWidth = request.form['sizeWidth']
        bookingDetails.append(aWidth)
        aLength = request.form['sizeLength']
        bookingDetails.append(aLength)
#work out estimate to add to tblBookings
        sqlAvgPrice = "SELECT avgPrice FROM tblArtists WHERE artistNumber =" + "'" + str(aArtist) + "'"
        cursor.execute(sqlAvgPrice)
        avgPrice = (cursor.fetchone()[0])
        estimate = float(aWidth) * float(aLength) * avgPrice
        estimate = round(estimate)
        bookingDetails.append(estimate)
#work out deposit to add to tblBookings
        if estimate<100:
            deposit = 20
        elif estimate>=100 and estimate<200:
            deposit = 50
        elif estimate>=200 and estimate<400:
            deposit = 100
        else:
            deposit = 150
        bookingDetails.append(deposit)
#work out sessionLength to add to tblBookings
        if (float(aWidth)*float(aLength))<300:
            sessionLength = "half day"
        else:
            sessionLength = "full day"
        bookingDetails.append(sessionLength)
        aMonth = request.form['months']
        bookingDetails.append(aMonth)
#add "N" to indicate estimate has not been received and booking has not been confirmed
        bookingDetails.append("N")
        bookingDetails.append("N")
#add details to tblBookings
        sqltblBookings = "INSERT INTO tblBookings (bookingID, clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit, sessionLength, desiredMonth, receivedEstimate, confirmedBooking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sqltblBookings, bookingDetails)
        conn.commit()
        msg = "Booking successfully requested"
        return render_template("/result.html", msg=msg)

#booking request for returning clients
@app.route('/booking-request-returning-client', methods = ["GET", "POST"])
def requestBookingReturning():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == 'GET':
       return render_template('bookingFormReturn.html')
    if request.method == 'POST':
#add booking details to tblBookings
        bookingDetails = []
#first create unique bookingID
        aFirstName = request.form['firstName']
        aSurname = request.form['surname']
        aArtist = request.form["artists"]
        sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + aFirstName + "'" + "AND surname =" + "'" + aSurname + "'"
        cursor.execute(sqlClientNo)
        clientNo = (cursor.fetchone()[0])
        bookingId = aFirstName[0] + aSurname[0] + str(clientNo) + str(aArtist)
        sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
        cursor.execute(sqlCheckID)
        checkID = cursor.fetchall()
        while checkID != None:
            i = 1
            bookingId = bookingId + str(i)
            sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
            cursor.execute(sqlCheckID)
            checkID = cursor.fetchall()
            bookingDetails.append(bookingId)
            i = i + 1
        bookingDetails.append(bookingId)
#can then add rest of info from form
        bookingDetails.append(int(clientNo))
        bookingDetails.append(int(aArtist))
        aDescription = request.form['description']
        bookingDetails.append(aDescription)
        aPlacement = request.form['placement']
        bookingDetails.append(aPlacement)
        aWidth = request.form['sizeWidth']
        bookingDetails.append(aWidth)
        aLength = request.form['sizeLength']
        bookingDetails.append(aLength)
#work out estimate to add to tblBookings
        sqlAvgPrice = "SELECT avgPrice FROM tblArtists WHERE artistNumber =" + "'" + str(aArtist) + "'"
        cursor.execute(sqlAvgPrice)
        avgPrice = (cursor.fetchone()[0])
        estimate = float(aWidth) * float(aLength) * avgPrice
        estimate = round(estimate)
        bookingDetails.append(estimate)
#work out deposit to add to tblBookings
        if estimate<100:
            deposit = 20
        elif estimate>=100 and estimate<200:
            deposit = 50
        elif estimate>=200 and estimate<400:
            deposit = 100
        else:
            deposit = 150
        bookingDetails.append(deposit)
#work out sessionLength to add to tblBookings
        if (float(aWidth)*float(aLength))<300:
            sessionLength = "half day"
        else:
            sessionLength = "full day"
        bookingDetails.append(sessionLength)
        aMonth = request.form['months']
        bookingDetails.append(aMonth)
#add "N" to indicate estimate has not been received and booking has not been confirmed
        bookingDetails.append("N")
        bookingDetails.append("N")
#add details to tblBookings
        sqltblBookings = "INSERT INTO tblBookings (bookingID, clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit, sessionLength, desiredMonth, receivedEstimate, confirmedBooking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sqltblBookings, bookingDetails)
        conn.commit()
        msg = "Booking successfully requested"
        return render_template("/result.html", msg=msg)


#function to verify client number in booking form
@app.route('/verifyClient')
def verifyClient():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    firstName = request.args.get('f', '')
    surname = request.args.get('s', '')
    sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + firstName + "'" + "AND surname =" + "'" + surname + "'"
    cursor.execute(sqlClientNo)
    clientNo = cursor.fetchone()
    if clientNo == None:
        return "Client not found in database. Please check you entered your name correctly or register as a new client."
    else:
        clientNo = str(clientNo[0])
        return "Please verify your unique clientNo is: "+ clientNo



#login to employee site
@app.route('/employee-login', methods =["GET", "POST"])
def employeeLogin():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template("employeeLogin.html")
    if request.method == "POST":
        aUsername = request.form['username']
        aPassword = request.form['password']
#fetch correct password from database
        cursor.execute("SELECT password FROM tblLogin WHERE username =" + "'" + aUsername + "'")
        correctPassword = cursor.fetchone()
#check username is in system
        if correctPassword == None:
            msg = "username not found in system"
            return render_template("/result.html", msg=msg)
#check given password matches hashed password in database
#first hash given password and remove salt from stored hashed password
        else:
            correctPassword = str(correctPassword[0])
            salt = correctPassword[:64]
            correctPassword = correctPassword[64:]
            pwdHash = hashlib.pbkdf2_hmac('sha512', str(aPassword).encode('utf-8'), str(salt).encode('ascii'), 100000)
            pwdHash = binascii.hexlify(pwdHash).decode('ascii')
#check passwords match
            if pwdHash == correctPassword:
                return render_template("/employeeHome.html")
            else:
                msg = 'username and password do not match'
                return render_template("/result.html", msg=msg)




#add new employee login
@app.route('/new-employee', methods=["GET", "POST"])
def addEmployee():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template("addEmployee.html")
    if request.method == "POST":
        aUsername = request.form["username"]
        aPassword1 = request.form["password1"]
        aPassword2 = request.form["password2"]
#verify passwords match
        if aPassword1 != aPassword2:
            msg = "Passwords do not match"
            return render_template("/result.html", msg=msg)
#check username is not already in system
        cursor.execute("SELECT * FROM tblLogin WHERE username =" + "'" + aUsername + "'")
        rows = cursor.fetchall()
        if len(rows) > 0:
            msg = "Username already in system"
            return render_template("/result.html", msg=msg)
#hash password before storing in database
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdHash = hashlib.pbkdf2_hmac('sha512', aPassword1.encode('utf-8'), salt, 100000)
        pwdHash = binascii.hexlify(pwdHash)
        hashedPwd = (salt + pwdHash).decode('ascii')
#add new login to database tblLogin
        newLogin = []
        newLogin.append(aUsername)
        newLogin.append(hashedPwd)
        sqlAddLogin = "INSERT INTO tblLogin (username, password) VALUES (?, ?)"
        cursor.execute(sqlAddLogin, newLogin)
        conn.commit()
        msg = "New login successfully added"
        return render_template("/result.html", msg=msg)

#add confirmed booking
@app.route('/add-booking', methods =["GET", "POST"])
def addBooking():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template('addBooking.html')
    if request.method == "POST":
        anID = request.form["bookingID"]
#update database with confirmed booking details
        booking = []
        booking.append("Y")
        aDay = request.form["day"]
        booking.append(aDay)
        aMonth = request.form["month"]
        booking.append(aMonth)
        aTime = request.form["sessionTime"]
        booking.append(aTime)
        sqlConfirmed = "UPDATE tblBookings SET confirmedBooking = ? ,bookedDay = ?,bookedMonth = ? ,bookedTime = ? WHERE bookingID =" + "'" + anID + "'"
        cursor.execute(sqlConfirmed, booking)
        conn.commit()
        msg = "Booking confirmed"
        return render_template("/result.html", msg=msg)



#edit booking details
@app.route('/edit-booking', methods = ["GET", "POST"])
def editBooking():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template('editBooking.html')
    if request.method == "POST":
        anID = request.form["bookingID"]
        aField = request.form["field"]
        aNew = request.form["new"]
#arrays to determine whether field to be editted is in tblBookings or tblClients
        clientDetails = ["phone", "email"]
        bookingDetails = ["description", "placement", "sizeWidth", "sizeLength"]
#update field in tblClients
        if aField in clientDetails:
 #fetch client number from database
            aFirstName = request.form["firstName"]
            aSurname = request.form["surname"]
            sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + aFirstName + "'" + "AND surname =" + "'" + aSurname + "'"
            cursor.execute(sqlClientNo)
            clientNo = cursor.fetchone()
            clientNo = clientNo[0]
            sqlUpdate = "UPDATE tblClients SET " + aField + "=" + "'" + aNew + "'" + " WHERE clientNumber =" + "'" + str(clientNo) + "'"
            cursor.execute(sqlUpdate)
            conn.commit()
            msg = "Client details updated"
        elif aField in bookingDetails:
            sqlUpdate = "UPDATE tblBookings SET " + aField + "=" + "'" + aNew + "'" + " WHERE bookingID =" + "'" + anID + "'"
            cursor.execute(sqlUpdate)
            conn.commit()
            msg = "Booking details updated"
        return render_template("/result.html", msg=msg)


@app.route('/findClient')
def findClient():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#array of artist names
    artists = ["Lana Fern", "Peggy Brown", "Jodie Ahnien", "El Rose"]
    bookingInfo = ""
#fetch name from form
    firstName = request.args.get('f', '')
    surname = request.args.get('s', '')
#find client number
    sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + firstName + "'" + "AND surname =" + "'" + surname + "'"
    cursor.execute(sqlClientNo)
    clientNo = cursor.fetchone()
#if client is not in database
    if clientNo == None:
        return "Client not found in system"
#find booking number
    sqlFindBooking = "SELECT bookingID, artistNumber FROM tblBookings WHERE clientNumber = " + str(clientNo[0])
    cursor.execute(sqlFindBooking)
    bookings = cursor.fetchall()
    for row in bookings:
        bookingInfo = bookingInfo + "Client name: "+firstName+" "+surname+" Booking ID: "+row[0]+" Artist: "+artists[row[1]-1] + "<br>"
    return bookingInfo



#delete existing booking
@app.route("/delete-booking", methods=["GET", "POST"])
def deleteBooking():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#connect to html page
    if request.method == "GET":
        return render_template('deleteBooking.html')
    if request.method == "POST":
        anID = request.form["bookingID"]
        sqlDelete = "DELETE FROM tblBookings WHERE clientNumber =" + "'" + anID + "'"
        cursor.execute(sqlDelete)
        conn.commit()
        msg = "Booking deleted"
        return render_template("/result.html", msg=msg)


#outstanding estimates
@app.route('/outstanding-estimates')
def printOutstandingEstimates():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    sqlList = "SELECT bookingID FROM tblBookings WHERE receivedEstimate = 'N'"
    cursor.execute(sqlList)
    clients = cursor.fetchall()
    return render_template('outstandingEstimates.html', rows=clients)
