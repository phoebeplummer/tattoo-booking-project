import sqlite3
import hashlib, binascii, os
from flask import Flask, request, render_template
import datetime

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

@app.route('/addCol')
def delete():
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblBookings WHERE clientNumber = 234")
    conn.commit()
    cursor.execute("SELECT * FROM tblBookings")
    result = cursor.fetchall()
    return ','.join(map(str, result))

@app.route('/index')
def index():
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX 'name' ON tblClients (firstName, surname)")
    conn.commit()
    cursor.execute("CREATE UNIQUE INDEX 'bookingID' ON tblBookings (bookingID)")
    conn.commit()
    return "completed"

#booking request for new clients
@app.route('/booking-request', methods = ["GET", "POST"])
def requestBookingNew():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == 'GET':
       return render_template('bookingForm.html')
    if request.method == 'POST':
#fetch from form and add client details to tblClients
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
        bookingId = aFirstName[0] + aSurname[0] + str(clientNo) + str(aArtist)
#check that ID is not already in database
        sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
        cursor.execute(sqlCheckID)
        checkID = cursor.fetchall()
#change booking ID until it is unique
        i = 1
        while len(checkID) != 0:
            bookingId = bookingId + str(i)
            sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
            cursor.execute(sqlCheckID)
            checkID = cursor.fetchall()
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
        if estimate <20:
            deposit = 0
        elif estimate<100:
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
#find year that client is requesting to book for
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        date = str(datetime.datetime.now())
        currentMonth = date[5] + date[6]
        currentMonth = int(currentMonth)
        monthNum = months.index(aMonth) + 1
#if month has already passed in 2021
        if currentMonth > monthNum:
            desiredYear = 2022
#if month is still to come in 2021
        else:
            desiredYear = 2021
        bookingDetails.append(desiredYear)
#add details to tblBookings
        sqltblBookings = "INSERT INTO tblBookings (bookingID, clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit, sessionLength, desiredMonth, receivedEstimate, confirmedBooking, desiredYear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            cursor.execute(sqltblBookings, bookingDetails)
            conn.commit()
            msg = "Booking successfully requested"
        except sqlite3.Error:
            conn.rollback()
            msg = 'the following error occured: ()'.format(sqlite3.Error)

        finally:
            return render_template("/requestResult.html", msg=msg)


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
#check booking ID is not already in databse
        sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
        cursor.execute(sqlCheckID)
        checkID = cursor.fetchall()
#change booking ID until it is unique
        i = 1
        while len(checkID) != 0:
            bookingId = bookingId + str(i)
            sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
            cursor.execute(sqlCheckID)
            checkID = cursor.fetchall()
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
        estimate = float(aWidth) * float(aLength) * int(avgPrice)
        estimate = round(estimate)
        bookingDetails.append(estimate)
#work out deposit to add to tblBookings
        if estimate <20:
            deposit = 0
        elif estimate<100:
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
#find year that client is requesting to book for
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        date = str(datetime.datetime.now())
        currentMonth = date[5] + date[6]
        currentMonth = int(currentMonth)
        monthNum = months.index(aMonth) + 1
#if month has already passed in 2021
        if currentMonth > monthNum:
            desiredYear = 2022
#if month is still to come in 2021
        else:
            desiredYear = 2021
        bookingDetails.append(str(desiredYear))
#add details to tblBookings
        sqltblBookings = "INSERT INTO tblBookings (bookingID, clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit, sessionLength, desiredMonth, receivedEstimate, confirmedBooking, desiredYear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sqltblBookings, bookingDetails)
        conn.commit()
        msg = "Booking successfully requested"
        return render_template("/requestResult.html", msg=msg)


#function to verify client number in booking form
@app.route('/verifyClient')
def verifyClient():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#fetch client name from html page
    firstName = request.args.get('f', '')
    surname = request.args.get('s', '')
#fetch client number from database
    sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName LIKE" + "'%" + firstName + "%'" + "AND surname LIKE" + "'%" + surname + "%'"
    cursor.execute(sqlClientNo)
    clientNo = cursor.fetchone()
