# -*- coding: utf-8 -*-
"""
File name: PyArduino_2DPOLIM_Sync_0.py
@author: Yutong

Code for controlling the Arduino for setup synchronization and image acquisition 
of 2DPOLIM setup. The setup is controlled by sending string commands to the 
Arduino by USB connection to call specific functions defined in the Arduino software.

Created on Fri Aug 5th 15:38:20 2022

Updates:
    - first implementation of sending string commands with functions. Implemented more commands for setting parameters @ 2022/08/10  
    - laser commands @ 2022/08/22
    - readout & set Configuration of Arduino @ 0:40 2022/10/18 

"""
#%% My code for select port automatically inspired by hello_laser.py
import sys
import serial
from serial import SerialException
from serial.tools import list_ports
import time

def enumerate_ports():
    devicesFoundList = list_ports.comports()  #list_ports.comports() returns a list of ListPortInfo objects. Use list_ports.comports()[0] to access the object
    i = 0
    if devicesFoundList!=[]:
        for device in devicesFoundList:
            print( "{} : ({}, {}, {})".format(i, device.device, device.description, device.hwid ) )
            i = i + 1
    else:
        print("No serial devices present!")
    return devicesFoundList

devFoundList = enumerate_ports()

### Connect to port by searching key words. Done @ 2022.08.14
'''
devicesFoundList = list_ports.comports()  #list_ports.comports() returns a list of ListPortInfo objects. Use list_ports.comports()[0] to access the object
portNoArduino=''
portNoLaser=''
if devicesFoundList!=[]:
    for device in devicesFoundList:
        # device = devicesFoundList[0]
        if ("Arduino Uno" in device.description) or ("Arduino Due" in device.description):
            portNoArduino = device.device
            arduino_Serial = serial.Serial(portNoArduino, baudrate=115200, timeout=1)
            print("Connect to Arduino at port:",portNoArduino)
            
        if ("VID:PID=25DC:0006" in device.hwid): # cobolt laser
            portNoLaser = device.device
            laser488_Serial = serial.Serial(portNoLaser, baudrate=115200, timeout=1)
            print("Connect to Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
'''

# Do it in a function:  Done @ 2022.08.14
# Declare global variables
arduino_Serial = None
laser488_Serial = None

