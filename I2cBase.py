import smbus2,logging


class I2cBase:
    def __init__(self, address, bus=0, debug=False):
        self.address = address
        self.bus = smbus2.SMBus(bus)
        self.debug = debug

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        try:
            self.bus.write_byte_data(self.address, reg, value)
            if (self.debug):
                logging.debug(f"I2C: Write {value:#x} to register {reg:#x}")
        except IOError:
            logging.debug(f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readU8(self, reg):
        "Read an unsigned byte from the I2C device"
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if (self.debug):
                logging.debug(f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logging.debug(f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readU16(self, reg):
        "Reads an unsigned 16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            result = (hibyte << 8) + self.bus.read_byte_data(
                self.address, reg + 1)
            if (self.debug):
                logging.debug(f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logging.debug(f"Error accessing {self.address:#x}: Check your I2C address")
            return -1

    def readS16(self, reg):
        "Reads a signed 16-bit value from the I2C device"
        try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            if (hibyte > 127):
                hibyte -= 256
            result = (hibyte << 8) + self.bus.read_byte_data(
                self.address, reg + 1)
            if (self.debug):
                logging.debug(f"I2C: Returned {result:#x} from register {reg:#x}")
            return result
        except IOError:
            logging.debug(f"Error accessing {self.address:#x}: Check your I2C address")
            return -1