#output verification
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
#fetch username and password from html page
        aUsername = request.form['username']
        aPassword = request.form['password']
#fetch correct password from database
        cursor.execute("SELECT password FROM tblLogin WHERE username =" + "'" + aUsername + "'")
        correctPassword = cursor.fetchone()
#check username is in system
        if correctPassword == None:
            msg = "Unable to login: username not found in system"
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
                msg = 'Unable to login: username and password do not match'
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
#fetch username and password from html page
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

#check username and password are valid for add new employee
@app.route('/checkPsw')
def checkPsw():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#initialise arrays and variables
    lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    uppercase = ['A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
    'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    specialChars = ['!', '@', '€', '£', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '=',
    '[', ']', '{', '}', ';', ':', '"', "'", '|', '<', ',', '.', '>', '?', '/']
    lower = False
    upper = False
    num = False
    special = False
    msg = ''
#fetch passwords and username from form
    password1 = request.args.get('a', '')
    password2 = request.args.get('b', '')
    username = request.args.get('c', '')
#check username is not already in system
    cursor.execute("SELECT * FROM tblLogin WHERE username =" + "'" + username + "'")
    rows = cursor.fetchall()
    if len(rows) > 0:
        msg = "Username already in system"
#verify passwords match
    elif password1 != password2:
        msg = "Passwords do not match"
#verify password meets all requirements
    else:
        for i in password1:
            if i in lowercase:
                lower = True
            elif i in uppercase:
                upper = True
            elif i in numbers:
                num = True
            elif i in specialChars:
                special = True
        if lower == False or upper == False or num == False or special == False:
            msg = "Password does not meet entry requirements"
    return msg

#add confirmed booking
@app.route('/add-booking', methods =["GET", "POST"])
def addBooking():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    if request.method == "GET":
        return render_template('addBooking.html')
    if request.method == "POST":
#fetch booking ID from tblBookings
        anID = request.form["bookingID"]
#fetch booking date from form and add to array
        booking = []
        booking.append("Y")
        aDay = request.form["day"]
        booking.append(aDay)
        aMonth = request.form["month"]
        booking.append(aMonth)
        aYear = request.form["year"]
        booking.append(aYear)
        aTime = request.form["sessionTime"]
        booking.append(aTime)
#fetch artist number from tblBookings
        sqlFindArtist = "SELECT artistNumber FROM tblBookings where bookingID =" + "'" + anID + "'"
        cursor.execute(sqlFindArtist)
        artistNo = (cursor.fetchone()[0])
#search to find if booking date is already taken
        sqlSearchDate = "SELECT * FROM tblBookings WHERE bookedDay = " + "'" + aDay + "' AND bookedMonth = " + "'" + aMonth + """'
        AND bookedTime = """ + "'" + aTime + "' AND bookedYear = " + "'" + str(aYear) + "' AND artistNumber = " + "'" + str(artistNo) + "'"
        cursor.execute(sqlSearchDate)
        result = cursor.fetchall()
#return message if booking date is taken
        if len(result) != 0:
            msg = "Booking date already taken"
            return render_template("/result.html", msg=msg)
#if booking date is free update tblBookings
        sqlConfirmed = "UPDATE tblBookings SET confirmedBooking = ? ,bookedDay = ?,bookedMonth = ? , bookedYear = ?, bookedTime = ? WHERE bookingID =" + "'" + anID + "'"
        cursor.execute(sqlConfirmed, booking)
        conn.commit()
#return success message
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


#if field editted is length or width must calculate new estimate, deposit and session length
            if aField == "sizeWidth" or aField == "sizeLength":
#set values for length and width if new field is width
                if aField == "sizeWidth":
                    sqlGetLength = "SELECT sizeLength, artistNumber FROM tblBookings WHERE bookingID =" + "'" + anID + "'"
                    cursor.execute(sqlGetLength)
                    calcInfo = cursor.fetchall()
                    length = calcInfo[0][0]
                    width = aNew
                    artistNo = calcInfo[0][1]
