# STM32F429I_DISC1
MicroPython for STM32F4 Discovery Board (LCD &amp; Touch Drivers, DAC Support, 158K Flash Code Space)

=======================
<p align="center">
  <img src="https://raw.githubusercontent.com/urogers/micropython-stm32f429i_disc1/master/logo/stm32f429disc.jpg" width=25% height=25% alt="Discovery Logo"/ >
</p>

The content in this repository is in support of EENG 163, an introductory course in Python, Micropython, and Embedded Systems at Eastern Washington University.

The following MicroPython firware modifications have been made:
  - ILI9341 Display support (Based on the code from rdagger:  https://github.com/rdagger/micropython-ili9341, and speed enhancements proposed by sumnerk)
  - STMPE811QTR Touch Screen Driver  (IRQ is not currently supported)
  - Enabled DAC Support (PA_4 or DAC1 is a shared pin for VSYNC and does not work properly.  PA_5 or DAC2 works as expected)
  - Enabled 158K of Flash File Storage in Sectors 1-6 to allow larger code files.
  - Note:  The Fonts are not currently embedded in the Firmware.

The ILI9341 and STMPE811QTR drivers are embedded in the firmware, please see the Python source code in the /boards/STM32F429DISC/ directory. 

The Firmware Images are based on the official released version, with the enhancements listed previously.
 
