import logging, time
from I2cBase import I2cBase
logger = logging.getLogger(__name__)

class HDC1080:
    __Temperature_reg = 0x00
    __Humidity_reg = 0x01
    __Configuration = 0x02

    def __init__(self, address=0x40, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug

    def configureSensor(self):
        self.i2c.writeByetsToI2c([self.__Configuration,0x00])

    def readTemp(self):
        self.i2c.writeByteToI2c(self.__Temperature_reg)
        return self.i2c.read2Bytes(self.__Temperature_reg)

    def readHum(self):
        self.i2c.writeByteToI2c(self.__Humidity_reg)
        return self.i2c.read2Bytes(self.__Humidity_reg)

    def readDevId(self):
        self.i2c.writeByteToI2c(0xFE)
        return self.i2c.read2Bytes(0xFE)

    def readBattery(self):
        self.i2c.writeByteToI2c(0x02)
        return self.i2c.read2Bytes(0x02)

a = HDC1080(bus=1)
a.configureSensor()
# time.sleep(0.0625)
devid = a.readDevId()
# battery = a.readBattery()
# temp = a.readTemp()
# hum = a.readHum()
print(devid)