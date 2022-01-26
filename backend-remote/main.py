from flask import Flask, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime;

app = Flask(__name__)
CORS(app)   # So that the frontend and backend can make requests with necessary permissions
# auth = HTTPBasicAuth()

# Setting Up DB
app.config['MYSQL_HOST'] = 'hyenaporal.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'hyenaporal'
app.config['MYSQL_PASSWORD'] = 'insane123'
app.config['MYSQL_DB'] = 'hyenaporal$hyperops'
mysql = MySQL(app)


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
    app.run()