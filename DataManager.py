from Sensor import BMP085
import time, pymysql, logging
from threading import Timer
from datetime import datetime

x_data = []
y_data = {'Temp': [], 'Pressure': []}


def creatTB() -> None:
    try:
        try:
            db = pymysql.connect("localhost", "sensor", "test123", "sensorDB")
        except Exception:
            logging.debug('connect error')
        cursor = db.cursor()
        sql = """CREATE TABLE SENSOR (TIME  char(12),TEMP  numeric(4,2),PRESSURE int(7))"""
        cursor.execute(sql)
        db.close()
    except Exception as e:
        logging.debug(f'creatDB error{e}')


def insertDB(time_now: str, temp: float, pressure: int) -> None:
    db = pymysql.connect("localhost", "sensor", "test123", "sensorDB")
    cursor = db.cursor()
    sql = f'INSERT INTO SENSOR(TIME, TEMP, PRESSURE) VALUES ("{time_now}", {temp}, {pressure})'
    try:
        try:
            cursor.execute(sql)
        except Exception as e:
            logging.debug(f'sql execute error{e}')
        db.commit()
    except Exception:
        db.rollback()
        logging.debug('insert Error')
    db.close()


def fetchDB() -> tuple:
    db = pymysql.connect("localhost", "sensor", "test123", "sensorDB")
    cursor = db.cursor()
    sql_time = "SELECT TIME FROM SENSOR" ""
    sql_temp = "SELECT TEMP FROM SENSOR" ""
    sql_pressure = "SELECT PRESSURE FROM SENSOR" ""
    try:
        cursor.execute(sql_time)
        results_time = [data[0] for data in cursor.fetchall()]
        cursor.execute(sql_temp)
        results_temp = [data[0] for data in cursor.fetchall()]
        cursor.execute(sql_pressure)
        results_pressure = [data[0] for data in cursor.fetchall()]
    except Exception:
        logging.debug("Error: unable to fetch data")
    db.close()
    return results_time, results_temp, results_pressure


def readSensorData() -> None:
    # while True:
    time_now = datetime.now().strftime("%m-%d/%H:%M")
    sensor = BMP085(debug=True, mode='ultra_high', bus=1)
    temp_readed = sensor.readTemperature()
    pressure_readed = sensor.readPressure()
    insertDB(time_now=time_now, temp=temp_readed, pressure=pressure_readed)
    Timer(60, readSensorData).start()
    # time.sleep(60)
