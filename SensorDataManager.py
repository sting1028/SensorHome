from Sensor import BMP085
import time, pymysql, logging
from datetime import datetime
logger = logging.getLogger(__name__)


class DataBase:

    def __init__(self, debug):
        self.debug = debug

    def creatTB(self) -> None:
        try:
            try:
                db = pymysql.connect("localhost", "sensor", "test123",
                                     "sensorDB")
            except Exception:
                logger.debug('connect error')
            cursor = db.cursor()
            sql = """CREATE TABLE SENSOR (TIME  char(12),TEMP  numeric(4,2),PRESSURE int(7))"""
            cursor.execute(sql)
            db.close()
        except Exception as e:
            logger.debug(f'creatDB error{e}')

    def insertDB(self, time_now: str, temp: float, pressure: int) -> None:
        db = pymysql.connect("localhost", "sensor", "test123", "sensorDB")
        cursor = db.cursor()
        sql = f'INSERT INTO SENSOR(TIME, TEMP, PRESSURE) VALUES ("{time_now}", {temp}, {pressure})'
        try:
            try:
                cursor.execute(sql)
                if self.debug:
                    logger.debug(
                        f'Insert to database: time:{time_now},temp{temp},pressure{pressure}'
                    )
            except Exception as e:
                logger.debug(f'sql execute error{e}')
            db.commit()
        except Exception:
            db.rollback()
            logger.debug('insert Error')
        db.close()

    def fetchDB(self) -> tuple:
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
            if self.debug:
                logger.debug(
                    f'Fetch from database count_time:{len(results_time)},count_temp:{len(results_temp)},count_pressure:{len(results_pressure)}'
                )
        except Exception:
            logger.debug("Error: unable to fetch data")
        db.close()
        return results_time, results_temp, results_pressure

class DataCollect:
    def __init__(self, debug=False, mode='ultra_high', bus=1):
        self.sensor = BMP085(debug=debug, mode=mode, bus=bus)

    def readSensorData(self) -> tuple:
        time_now = datetime.now().strftime("%m-%d/%H:%M")
        temp = self.sensor.readTemperature()
        pressure = self.sensor.readPressure()
        return (time_now, temp ,pressure)

