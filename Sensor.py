import time, logging, adafruit_ccs811
from I2cBase import I2cBase
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
            logger.debug('Invalid Mode: Using STANDARD by default')
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
        self._cal_AC1_data = self.i2c.readS16(self.__CAL_AC1_REG)  # INT16
        self._cal_AC2_data = self.i2c.readS16(self.__CAL_AC2_REG)  # INT16
        self._cal_AC3_data = self.i2c.readS16(self.__CAL_AC3_REG)  # INT16
        self._cal_AC4_data = self.i2c.readU16(self.__CAL_AC4_REG)  # UINT16
        self._cal_AC5_data = self.i2c.readU16(self.__CAL_AC5_REG)  # UINT16
        self._cal_AC6_data = self.i2c.readU16(self.__CAL_AC6_REG)  # UINT16
        self._cal_B1_data = self.i2c.readS16(self.__CAL_B1_REG)  # INT16
        self._cal_B2_data = self.i2c.readS16(self.__CAL_B2_REG)  # INT16
        self._cal_MB_data = self.i2c.readS16(self.__CAL_MB_REG)  # INT16
        self._cal_MC_data = self.i2c.readS16(self.__CAL_MC_REG)  # INT16
        self._cal_MD_data = self.i2c.readS16(self.__CAL_MD_REG)  # INT16

    def __readRawTemp(self):
        "Reads the raw temperature data from the sensor"
        self.i2c.write8(self.__CONTROL_REG, self.__READTEMPCMD)
        time.sleep(self.conversion_time)
        raw_temp = self.i2c.readU16(self.__TEMPDATA_REG)
        if (self.debug):
            logger.debug(f"Debug: Raw Temp: {raw_temp:#x} ({raw_temp})")
        return raw_temp

    def __readRawPressure(self):
        "Reads the raw pressure data from the sensor"
        self.i2c.write8(self.__CONTROL_REG,
                        self.__READPRESSURECMD + (self.mode << 6))
        time.sleep(self.conversion_time)
        msb = self.i2c.readU8(self.__PRESSUREDATA_REG)
        lsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 1)
        xlsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 2)
        raw_pressure = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)
        if (self.debug):
            logger.debug(
                f"Debug: Raw Pressure: {raw_pressure:#x} ({raw_pressure})")
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
            logger.debug(f"Debug: Calibrated temperature = {temp} C")
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
            logger.debug("Debug: Pressure = %d Pa" % (p))
        return p

    def readAltitude(self, seaLevelPressure=101325, pressure=0):
        "Calculates the altitude in meters"
        altitude = 44330.0 * (1.0 - pow(pressure / seaLevelPressure, 0.1903))
        if (self.debug):
            logger.debug("Debug: Altitude = %d" % (altitude))
            return altitude
        else:
            return 0

    def readMSLPressure(self, altitude, pressure=0):
        "Calculates the mean sea level pressure"
        T0 = float(altitude) / 44330
        T1 = pow(1 - T0, 5.255)
        mslpressure = pressure / T1
        return mslpressure

