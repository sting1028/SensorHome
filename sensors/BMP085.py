import time, logging
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)

class BMP085:
    # BMP085 Registers
    __CAL_AC1_REG = 0xAA  # R   Calibration data (16 bits)
    __CAL_AC2_REG = 0xAC  # R   Calibration data (16 bits)
    __CAL_AC3_REG = 0xAE  # R   Calibration data (16 bits)
    __CAL_AC4_REG = 0xB0  # R   Calibration data (16 bits)
    __CAL_AC5_REG = 0xB2  # R   Calibration data (16 bits)
    __CAL_AC6_REG = 0xB4  # R   Calibration data (16 bits)
    __CAL_B1_REG = 0xB6  # R   Calibration data (16 bits)
    __CAL_B2_REG = 0xB8  # R   Calibration data (16 bits)
    __CAL_MB_REG = 0xBA  # R   Calibration data (16 bits)
    __CAL_MC_REG = 0xBC  # R   Calibration data (16 bits)
    __CAL_MD_REG = 0xBE  # R   Calibration data (16 bits)
    __CONTROL_REG = 0xF4
    __TEMPDATA_REG = 0xF6
    __PRESSUREDATA_REG = 0xF6
    __READTEMPCMD = 0x2E
    __READPRESSURECMD = 0x34

    def __init__(self, address=0x77, mode='standard', bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        self._cal_AC1_data = 0
        self._cal_AC2_data = 0
        self._cal_AC3_data = 0
        self._cal_AC4_data = 0
        self._cal_AC5_data = 0
        self._cal_AC6_data = 0
        self._cal_B1_data = 0
        self._cal_B2_data = 0
        self._cal_MB_data = 0
        self._cal_MC_data = 0
        self._cal_MD_data = 0
        # Make sure the specified mode is in the appropriate range
        try:
            self.mode, self.conversion_time = self.__convertOperationMode(mode)
        except KeyError:
            logger.debug('Debug: BMP085:Invalid Mode: Using STANDARD by default')
            self.mode = 1
            self.conversion_time = 0.0075

        # Read the calibration data
        self.__readCalibrationData()

    def __convertOperationMode(self, mode):
        op = {
            'low': (0, 0.005),  #mode 0, conversion time 4.5ms
            'standard': (1, 0.008),
            'high': (2, 0.014),
            'ultra_high': (3, 0.026)
        }
        return op[mode]

    def __readCalibrationData(self):
        "Reads the calibration data from the EEPROM on sensor"
        self._cal_AC1_data = self.i2c.readS16_BMP085(self.__CAL_AC1_REG)  # INT16
        self._cal_AC2_data = self.i2c.readS16_BMP085(self.__CAL_AC2_REG)  # INT16
        self._cal_AC3_data = self.i2c.readS16_BMP085(self.__CAL_AC3_REG)  # INT16
        self._cal_AC4_data = self.i2c.readU16_BMP085(self.__CAL_AC4_REG)  # UINT16
        self._cal_AC5_data = self.i2c.readU16_BMP085(self.__CAL_AC5_REG)  # UINT16
        self._cal_AC6_data = self.i2c.readU16_BMP085(self.__CAL_AC6_REG)  # UINT16
        self._cal_B1_data = self.i2c.readS16_BMP085(self.__CAL_B1_REG)  # INT16
        self._cal_B2_data = self.i2c.readS16_BMP085(self.__CAL_B2_REG)  # INT16
        self._cal_MB_data = self.i2c.readS16_BMP085(self.__CAL_MB_REG)  # INT16
        self._cal_MC_data = self.i2c.readS16_BMP085(self.__CAL_MC_REG)  # INT16
        self._cal_MD_data = self.i2c.readS16_BMP085(self.__CAL_MD_REG)  # INT16

    def __readRawTemp(self):
        "Reads the raw temperature data from the sensor"
        self.i2c.writeU8(self.__CONTROL_REG, self.__READTEMPCMD)
        time.sleep(self.conversion_time)
        raw_temp = self.i2c.readU16_BMP085(self.__TEMPDATA_REG)
        if (self.debug):
            logger.debug(f"Debug: BMP085:Raw Temp: {raw_temp:#x} ({raw_temp})")
        return raw_temp

    def __readRawPressure(self):
        "Reads the raw pressure data from the sensor"
        self.i2c.writeU8(self.__CONTROL_REG,
                        self.__READPRESSURECMD + (self.mode << 6))
        time.sleep(self.conversion_time)
        msb = self.i2c.readU8(self.__PRESSUREDATA_REG)
        lsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 1)
        xlsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 2)
        raw_pressure = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)
        if (self.debug):
            logger.debug(
                f"Debug: BMP085:Raw Pressure: {raw_pressure:#x} ({raw_pressure})")
        return raw_pressure

    def readTemperature(self):
        "Gets the compensated temperature in degrees celcius"

        # Read raw temp before aligning it with the calibration values
        UT = self.__readRawTemp()
        X1 = ((UT - self._cal_AC6_data) * self._cal_AC5_data) >> 15
        X2 = (self._cal_MC_data << 11) // (X1 + self._cal_MD_data)
        self.B5 = X1 + X2
        temp = ((self.B5 + 8) >> 4) / 10
        if (self.debug):
            logger.debug(f"Debug: BMP085:Calibrated temperature = {temp} C")
        return temp

    def readPressure(self):
        "Gets the compensated pressure in pascal"
        UP = self.__readRawPressure()

        # Pressure Calculations
        B6 = self.B5 - 4000
        X1 = (self._cal_B2_data * (B6 * B6) >> 12) >> 11
        X2 = (self._cal_AC2_data * B6) >> 11
        X3 = X1 + X2
        B3 = (((self._cal_AC1_data * 4 + X3) << self.mode) + 2) // 4
        X1 = (self._cal_AC3_data * B6) >> 13
        X2 = (self._cal_B1_data * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self._cal_AC4_data * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self.mode)
        if (B7 < 0x80000000):
            p1 = (B7 * 2) // B4
        else:
            p1 = (B7 // B4) * 2
        X1 = (p1 >> 8) * (p1 >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7375 * p1) >> 16
        p = p1 + ((X1 + X2 + 3791) >> 4)
        if (self.debug):
            logger.debug("Debug: BMP085:Calibrated Pressure = %d Pa" % (p))
        return p

    def readAltitude(self, seaLevelPressure=101325, pressure=0):
        "Calculates the altitude in meters"
        altitude = 44330.0 * (1.0 - pow(pressure / seaLevelPressure, 0.1903))
        if (self.debug):
            logger.debug("Debug: BMP085:Altitude = %d" % (altitude))
            return altitude
        else:
            return 0

    def readMSLPressure(self, altitude, pressure=0):
        "Calculates the mean sea level pressure"
        T0 = float(altitude) / 44330
        T1 = pow(1 - T0, 5.255)
        mslpressure = pressure / T1
        return mslpressure

# a = BMP085(bus=1)
# print(a.readTemperature(),a.readPressure())