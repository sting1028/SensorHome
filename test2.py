
# import struct
# a = bytearray(2)
# a[0] = 0xAA
# a[1] = 0xAB
# print(struct.unpack('h',a))

# hibyte = 0xAB
# lowbyte = 0xAA

# if (hibyte > 127):
#     hibyte -= 256

# result = (hibyte << 8) + lowbyte

# # if result > 32767:
# #             result = result - 65536
# print(result)
# a = 113056
# b = struct.pack('i', a)
# print(struct.unpack('I',b))

import time,sys,logging
from pathlib import Path
from datetime import datetime

from sensors.BMP085 import BMP085
from sensors.BMP280 import BMP280
from sensors.SI7021 import SI7021
from sensors.CCS811 import CCS811
from sensors.BH1750 import BH1750
from sensors.HMC5883L import HMC5883
ccs81 = CCS811(bus=1,debug=True)
bmp08 = BMP085(bus=1,debug=True)
bmp28 = BMP280(bus=1,debug=True)
SI702 = SI7021(bus=1,debug=True)
bh1750 = BH1750(bus=1,debug=True)
hmc588 = HMC5883(bus=1,debug=True)
n = 1

def log_config():
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    log_folder = Path(sys.path[0], 'log/')
    if not log_folder.exists():
        log_folder.mkdir(log_folder)
    log_filename = f"{Path(log_folder,date_time)}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '{asctime} - {levelname} - {name} - {lineno} - {funcName} ::: {message}',
        filename=log_filename,
        style='{',
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    
log_config()

while n < 600:
    bh1750.readData()
    bmp08.readTemperature()
    bmp08.readPressure()
    bmp28.readTemperature()
    bmp28.readPressure()
    temp = SI702.readTemperature()
    hum = SI702.readHumidity()
    ccs81.readData(humidity=hum,temp=temp)
    hmc588.readData()
    print('-------------------------------')
    time.sleep(60)
    n += 1
