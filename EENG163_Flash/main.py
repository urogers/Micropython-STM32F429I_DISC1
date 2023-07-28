# main.py -- put your code here!

from touch811 import Touch811
from lcd9341 import LCD9341, color565
from xglcd_font import XglcdFont
from machine import Pin, SoftI2C, SPI
from time import sleep

#ST32 DISCO1 LCD Port
LCD_SPI_BUS = 5
SPI5_BAUD_RATE = 10_000_000

#ST32 DISCO1 I2C Port for touch
FREQ_I2C = 1_000_000
STMPE811_I2C_ADDR = 0x41
DISCO1_SCL_PIN = 'PA8'
DISCO1_SD_PIN = 'PC9'   
i2c = SoftI2C(scl=Pin(DISCO1_SCL_PIN), sda=Pin(DISCO1_SD_PIN ), freq=FREQ_I2C)     
tt = Touch811(i2c, STMPE811_I2C_ADDR, rotation = 0)

# Configure LCD Display
spi = SPI(LCD_SPI_BUS, baudrate=SPI5_BAUD_RATE)
        
# SPI5  SCK/MISO/MOSI   PF7/8/9   19/20/21
# 19-PF7-DCX/SCL-RS/SCL  SPI5_SCK
# 20-PF8 -               SPI5_MISO 
# 21-PF9- SDA - SDA      SP5_MOSI

#   28-PC2-CSX-CS, 81-PD12-RDx-RD, 80-PD11-TE-TE   82-PD13-WRX/ DCX - WR
# Note:  The reset is not connected, so use a throw away pin.  PC11 is unconnected
lcd = LCD9341(spi, dc=Pin('PD13'), cs=Pin('PC2'), rst=Pin('PC11'))

lcd.draw_circle(2, 2, 2, color565(255, 0, 0))
lcd.draw_circle(80, 110, 2, color565(255, 255, 255))
lcd.draw_circle(160, 220, 2, color565(255, 255, 255))
lcd.draw_circle(237, 317, 2, color565(0, 255, 255))

lcd.draw_text8x8(5, 130, 'Touch The Screen', color565(0, 255, 0))
lcd.draw_text8x8(8, 140, 'Multiple Times', color565(0, 255, 0))

print('Loading arcadepix')
arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
lcd.draw_text(50, 0, 'Arcade Pix 9x11', arcadepix, color565(255, 0, 0))
                      
print('Loading Bally')
bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
lcd.draw_text(30, 50, 'bally 7x9 or 5x8', bally,
                      color565(255, 0, 0))

print('Loading Unispace12x24')
unispace = XglcdFont('fonts/Unispace12x24.c', 12, 24)
lcd.draw_text(50, 220, 'Unispace 12x24', unispace,
                      color565(255, 255, 255))

sleep(2)

print('Touches are [x, y, pressure]: \n', tt.get_xyz_touch_points())
tt.get_xyz_touch_points() 
