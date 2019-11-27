import logging, time
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)


class CCS811:
    __BASELINE = 0x11
    __HW_ID = 0x20
    __Status = 0x00
    __ALG_RESULT_DATA = 0x02
    __ERROR = 0xE0
    __BOOTLOADER_APP_START = 0xF4
    __MeasMode = 0x01
    __ResetSW = 0xFF
    __BaseLine = 0x11
    __ResetData = [0x11, 0xE5, 0x72, 0x8A]
    __MeasModeData = 0x10  #Constant power mode, IAQ measurement 0x10 for every second/ 0x20 for every 10sec/ 0x30 for every 60sec
    __EnvData = 0x05

    def __init__(self, address=0x5A, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        self._readError()
        self.initSensor()

    def _startApp(self):
        self.i2c.writeByteToI2c(self.__BOOTLOADER_APP_START)
        # time.sleep(.1)
        # self.i2c.writeAddress([self.__BOOTLOADER_APP_START,])

    def _readStatus(self):
        self.i2c.writeByteToI2c(self.__Status)
        # time.sleep(.1)
        return self.i2c.readByteFromI2c()

    def _readHwId(self):
        self.i2c.writeByteToI2c(self.__HW_ID)
        # time.sleep(.1)
        return self.i2c.readByteFromI2c()

    def _writeMeasMode(self):
        self.i2c.writeU8(self.__MeasMode, self.__MeasModeData)
        # time.sleep(.1)

    def _readResults(self):
        self.i2c.writeByetsToI2c(self.__ALG_RESULT_DATA)
        # time.sleep(.1)
        return self.i2c.readBlockData(self.__ALG_RESULT_DATA, 5)

    def _resetSW(self):
        self.i2c.writeBlock(self.__ResetSW, self.__ResetData)
        # time.sleep(.5)

    def _readError(self):
        self.i2c.writeByteToI2c(self.__ERROR)
        # time.sleep(.1)
        return self.i2c.readByteFromI2c()

    def _readMeasMode(self):
        self.i2c.writeByteToI2c(self.__MeasMode)
        # time.sleep(.1)
        return self.i2c.readByteFromI2c()

    def _setEnv(self, humidity, temperature):
        hum = hex(round(humidity * 512))[2:]
        temp = hex(round((temperature + 25) * 512))[2:]
        data = list(bytearray.fromhex(hum)) + list(bytearray.fromhex(temp))
        self.i2c.writeBlock(self.__EnvData, data)
        # time.sleep(.1)

    def _readBaseLine(self):
        self.i2c.writeByteToI2c(self.__BASELINE)
        return self.i2c.read2Bytes(self.__BASELINE)

    def initSensor(self):
        if self._readStatus() == 16:
            self._startApp()
            while self._readStatus() != 144:
                time.sleep(0.5)
                self._startApp()
                print('Try to Start App')
            self._writeMeasMode()
            while self._readMeasMode() != self.__MeasModeData:
                time.sleep(0.5)
                self._writeMeasMode()
                print('Try to Setting MeasMode')
        else:
            pass

    def readData(self, humidity=None, temp=None):
        if humidity or temp:
            self._setEnv(humidity, temp)
        # meas_mode = self.readMeasMode()
        # print(f'meas_mode:{meas_mode}')
        # while meas_mode != 16:
        #     print(f'meas_mode:{self._writeMeasMode()}')
        #     time.sleep(10)
        status = (144, 145, 255, 0)
        data = self._readResults()
        while type(data) is int:
            time.sleep(2)
            data = self._readResults()
        while data[4] in status:
            time.sleep(2)
            data = self._readResults()
        # if data[0] >= 128:
        #     data[0] -= 128
        # if data[2] >= 128:
        #     data[2] -= 128
        if data != -1:
            co2 = data[0] << 8 | data[1]
            voc = data[2] << 8 | data[3]
        else:
            co2 = -1
            voc = -1
        while self._readHwId() != 129:
            self.initSensor()
            data = self._readResults()
        return co2, voc
    
# a = CCS811(bus=1)
# # # a._resetSW
# # # a._startApp()
# # a._writeMeasMode()
# # print(a._readBaseLine())
# n = 0
# while n < 600:
#     # print(f'measMode:{a._readMeasMode()}')
#     print(f'status: {a._readStatus()}')
#     # print(f'error:{a._readError()}')
#     print(f'result:{a.readData(humidity=50, temp=21)}')
#     print('_______________________________________')
#     n += 1
#     time.sleep(1)