#set values for length and width if new field is length
                elif aField == "sizeLength":
                    sqlGetWidth = "SELECT sizeWidth, artistNumber FROM tblBookings WHERE bookingID =" + "'" + anID + "'"
                    cursor.execute(sqlGetWidth)
                    calcInfo = cursor.fetchall()
                    width = calcInfo[0][0]
                    length = aNew
                    artistNo = calcInfo[0][1]
#work out new estimate
                sqlAvgPrice = "SELECT avgPrice FROM tblArtists WHERE artistNumber =" + "'" + str(artistNo) + "'"
                cursor.execute(sqlAvgPrice)
                avgPrice = (cursor.fetchone()[0])
                estimate = float(width) * float(length) * avgPrice
                estimate = round(estimate)
#work out new deposit
                if estimate <20:
                    deposit = 0
                elif estimate<100:
                    deposit = 20
                elif estimate>=100 and estimate<200:
                    deposit = 50
                elif estimate>=200 and estimate<400:
                    deposit = 100
                else:
                    deposit = 150
#work out new sessionLength
                if (float(width)*float(length))<300:
                    sessionLength = "half day"
                else:
                    sessionLength = "full day"
#add new calculated values to tblBookings
                sqlUpdateCalc = "UPDATE tblBookings SET estimate = " + "'" + str(estimate) + "', deposit = " + "'" + str(deposit) + """'
                , sessionLength = """ + "'" + sessionLength + "' WHERE bookingID =" + "'" + anID + "'"
                cursor.execute(sqlUpdateCalc)
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
    sqlClientNo = "SELECT clientNumber FROM tblClients WHERE firstName LIKE" + "'%" + firstName + "%'" + "AND surname LIKE" + "'%" + surname + "%'"
    cursor.execute(sqlClientNo)
    clientNo = cursor.fetchone()
#if client is not in database
    if clientNo == None:
        return "Client not found in system"
#find booking number
    sqlFindBooking = "SELECT bookingID, artistNumber FROM tblBookings WHERE clientNumber = " + str(clientNo[0])
    cursor.execute(sqlFindBooking)
    bookings = cursor.fetchall()
#if client has no bookings
    if len(bookings) == 0:
        return "No bookings found for client in system"
#output check
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

#delete existing booking
@app.route("/change-date", methods=["GET", "POST"])
def changeDate():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#connect to html page
    if request.method == "GET":
        return render_template('changeDate.html')
    if request.method == "POST":
#fetch booking ID from form
        anID = request.form["bookingID"]
#fetch new date from form
        aDay = request.form["day"]
        aMonth = request.form["month"]
        aYear = request.form["year"]
        aTime = request.form["sessionTime"]
#fetch artist number from tblBookings
        sqlFindArtist = "SELECT artistNumber FROM tblBookings where bookingID =" + "'" + anID + "'"
        cursor.execute(sqlFindArtist)
        artistNo = (cursor.fetchone()[0])
#search to find if booking date is already taken
        sqlSearchDate = "SELECT * FROM tblBookings WHERE bookedDay = " + "'" + aDay + "' AND bookedMonth = " + "'" + aMonth + """'
        AND bookedTime = """ + "'" + aTime + "' AND bookedYear = " + "'" + str(aYear) + "' AND artistNumber = " + "'" + str(artistNo) + "'"
        cursor.execute(sqlSearchDate)
        result = cursor.fetchall()
#return message if booking date is taken
        if len(result) != 0:
            msg = "Booking date already taken"
            return render_template("/result.html", msg=msg)
#if bookig date is free update tblBookings
        sqlNewDate = """UPDATE tblBookings SET bookedDay = """ + "'" + aDay + "', bookedMonth = " + "'" + aMonth + """'
        ,bookedTime = """ + "'" + aTime + "', bookedYear =" + "'" + aYear + "' WHERE bookingID =" + "'" + anID + "'"
        cursor.execute(sqlNewDate)
        conn.commit()
#return success message
        msg = "Booking date updated"
        return render_template("/result.html", msg=msg)


