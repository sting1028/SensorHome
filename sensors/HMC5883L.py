import logging, time
from .I2cBase import I2cBase
logger = logging.getLogger(__name__)


class HMC5883:

    def __init__(self, address=0x1e, bus=0, debug=False):
        self.i2c = I2cBase(address=address, bus=bus, debug=debug)
        self.address = address
        self.debug = debug
        self.config()

    def readData(self):
        raw_data = self.i2c.readBlockData(0x03,6)
        # if raw_data[0] >= 128:
        #     raw_data[0] -= 128
        x = raw_data[0] << 8 | raw_data[1]
        z = raw_data[2] << 8 | raw_data[3]
        y = raw_data[4] << 8 | raw_data[5]
        if x > 32768:
            x -= 65536
        if y > 32768:
            y -= 65536
        if z > 32768:
            z -= 65536
        return x,y,z
    
    def config(self):
        self.i2c.writeU8(0x00,0x12)
        self.i2c.writeU8(0x01,0x20)
        self.i2c.writeU8(0x02,0x00)



# a = HMC5883(bus=1)
# n = 0 

# while n < 600:
#     print(a.readData())
#     n += 1
#     time.sleep(1)

# # # # print(a.readConfig())
# # print(a.readTemperature(),a.readHumidity())
