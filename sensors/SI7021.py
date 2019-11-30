import logging, time
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)


class SI7021:
    __Temperature_reg = 0x00
    __Humidity_reg = 0x01
    __Configuration = 0x02

    def __init__(self, address=0x40, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        self._writeConfig()

    def _writeConfig(self):
        self.i2c.writeBytesToI2c([0xE6,0x3A])

    def _readConfig(self):
        return self.i2c.readU8(0xE7)

    def readTemperature(self):
        raw_temp = self.i2c.read2Bytes(0xE3)
        temp_read = (raw_temp[0] << 8) + raw_temp[1]
        temp = round((175.72*temp_read/65536 - 46.85),2)
        if self.debug:
            logger.debug(f'Debug: SI7021:RAW_temp:{raw_temp},Temp:{temp}')
        return temp

    def readHumidity(self):
        raw_hum = self.i2c.read2Bytes(0xE5)
        hum_read = (raw_hum[0] << 8) + raw_hum[1]
        hum = round((125*hum_read/65536 - 6),2)
        if self.debug:
            logger.debug(f'Debug: SI7021: RAW_humidity:{raw_hum}, Humidity:{hum}')
        return hum


# a = SI7021(bus=1,debug=False)
# n = 0
# while n < 600:
#     # print(a._readConfig())
#     print(a.readTemperature(),a.readHumidity())
#     n += 1
#     time.sleep(1)
