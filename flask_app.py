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

@app.route('/delete')
def delete():
    conn = sqlite3.connect('queen-bitch-db.db')
    cursor = conn.cursor()
    cursor.execute("DELETE from tblLogin where username = 'hello'")
    conn.commit()
    cursor.execute("SELECT * FROM tblLogin")
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
        msg = "client added"


#add booking details to tblBookings
        bookingDetails = []
#first create unique bookingID
        aArtist = request.form["artists"]
        sqlClientNo = "SELECT clientNumber FROM tblClients WHERE email =" + "'" + aEmail + "'"
        cursor.execute(sqlClientNo)
        clientNo = (cursor.fetchone()[0])
        bookingId = aFirstName[0] + aSurname[0] + str(clientNo) + str(aArtist)
        sqlCheckID = "SELECT * FROM tblBookings WHERE bookingID = " +"'" + bookingId + "'"
        cursor.execute(sqlCheckID)
        checkID = cursor.fetchall()
        while len(checkID) != 0:
            i = 1
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
        try:
            cursor.execute(sqltblBookings, bookingDetails)
            conn.commit()
            msg = "Booking successfully requested"
        except sqlite3.Error:
            conn.rollback()
            msg = 'the following error occured: ()'.format(sqlite3.Error)

        finally:
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
        while len(checkID) != 0:
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
        estimate = float(aWidth) * float(aLength) * int(avgPrice)
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
#fetch booking ID from tblBookings
        anID = request.form["bookingID"]
#fetch booking date from form and add to array
        booking = []
        booking.append("Y")
        aDay = request.form["day"]
        booking.append(aDay)
        aMonth = request.form["month"]
        booking.append(aMonth)
        aTime = request.form["sessionTime"]
        booking.append(aTime)
#fetch artist number from tblBookings
        sqlFindArtist = "SELECT artistNumber FROM tblBookings where bookingID =" + "'" + anID + "'"
        cursor.execute(sqlFindArtist)
        artistNo = (cursor.fetchone()[0])
#search to find if booking date is already taken
        sqlSearchDate = "SELECT * FROM tblBookings WHERE bookedDay = " + "'" + aDay + "' AND bookedMonth = " + "'" + aMonth + "' AND bookedTime = " + "'" + aTime + "' AND artistNumber = " + "'" + str(artistNo) + "'"
        cursor.execute(sqlSearchDate)
        result = cursor.fetchall()
#return message if booking date is taken
        if result != None:
            msg = "Booking date already taken"
            return render_template("/result.html", msg=msg)
#if booking date is free update tblBookings
        sqlConfirmed = "UPDATE tblBookings SET confirmedBooking = ? ,bookedDay = ?,bookedMonth = ? ,bookedTime = ? WHERE bookingID =" + "'" + anID + "'"
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
        aTime = request.form["sessionTime"]
#fetch artist number from tblBookings
        sqlFindArtist = "SELECT artistNumber FROM tblBookings where bookingID =" + "'" + anID + "'"
        cursor.execute(sqlFindArtist)
        artistNo = (cursor.fetchone()[0])
#search to find if booking date is already taken
        sqlSearchDate = "SELECT * FROM tblBookings WHERE bookedDay = " + "'" + aDay + "' AND bookedMonth = " + "'" + aMonth + "' AND bookedTime = " + "'" + aTime + "' AND artistNumber = " + "'" + str(artistNo) + "'"
        cursor.execute(sqlSearchDate)
        result = cursor.fetchall()
#return message if booking date is taken
        if result != None:
            msg = "Booking date already taken"
            return render_template("/result.html", msg=msg)
#if bookig date is free update tblBookings
        sqlNewDate = "UPDATE tblBookings SET bookedDay = " + "'" + aDay + "', bookedMonth = " + "'" + aMonth + "', bookedTime = " + "'" + aTime + "' WHERE bookingID =" + "'" + anID + "'"
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
    sqlBookingDetails = "SELECT artistNumber, estimate, deposit, sessionLength, desiredMonth FROM tblBookings WHERE bookingID = " + "'" + bookingID + "'"
    cursor.execute(sqlBookingDetails)
    bookingDetails = cursor.fetchall()
    artistNo = str(bookingDetails[0][0])
    estimate = str(bookingDetails[0][1])
    deposit = str(bookingDetails[0][2])
    sessionLen = bookingDetails[0][3]
    month = bookingDetails[0][4]
#find days in month artist has booking
#if desired month is january
    if month == "january":
        for idx in range (1, 32):
#select times with a booking already
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
            sqlTakenTimes = "SELECT bookedTime FROM tblBookings WHERE artistNumber = " + "'" + artistNo + "'" + "AND bookedMonth = " + "'" + month + "'" + "AND bookedDay =" + "'" + str(idx) + "'"
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
    output = "Name: " + firstName + " " + surname + "<br> Email: " + email + "<br> Estimate: £" + estimate + "<br> Deposit: £" + deposit + "<br> Session length: " + sessionLen + "<br> Month: " + month + "<br> Optional days and times: <br>" + '<br>'.join(map(str, optionalTimes))
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

