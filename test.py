# print(34671 << 1)
# var1 = ((((uncomp_temp / 8) - (self._cal_T1_data << 1))) * (self._cal_T1_data << 1)) / 2048

# uncomp_temp  = 519888
# cal_T1_data = 27504
# cal_T2_data = 26435
# cal_T3_data = -1000
# var1 = (uncomp_temp/16384 - cal_T1_data/1024) * cal_T2_data
# var2 = (uncomp_temp/131072 - cal_T1_data/8192) * ((uncomp_temp/131072-cal_T1_data/8192)*cal_T3_data)
# t_fine = var1 + var2
# temp = t_fine/5120
# print(temp)
# print(var1,var2)

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
import time
from sensors.BMP085 import BMP085
from sensors.BMP280 import BMP280
from sensors.SI7021 import SI7021
from sensors.CCS811 import CCS811
from sensors.BH1750 import BH1750
from sensors.HMC5883L import HMC5883
ccs81 = CCS811(bus=1)
bmp08 = BMP085(bus=1)
bmp28 = BMP280(bus=1)
SI702 = SI7021(bus=1)
bh1750 = BH1750(bus=1)
hmc588 = HMC5883(bus=1)
n = 1
while n < 600:
    print(f'lx:{bh1750.readData()}')
    print(f'bmp085:{bmp08.readTemperature()}C,{bmp08.readPressure()}Pa')
    print(f'bmp280:{bmp28.readTemperature()}C,{bmp28.readPressure()}Pa')
    temp = SI702.readTemperature()
    hum = SI702.readHumidity()
    print(f'si702:{temp}C,{hum}%')
    print(f'{ccs81.readData(humidity=hum,temp=temp)}ppm,ppb')
    print(f'{hmc588.readData()}')
    print('-------------------------------')
    time.sleep(2)
    n += 1