#outstanding estimates
@app.route('/outstanding-estimates')
def printOutstandingEstimates():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#select all booking IDs of bookings which have not recieved an estimate
    sqlList = "SELECT bookingID FROM tblBookings WHERE receivedEstimate = 'N'"
    cursor.execute(sqlList)
    clients = cursor.fetchall()
#return booking IDs to html page
    return render_template('outstandingEstimates.html', rows=clients)


@app.route('/findEstimateInfo')
def findEstimateInfo():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#get bookingID from html page
    bookingID = request.args.get('b', '')
#initialise arrays
    optionalTimes = []
    dayOption = ""
#create arrays of days within month it is not possible to book in i.e. sundays and bank holidays
    janNo = [1, 3, 10, 17, 24, 31]
    febNo = [7, 14, 21, 28, 29, 30, 31]
    marNo = [7, 14, 21, 28]
    aprNo = [2, 4, 5, 11, 18, 25, 31]
    mayNo = [2, 3, 9, 16, 23, 30, 31]
    junNo = [6, 13, 20, 27, 31]
    julNo = [4, 11, 18, 25]
    augNo = [1, 8, 15, 22, 29, 30]
    sepNo = [5, 12, 9, 26, 31]
    octNo = [3, 10, 17, 24, 31]
    novNo = [7, 14, 21, 28, 31]
    decNo = [5, 12, 19, 25, 26, 27, 28, 31]
#get client number from database
    sqlClientNo = "SELECT clientNumber FROM tblBookings WHERE bookingID =" + "'" + bookingID + "'"
    cursor.execute(sqlClientNo)
    clientNo = cursor.fetchone()
    clientNo = str(clientNo[0])
#get booking details from database
    sqlBookingDetails = """SELECT artistNumber, estimate, deposit, sessionLength, desiredMonth, desiredYear FROM tblBookings
    WHERE bookingID = """ + "'" + bookingID + "'"
    cursor.execute(sqlBookingDetails)
    bookingDetails = cursor.fetchall()
    artistNo = str(bookingDetails[0][0])
    estimate = str(bookingDetails[0][1])
    deposit = str(bookingDetails[0][2])
    sessionLen = bookingDetails[0][3]
    month = bookingDetails[0][4]
    year = str(bookingDetails[0][5])
#find days in month artist has booking
#if desired month is january
    if month == "january":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + """
            AND bookedMonth = """ + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in janNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is february
    elif month == "february":
        for idx in range (1, 29):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + """
            AND bookedYear = """ + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in febNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is march
    elif month == "march":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in marNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is april
    elif month == "april":
        for idx in range (1, 31):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in aprNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is may
    elif month == "may":
        for idx in range (1, 29):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in mayNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is june
    elif month == "june":
        for idx in range (1, 31):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in junNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is july
    elif month == "july":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in julNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is august
    elif month == "august":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in augNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is september
    elif month == "september":
        for idx in range (1, 31):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in sepNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is october
    elif month == "october":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in octNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is november
    elif month == "november":
        for idx in range (1, 31):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in novNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#if desired month is december
    elif month == "december":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedYear = " + "'" + year + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
            cursor.execute(sqlTakenTimes)
            takenTimes = cursor.fetchall()
#ignore days it is not possible to book
            if idx in decNo:
                dayOption = "none"
#if there are no bookings that day
            elif len(takenTimes) == 0:
                dayOption= str(idx) + ": all day"
                optionalTimes.append(dayOption)
#if half day session is possible
            elif len(takenTimes[0]) == 1 and sessionLen == "half day":
                if takenTimes[0][0] == "morning":
                    dayOption= str(idx) + ": afternoon"
                    optionalTimes.append(dayOption)
                elif takenTimes[0][0] == "afternoon":
                    dayOption= str(idx) + ": morning"
                    optionalTimes.append(dayOption)
#get client details from database
    sqlClientDetails = "SELECT firstName, surname, email FROM tblClients WHERE clientNumber = " + "'" + str(clientNo) + "'"
    cursor.execute(sqlClientDetails)
    clientDetails = cursor.fetchall()
    firstName = clientDetails[0][0]
    surname = clientDetails[0][1]
    email = clientDetails[0][2]
