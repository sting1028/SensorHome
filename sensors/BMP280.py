import time, logging
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)


class BMP280:
    # BMP280 Registers
    __T1_REG = 0x88  # R   Calibration data (16 bits)
    __T2_REG = 0x8A  # R   Calibration data (16 bits)
    __T3_REG = 0x8C  # R   Calibration data (16 bits)
    __P1_REG = 0x8E  # R   Calibration data (16 bits)
    __P2_REG = 0x90  # R   Calibration data (16 bits)
    __P3_REG = 0x92  # R   Calibration data (16 bits)
    __P4_REG = 0x94  # R   Calibration data (16 bits)
    __P5_REG = 0x96  # R   Calibration data (16 bits)
    __P6_REG = 0x98  # R   Calibration data (16 bits)
    __P7_REG = 0x9A  # R   Calibration data (16 bits)
    __P8_REG = 0x9C  # R   Calibration data (16 bits)
    __P9_REG = 0x9E  # R   Calibration data (16 bits)
    __CONTROL_REG = 0xF4
    __TEMPDATA_REG = 0xFA
    __PRESSUREDATA_REG = 0xF7
    __OnlyPressure = 0xB
    __Temp_Pressure = 0x4B

    def __init__(self, address=0x76, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        self._cal_T1_data = 0
        self._cal_T2_data = 0
        self._cal_T3_data = 0
        self._cal_P1_data = 0
        self._cal_P2_data = 0
        self._cal_P3_data = 0
        self._cal_P4_data = 0
        self._cal_P5_data = 0
        self._cal_P6_data = 0
        self._cal_P7_data = 0
        self._cal_P8_data = 0
        self._cal_P9_data = 0
        # self._cal_T1_data = 27504
        # self._cal_T2_data = 26435
        # self._cal_T3_data = -1000
        # self._cal_P1_data = 36477
        # self._cal_P2_data = -10785
        # self._cal_P3_data = 3024
        # self._cal_P4_data = 2855
        # self._cal_P5_data = 140
        # self._cal_P6_data = -7
        # self._cal_P7_data = 15500
        # self._cal_P8_data = -14600
        # self._cal_P9_data = 6000
        # Read the calibration data
        self.__readCalibrationData()
        self._ctrlMeas()

    def __readCalibrationData(self):
        "Reads the calibration data from the EEPROM on sensor"
        self._cal_T1_data = self.i2c.readU16_BMP280(self.__T1_REG)  # INT16
        self._cal_T2_data = self.i2c.readS16_BMP280(self.__T2_REG)  # INT16
        self._cal_T3_data = self.i2c.readS16_BMP280(self.__T3_REG)  # INT16
        self._cal_P1_data = self.i2c.readU16_BMP280(self.__P1_REG)  # UINT16
        self._cal_P2_data = self.i2c.readS16_BMP280(self.__P2_REG)  # UINT16
        self._cal_P3_data = self.i2c.readS16_BMP280(self.__P3_REG)  # UINT16
        self._cal_P4_data = self.i2c.readS16_BMP280(self.__P4_REG)  # INT16
        self._cal_P5_data = self.i2c.readS16_BMP280(self.__P5_REG)  # INT16
        self._cal_P6_data = self.i2c.readS16_BMP280(self.__P6_REG)  # INT16
        self._cal_P7_data = self.i2c.readS16_BMP280(self.__P7_REG)  # INT16
        self._cal_P8_data = self.i2c.readS16_BMP280(self.__P8_REG)  # INT16
        self._cal_P9_data = self.i2c.readS16_BMP280(self.__P9_REG)  # INT16
        # print(self._cal_T1_data)
        # print(self._cal_T2_data)
        # print(self._cal_P1_data)
        # print(self._cal_P2_data)
        # print(self._cal_P3_data)
        # print(self._cal_P4_data)
        # print(self._cal_P5_data)
        # print(self._cal_P6_data)
        # print(self._cal_P7_data)
        # print(self._cal_P8_data)
        # print(self._cal_P9_data)

    def __readRawTemp(self):
        "Reads the raw temperature data from the sensor"
        self.i2c.writeU8(self.__CONTROL_REG, 0x25)
        msb = self.i2c.readU8(self.__TEMPDATA_REG)
        lsb = self.i2c.readU8(self.__TEMPDATA_REG + 1)
        xlsb = self.i2c.readU8(self.__TEMPDATA_REG + 2)
        raw_temp = (msb << 12) + (lsb << 4) + (xlsb >> 4)
        if self.debug:
            logger.debug(f"Debug: BMP280:Raw Temp: {raw_temp:#x} ({raw_temp})")
        return raw_temp

    def __readRawPressure(self):
        "Reads the raw pressure data from the sensor"
        self.i2c.writeU8(self.__CONTROL_REG, 0x25)
        msb = self.i2c.readU8(self.__PRESSUREDATA_REG)
        lsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 1)
        xlsb = self.i2c.readU8(self.__PRESSUREDATA_REG + 2)
        raw_pressure = (msb << 12) + (lsb << 4) + (xlsb >> 4)
        if self.debug:
            logger.debug(
                f"Debug: BMP280:Raw Pressure: {raw_pressure:#x} ({raw_pressure})")
        return raw_pressure

    def readTemperature(self):
        "Gets the compensated temperature in degrees celcius"
        # uncomp_temp = 519888
        uncomp_temp = self.__readRawTemp()
        # Read raw temp before aligning it with the calibration values
        var1 = ((((uncomp_temp // 8) -
                  (self._cal_T1_data << 1))) * self._cal_T2_data) // 2048
        var2 = (((
            ((uncomp_temp // 16) -
             (self._cal_T1_data))**2) // 4096) * self._cal_T3_data) // 16384
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) // 256
        # var1 = (uncomp_temp//16384 - self._cal_T1_data//1024) * self._cal_T2_data
        # var2 = (uncomp_temp//131072 - self._cal_T1_data//8192) * ((uncomp_temp//131072 - self._cal_T1_data//8192) * self._cal_T3_data)
        # self.t_fine = var1 + var2
        # temp = self.t_fine/5120
        # var1 = (((uncomp_temp >> 3) - (self._cal_T1_data << 1)) * self._cal_T2_data) >> 11
        # var2 = (((((uncomp_temp >> 4) - self._cal_T1_data) * (uncomp_temp - self._cal_T1_data)) >> 12) * self._cal_T3_data) >> 14
        # self.t_fine = var1 + var2
        # temp = (self.t_fine * 5 +128) >> 8

        if self.debug:
            logger.debug(f"Debug: BMP280:Calibrated temperature = {temp} C")
        return temp/100

    def readPressure(self):
        "Gets the compensated pressure in pascal"
        # Pressure Calculations
        # uncomp_pressure = 415148
        uncomp_pressure = self.__readRawPressure()
        # var1 = self.t_fine - 128000
        # var2 = var1 * var1 * self._cal_P6_data
        # var2 = var2 + ((var1 * self._cal_P5_data) << 17)
        # var2 = var2 + (self._cal_P4_data << 35)
        # var1 = ((var1 * var1 * self._cal_P3_data) >> 8) + ((var1 * self._cal_P2_data) << 12)
        # var1 = (((1 << 47) + var1) * self._cal_P1_data) >> 33
        # p = 1048576 -uncomp_pressure
        # p =  (((p << 31) - var2) * 3125) // var1
        # var1 = (self._cal_P9_data * (p >> 13) * (p >> 13)) >> 25
        # var2 =  (self._cal_P8_data * p) >> 19
        # pressure = ((p + var1 +var2) >> 8) + (self._cal_P7_data << 4)

        var1 = (self.t_fine // 2) - 64000
        var2 = (((var1 // 4)**2) // 2048) * self._cal_P6_data
        var3 = var2 + (var1 * self._cal_P5_data * 2)
        var4 = (var3 // 4) + (self._cal_P4_data * 65536)
        var5 = (((self._cal_P3_data * (((var1 // 4)**2) // 8192)) // 8) +
                ((self._cal_P2_data * var1) // 2)) // 262144
        var6 = ((32768 + var5) * self._cal_P1_data) // 32768
        p1 = ((1048576 - uncomp_pressure) - (var4 // 4096)) * 3125
        if p1 < 0x80000000:
            p2 = (p1 << 1) // var6
        else:
            p2 = (p1 // var6) * 2
        var7 = (self._cal_P9_data * (((p2 // 8)**2) // 8192)) // 4096
        var8 = ((p2 // 4) * self._cal_P8_data) // 8192
        pressure = p2 + (var7 + var8 + self._cal_P7_data) // 16

        # var1 = self.t_fine/2 -64000
        # var2 = var1 * var1 * self._cal_P6_data/32768
        # var2 = var2 + var1* self._cal_P5_data * 2
        # var2 = var2/4 + self._cal_P4_data * 65536
        # var1 = self._cal_P3_data * var1 * var1/524288 + self._cal_P2_data * var1/524288
        # var1 = (var1/32768 + 1) * self._cal_P1_data
        # p = 1048576 - uncomp_pressure
        # p = p-var2/4096 * 6250/var1
        # var1 = self._cal_P9_data * p * p/2147483648
        # var2 = p * self._cal_P8_data/32768
        # pressure = p + (var1 + var2 + self._cal_P7_data)/16
        if self.debug:
            logger.debug("Debug: BMP280:Calibrated Pressure = %d Pa" % (pressure))
        return pressure

    # def get(self):
    #     adc_T = self.__readRawTemp()
    #     # adc_T = 519888
    #     var1 = (((adc_T >> 3) -
    #              (self._cal_T1_data << 1)) * self._cal_T2_data) >> 11
    #     var2 = (((((adc_T >> 4) - self._cal_T1_data) *
    #               ((adc_T >> 4) - self._cal_T1_data)) >> 12) *
    #             self._cal_T1_data) >> 14
    #     t = var1 + var2
    #     self.T = ((t * 5 + 128) >> 8) / 100
    #     var1 = (t >> 1) - 64000
    #     var2 = (((var1 >> 2) * (var1 >> 2)) >> 11) * self._cal_P6_data
    #     var2 = var2 + ((var1 * self._cal_P5_data) << 1)
    #     var2 = (var2 >> 2) + (self._cal_P4_data << 16)
    #     var1 = (((self._cal_P3_data * ((var1 >> 2) *
    #                                    (var1 >> 2)) >> 13) >> 3) +
    #             (((self._cal_P2_data) * var1) >> 1)) >> 18
    #     var1 = ((32768 + var1) * self._cal_P1_data) >> 15
    #     if var1 == 0:
    #         return  # avoid exception caused by division by zero
    #     adc_P = self.__readRawPressure()
    #     # adc_P = 415148
    #     p = ((1048576 - adc_P) - (var2 >> 12)) * 3125
    #     if p < 0x80000000:
    #         p = (p << 1) // var1
    #     else:
    #         p = (p // var1) * 2
    #     var1 = (self._cal_P9_data * (((p >> 3) * (p >> 3)) >> 13)) >> 12
    #     var2 = (((p >> 2)) * self._cal_P8_data) >> 13
    #     self.P = p + ((var1 + var2 + self._cal_P7_data) >> 4)
    #     return [self.T, self.P]

    def _getStatus(self):
        return self.i2c.readBlockData(0xF3, 8)

    def reset(self):
        self.i2c.writeU8(0xE0, 0xB6)

    def _ctrlMeas(self):
        self.i2c.writeU8(self.__CONTROL_REG, 0x25) #force mode ,p: oversampling ×1 , t:oversampling ×1
        time.sleep(.1)
        self.i2c.writeU8(0xF5, 0x70) #4s report in normal mode and filter is off


# a = BMP280(bus=1)
# # # # a._ctrlMeas()
# # # # a.reset()
# n = 0
# while n < 600:
#     temp = a.readTemperature()
#     pressure = a.readPressure()
#     print(temp,pressure)
#     n += 1
#     time.sleep(5)
# # a.reset()
# print(a.get())
