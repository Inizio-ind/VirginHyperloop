from flask import Flask, request, session
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime;
from flask_session import Session
import MySQLdb.cursors

app = Flask(__name__)
CORS(app)   # So that the frontend and backend can make requests with necessary permissions
# auth = HTTPBasicAuth()

# Setting Up DB
app.config['MYSQL_HOST'] = 'hyenaporal.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'hyenaporal'
app.config['MYSQL_PASSWORD'] = 'insane123'
app.config['MYSQL_DB'] = 'hyenaporal$hyperops'
mysql = MySQL(app)

app.secret_key = '\xcb\x9e\x84(#/\t\xf74\xfd\x10\x06~2.\xe7\xed\x90hGNNX\xc7'

app.config["SECRET_KEY"] = 'DOTHACK2022'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
Session(app)


# users = {
#     "admin": generate_password_hash("insane")
# }

# @auth.verify_password
# def verify_password(username, password):
#     if username in users and \
#             check_password_hash(users.get(username), password):
#         return username

@app.route('/')
def home():
    return "hello World"


def get_seat_mapping():
    starting_seats = [146,88,30,117,59,1]
    map_seats = {}
    for i in range(1,7):
        map_seats[i] = []
        for j in range(starting_seats[i-1]+27, starting_seats[i-1]-1 , -1):
            map_seats[i].append(j)
    return map_seats

@app.route('/get_bookings', methods=['POST'])
# @auth.login_required
def getBookings():
    map_seats = get_seat_mapping()
    data = request.get_json()

    date_object = datetime.strptime(data['date'], "%a %b %d %Y")
    date = date_object.strftime("%-d/%-m/%Y")

    time_object = datetime.strptime(data['time'], "%H:%M:%S.%f")
    time = time_object.strftime("%-H:%M")

    if data:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT `Pod Bay`,`Seat` FROM `bookings` WHERE `Date` = '{date}' AND `Platform` = '{data['platform']}' AND ('{time}' BETWEEN Arrival AND Departure);")
        rows = cursor.fetchall()
        cursor.close()
        return { 'seats' : [ map_seats[x[0]][x[1]-1] for x in rows ] }


@app.route('/get_q', methods=['POST'])
# @auth.login_required
def getQ():
    data = request.get_json()

    date_object = datetime.strptime(data['date'], "%a %b %d %Y")
    date = date_object.strftime("%-m/%-d/%Y")

    time_object = datetime.strptime(data['time'], "%H:%M:%S.%f")
    time = time_object.strftime("%-H:%M")

    if data:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT `WaitTime` FROM `qwaittimes` WHERE `Date` = '{date}' AND `Time` = '{time}' ;")
        rows = cursor.fetchall()
        cursor.close()
        return { 'q' : [x[0] for x in rows] }

@app.route('/get_qavg', methods=['POST'])
# @auth.login_required
def getQAvg():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT AVG(WaitTime) from qwaittimes where QueueNo = 'Q1';")
    Q1 = cursor.fetchone()
    cursor.execute("SELECT AVG(WaitTime) from qwaittimes where QueueNo = 'Q2';")
    Q2 = cursor.fetchone()
    cursor.execute("SELECT AVG(WaitTime) from qwaittimes where QueueNo = 'Q3';")
    Q3 = cursor.fetchone()
    cursor.execute("SELECT AVG(WaitTime) from qwaittimes where QueueNo = 'Q4';")
    Q4 = cursor.fetchone()
    cursor.execute("SELECT AVG(WaitTime) from qwaittimes where QueueNo = 'Q5';")
    Q5 = cursor.fetchone()
    cursor.close()
    return { 'avg' : [Q1[0],Q2[0],Q3[0],Q4[0],Q5[0]] }




@app.route('/get_weather', methods=['POST'])
# @auth.login_required
def getWeather():


    cursor = mysql.connection.cursor()

    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'Clear';")
    clear = cursor.fetchone()
    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'Humid';")
    humid = cursor.fetchone()
    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'Hot';")
    hot = cursor.fetchone()
    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'LightShower';")
    ls = cursor.fetchone()
    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'Cloudy';")
    cl = cursor.fetchone()
    cursor.execute("SELECT AVG(PassengerCount) from hypdata where Weather = 'HeavyRain';")
    hr = cursor.fetchone()

    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'Clear';")
    clearCount = cursor.fetchone()
    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'Humid';")
    humidCount = cursor.fetchone()
    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'Hot';")
    hotCount = cursor.fetchone()
    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'LightShower';")
    lsCount = cursor.fetchone()
    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'Cloudy';")
    clCount = cursor.fetchone()
    cursor.execute("SELECT COUNT(PassengerCount) from hypdata where Weather = 'HeavyRain';")
    hrCount = cursor.fetchone()
    cursor.close()
    return {
        'weather' : [clear[0],humid[0],hot[0],ls[0],cl[0],hr[0]],
        'count' : [clearCount[0],humidCount[0],hotCount[0],lsCount[0],clCount[0],hrCount[0]]
    }


@app.route('/get_hourlyPass', methods=['POST'])
# @auth.login_required
def getHourlyPass():
    data = request.get_json()

    date_object = datetime.strptime(data['date'], "%a %b %d %Y")
    date = date_object.strftime("%-m/%-d/%Y")

    if data:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT `PassengerCount` FROM `hypdata` WHERE `Date` = '{date}';")
        rows = cursor.fetchall()
        cursor.close()
        return { 'hourlyPass' : [x[0] for x in rows] }




@app.route('/login', methods=['GET', 'POST'])
def login():
    data=request.get_json()

    # Output message if something goes wrong...

    # Check if "username" and "password" POST requests exist (user submitted form)

    username = data['username']
    password = data['password']
    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
    # Fetch one record and return result
    account = cursor.fetchone()
    # If account exists in accounts table in out database
    if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['password'] = account['password']
            session['username'] = account['username']
            # Redirect to home page
            return '5'
    else:
            # Account doesnt exist or username/password incorrect
            return 'unsuccessfull!'






@app.route('/get_passenger_count', methods=['POST'])
# @auth.login_required
def getPassCount():
    data = request.get_json()
    passCount = int(data['input'])
    if data:
        # cursor = mysql.connection.cursor()
        # cursor.execute(f"SELECT `Pod Bay`,`Seat` FROM `bookings` WHERE `Date` = '{date}' AND `Platform` = '{data['platform']}' AND ('{time}' BETWEEN Arrival AND Departure);")
        # rows = cursor.fetchall()
        # cursor.close()
        if(passCount >= 16000):
            return {'freq':0.5}
        elif(passCount > 8000):
            return {'freq':2}
        elif(passCount > 6000):
            return {'freq':4}
        else:
            return {'freq':6}



@app.route('/test-db', methods=['GET','POST'])
# @auth.login_required
def getData():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM `variables` WHERE `name` = 'time_selection'")
        row = cursor.fetchone()
        cursor.close()
        print(row)
        return {row[0]:row[1]}

    elif request.method == 'POST':
        data = request.get_json()
        if data and 'time' in data :
            time = data['time']
            print(time)
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(f"UPDATE `variables` SET `value` = '{time}' WHERE `variables`.`name` = 'time_selection';")
                mysql.connection.commit()
                cursor.close()
            except Exception as e:
                print(e)
            return "success"





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)
