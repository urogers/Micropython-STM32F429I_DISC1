"""STMPE811QTR I2C Touch Controller for the ILI9341 LCD/Touch module."""
from machine import Pin, SoftI2C 


class Touch811(object):
    ''' I2C Interface to the STMPE811 touch screen controller for the ILI9341 LCD/Touch Screen
    Note:  A calibration is recommended to align touch and display pixel locations
    See "Touchscreen controller programming sequence" in the STMPE811 data sheet
    
    Configuration of interrupts for detecting a touch is not currently supported
    '''
    CHIP_ID = const(0x00)    # Reset value 0x0811, 16 bit
    ID_VER = const(0x02)     # ID #, 0x03 (0x01 for engineering samples)
    SYS_CTRL1 = const(0x03)  # Bit 1 is soft reset, bit 0 Hibernate
    SYS_CTRL2 = const(0x04)  # Reset: 0x0F (all clocks off), bit 1 is Touch Screen Clock, active low
    SPI_CFG = const(0x08)    # Not using SPI, so this is a reference place holder
    INT_CTL = const(0x09)    # Configure Touch Interrupt Interface (Polarity, Level, ...)
    INT_EN = const(0x0A)     # Bit 0 is for Touch Detect, active high
    INT_STA = const(0x0B)    # InterruptStatus register, bit 0 is touch detect
    GPIO_INT_EN = const(0x0C)    # No GPIO Interrupts
    GPIO_INT_STA = const(0x0D)   
    ADC_INT_EN = const(0x0A)     # No ADC usage Interrupts
    ADC_INT_STA = const(0x0F)
    # Not Coding ADC  0x20, 0x21, 0x22, 0x30, 0x32, 0x34, 0x36, 0x3A, 0x3C, 0x3E
    TSC_CTRL = const(0x40)   #4-wire Touchscreen Controller setup.  0x90 Power On
    TSC_CFG =const(0x41)
    WDW_TR_X = const(0x42)   # 12 bits (Blocking Window to ignore touches)
    WDW_TR_Y = const(0x44)   # 12 bits
    WDW_BL_X = const(0x46)   # 12 bits
    WDW_BL_Y = const(0x48)   # 12 bits
    FIFO_TH = const(0x4A)    # Trigger level for interrupt, must not be set to 0
    FIFO_STA = const(0x4B)
    FIFO_SIZE = const(0x4C)  # Available # of samples
    TSC_DATA_X  = const(0x4D)    # x-data 12 bits
    TSC_DATA_Y  = const(0x4F)    # y-data 12 bits
    TSC_DATA_Z  = const(0x51)    # z-data 12 bits read, 8 bit value 
    TSC_DATA_XYZ  = const(0x57)  # See options, 4 byte read
    TSC_I_DRIVE = const(0x58)
    TSC_SHIELD = const(0x59)
    TSC_FRACTION_Z = const(0x56)
    # Not Coding Temp Sensor 0x60, 0x61, 0x63, and GPIO Controller 
    # 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17
    
    SW_RESET = const(0x02)      #Soft Reset in SYS_CTRL1
    CLEAR_FIFO = const(0x01)    #Reset FIFO in FIFO_STA
    STMPE811_ID = const(0x0811)
    EN_TSC = const(0x01)        # Enable is bit 0 in TSC_CTRL
    CONFIG_TSC = const(0xE4)    # In TSC_CFG [7:6] 0b11 -> 8 sample avg, [5:3] 0b100 -> 1m Touch Delay, [2:0] 0b100 -> 5ms settling
    TS_on_GPIO_off_TSC_on_ADC_on = const(0x04)  # Enable Clocks for Temp Sensor, Touch Controller, & ADC, leave GPIO Off (active low)
    
    ROTATE = (0, 90, 180, 270)
    SLOPE_X = const(1.13)      # Calibration slope for x,  x_pix = x_touch*m_x+b_x
    SLOPE_Y = const(1.145)     # Calibration slope for y,  y_pix = y_touch*m_y+b_y
    OFFSET_X = const(-15)
    OFFSET_Y = const(-13)
        
        
    def __init__(self, i2c_obj, i2c_address=0x41, x_pixels=240, y_pixels=320, rotation=0, tracking_window=6):
        '''Initialize Touch Controller.
        Args:
            i2c_obj (Class SoftI2C):  I2C Interface to stmpe811
            i2c_address (Optional int):  I2C bus address
            x_pixels (Optional int): Screen width (default 240)
            y_pixels (Optional int): Screen height (default 320)
            rotation (Optional int): Rotation matches LDC orientation {0, 90, 180, 270}
            tracking_window (Optional int): Ignore multiple touches within a window (7 is largest, 0 is no window)
        '''
        self._i2c = i2c_obj
        self._address = i2c_address
        self._x_pix = x_pixels
        self._y_pix = y_pixels
        
        self._m_x = SLOPE_X
        self._m_y = SLOPE_Y
        self._b_x = OFFSET_X
        self._b_y = OFFSET_Y   # y_pix = m_y*y_touch+b_y
        
        if rotation in self.ROTATE:
            self._rotation = rotation
        else:
            raise ValueError('Rotation must be 0, 90, 180, or 270 degrees')
        
        if tracking_window in range(8):
            track_window = tracking_window<<4    #0 is most sensitive, 7 least (bits [6:4])
        else:
            raise ValueError('Tracking window must be in [0, 7]')
        
        # Check for communications
        chip_id = self.i2c_read(CHIP_ID, 2)
        # print('Chip ID=', chip_id)
        if chip_id != STMPE811_ID:
            raise RuntimeError('STMPE811 I2C Error.  Could not validate the Chip ID')
        
        self.i2c_write(SYS_CTRL1, SW_RESET)       # Reset the Touch Controller
        self.i2c_write(SYS_CTRL2, TS_on_GPIO_off_TSC_on_ADC_on)       # Turn clocks On for TS, TSC, ADC, and off for GPIO (Active Low)
        
        self.i2c_write(FIFO_TH, 0x01)         # Set the threshold for # of touches for interrupts to be signaled
        self.i2c_write(TSC_CFG, CONFIG_TSC)   # Use setter to fine tune
        self.i2c_write(TSC_CTRL, track_window + EN_TSC)

    def is_touched(self):
        num_touches = self.i2c_read(FIFO_SIZE)
        if num_touches == 0:
            return False
        else:
            return True
    
    def set_tsc_config(self, op_mode = 0, window=None, average=None, touch_delay=None, settle=None):
        ''' Configure the TSC_CTRL and TSC_CFG Parameters
        Resets TSC and FIFO Buffers
        Parameters that are not passed in, use the value currently in the register.
        Args:
            average (Opt Int):      b[7:6] in TSC_CFG:  2**average = # of averages made
            touch_delay (Opt Int):  b[5:3] in TSC_CFG:  0->10us, 1->50us, 2->100us, 3->500us, ... 7->50ms
            settle (Opt Int):       b[2:0] in TSC_CFG:  0->10us, 1->100us, 2->500us, 3->1ms, ... 7->100ms
            window (Opt Int):       b[6:4] in TSC_CTRL  0 No Window, 1->4, 2->8, 3->16, 4->32, 5->64, 6->92, 7->127
            op_mode (Opt Int):      b[3:1] in TSC_CTRL  0->XYZ), 1->XY, 2->X only, 3->Y only, 4->Z only
        '''
        
        tsc_cfg_val = self.i2c_read(TSC_CFG)
        print('TSC_CFG =', hex(tsc_cfg_val))
        tsc_ctrl_val = self.i2c_read(TSC_CTRL)
        print('TSC_ctrl =', hex(tsc_ctrl_val))
        
        #First Error Checking
        if op_mode in range(5):
            touch_mode = op_mode<<1   
        else:
            raise ValueError('Operating Mode must be in [0, 4]')
      
        if window == None:
            track_window = tsc_ctrl_val & 0x70
        elif window in range(8):
           track_window = window<<4   
        else:
            raise ValueError('Tracking window must be in [0, 7]')
            
        if average == None:
            avg = tsc_cfg_val & 0xC0
        elif average in range(4):
            avg = average<<6
        else:
            raise ValueError('Average must be in [0, 3]')
        
        if touch_delay == None:
            tch_delay = tsc_cfg_val & 0x38
        elif touch_delay in range(8):
            tch_delay = touch_delay<<3   
        else:
            raise ValueError('Touch Delay must be in [0, 7]')
        
        if settle == None:
            settle_time = tsc_cfg_val & 0x07
        elif settle in range(8):
            settle_time = settle
        else:
            raise ValueError('Settle Time must be in [0, 7]')
        
        self.i2c_write(TSC_CTRL, 0x00)         # Disable TSC
        self.i2c_write(FIFO_STA, CLEAR_FIFO)   # Reset the FIFO
        self.i2c_write(TSC_CFG, avg + tch_delay + settle_time)
        self.i2c_write(TSC_CTRL, track_window + touch_mode + EN_TSC) # Modify & Enable TSC
        
        tsc_cfg_val = self.i2c_read(TSC_CFG)
        print('TSC_CFG =', hex(tsc_cfg_val))
        tsc_ctrl_val = self.i2c_read(TSC_CTRL)
        print('TSC_ctrl =', hex(tsc_ctrl_val))
    
    def get_num_touches(self):
        num_touches = self.i2c_read(FIFO_SIZE)
        return num_touches
    
    def get_xyz_touch_points(self): 
        '''Reads the touch buffer for x, y, and pressure points the screen reports'''
        
        num_touches = self.i2c_read(FIFO_SIZE)  
        touches = []
        while num_touches > 0:
            x_raw = self.i2c_read(TSC_DATA_X, 2)
            y_raw = self.i2c_read(TSC_DATA_Y, 2)
            pressure_raw = self.i2c_read(TSC_DATA_Z, 2)
                
            if self._rotation == 0:
                touches.append([self._x_pix-int(x_raw/4095*self._x_pix*self._m_x + self._b_x), 
                    self._y_pix-int(y_raw/4095*self._y_pix*self._m_y + self._b_y), 
                    pressure_raw/255])
                
            elif self._rotation == 90:
                touches.append([self._y_pix-int(y_raw/4095*self._y_pix*self._m_y + self._b_y), 
                    int(x_raw/4095*self._x_pix*self._m_x + self._b_x), 
                    pressure_raw/255])
                
            elif self._rotation == 180:
                touches.append([int(x_raw/4095*self._x_pix*self._m_x + self._b_x), 
                    int(y_raw/4095*self._y_pix*self._m_y + self._b_y), 
                    pressure_raw/255])
            
            else:
                touches.append([int(y_raw/4095*self._y_pix*self._m_y + self._b_y), 
                    self._x_pix-int(x_raw/4095*self._x_pix*self._m_x + self._b_x), 
                    pressure_raw/255])
                
            num_touches = self.i2c_read(FIFO_SIZE)        # Note:  Asynchronous touches (can change in loop)

        return touches  
    
    def get_xyz_unique(self, deviation=5): 
        all_touches = self.get_xyz_touch_points() 
        if len(all_touches) != 0:
            return self.check_xy_match(all_touches, deviation)
        else:
            return all_touches
        
    # Now Helper Methods
    def check_xy_match(self, list_touch_points, delta_xy=5):
        '''Here the xyz touch points are parsed to see if consecutive x & y are essentially the same 
        (within a delta_xy of one other) while pressure is ignored. 
        
        Args:
            list_touch_points: list of list: [x,y,p] points
            delta_xy (int): Green value.
        Return:
            List of lists'''
            
        all_unique = []
        unique_xyz = list_touch_points[0][:]           #First is unique by definition
        all_unique.append(unique_xyz[:])
         
        for ii in range(1,len(list_touch_points)):
            next_xyz = list_touch_points[ii][:]
            
            if abs(unique_xyz[0]-next_xyz[0]) > delta_xy or abs(unique_xyz[1]-next_xyz[1]) > delta_xy:
                all_unique.append(next_xyz)
                unique_xyz = next_xyz[:]
               
        return all_unique
        
    # 
    def i2c_read(self, reg, bytes=1):
        if bytes in [1, 2, 3, 4]:
            _ = self._i2c.writeto(self._address, bytearray([reg]))
            data = self._i2c.readfrom(self._address, bytes)
            if bytes == 1:
                value = data[0]
            elif bytes == 2:
                value = data[0]<<8 | data[1]
                # print('Value =', value)
            elif bytes == 3:
                value = data[0]<<16 | data[1]<<8 | data[2]
            else:
                value = data[0]<<24 | data[1]<<16 | data[2]<<8 | data[3]
        else:
            raise ValueError('Byte Error')
            value = -1
        return value
        
    def i2c_write(self, reg, value):
        return_value = self._i2c.writeto(self._address, bytearray([reg, value]))
        # Do Error Checking
        
    
# End Touch811 Class 