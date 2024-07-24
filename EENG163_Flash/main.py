# main.py -- put your code here!

from touch811 import Touch811
from lcd9341 import LCD9341, color565
#[JAS] Font engine changed from firmware v1.20.0_163 to v1.23.0_163, use only one!
from xfglcd_font import XglcdFont # for firmware v1.23.0.163, supports "frozen" fonts
#from xglcd_font import XglcdFont # for firmware v1.20.0.163
from machine import Pin, SoftI2C, SPI
from time import sleep
#[JAS] "frozen" fonts (not present in firmware v1.20.0_163)
from ArcadePix9x11_Froze import ArcadePix9x11
from Bally7x9_Froze import Bally7x9
#from Broadway17x15_Froze import Broadway17x15
#from EspressoDolce18x24_Froze import EspressoDolce18x24
#from IBMPlexMono12x24_Froze import IBMPlexMono12x24
from Robotron13x21_Froze import Robotron13x21
from Unispace12x24_Froze import Unispace12x24

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

#[JAS] All fonts using firmware v1.23.0_163 "frozen" fonts by default, arcadepix will show an alternate method
print('Loading arcadepix')
arcadepix = ArcadePix9x11() # firmware v1.23.0_163 only
#arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11) # requires specified font file in fonts folder on drive
lcd.draw_text(50, 0, 'Arcade Pix 9x11', arcadepix, color565(255, 0, 0))
                      
print('Loading Bally')
bally = Bally7x9()
lcd.draw_text(30, 50, 'bally 7x9 or 5x8', bally,
                      color565(255, 0, 0))

#print('Loading Broadway')
#broadway = Broadway17x15()
#lcd.draw_text(10, 70, 'Broadway 17x15', broadway, color565(0,0,255))

#print('Loading EspressoDolce')
#espresso = EspressoDolce18x24()
#lcd.draw_text(10, 70, 'EspressoDolce 18x24', espresso, color565(0,0,255))

#print('Loading IBMPlexMono')
#ibmplex = IBMPlexMono12x24()
#lcd.draw_text(10, 70, 'IBMPlexMono 12x24', ibmplex, color565(0,0,255))

print('Loading Robotron')
robotron = Robotron13x21()
lcd.draw_text(10, 70, 'ROBOTRON 12X24', robotron, color565(0,0,255))

print('Loading Unispace12x24')
unispace = Unispace12x24()
lcd.draw_text(50, 220, 'Unispace 12x24', unispace,
                      color565(255, 255, 255))

sleep(2)

print('Touches are [x, y, pressure]: \n', tt.get_xyz_touch_points())
tt.get_xyz_touch_points() 
