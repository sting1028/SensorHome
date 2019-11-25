import logging, time
from I2cBase import I2cBase
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
    __ResetData = [0x11, 0xE5, 0x72, 0x8A]
    __MeasModeDataSec = 0x10  #Constant power mode, IAQ measurement every second
    __MeasModeData10Sec = 0x20  #Constant power mode, IAQ measurement every 10second
    __MeasModeData60Sec = 0x30  #Constant power mode, IAQ measurement every 60second
    __EnvData = 0x05

    def __init__(self, address=0x5A, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        # self._resetSW()
        # time.sleep(1)
        self.initSensor()

    def _startApp(self):
        self.i2c.writeByteToI2c(self.__BOOTLOADER_APP_START)
        # self.i2c.writeAddress([self.__BOOTLOADER_APP_START,])

    def _readStatus(self):
        return self.i2c.readU8(self.__Status)

    def _readHwId(self):
        return self.i2c.readU8(self.__HW_ID)

    def _writeMeasMode(self):
        self.i2c.writeU8(self.__MeasMode, self.__MeasModeDataSec)

    def _readResults(self):
        return self.i2c.readBlockData(self.__ALG_RESULT_DATA, 8)

    def _resetSW(self):
        self.i2c.writeBlock(self.__ResetSW, self.__ResetData)

    def _readError(self):
        return self.i2c.readU8(self.__ERROR)

    def setEnv(self, humidity, temperature):
        hum = hex(round(humidity * 512))[2:]
        temp = hex(round((temperature + 25) * 512))[2:]
        data = list(bytearray.fromhex(hum)) + list(bytearray.fromhex(temp))
        self.i2c.writeBlock(self.__EnvData, data)

    def initSensor(self):
        status = self._readStatus()
        print(f'staus:{status}')
        if status != 152:
            id = self._readHwId()
            print(f'id:{id}')
            while id != 129:
                time.sleep(1)
            self._startApp()
            time.sleep(2)
            self._writeMeasMode()
            time.sleep(5)
            status = self._readStatus()
            print(f'status:{status}')
            n = 0
            while status != 152:
                time.sleep(2)
                status = self._readStatus()
                n += 1
                if n > 5:
                    self._writeMeasMode()
                    time.sleep(5)
                    n = 0
                print(f'status:{status}')
                print('Setting Measurement Mode')
        else:
            pass


    def readData(self, humidity=None, temp=None):
        if humidity or temp:
            self.setEnv(humidity, temp)
            time.sleep(2)
        while self._readHwId() != 129:
            time.sleep(2)
        # if self.readMeasMode != 16:
        #     self._writeMeasMode()
        #     time.sleep(10)
        data = self._readResults()
        co2 = data[0] << 8 | data[1]
        voc = data[2] << 8 | data[3]
        return co2, voc, data
    
    def readMeasMode(self):
        return self.i2c.readU8(self.__MeasMode)

a = CCS811(bus=1)
# a._resetSW
n = 0
while n < 600:
    print(f'measMode:{a.readMeasMode()}')
    print(f'status: {a._readStatus()}')
    print(f'id:{a._readHwId()}')
    print(f'result:{a.readData(humidity=50, temp=21)}')
    n += 1
    time.sleep(2)