def openSerialPort(dev="None"):
    '''

    Parameters
    ----------
    dev : TYPE: string, optional
        DESCRIPTION. The default is "None". 
                     "arduino": open the serial port of arduino if found.
                     "laser": open the serial port of laser if found.

    Returns
    -------
    list [COM port number of Arduino, COM port number of Cobolt 06-MLD 488nm Laser]
        DESCRIPTION. A list of COM port number of Arduino and Cobolt 06-MLD 488nm Laser if they are found. Otherwise, return empty string '' as list element.

    '''
    # First, enumerate and search ports of both Arduino and Laser
    devicesFoundList = list_ports.comports()  #list_ports.comports() returns a list of ListPortInfo objects. Use list_ports.comports()[0] to access the object
    portNoArduino=''
    portNoLaser=''
    if devicesFoundList!=[]:
        for device in devicesFoundList:
            # device = devicesFoundList[0]
            if ("Arduino Uno" in device.description) or ("Arduino Due" in device.description):
                portNoArduino = device.device
                print("Found Arduino at port:",portNoArduino)
            
            if ("VID:PID=25DC:0006" in device.hwid):
                portNoLaser = device.device
                print("Found Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
    # Second, connect to the port specified by the function argument  
    if dev == "None":
        pass # By default: Only returns port number of found devices, without connecting to the devices.
    elif dev == "arduino":
        global arduino_Serial
        open_flag=False
        try: open_flag = arduino_Serial.is_open # Check open state in order to Skip if the port is already opened to avoid PermissionError(13, 'Access is denied.', None, 5)
        except:
            pass
        # print(open_flag)
        
        if (portNoArduino !='' and open_flag==False):
            try:
                arduino_Serial = serial.Serial(portNoArduino, baudrate=115200, timeout=1)
                print("Connect to Arduino at port:",portNoArduino)
            except Exception as error:
                raise SerialException (f'{portNoArduino} not accesible. Error: {error}')
        elif open_flag==True:
            print("Arduino is already opened at port:",portNoArduino)
        else:
            try: arduino_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Arduino Devices Present.")

    elif dev == "laser":
        global laser488_Serial
        open_flag=False
        try: open_flag = laser488_Serial.is_open # Check open state in order to Skip if the port is already opened to avoid PermissionError(13, 'Access is denied.', None, 5)
        except:
            pass
        # print(open_flag)
        
        if (portNoLaser !='' and open_flag==False):
            try:
                laser488_Serial = serial.Serial(portNoLaser, baudrate=115200, timeout=1)
                print("Connect to Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
            except Exception as error:
                raise SerialException (f'{portNoLaser} not accesible. Error: {error}')
        elif open_flag==True:
            print("Cobolt 06-MLD 488nm Laseris already opened at port:",portNoLaser)
        else:
            try: laser488_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Cobolt 06-MLD 488nm Laser Presents.")
    else:
        print("Wrong function argument.")
        
    
    # Last, return port of devices for further use
    return [portNoArduino, portNoLaser]

openSerialPort()
openSerialPort("arduino")
openSerialPort("laser")
openSerialPort("lc")

arduino_Serial.__del__()
laser488_Serial.__del__()


#%% Arduino serial communication

# import time
# import serial

# arduino_Serial = serial.Serial('COM4', baudrate=115200, timeout=1) # 115200

# time.sleep(1.)
# print(arduino_Serial.name,"is opened.")

def readArduino():
    arduinoDataPacket_list=[]
    # global running # refer to global variable 'running' inside function
    while True: # or use flag: (running==True)
        # while (arduino_Serial.in_waiting==0):
        #     pass # pass is just a placeholder that does nothing
        while (arduino_Serial.in_waiting!=0):
            arduinoDataPacket = str(arduino_Serial.readline(),'utf-8').strip('\r\n')
            arduinoDataPacket_list.append(arduinoDataPacket)
            # if(arduinoDataPacket==".-.-."): # Morse code for "End of transmission/New page"
            if(arduinoDataPacket=="Arduino is ready. PUSH Button / SEND Command to start triggering..."):
                # return # terminate the function
                return arduinoDataPacket_list
            print(arduinoDataPacket)

# Define a function for calling Arduino with command
def PyArduinoCMD(arduCMD, if_return = False):
    """
    Input: arduCMD - a string of ASCII command. e.g. "acqm"

    Returns: if_return = False, no return (return None). Otherwise returns the list from readArduino()

    """
    print("Send command to Arduino:",arduCMD)

    arduCMD = arduCMD + '\r'  # add termination carriage return
    
    # Send arguement cmd to 
    arduino_Serial.write(arduCMD.encode())
    
    # Go into Serial Port Reading loop for reading response       
    arduinoDataPacket_list = readArduino()
    
    # Return response from Arduino if is asked
    if if_return == True:
        return arduinoDataPacket_list
    
    # close serial
    # arduino_Serial.__del__()

#%% Running the code for operating - 1. by input()

### Send command to Arduino
# print("Enter command to Arduino:")

# while True:
inputData = input("Enter command to Arduino:")
print("You entered: ", inputData)
    
inputData = inputData + '\r'  # add termination carriage return
arduino_Serial.write(inputData.encode())
    
# while (arduino_Serial.in_waiting!=0):
#     print("Arduino: " + arduino_Serial.readline().decode('ascii'))

# running=True  # Global variable
                
# Go into Serial Port Reading loop        
readArduino()

# running=False
arduino_Serial.__del__()

#%% Running the code for operating - 2. by PyArduinoCMD(arduCMD):

PyArduinoCMD("parm?")

PyArduinoCMD("nscan:3")

PyArduinoCMD("lcpt:10")

PyArduinoCMD("lcwait:40")

PyArduinoCMD("mnpt:100")

PyArduinoCMD("pdly:60")

PyArduinoCMD("parm?")
    
PyArduinoCMD("acqm")

PyArduinoCMD("infm")

PyArduinoCMD("infm0")

PyArduinoCMD("cwm1") #issue: the cam cannot work in cw mode. need to turn off trigger in cam setting manually

PyArduinoCMD("cwm0")


# running=False
arduino_Serial.__del__()

#%% Only read from Arduino serial port
# Alternative
while (arduino_Serial.in_waiting!=0):
    arduinoDataPacket = arduino_Serial.readline()
    arduinoDataPacket = str(arduinoDataPacket,'utf-8')
    arduinoDataPacket = arduinoDataPacket.strip('\r\n')
    print(arduinoDataPacket)
    
    
arduino_Serial.__del__()

#%% Further codes for Arduino
### Parameter Conf. of Arduino

####### Inspired by: https://www.geeksforgeeks.org/python-finding-strings-with-given-substring-in-list/
# Python code to demonstrate
# to find strings with substrings
# using list comprehension

# # initializing list
# test_list = ['GeeksforGeeks', 'Geeky', 'Computers', 'Algorithms']

# # printing original list
# print ("The original list is : " + str(test_list))

# # initializing substring
# subs = 'Geek'

# # using list comprehension
# # to get string with substring
# res = [i for i in test_list if subs in i]

# # printing result
# print ("All strings with given substring are : " + str(res))
# ####### end of material
# Readout current config. of Arduino. on 2022/10/16-17

CurrentArduinoConfigList = PyArduinoCMD("parm?", if_return = True)

# Readout numScan:
findSub = "numScan = "
# locate substring in the list
numScanVal = [i for i in CurrentArduinoConfigList if findSub in i] #RTN:['numScan = 5']
# Retrive the value of config. and convert it into int
numScanVal = int(numScanVal[0].split("= ")[-1])
print(numScanVal)

# Readout triggerPulseWidthLC:
findSub = "triggerPulseWidthLC = "
triggerPulseWidthLCVal = [i for i in CurrentArduinoConfigList if findSub in i]
triggerPulseWidthLCVal = int(triggerPulseWidthLCVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
print(triggerPulseWidthLCVal)

# Readout LCWaitTime:
findSub = "LCWaitTime = "
LCWaitTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
LCWaitTimeVal = int(LCWaitTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
print(LCWaitTimeVal)

# Readout triggerPulseWidthMain:
findSub = "triggerPulseWidthMain = "
triggerPulseWidthMainVal = [i for i in CurrentArduinoConfigList if findSub in i]
triggerPulseWidthMainVal = int(triggerPulseWidthMainVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
print(triggerPulseWidthMainVal)

# Readout triggerDelayTime:
findSub = "triggerDelayTime = "
triggerDelayTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
triggerDelayTimeVal = int(triggerDelayTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
print(triggerDelayTimeVal)

### set new values of config. to Arduino

# Assign numScan:
numScanVal = 6
# send it to Arduino
PyArduinoCMD("nscan:{}".format(numScanVal))

# Assign triggerPulseWidthLC:
triggerPulseWidthLCVal = 8
PyArduinoCMD("lcpt:{}".format(triggerPulseWidthLCVal))

# Assign LCWaitTime:
LCWaitTimeVal = 55
PyArduinoCMD("lcwait:{}".format(LCWaitTimeVal))

# Assign triggerPulseWidthMain:
triggerPulseWidthMainVal = 90
PyArduinoCMD("mnpt:{}".format(triggerPulseWidthMainVal))

# Assign triggerDelayTime:
triggerDelayTimeVal =  55
PyArduinoCMD("pdly:{}".format(triggerDelayTimeVal))

CurrentArduinoConfigList = PyArduinoCMD("parm?", if_return = True)

################################ Do it in function: (for GUI software)
### Parameter Configuration of Arduino.  done @ 0:40 2022/10/18 
# Readout current config. of Arduino. on 2022/10/16-17

# Read and Show current config.
def getArduinoConfig():
    CurrentArduinoConfigList = PyArduinoCMD("parm?", if_return = True)
    
    # Readout numScan:
    findSub = "numScan = "
    # locate substring in the list
    numScanVal = [i for i in CurrentArduinoConfigList if findSub in i] #RTN:['numScan = 5']
    # Retrive the value of config. and convert it into int
    numScanVal = int(numScanVal[0].split("= ")[-1])
    print(numScanVal)
    # Assign value to input box
    entry1_nscan.delete(0, 'end')
    entry1_nscan.insert(0, str(numScanVal))
    
    # Readout triggerPulseWidthLC:
    findSub = "triggerPulseWidthLC = "
    triggerPulseWidthLCVal = [i for i in CurrentArduinoConfigList if findSub in i]
    triggerPulseWidthLCVal = int(triggerPulseWidthLCVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(triggerPulseWidthLCVal)
    # Assign value to input box
    entry2_lcpt.delete(0, 'end')
    entry2_lcpt.insert(0, str(triggerPulseWidthLCVal))
    
    # Readout LCWaitTime:
    findSub = "LCWaitTime = "
    LCWaitTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
    LCWaitTimeVal = int(LCWaitTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(LCWaitTimeVal)
    # Assign value to input box
    entry3_lcwait.delete(0, 'end')
    entry3_lcwait.insert(0, str(LCWaitTimeVal))
    
    # Readout triggerPulseWidthMain:
    findSub = "triggerPulseWidthMain = "
    triggerPulseWidthMainVal = [i for i in CurrentArduinoConfigList if findSub in i]
    triggerPulseWidthMainVal = int(triggerPulseWidthMainVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(triggerPulseWidthMainVal)
    # Assign value to input box
    entry4_mnpt.delete(0, 'end')
    entry4_mnpt.insert(0, str(triggerPulseWidthMainVal))
    
    # Readout triggerDelayTime:
    findSub = "triggerDelayTime = "
    triggerDelayTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
    triggerDelayTimeVal = int(triggerDelayTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(triggerDelayTimeVal)
    # Assign value to input box
    entry5_pdly.delete(0, 'end')
    entry5_pdly.insert(0, str(triggerDelayTimeVal))
        
    return [numScanVal, triggerPulseWidthLCVal, LCWaitTimeVal, triggerPulseWidthMainVal, triggerDelayTimeVal]

def setArduinoConfig():
    ### Assign new values of config. to Arduino
    # First, Get value from input boxes and convert to int
    try:
        numScanVal = int(entry1_nscan.get())
        triggerPulseWidthLCVal = int(entry2_lcpt.get())
        LCWaitTimeVal = int(entry3_lcwait.get())
        triggerPulseWidthMainVal = int(entry4_mnpt.get())
        triggerDelayTimeVal =  int(entry5_pdly.get())
    except ValueError:
        print("Error: check if any character other than numbers is in the input box.")
        TBOX_MN_print("Error: check if any character other than numbers is in the input box.")
    except: 
        print("Error: something wrong during getting values from input boxes.")
        TBOX_MN_print("Error: something wrong during getting values from input boxes.")
    
    # Then, assign the values to Arduino
    
    try:
        # Assign 1 numScan:
        # numScanVal = 5
        # send it to Arduino
        PyArduinoCMD("nscan:{}".format(numScanVal))
        
        # Assign 2 triggerPulseWidthLC:
        # triggerPulseWidthLCVal = 8
        PyArduinoCMD("lcpt:{}".format(triggerPulseWidthLCVal))
        
        # # Assign 3 LCWaitTime:
        # LCWaitTimeVal = 55
        PyArduinoCMD("lcwait:{}".format(LCWaitTimeVal))
        
        # # Assign 4 triggerPulseWidthMain:
        # triggerPulseWidthMainVal = 90
        PyArduinoCMD("mnpt:{}".format(triggerPulseWidthMainVal))
        
        # # Assign 5 triggerDelayTime:
        # triggerDelayTimeVal =  55
        PyArduinoCMD("pdly:{}".format(triggerDelayTimeVal))
    except:
        print("Error: something wrong when assign values to Arduino")



#%% PyLaser 
    
# Define a function for calling Laser with command
def PyLaserCMD(laserCMD):
    """
    Input: laserCMD - a string of ASCII command according to the laser manual: D0136-Laser_Manual-Cobolt-06-01-Series_January_2020.pdf. e.g. "gsn?" Get serial number

    Returns: Returned value from Cobolt 06-MLD 488nm Laser read from serial.

    """
    print("Send command to laser:",laserCMD)

    laserCMD += '\r\n'  # add termination: carriage return & new line
    
    # Send arguement cmd to 
    try:
        laser488_Serial.write( laserCMD.encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation
    except:
        print("Writing Error at serial port of laser!")
        response = None
        return response
        
    # Read Serial Port for laser's response       
    try:
        response = laser488_Serial.readline().decode('ascii').strip('\r\n') # convert bytes to string and remove ending '\r\n'
    except:
        response = None
    
    print("Laser returns:",response)
    return response


######### Some cmd of laser:
open_flag = laser488_Serial.is_open # Check open state 

## "gsn?" Get serial number
PyLaserCMD("gsn?") 
# Returns '17706'

#### Output power setting:
## "cp" Enter constant power mode
PyLaserCMD("cp")
# Returned value: OK

## set output power "p"; All arguments are in lower case and separated by a space (ASCII 32). 
PyLaserCMD("p 0.0100") # Arg:Float (W); set to 0.01W
# Returned value: OK

## Get output power set point "p?"
PyLaserCMD("p?") # Re:Float (W)
# Returned value:'0.0100'

## Read actual output power "pa?"
PyLaserCMD("pa?") # Re:Float (W)
# Returned value: '0.0000'
#########

#### laser current setting:
## "ci" Enter constant current mode
PyLaserCMD("ci") 
# Returned value: 'OK'

## "slc" Set laser current
PyLaserCMD("slc 30") # Arg:Float (mA); set to 30mA
# Returned value: OK

## "glc?" Get laser current set point
PyLaserCMD("glc?") # Re:Float (mA)
# Returned value: '30.0'

# "i?" Read actual laser current: "rlc" do not work?!
PyLaserCMD("i?") # Re:Float (mA)
# '0.0100'
# Returned value: Syntax error: illegal command
#########


## "gom?" Returns the operating mode
PyLaserCMD("gom?") # Re:
# Returned value: 1

## "f?" Get operating fault
PyLaserCMD("f?") # Re:
# Returned value: 0

#### Turn ON/OFF LASER
#@cobasks Get key switch state
PyLaserCMD('@cobasks?') #'Syntax error: illegal command\r\n'

##l? Get laser ON/OFF state
PyLaserCMD('l?') 

##@cob1 Laser ON – Force autostart
PyLaserCMD('@cob1')

##@cob0 Laser OFF
PyLaserCMD('@cob0')

##l1 Laser ON.
PyLaserCMD('l1') #Syntax error: not allowed in autostart mode.

##l0 Laser OFF
PyLaserCMD('l0')

###### For 2D POLIM acquisition:
## "gsn?" Get serial number
PyLaserCMD("gsn?")

## "cp" Enter constant power mode
PyLaserCMD("cp")

## "ci" Enter constant current mode
PyLaserCMD("ci") 

## "slmp" Set laser modulation power. Arguement: Float (mW)
PyLaserCMD("slmp 30") # Set laser modulation power to 30 mW

## "glmp?" Get laser modulation power set point. Return: Float (mW)
PyLaserCMD("glmp?")

## "em" Enter modulation mode ??? for ON/OFF
PyLaserCMD("em")
# Do not use it for On/Off modulation!!!
           
''' "gom?" Returns the operating mode
Returns: 
0 – Off
1 – Waiting for key
2 – Continuous
3 – On/Off Modulation
4 – Modulation
5 – Fault
6 – Aborted
'''
PyLaserCMD("gom?") # Re:
# Returned value: 1


#####
laser488_Serial.close()


#%% Some tests
total = 100
def func3():
    listOfGlobals = globals()
    listOfGlobals['total'] = 15
    total = 22
    print('Local Total = ', total)
print('Total = ', total)
func3()
print('Total = ', total)
'''
Total =  100
Local Total =  22
Total =  15
'''

###
total = 100
def func():
    # refer to global variable 'total' inside function
    global total
    if total > 10:
        total = 15
print('Total = ', total)
func()
print('Total = ', total)

'''
Total =  100
Total =  15
'''

###
'''
else in loop:
Inspired by: 
作者：三无小号
链接：https://www.zhihu.com/question/37076998/answer/935963167
来源：知乎
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
'''
for i in range(3):
    for j in range(3):
        for k in range(3):
            print(i, j, k)
            if i == j == k == 1:
                print('break')
                break
        else:
            continue # Skip and go to next iteration. The continue statement is used to skip the rest of the code inside a loop for the current iteration only. Loop does not terminate but continues on with the next iteration.
        break
    else:
        continue
    break
