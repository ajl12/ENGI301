
"""
--------------------------------------------------------------------------
Inflation Device
--------------------------------------------------------------------------
License:   
Copyright 2020 Alex Lammers

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

Use the following hardware components to make a programmable combination lock:  
  - HT16K33 Display
  - Button
  - Micro Air Pump
  - Normally-Closed Solenoid Valve (2)
  - 0-1 PSI pressure sensor
  
Requirements:
  - Hardware:
    - User Interface: 
        - When button is pressed, turn on the air pump to inflate blood pressure cuff
        - When button is pressed a second time, turn off pump
        - When button is pressed a third time, open solenoid valve to release air 
    - While cuff is inflating: Monitor air pressure and display messages based on pressure readings
    - While cuff is deflating: Monitor air pressure and display messages based on pressure readings
    - When pressure readings indicate full deflation: Reset solenoid valve

Uses:
  - Custom HT16K33 display library

"""
import time
import os

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.PWM as PWM

import ht16k33 as HT16K33


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

# None

# ------------------------------------------------------------------------
# Functions / Classes
# ------------------------------------------------------------------------

class InflationDevice():
    """ InflationDevice """

    button1  = None
    button2 = None
    pump    = None
    reset_time = None
    solenoid_1 = None
    analog_in  = None
    v_supply = None
    display    = None

    def __init__(self, button1="P2_2", button2="P2_8", pump="P2_4", reset_time=0.5, solenoid_1="P1_6",analog_in="P2_35",v_supply="P1_2",i2c_bus=1,i2c_address=0x70):
        """ Initialize variables """

        self.button1    = button1
        self.button2    = button2
        self.pump       = pump
        self.reset_time = reset_time
        self.solenoid_1 = solenoid_1
        self.analog_in  = analog_in
        self.v_supply   = v_supply
        self.display    = HT16K33.HT16K33(i2c_bus, i2c_address)

        self._setup()

    # End def


    def _setup(self):
        """Setup the hardware components."""

        # Initialize Button
        GPIO.setup(self.button1, GPIO.IN)
        GPIO.setup(self.button2, GPIO.IN)

        # Initialize Pump
        GPIO.setup(self.pump, GPIO.OUT)
        GPIO.setup(self.solenoid_1, GPIO.OUT)

        # Initialize Analog Input
        ADC.setup()
        
        # Initialize Display
        self.display.set_digit(0, 0)        # "0" 
        self.display.set_digit(1, 0)        # "0"
        self.display.set_digit(2, 0)        # "0"
        self.display.set_digit(3, 0)        # "0"
        
    def read_v_out(self):
        """Read the v_out voltage of the pressure sensor:
               - Return raw analog value from input pin 
        """
        
        # Return raw value from system path 
        return int(os.popen("cat /sys/bus/iio/devices/iio\:device0/in_voltage5_raw").read())
    
    #End def
    
    def read_v_supply(self):
        """Read the v_supply voltage of the pressure sensor:
               - Return raw analog value from input pin 
        """
        
        # Return raw value from system path
        return int(os.popen("cat /sys/bus/iio/devices/iio\:device0/in_voltage6_raw").read())
    
    #End def
    
    def messages(self,pressure):
        """Display funny messages about stress intensity based on pressure reading input:
               - Classify pressure input in specified ranges
                    - 0-30 mmHg : "COOL"
                    - 30-40 mmHg : "OOOP"
                    - 40-50 mmHg : "AHHH"
                    - >50 mmHg : "HELP"
                - Update display with corresponding messages
        """
        
        if (pressure > 50):
            self.display.set_digit(0, 13)        # "H"
            self.display.set_digit(1, 11)        # "E"
            self.display.set_digit(2, 14)        # "L"
            self.display.set_digit(3, 12)        # "P"
        elif (pressure > 40):
            self.display.set_digit(0, 10)        # "A"
            self.display.set_digit(1, 13)        # "H"
            self.display.set_digit(2, 13)        # "H"
            self.display.set_digit(3, 13)        # "H"
        elif (pressure > 30): 
            self.display.set_digit(0, 0)         # "O"
            self.display.set_digit(1, 0)         # "O"
            self.display.set_digit(2, 0)         # "O"
            self.display.set_digit(3, 12)        # "P"
        else: 
            self.display.set_digit(0, 15)        # "C"
            self.display.set_digit(1, 0)         # "O"
            self.display.set_digit(2, 0)         # "O"
            self.display.set_digit(3, 14)        # "L"
        
    # End def

    def run(self):
        """Execute the main program."""

        GPIO.output(self.pump, GPIO.LOW)
        GPIO.output(self.solenoid_1, GPIO.LOW)
        v_out = self.read_v_out()

        while(1):

            # Wait for button press
            while(GPIO.input(self.button1) == 1):
                time.sleep(0.1)
                
            time.sleep(0.5)
            GPIO.output(self.pump, GPIO.HIGH)
            
            # Wait for maximum pressure or button press
            while(GPIO.input(self.button1) == 1):
                v_out = self.read_v_out()
                v_supply = self.read_v_supply()
                pressure = abs(round(57.7149*((v_out - 0.1*v_supply)/(0.8*v_supply))))
                # Update the display
                self.messages(pressure) 
                print(pressure)
                time.sleep(0.1)
               
            time.sleep(0.5)
            GPIO.output(self.pump, GPIO.LOW)
            
            # Wait for button press
            while(GPIO.input(self.button1) == 1):
                time.sleep(0.5)
                
            time.sleep(0.1)
            GPIO.output(self.solenoid_1, GPIO.HIGH)
            GPIO.output(self.pump, GPIO.LOW)
            
            while(v_out > 500):
                v_out = self.read_v_out()
                v_supply = self.read_v_supply()
                pressure = abs(round(57.7149*((v_out - 0.1*v_supply)/(0.8*v_supply))))
                # Update the display
                self.messages(pressure) 
                print(v_out)
                time.sleep(0.1)
                
            
            GPIO.output(self.solenoid_1, GPIO.LOW)
  
    def cleanup(self):
        """Cleanup the hardware components."""

        # Clean up GPIOs
        GPIO.output(self.pump, GPIO.LOW)
        GPIO.output(self.solenoid_1, GPIO.LOW)

        # Clean up GPIOs
        GPIO.cleanup()
        
        # Set Display to something fun to show program is complete
        self.display.set_digit(0, 0)        # "0" 
        self.display.set_digit(1, 0)        # "0"
        self.display.set_digit(2, 0)        # "0"
        self.display.set_digit(3, 0)        # "0"

    # End def

# End class


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':

    print("Program Start")

    # Create instantiation of the lock
    project_1 = InflationDevice()

    try:
        # Run the inflatable device
        project_1.run()

    except KeyboardInterrupt:
        # Clean up hardware when exiting
        project_1.cleanup()
        
        print("Program Complete")