#create string of estimate details to be sent back to html page
    output = "<b>Name:</b> " + firstName + " " + surname + "<br><b>Client Number:</b> "+ str(clientNo) + """
    <br><b> Email: </b>""" + email + "<br><b> Estimate:</b> £""" + estimate + """
    <br><b> Deposit:</b> £""" + deposit + "<br><b> Session length:</b> " + sessionLen + "<br><b> Month:</b> " + month + """
    <br><b>Year:</b> """ + year + " <br><b> Optional days and times:</b> <br>""" + '<br>'.join(map(str, optionalTimes))
#return output to html page
    return output

@app.route('/estimateSent')
def estimateSent():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#get bookingID from html page
    bookingID = request.args.get('b', '')
#update received estimate to Y in database
    sqlSent = "UPDATE tblBookings SET receivedEstimate = 'Y' WHERE bookingID =" + "'" + bookingID + "'"
    cursor.execute(sqlSent)
    conn.commit()
#return message to html page to confirm database has been changed
    return "Estimate sent to client"

@app.route('/artist-calendars', methods=["GET", "POST"])
def getCalendar():
    if request.method == "GET":
        return render_template('calendar.html')
    if request.method == "POST":
#fetch artist + month from form
        global artistNum
        artistNum = int(request.form["artists"])
        global calMonth
        calMonth = request.form["months"]
        global calYear
        calYear = request.form["year"]
#initialise array of artist names
        artists = ["Lana Fern", "Peggy Brown", "Jodie Ahnien", "El Rose"]
        artistName = artists[(artistNum-1)]
#find number of days in month and shift
        thirtyDays = ["april", "june", "september", "november"]
        if calMonth in thirtyDays:
            days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
            if calMonth == 'april':
                shift = ['', '', '']
            elif calMonth == 'june':
                shift = ['']
            elif calMonth == 'september':
                shift = ['', '']
            else:
                shift = []
        elif calMonth == 'february':
            days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
            shift = []
        else:
            days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
            if calMonth == 'january':
                shift = ['', '', '', '']
            elif calMonth == 'march':
                shift = []
            elif calMonth == 'may':
                shift = ['', '', '', '', '']
            elif calMonth == 'july':
                shift = ['', '', '']
            elif calMonth == 'august':
                shift = ['', '', '', '', '', '']
            elif calMonth == 'october':
                shift = ['', '', '', '']
            else:
                shift = ['', '']
        if calYear == '2022':
            shift.append(' ')
        return render_template("/viewCalendar.html", artist=artistName, month=calMonth, year=calYear, days=days, shift=shift )

@app.route('/findBookings')
def findBookings():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#get variables from html page
    day = request.args.get('d', '')
#get booking data from database
    sqlBookings = "SELECT bookingID, clientNumber, bookedTime FROM tblBookings WHERE artistNumber = " + "'" + str(artistNum) + "'" + """ AND
    bookedMonth = """ + "'" + calMonth + "'" + "AND bookedDay = " + "'" + str(day) + "' AND bookedYear =" + "'" + calYear + "'"
    cursor.execute(sqlBookings)
    bookings = cursor.fetchall()
#if there are no bookings that day
    if len(bookings) == 0:
        calendar = "<h4>Morning:</h4> No bookings <br> <h4>Afternoon:</h4> No bookings"
#if there is one booking that day
    elif len(bookings) == 1:
#fetch client name from database
        clientNo1 = bookings[0][1]
        sqlName1 = "SELECT firstName, surname FROM tblClients WHERE clientNumber = " + "'" + str(clientNo1) + "'"
        cursor.execute(sqlName1)
        name1 = cursor.fetchall()
#if booking is in the morning
        if bookings[0][2] == 'morning':
            calendar = "<h4>Morning:</h4><b>Client:</b> " + str(name1[0][0]) + " " + str(name1[0][1]) + """
            <b> Booking ID:</b> """ + str(bookings[0][0]) + """
            <br><h4>Afternoon:</h4> No bookings"""