class CCS811:
    class CCS811:
    """CCS811 gas sensor driver.

    :param ~busio.I2C i2c: The I2C bus.
    :param int addr: The I2C address of the CCS811.
    """
    #set up the registers
    error = i2c_bit.ROBit(0x00, 0)
    """True when an error has occured."""
    data_ready = i2c_bit.ROBit(0x00, 3)
    """True when new data has been read."""
    app_valid = i2c_bit.ROBit(0x00, 4)
    fw_mode = i2c_bit.ROBit(0x00, 7)

    hw_id = i2c_bits.ROBits(8, 0x20, 0)

    int_thresh = i2c_bit.RWBit(0x01, 2)
    interrupt_enabled = i2c_bit.RWBit(0x01, 3)
    drive_mode = i2c_bits.RWBits(3, 0x01, 4)

    temp_offset = 0.0
    """Temperature offset."""

    def __init__(self, i2c_bus, address=0x5A):
        self.i2c_device = I2CDevice(i2c_bus, address)

        #check that the HW id is correct
        if self.hw_id != _HW_ID_CODE:
            raise RuntimeError("Device ID returned is not correct! Please check your wiring.")

        #try to start the app
        buf = bytearray(1)
        buf[0] = 0xF4
        with self.i2c_device as i2c:
            i2c.write(buf, end=1)
        time.sleep(.1)

        #make sure there are no errors and we have entered application mode
        if self.error:
            raise RuntimeError("Device returned a error! Try removing and reapplying power to "
                               "the device and running the code again.")
        if not self.fw_mode:
            raise RuntimeError("Device did not enter application mode! If you got here, there may "
                               "be a problem with the firmware on your sensor.")

        self.interrupt_enabled = False

        #default to read every second
        self.drive_mode = DRIVE_MODE_1SEC

        self._eco2 = None # pylint: disable=invalid-name
        self._tvoc = None # pylint: disable=invalid-name

    @property
    def error_code(self):
        """Error code"""
        buf = bytearray(2)
        buf[0] = 0xE0
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)
        return buf[1]

    def _update_data(self):
        if self.data_ready:
            buf = bytearray(9)
            buf[0] = _ALG_RESULT_DATA
            with self.i2c_device as i2c:
                i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)

            self._eco2 = (buf[1] << 8) | (buf[2])
            self._tvoc = (buf[3] << 8) | (buf[4])

            if self.error:
                raise RuntimeError("Error:" + str(self.error_code))

    @property
    def tvoc(self): # pylint: disable=invalid-name
        """Total Volatile Organic Compound in parts per billion."""
        self._update_data()
        return self._tvoc

    @property
    def eco2(self): # pylint: disable=invalid-name
        """Equivalent Carbon Dioxide in parts per million. Clipped to 400 to 8192ppm."""
        self._update_data()
        return self._eco2

    @property
    def temperature(self):
        """
        .. deprecated:: 1.1.5
           Hardware support removed by vendor

        Temperature based on optional thermistor in Celsius."""
        buf = bytearray(5)
        buf[0] = _NTC
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)

        vref = (buf[1] << 8) | buf[2]
        vntc = (buf[3] << 8) | buf[4]

        # From ams ccs811 app note 000925
        # https://download.ams.com/content/download/9059/13027/version/1/file/CCS811_Doc_cAppNote-Connecting-NTC-Thermistor_AN000372_v1..pdf
        rntc = float(vntc) * _REF_RESISTOR / float(vref)

        ntc_temp = math.log(rntc / 10000.0)
        ntc_temp /= 3380.0
        ntc_temp += 1.0 / (25 + 273.15)
        ntc_temp = 1.0 / ntc_temp
        ntc_temp -= 273.15
        return ntc_temp - self.temp_offset

    def set_environmental_data(self, humidity, temperature):
        """Set the temperature and humidity used when computing eCO2 and TVOC values.

        :param int humidity: The current relative humidity in percent.
        :param float temperature: The current temperature in Celsius."""
        # Humidity is stored as an unsigned 16 bits in 1/512%RH. The default
        # value is 50% = 0x64, 0x00. As an example 48.5% humidity would be 0x61,
        # 0x00.
        humidity = int(humidity * 512)

        # Temperature is stored as an unsigned 16 bits integer in 1/512 degrees
        # there is an offset: 0 maps to -25C. The default value is 25C = 0x64,
        # 0x00. As an example 23.5% temperature would be 0x61, 0x00.
        temperature = int((temperature + 25) * 512)

        buf = bytearray(5)
        buf[0] = _ENV_DATA
        struct.pack_into(">HH", buf, 1, humidity, temperature)

        with self.i2c_device as i2c:
            i2c.write(buf)

    def set_interrupt_thresholds(self, low_med, med_high, hysteresis):
        """Set the thresholds used for triggering the interrupt based on eCO2.
        The interrupt is triggered when the value crossed a boundary value by the
        minimum hysteresis value.

        :param int low_med: Boundary between low and medium ranges
        :param int med_high: Boundary between medium and high ranges
        :param int hysteresis: Minimum difference between reads"""
        buf = bytearray([_THRESHOLDS,
                         ((low_med >> 8) & 0xF),
                         (low_med & 0xF),
                         ((med_high >> 8) & 0xF),
                         (med_high & 0xF),
                         hysteresis])
        with self.i2c_device as i2c:
            i2c.write(buf)

    def reset(self):
        """Initiate a software reset."""
        #reset sequence from the datasheet
        seq = bytearray([_SW_RESET, 0x11, 0xE5, 0x72, 0x8A])
        with self.i2c_device as i2c:
            i2c.write(seq)
