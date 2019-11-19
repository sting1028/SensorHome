from Sensor import BMP085
from flask import Flask, render_template
import time,json,pymysql
from multiprocessing import Process

app = Flask(__name__)

x_data = []
y_data = {'Temp':[], 'Pressure':[]}

def creatTB():
    try:
        try:
            db = pymysql.connect("localhost","sensor","test123","sensorDB" )
        except:
            print('connect error')
        cursor = db.cursor()
        sql = """CREATE TABLE SENSOR (TIME  char(12),TEMP  numeric(4,2),PRESSURE int(7))"""
        cursor.execute(sql)
        db.close()
    except Exception as e:
        print(f'creatDB error{e}')

def insertDB(time_now:str, temp:float, pressure:int):
    db = pymysql.connect("localhost","sensor","test123","sensorDB" )
    cursor = db.cursor()
    sql = f'INSERT INTO SENSOR(TIME, TEMP, PRESSURE) VALUES ("{time_now}", {temp}, {pressure})'
    try:
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f'sql execute error{e}')
        db.commit()
    except:
        db.rollback()
        print('insert Error')
    db.close()


def fetchDB():
    db = pymysql.connect("localhost","sensor","test123","sensorDB" )
    cursor = db.cursor()
    sql_time = "SELECT TIME FROM SENSOR"""
    sql_temp = "SELECT TEMP FROM SENSOR"""
    sql_pressure = "SELECT PRESSURE FROM SENSOR"""
    try:
        cursor.execute(sql_time)
        results_time = [data[0] for data in cursor.fetchall()]
        cursor.execute(sql_temp)
        results_temp = [data[0] for data in cursor.fetchall()]
        cursor.execute(sql_pressure)
        results_pressure = [data[0] for data in cursor.fetchall()]
    except:
        print ("Error: unable to fetch data")
    db.close()
    return results_time,results_temp,results_pressure

def readSensorData() -> None:
    while True:
        time_now = time.strftime("%m-%d/%H:%M", time.localtime())
        sensor = BMP085(debug=False, mode='ultra_high',bus=1)
        temp_readed= sensor.readTemperature()
        pressure_readed = sensor.readPressure()
        insertDB(time_now=time_now, temp=temp_readed, pressure=pressure_readed)
        time.sleep(60)


def start():
    app.run(port=8888, debug=True, host='0.0.0.0')

@app.route('/')
def index():
    results_time, results_temp, results_pressure = fetchDB()
    return render_template('index.html', x_data=results_time, temp=results_temp, pressure=results_pressure)

if __name__ == '__main__':
    p1 = Process(target=readSensorData)
    p1.start()
    p2 = Process(target=start)
    p2.start()
    # # insertDB('11-19-13:49',23.6,100020)
    # fetchDB()
    # creatTB()

