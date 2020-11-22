import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def start():
    return render_template('clientHome.html')

@app.route('/db')
def view():
    with sqlite3.connect('queen-bitch-db.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tblLogin")
        result = cursor.fetchall()
        return ','.join(map(str, result))

#booking request
@app.route('/booking-request', methods = ["GET", "POST"])
def makeBooking():
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
        sqlClientNo = "SELECT clientNumber FROM tblClients WHERE email =" + "'" + aEmail + "'"
        cursor.execute(sqlClientNo)
        clientNo = (cursor.fetchone()[0])
        clientNo = clientNo + 1
        clientNo = str(clientNo)
        artistNo = str(aArtist)
        letter1 = aFirstName[0]
        letter2 = aSurname[0]
        bookingId = letter1 + letter2 + clientNo + artistNo
        bookingDetails.append(bookingId)
#can then add rest of info from form
        clientNo = int(clientNo)
        bookingDetails.append(clientNo)
        artistNo = int(artistNo)
        bookingDetails.append(artistNo)
        aDescription = request.form['description']
        bookingDetails.append(aDescription)
        aPlacement = request.form['placement']
        bookingDetails.append(aPlacement)
        aWidth = request.form['sizeWidth']
        bookingDetails.append(aWidth)
        aLength = request.form['sizeLength']
        bookingDetails.append(aLength)
#work out estimate to add to tblBookings
        sqlAvgPrice = "SELECT avgPrice FROM tblArtists WHERE artistNumber =" + "'" + str(artistNo) + "'"
        cursor.execute(sqlAvgPrice)
        avgPrice = (cursor.fetchone()[0])
        estimate = int(aWidth) * int(aLength) * avgPrice
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
        if (int(aWidth)*int(aLength))<300:
            sessionLength = "half day"
        else:
            sessionLength = "full day"
        bookingDetails.append(sessionLength)
        aMonth = request.form['months']
        bookingDetails.append(aMonth)
#add "N" to indicate estimate has not been received and booking has not been confirmed
        bookingDetails.append("N")
        bookingDetails.append("N")
        sqltblBookings = "INSERT INTO tblBookings (bookingID, clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit, sessionLength, desiredMonth, receivedEstimate, confirmedBooking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sqltblBookings, bookingDetails)
        conn.commit()
        return "booking successfully requested"

@app.route('/employee-login', methods =["GET", "POST"])
def employeeLogin():
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template("employeeLogin.html")
    if request.method == "POST":
        aUsername = request.form['username']
        aPassword = request.form['password']
        cursor.execute("SELECT password FROM tblLogin WHERE username =" + "'" + aUsername + "'")
        correctPassword = cursor.fetchone()
        if correctPassword == None:
            return "username not found in system"
        elif aPassword != correctPassword[0]:
            return 'username and password do not match'
        else:
            return render_template("/employeeHome.html")

@app.route('/new-employee', methods=["GET", "POST"])
def addEmployee():
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template("addEmployee.html")
    if request.method == "POST":
        aUsername = request.form["username"]
        aPassword1 = request.form["password1"]
        aPassword2 = request.form["password2"]
        if aPassword1 != aPassword2:
            return "passwords do not match"
        cursor.execute("SELECT * FROM tblLogin WHERE username =" + "'" + aUsername + "'")
        rows = cursor.fetchall()
        if len(rows) > 0:
            return "username already in system"
        newLogin = []
        newLogin.append(aUsername)
        newLogin.append(aPassword1)
        sqlAddLogin = "INSERT INTO tblLogin (username, password) VALUES (?, ?)"
        cursor.execute(sqlAddLogin, newLogin)
        conn.commit()
        return "new login added"

#add confirmed booking
@app.route('/add-booking', methods =["GET", "POST"])
def addBooking():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template('addBooking.html')
    if request.method == "POST":
        aFirstName = request.form["firstName"]
        aSurname = request.form["surname"]
 #fetch client number and check client is in database
        sqlCheck = "SELECT clientNumber FROM tblClients WHERE firstName =" + "'" + aFirstName + "'" + "AND surname =" + "'" + aSurname + "'"
        cursor.execute(sqlCheck)
        clientNo = cursor.fetchone()
        if clientNo == None:
            return "client not found in system"
#update database with confirmed booking details
        booking = []
        booking.append("Y")
        aDay = request.form["day"]
        booking.append(aDay)
        aMonth = request.form["month"]
        booking.append(aMonth)
        aTime = request.form["sessionTime"]
        booking.append(aTime)
        clientNo = clientNo[0] + 1
        sqlConfirmed = "UPDATE tblBookings SET confirmedBooking = ? ,bookedDay = ?,bookedMonth = ? ,bookedTime = ? WHERE clientNumber =" + "'" + str(clientNo) + "'"
        cursor.execute(sqlConfirmed, booking)
        conn.commit()
        return "booking confirmed"
