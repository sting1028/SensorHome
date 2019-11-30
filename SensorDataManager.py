# from sensors.BMP085 import BMP085
from sensors.BMP280 import BMP280
from sensors.SI7021 import SI7021
from sensors.CCS811 import CCS811
from sensors.BH1750 import BH1750
from sensors.HMC5883L import HMC5883
import time, pymysql, logging
from datetime import datetime
logger = logging.getLogger(__name__)


class DataBase:
    def __init__(self, debug=False):
        self.debug = debug

    def isNotZero(x):
        return x != 0

    def creatTB(self) -> None:
        try:
            try:
                db = pymysql.connect("localhost", "sensor", "test123",
                                     "sensorDB")
            except Exception:
                logger.debug('connect error')
            cursor = db.cursor()
            sql = """CREATE TABLE IF NOT EXISTS SENSOR (TIME  char(12),TEMP  float(4,2), PRESSURE int(7), HUMIDITY float(4,2), ILLUMINANCE float(5,1), CO2 smallint, VOC smallint, MAG_X smallint, MAG_Y smallint, MAG_Z smallint)"""
            cursor.execute(sql)
            db.close()
        except Exception as e:
            logger.debug(f'creatDB error{e}')
            print(e)

    def insertDB(self, time_now: str, temp: float, pressure: int,
                 humidity: float, illuminance: float, co2: int, voc: int,
                 mag_x: int, mag_y: int, mag_z: int) -> None:
        db = pymysql.connect("localhost", "sensor", "test123", "sensorDB")
        cursor = db.cursor()
        sql = f'INSERT INTO SENSOR(TIME, TEMP, PRESSURE, HUMIDITY, ILLUMINANCE, CO2, VOC, MAG_X, MAG_Y, MAG_Z) VALUES ("{time_now}", {temp}, {pressure}, {humidity}, {illuminance}, {co2}, {voc}, {mag_x}, {mag_y},{mag_z})'
        try:
            try:
                cursor.execute(sql)
                if self.debug:
                    logger.debug(
                        f'debug: Insert to database: time:{time_now},temp:{temp},pressure:{pressure},humidity:{humidity},illuminance:{illuminance},co2:{co2},voc:{voc},mag_x:{mag_x},mag_y:{mag_y},mag_z:{mag_z}'
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
        sql_time = "SELECT TIME FROM SENSOR"
        sql_temp = "SELECT TEMP FROM SENSOR"
        sql_pressure = "SELECT PRESSURE FROM SENSOR"
        sql_humidity = "SELECT HUMIDITY FROM SENSOR"
        sql_illu = "SELECT ILLUMINANCE FROM SENSOR"
        sql_co2 = "SELECT CO2 FROM SENSOR"
        sql_voc = "SELECT VOC FROM SENSOR"
        sql_mag_x = "SELECT MAG_X FROM SENSOR"
        sql_mag_y = "SELECT MAG_Y FROM SENSOR"
        sql_mag_z = "SELECT MAG_Z FROM SENSOR"
        try:
            cursor.execute(sql_time)
            results_time = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_temp)
            results_temp = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_pressure)
            results_pressure = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_humidity)
            results_humidity = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_illu)
            results_illu = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_co2)
            results_co2 = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_voc)
            results_voc = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_mag_x)
            results_mag_x = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_mag_y)
            results_mag_y = [data[0] for data in cursor.fetchall()]
            cursor.execute(sql_mag_z)
            results_mag_z = [data[0] for data in cursor.fetchall()]
            if self.debug:
                logger.debug(
                    f'Fetch from database count_time:{len(results_time)},count_temp:{len(results_temp)},count_pressure:{len(results_pressure)}'
                )
        except Exception:
            logger.debug("Error: unable to fetch data")
        db.close()
        return results_time, results_temp, results_pressure, results_humidity, results_illu, results_co2, results_voc, results_mag_x, results_mag_y, results_mag_z


class DataCollect:
    def __init__(self, debug=False, bus=1):
        self.sensor_ccs811 = CCS811(bus=bus, debug=debug)
        self.sensor_bmp280 = BMP280(bus=bus, debug=debug)
        self.sensor_si702 = SI7021(bus=bus, debug=debug)
        self.sensor_bh1750 = BH1750(bus=bus, debug=debug)
        self.sensor_hmc5883 = HMC5883(bus=bus, debug=debug)

    def readSensorData(self) -> tuple:
        time_now = datetime.now().strftime("%m-%d/%H:%M")
        temp = self.sensor_si702.readTemperature()
        humidity = self.sensor_si702.readHumidity()
        self.sensor_bmp280.readTemperature()
        pressure = self.sensor_bmp280.readPressure()
        illuminance = self.sensor_bh1750.readData()
        co2, voc = self.sensor_ccs811.readData()
        mag_x, mag_y, mag_z = self.sensor_hmc5883.readData()
        return (time_now, temp, humidity, pressure, illuminance, co2, voc,
                mag_x, mag_y, mag_z)


# a = DataBase()
# a.creatTB()
# # b = DataCollect()
# # time_now,temp,humidity,pressure,illuminance,co2,voc,mag_x,mag_y,mag_z = b.readSensorData()
# # a.insertDB(time_now=time_now,temp=temp,pressure=pressure,humidity=humidity,illuminance=illuminance,co2=co2,voc=voc,mag_x=mag_x,mag_y=mag_y,mag_z=mag_z)
# print(a.fetchDB())