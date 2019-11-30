import logging,struct
from smbus2 import SMBus, i2c_msg
logger = logging.getLogger(__name__)


class I2cBase:
    def __init__(self, address, bus=0, debug=False):
        self.address = address
        self.bus = SMBus(bus)
        self.debug = debug

    def open(self):
        self.bus.open('/dev/i2c-1')

    def close(self):
        self.bus.close()

    def writeU8(self, reg, value):
        "Write a byte to a given register"
        try:
            self.bus.write_byte_data(self.address, reg, value)
            if (self.debug):
                logger.debug(f"I2C: Write {value:#x} to register {reg:#x}")
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readU8(self, reg):
        "Read a single byte from a designated register"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readBlockData(self, reg, length):
        try:
            result = self.bus.read_i2c_block_data(self.address, reg, length)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def read2Bytes(self, reg):
        try:
            result = self.bus.read_i2c_block_data(self.address, reg, 2)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readS16_BMP085(self, reg):
        "Reads a signed 16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            if (hibyte > 127):
                hibyte -= 256
            result = (hibyte << 8) + self.bus.read_byte_data(
                self.address, reg + 1)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readU16_BMP085(self, reg):
        "Reads an unsigned 16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            result = (hibyte << 8) + self.bus.read_byte_data(
                self.address, reg + 1)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def read_byte(self):
        return self.bus.read_byte(self.address)
    
    def writeBlock(self, reg, value):
        try:
            self.bus.write_i2c_block_data(self.address, reg, value)
            if (self.debug):
                logger.debug(f"I2C: Write {value} to register {reg:#x}")
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def writeBytesToI2c(self, value):
        try:
            msg = i2c_msg.write(self.address, value)
            self.bus.i2c_rdwr(msg)
            if (self.debug):
                logger.debug(f"I2C: Write {value} to I2C {self.address:#x}")
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def writeByteToI2c(self, value):
        try:
            self.bus.write_byte(self.address, value)
            if (self.debug):
                logger.debug(f"I2C: Write {value:#x} to I2C {self.address:#x}")
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readByteFromI2c(self):
        "Read a single byte from a i2c address"
        try:
            result = self.bus.read_byte(self.address)
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from I2C {self.address:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1
    
    def readS16_BMP280(self, reg):
        "Reads a signed short intger16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            lowbyte = self.bus.read_byte_data(self.address, reg + 1)
            buf = bytearray(2)
            buf[0] = hibyte
            buf[1] = lowbyte
            result = struct.unpack('<h',buf)[0]
            # hibyte = self.bus.read_byte_data(self.address, reg)
            # result = (hibyte << 8) + self.bus.read_byte_data(
            #     self.address, reg + 1)
            # if result > 32767:
            #     return (result - 65536)
            # else:
            #     return result
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readU16_BMP280(self, reg):
        "Reads an unsigned short intger 16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            lowbyte = self.bus.read_byte_data(self.address, reg + 1)
            buf = bytearray(2)
            buf[0] = hibyte
            buf[1] = lowbyte
            result = struct.unpack('<H',buf)[0]
            if (self.debug):
                logger.debug(
                    f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logger.debug(
                f"Error accessing {self.address:#x}: Check your I2C address")
            return -1