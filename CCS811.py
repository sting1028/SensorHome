import logging, time
from I2cBase import I2cBase
logger = logging.getLogger(__name__)


class CSS811:
    __BASELINE = 0x11
    __HW_ID = 0x20
    __Status = 0x00
    __ALG_RESULT_DATA  = 0x02
    __HW_VERSION = 0x21
    __FW_BOOT_VERSION = 0x23
    __FW_APP_VERSION = 0x24
    __ERROR = 0xE0
    __BOOTLOADER_APP_START = 0xF4
    __MeasMode = 0x01
    __ResetSW = 0xFF
    __ResetData = [0x11,0xE5,0x72,0x8A]
    __MeasModeDataSec = 0x10 #Constant power mode, IAQ measurement every second
    __MeasModeData10Sec = 0x20 #Constant power mode, IAQ measurement every 10second
    __MeasModeData60Sec = 0x30 #Constant power mode, IAQ measurement every 60second
    __EnvData = 0x05


    def __init__(self, address=0x5A, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug

    def _startApp(self):
        self.i2c.writeByteToI2c(self.__BOOTLOADER_APP_START)
        # self.i2c.writeAddress([self.__BOOTLOADER_APP_START,])

    def _readStatus(self):
        return self.i2c.readU8(self.__Status)

    def _readHwId(self):
        return self.i2c.readU8(self.__HW_ID)

    def _readHwVersion(self):
        return self.i2c.readU8(self.__HW_VERSION)

    def _readFwAppVersion(self):
        return self.i2c.read2Bytes(self.__FW_APP_VERSION)

    def _readFwBootVersion(self):
        return self.i2c.read2Bytes(self.__FW_BOOT_VERSION)

    def _writeMeasMode(self):
        self.i2c.writeU8(self.__MeasMode,self.__MeasModeData10Sec)

    def _readResults(self):
        return self.i2c.readBlockData(self.__ALG_RESULT_DATA,5)
    
    def _resetSW(self):
        self.i2c.writeBlock(self.__ResetSW,self.__ResetData)

    def _readError(self):
        return self.i2c.readU8(self.__ERROR)

    def setEnv(self,humidity,temperature):
        hum= hex(humidity * 512)[2:]
        temp = hex((temperature + 25) * 512)[2:]
        data = list(bytearray.fromhex(hum)) + list(bytearray.fromhex(temp))
        self.i2c.writeBlock(self.__EnvData,data)

    def initSensor(self):
        self._startApp()
        time.sleep(1)
        self._writeMeasMode()
        time.sleep(10)

    
    def readData(self,humidity,temp):
        self.setEnv(humidity,temp)
        time.sleep(0.2)
        data = self._readResults()
        co2 =  data[0] << 8 | data[1]
        voc = data[2] << 8 | data[3]
        return co2,voc,data

a = CSS811(bus=1)
# a._resetSW
# a.initSensor()
n = 0
while n < 600:
    status = a._readStatus()
    print(f'status:{status}')
    if status == 152:
        time.sleep(.6)
        result = a.readData(humidity=50,temp=21)
        print(f'result:{result}')
    #     if result[2][4] == 144:
    #         time.sleep(20)
    #         result = a.readData(humidity=50,temp=21)
    #         print(f'result:{result}')
    #     if result[2][4] == 255:
    #         time.sleep(2)
    #         result = a.readData(humidity=50,temp=21)
    #         print(f'result:{result}')
    # if status == 153:
    #     print(f'error:{a._readError()}')
    n += 1
    time.sleep(2)