#if booking is in the afternoon
        elif bookings[0][2] == 'afternoon':
            calendar = "<h4>Morning:</h4> No bookings <br><h4>Afternoon:</h4><b>Client:</b> " + str(name1[0][0]) + " " + str(name1[0][1]) + """
            <b> Booking ID:</b> """ + str(bookings[0][0])
#if booking is full day
        else:
            calendar = "<h4>Morning:</h4><b>Client:</b> " + str(name1[0][0]) + " " + str(name1[0][1]) +  """
            <b> Booking ID:</b> """ + str(bookings[0][0]) + """
            <br><h4>Afternoon:</h4><b>Client:</b> """ + str(name1[0][0]) + " " + str(name1[0][1]) + """
            <b> Booking ID:</b> """ + str(bookings[0][0])
#if there are 2 bookings that day
    else:
#fetch client name from database
        clientNo1 = bookings[0][1]
        sqlName1 = "SELECT firstName, surname FROM tblClients WHERE clientNumber = " + "'" + str(clientNo1) + "'"
        cursor.execute(sqlName1)
        name1 = cursor.fetchall()
        clientNo2 = bookings[1][1]
        sqlName2 = "SELECT firstName, surname FROM tblClients WHERE clientNumber = " + "'" + str(clientNo2) + "'"
        cursor.execute(sqlName2)
        name2 = cursor.fetchall()
#if booking 1 is in the morning
        if bookings[0][2] == 'morning':
            calendar = "<h4>Morning:</h4><b>Client:</b> " + str(name1[0][0]) + " " + str(name1[0][1]) + """
            <b>  Booking ID:</b> """ + str(bookings[0][0]) + """
            <br><h4>Afternoon:</h4><b>Client:</b> """ + str(name2[0][0]) + " " + str(name2[0][1]) + """
            <b>  Booking ID:</b> """ + str(bookings[1][0])
#if booking 1 is in the afternoon
        elif bookings[0][2] == 'afternoon':
            calendar = "<h4>Morning:</h4><b>Client:</b> " + str(name2[0][0]) + " " + str(name2[0][1]) + """
            <b> Booking ID:</b> """ + str(bookings[1][0]) + """
            <br><h4>Afternoon:</h4><b>Client:</b> """ + str(name1[0][0]) + " " + str(name1[0][1]) + """
            <b> Booking ID:</b> """ + str(bookings[0][0])
#return day's calendar
    return calendar

@app.route('/client-directory')
def clientDirectory():
    return render_template("/clientDirectory.html")

#AJAX FOR CLIENT DETAILS CLIENT DIRECTORY
@app.route('/clientDetails')
def clientDetails():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
#get variables from html page
    firstName = request.args.get('f', '')
    surname = request.args.get('s', '')
#fetch client data from database
    sqlClientDeets = "SELECT clientNumber, email, phone FROM tblClients WHERE firstName LIKE '%" + firstName + """%'
    AND surname LIKE '%""" + surname + "%'"
    cursor.execute(sqlClientDeets)
    clientDeets = cursor.fetchall()
#if client is not in system
    if len(clientDeets) == 0:
        return("Client not found in system")
    clientNo = str(clientDeets[0][0])
#find client bookings
    sqlClientBookings = "SELECT bookingID FROM tblBookings WHERE clientNumber ='" + clientNo + "'"
    cursor.execute(sqlClientBookings)
    clientBookings = cursor.fetchall()
#concatonate bookings into one string
    bookings = ''
    for i in range (len(clientBookings)):
        bookings = bookings + str(clientBookings[0][i])
#only add comma if it will be followed by another booking
        if i != (len(clientBookings)-1):
            bookings = bookings + ", "
#concatonate output into one string and return
    clientDetails = "<b>Name:</b> " + firstName + " " + surname + "<br><b>Client Number:</b> "+ str(clientNo) + """
    <br><b> Email: </b>""" + clientDeets[0][1] + "<br><b>Phone:</b> " + clientDeets[0][2] + "<br><b>Bookings: </b>" + bookings
    return clientDetails

