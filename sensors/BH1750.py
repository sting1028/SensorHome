import logging, time
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)


class BH1750:

    def __init__(self, address=0x23, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug

    def readData(self):
        self.i2c.writeByetsToI2c(0x11)
        time.sleep(0.2)
        raw_lx = self.i2c.read2Bytes(0x23)
        lx = round((((raw_lx[0] << 8) + raw_lx[1]) / 1.2),2)
        return lx



# a = BH1750(bus=1)
# n = 0 

# while n < 600:
#     print(a.readData())
#     n += 1
#     time.sleep(1)

# # print(a.readConfig())
# print(a.readTemperature(),a.readHumidity())