#AJAX FOR BOOKING DETAILS CLIENT DIRECTORY
@app.route('/bookingDetails')
def bookingDetails():
#connect to database
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()

#get variables from html page
    bookingID = request.args.get('b', '')
#fetch booking details from database
    sqlBookingDeets = """SELECT clientNumber, artistNumber, description, placement, sizeWidth, sizeLength, estimate, deposit,
    sessionLength, desiredMonth, desiredYear, receivedEstimate, confirmedBooking, bookedDay, bookedMonth, bookedYear, bookedTime
    FROM tblBookings WHERE bookingID = '""" + bookingID + "'"
    cursor.execute(sqlBookingDeets)
    bookingDeets = cursor.fetchall()
    if len(bookingDeets) == 0:
        return ("Booking not found in system")
    clientNo = str(bookingDeets[0][0])
    artistNo = str(bookingDeets[0][1])
#fetch client name from tblClients
    sqlClientName = "SELECT firstName, surname FROM tblClients WHERE clientNumber = '" + clientNo + "'"
    cursor.execute(sqlClientName)
    name = cursor.fetchall()
#fetch artist name from tblArtist
    sqlArtistName = "SELECT artistName FROM tblArtists WHERE artistNumber = '" + artistNo + "'"
    cursor.execute(sqlArtistName)
    artist = cursor.fetchone()[0]
#if booking date has been confirmed
    if bookingDeets[0][12] == "Y":
        bookingDetails = "<b>Booking ID:</b> " + bookingID + "<br><b>Client Name:</b> " + name[0][0] + " " + name[0][1] + """
        <br><b>Artist:</b> """ + artist + "<br><b>Description:</b> " + bookingDeets[0][2] + "<br><b>Placement: </b> " + bookingDeets[0][3] + """
        <br><b>Width:</b> """ + str(bookingDeets[0][4]) + "<br><b>Length:</b> " + str(bookingDeets[0][5]) + """
        <br><b>Estimate:</b> """ + str(bookingDeets[0][6]) + "<br><b>Deposit:</b> " + str(bookingDeets[0][7]) + """
        <br><b>Session Length:</b> """ + bookingDeets[0][8] + "<br><b>Desired Month:</b> " + bookingDeets[0][9] + """
        <br><b>Desired Year:</b> """ +  str(bookingDeets[0][10]) + "<br><b>Received Estimate:</b> " + bookingDeets[0][11] + """
        <br><b>Confirmed booking:</b> """ + bookingDeets[0][12] + "<br><b>Booked day:</b> " + str(bookingDeets[0][13]) + """
        <br><b>Booked Month:</b> """ + bookingDeets[0][14] + "<br><b>Booked Year:</b> " + str(bookingDeets[0][15]) + """
        <br><b>Booked Time:</b> """ + bookingDeets[0][16]
#if no booking date has been confirmed
    else:
        bookingDetails = "<b>Booking ID:</b> " + bookingID + "<br><b>Client Name:</b> " + name[0][0] + " " + name[0][1] + """
        <br><b>Artist:</b> """ + artist + "<br><b>Description:</b> " + bookingDeets[0][2] + "<br><b>Placement: </b> " + bookingDeets[0][3] + """
        <br><b>Width:</b> """ + str(bookingDeets[0][4]) + "<br><b>Length:</b> " + str(bookingDeets[0][5]) + """
        <br><b>Estimate:</b> """ + str(bookingDeets[0][6]) + "<br><b>Deposit:</b> " + str(bookingDeets[0][7]) + """
        <br><b>Session Length:</b> """ + bookingDeets[0][8] + "<br><b>Desired Month:</b> " + bookingDeets[0][9] + """
        <br><b>Desired Year:</b> """ +  str(bookingDeets[0][10]) + "<br><b>Received Estimate:</b> " + bookingDeets[0][11] + """
        <br><b>Confirmed booking:</b> """ + bookingDeets[0][12]
    return bookingDetails

@app.route('/employee-home')
def employeeHome():
    return render_template("/employeeHome.html")

