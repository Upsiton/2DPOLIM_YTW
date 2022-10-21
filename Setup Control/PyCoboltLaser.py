"""
 File name: PyCoboltLaser.py
     
 @author: Yutong
 2022
"""
#%% Source
"""
    This cell shows the original code for Cobolt Lasers developed by Cobolt AB. 
    Project: https://github.com/cobolt-lasers/pycobolt.git
"""

"""
* hello_laser.py
* 
*   THE PRESENT SAMPLE CODE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
*      * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
*        TIME.
*
* The following code is released under the MIT license.
*
* Please refer to the included license document for further information.
"""

import sys
import serial
from serial import SerialException
from serial.tools import list_ports
# import time

def enumerate_ports( devices_found ):
    devices_found.extend( list_ports.comports() ) #list_ports.comports() returns a list of ListPortInfo objects. Use list_ports.comports()[0] to access the object
    i = 0
    if devices_found!=[]:
        for device in devices_found:
            print( "{} : ({}, {}, {})".format(i, device.device, device.description, device.hwid ) )
            i = i + 1
    else:
        print("No serial devices present!")


class InvalidPortException(Exception):
    def __str__(self):
        return "Port ID out of range"

baud = 112500
devices_found = list()

try:
    print( "Please select serial port!" )
    
    enumerate_ports( devices_found )

    port_id = int( input() )

    # Check that the user selected a valid port
    if ( port_id  >=  len( devices_found ) ):
        raise InvalidPortException()

except Exception as e:
    print(e)

### Connect to the slected port port, baudrate, timeout in milliseconds
laser_serial = serial.Serial( devices_found[port_id].device, baud, timeout=1)

# time.sleep(1.9)
try:
    #Check if we managed to open the port (optional)
    print( "Is the serial port open?", end='' )
    if ( laser_serial.is_open ): 
        print(" Yes.")
    else:
        print( " No." )

    # Ask the laser for its serial number, ( note the required ending \r\n )
    # Look in manual for the commands and response formatting of your laser!
    command = "gsn?"
    termination = "\r\n"
    laser_serial.write( (command + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation
    print("cmd:",command)
    
    result = laser_serial.readline().decode('ascii')

    print( "Serial number was: {}\n".format( result ))
    # print(result)

except Exception as e:
    print(e)
    if laser_serial.is_open:
        laser_serial.close()

# Above: original code

#%% My code:
"""
 The following code is for controlling the Cobolt laser inspired from the sample code

"""

# Def. of a function to transfer cmd
def fullCmdString(cmdStr, arguments = None):
    # termination = "\r\n"
    if (arguments == None):
        fullCmd = cmdStr + "\r\n"
    else:
        fullCmd = cmdStr + " " + arguments + "\r\n"
    print(fullCmd)
    return fullCmd
    
rslt = fullCmdString("cp")
rslt0 = fullCmdString("p","0.0100")
rslt1 = fullCmdString("p 0.0100")
fullCmd = fullCmdString("p","0.0100")

(fullCmd.encode('ascii')).decode('ascii') == fullCmd # True

print(rslt)
rslt0 == rslt1

def laserCmd(cmdStr, arguments = None):
    # Step 1. generate fullCmd
    # termination = "\r\n"
    if (arguments == None):
        fullCmd = cmdStr + "\r\n"
    else:
        fullCmd = cmdStr + " " + arguments + "\r\n"
    print(fullCmd)
    
    # Step 2. write & read device
    laser_serial.write(fullCmd.encode('ascii'))
    try:
        feedback = laser_serial.readline().decode('ascii')
    except:
        feedback = None
    
    print(feedback)
    return feedback

laserCmd("cp")

#%%
class coboltlaser488:
    '''' class to control Cobolt MLD laser 488 nm '''
    def __init__(self, baud = 112500, cmdStr):
        self.cmdStr = cmdStr
        

#%% Play with the ASCII cmds:
# Ask the laser for its serial number, ( note the required ending \r\n )
# Look in manual for the commands and response formatting of your laser!


cmdStr = "p 0.0100"#"p?"#"@cobasks"#"l?"#"gsn?"
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

# result = laser_serial.readline()
result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result ))

######### Output power setting:
# "cp" Enter constant power mode
cmdStr = "cp" 
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: OK

#set output power "p"; All arguments are in lower case and separated by a space (ASCII 32). 
cmdStr = "p 0.0100" # Arg:Float (W); set to 0.01W
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: OK

# Get output power set point "p?"
cmdStr = "p?" # Re:Float (W)
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: 0.0100

# Read actual output power "pa?"
cmdStr = "pa?" # Re:Float (W)
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: 0.0000
#########

######### laser current setting:
# "ci" Enter constant current mode
cmdStr = "ci" 
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: OK

# "slc" Set laser current
cmdStr = "slc 30" # Arg:Float (mA); set to 30mA
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: OK

# "glc?" Get laser current set point
cmdStr = "glc?" # Re:Float (mA)
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: 30.0

# "i?" Read actual laser current: "rlc" do not work?!
cmdStr = "i?" # Re:Float (mA)
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: Syntax error: illegal command ???
#########


## "gom?" Returns the operating mode
cmdStr = "gom?" # Re:
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: 1

## "f?" Get operating fault
cmdStr = "f?" # Re:
termination = "\r\n"
laser_serial.write( (cmdStr + termination).encode('ascii') ) # encode('ascii') converts python string to a binary ascii representation

result = laser_serial.readline().decode('ascii')
print( "Returned value: {}\n".format( result )) # Returned value: 0

### Turn ON/OFF LASER
#@cobasks Get key switch state
laserCmd('@cobasks?') #'Syntax error: illegal command\r\n'

##l? Get laser ON/OFF state
laserCmd('l?') 

##@cob1 Laser ON – Force autostart
laserCmd('@cob1')

##@cob0 Laser OFF
laserCmd('@cob0')

##l1 Laser ON.
laserCmd('l1') #Syntax error: not allowed in autostart mode.

##l0 Laser OFF
laserCmd('l0')


#%%
laser_serial.close()

#%% PyLaser 

# My code for select port automatically inspired by hello_laser.py
import sys
import serial
from serial import SerialException
from serial.tools import list_ports
import time

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
# openSerialPort("arduino")
openSerialPort("laser")
# openSerialPort("lc")

# arduino_Serial.__del__()
laser488_Serial.__del__()

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
        response = "ErrorWrite"
        return response
        
    # Read Serial Port for laser's response       
    try:
        response = laser488_Serial.readline().decode('ascii').strip('\r\n') # convert bytes to string and remove ending '\r\n'
    except:
        response = "ErrorRead"
    
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
       
## "gom?" Returns the operating mode    
''' 
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

#%% Characterization of laser output power and diode current @ 2022/08/23, Completed @ 2022/08/26
'''
Idea: Set diode current, get internal measurement of actual laser power. And/or set power, 
read diode current. 
'''
import sys
import serial
from serial import SerialException
from serial.tools import list_ports
import time
import numpy as np
from datetime import datetime, timedelta

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

# openSerialPort()
# openSerialPort("arduino")
# openSerialPort("laser")
# openSerialPort("lc")

# arduino_Serial.__del__()
# laser488_Serial.__del__()

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


##################################### Characterization Main Code:

################ Acquisition of Data: ################
## Open laser's serial port
openSerialPort("laser")

# laser488_Serial.__del__()

## set output power "p"; 
PyLaserCMD("p 0.020") # Arg:Float (W); set to 0.020W
# Returned value: OK

## Get output power set point "p?"
PyLaserCMD("p?") # Re:Float (W)
# Returned value:'0.0100'

## "cp" Enter constant power mode
PyLaserCMD("cp")

## Read actual output power "pa?"
PyLaserCMD("pa?") # Re:Float (W)
# Returned value: '0.0000'

##"gom?" Returns the operating mode
''' 
Returns: 
0 – Off
1 – Waiting for key
2 – Continuous
3 – On/Off Modulation
4 – Modulation
5 – Fault
6 – Aborted
'''
laserStatus = PyLaserCMD("gom?") # Re:
if laserStatus == '2':
    input("Laser is ON! Make sure Laser Safety before PRESS ANY key to continue.")
print("Measurement start!")
laserPowerCurrentData = []

for i in range(0,211): # Full range:(0,211)
# acceptable range of value: Power: 0 ~ 210 mW; Diode current: 0 ~ 285 mA
    setPowerValue = i/1000 # Power values. unit: mW
    print(f"Current power value: {i} mW")
    
    laserCMD = f"p {setPowerValue}"
    # print(laserCMD)
    ## set output power "p"; 
    PyLaserCMD(laserCMD)
    powerSetPoint = float(PyLaserCMD("p?"))
    
    if (powerSetPoint != setPowerValue): # verify if the power value is set correctly
        print("Error in setting power value!")
        continue
    
    # Read actual power and diode current
    # wait until stable lasing
    print("Waiting...")
    time.sleep(10.)
    
    while True:
        ## Read actual output power "pa?"
        powerActualValue = float(PyLaserCMD("pa?")) # Re:Float (W)
        ## Comparing powerActualValue with powerSetPoint to see if it become stable
        if ( abs(powerActualValue-powerSetPoint) <= 0.0001 ): # Stable if deviation less than 0.1 mW. Jump out of loop, otherwise wait for 1s
            print("Laser power is Stable.")
            break
        else:
            time.sleep(1.5)
    
    # Read acutal diode current.
    # "i?" Read actual laser current
    currentActualValue = float(PyLaserCMD("i?")) # Re:Float (mA)

    # Record Data into an array
    
    # Option 1: Store via numpy array:
    # laserPowerCurrentData = np.empty((0,3), float) # creat in advance of Loop!
    # laserPowerCurrentData =np.append(laserPowerCurrentData, np.array([[powerSetPoint, powerActualValue, currentActualValue]]), axis=0)
    
    # Option 2: Easier. Store via list. Later convert it to numpy array in the end.
    laserPowerCurrentData.append([powerSetPoint, powerActualValue, currentActualValue])
    # nparrayL=np.array(laserPowerCurrentData, float)
    print("Current data is stored.")

### Laser OFF by setting current = 0mA
## "slc" Set laser current
PyLaserCMD("slc 0") # Arg:Float (mA); set to 0mA

## "ci" Enter constant current mode
PyLaserCMD("ci")

print("Measurement is done!")
laserPowerCurrentDataArray=np.array(laserPowerCurrentData, float)
# print(laserPowerCurrentData)
# print(laserPowerCurrentDataArray)

### Export Result as csv file
# Creat name (including path) of file
dateTimeStr = datetime.now().strftime("%Y%m%d-%H-%M")[2:]
savePath =  r"D:\Research\HeintzmannLab\Data\LaserPowerCurrentChar\\" + "LaserP-IResult_"+dateTimeStr+".csv" # Laptop
# savePath =  r"D:\2DPOLIM\Setup\Characterization\LaserPowerCurrentChar\\" + "LaserP-IResult_"+dateTimeStr+".csv" # Lab PC

# headerStr = "Laser Power-Diode Current measurement @ {}\npowerSetPoint(W), powerActualValue(W), currentActualValue(mA)".format(dateTimeStr)
headerStr = f"Laser Power-Diode Current measurement @ {dateTimeStr}\npowerSetPoint(W), powerActualValue(W), currentActualValue(mA)"

# using the savetxt for exporting csv file
# from the numpy module
np.savetxt(savePath, 
           laserPowerCurrentDataArray,
           delimiter ="; ", 
           header = headerStr, 
           fmt ='% s')
np.save(savePath.strip(".csv"),laserPowerCurrentDataArray)
print("Data is exported as:",savePath)
# CLose serial port
laser488_Serial.__del__()

################ Analysis of Data ################
### Polt the data
import matplotlib.pyplot as plt
import numpy as np
# from scipy.stats import linregress
from scipy import stats
# from matplotlib.ticker import MultipleLocator

# laserPowerCurrentDataArray = np.load(r"D:\2DPOLIM\Setup\Characterization\LaserPowerCurrentChar\LaserP-IResult_220824-11-37.npy")
laserPowerCurrentDataArray = np.load(r"D:\Research\HeintzmannLab\Data\LaserPowerCurrentChar\LaserP-IResult_220824-11-37.npy")

plt.figure()#(figsize=(6, 4))
# Output power (mW)
p_data = laserPowerCurrentDataArray[1:,1]*1000
# Diode current (mA)
i_data = laserPowerCurrentDataArray[1:,2]

plt.scatter(i_data, p_data, s=0.5, marker='o', label="data")
plt.title("Laser Diode's Output Optical Power vs. Diode Current")
plt.xlabel("Diode Current (mA)")
plt.ylabel("Output Power (mW)")

# plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.xticks(np.arange(0, 301, 25.0)) # locations of major ticks of x axis
plt.xlim((25, 301)) # range limit of x axis
# plt.axes().xaxis.set_minor_locator(MultipleLocator(5)) ## set minor ticks. Error!?
         
plt.yticks(np.arange(0., 221, 10.0))
plt.ylim((0., 221.))

plt.legend()
plt.show()

## Fit the curve @ 2022/08/24
## Method 1: By np.polyfit() - a general least squares polynomial fit function
# 1.Current(mA) -> Power(mW)
coeff_IP = np.polyfit(i_data, p_data, 1)
# coeff_IP = np.polyfit(i_data, p_data, 2)
print(coeff_IP)
# [  0.82519992 -24.05088542]
currentV = 161.1# mA
powerV = coeff_IP[0]*currentV + coeff_IP[1]
print(f"{currentV} mA -> {powerV} mW")

currentV = i_data
powerV = coeff_IP[0]*currentV + coeff_IP[1]
delt_power=powerV-p_data
# print(delt_power)

# 2.Power(mW) -> Current(mA) (what I actually did in the measurement)
coeff_PI = np.polyfit(p_data, i_data, 1)
print(coeff_PI)
# [ 1.21182728 29.1455548 ]
# test the fitting function:
powerV = 109 # mW
currentV = coeff_PI[0]*powerV + coeff_PI[1]
print(f"{powerV} mW -> {currentV} mA")

powerV=p_data
currentV = coeff_PI[0]*powerV + coeff_PI[1]
delt_current=currentV-i_data

# comparing coeff. from two ways
print(1/(coeff_IP[0])- coeff_PI[0])
print(-coeff_IP[1]/coeff_IP[0]-coeff_PI[1])

## Method 2: By scipy.stats.linregress(x, y=None, alternative='two-sided') @ 2022-08-26
# Perform the linear regression:
# P->I
LinReg_PI = stats.linregress(p_data, i_data)
print(LinReg_PI)
# I->P
LinReg_IP = stats.linregress(i_data, p_data)
print(LinReg_IP)

# Print result
print(f"slope: {LinReg_IP.slope:.4f}")
print(f"intercept: {LinReg_IP.intercept:.4f}")
# Coefficient of determination (R-squared):
print(f"R-squared: {LinReg_IP.rvalue**2:.9f}")

# Plot the data along with the fitted line:
plt.figure()#(figsize=(6, 4))

plt.scatter(i_data, p_data, s=0.7, marker='o', label="original data")
i_DataPlot = np.array(range(30,286))
plt.plot(i_DataPlot, LinReg_IP.slope*i_DataPlot + LinReg_IP.intercept, color='r', linestyle='-', linewidth=0.3, label="fitted line")
plt.title("Laser Diode's Output Optical Power vs. Diode Current")
plt.xlabel("Diode Current (mA)")
plt.ylabel("Output Power (mW)")

# plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.xticks(np.arange(0, 301, 25.0)) # locations of major ticks of x axis
plt.xlim((25, 301)) # range limit of x axis
# plt.axes().xaxis.set_minor_locator(MultipleLocator(5)) ## set minor ticks. Error!?
         
plt.yticks(np.arange(0., 221, 10.0))
plt.ylim((0., 221.))

plt.legend()
plt.show()

################ Final Result ################
### Take Home Message: Function of Laser_Power(current), Laser_Current(Power)

def LaserI2P(current):
    '''
    Give laser output power (mW) by input diode current (mA)
    Parameters
    ----------
    current : float
        DESCRIPTION: diode current (mA)

    Returns
    -------
    power : float
        DESCRIPTION: laser output power (mW)
    '''
    # power = LinReg_IP.slope*current + LinReg_IP.intercept
    power = 0.8251999156433668*current + (-24.050885423237645)
    return power

def LaserP2I(power):
    '''
    Give laser diode current (mA) by input output power (mW)
    Parameters
    ----------
    power : float
        DESCRIPTION: laser output power (mW)

    Returns
    -------
    current : float
        DESCRIPTION: diode current (mA)
    '''
    # current = LinReg_PI.slope*power + LinReg_PI.intercept
    current = 1.2118272847132912*power + 29.14555479608113
    return current


print(f"Laser Power(mW)={LinReg_IP.slope:.4f}*I(mA)+({LinReg_IP.intercept:.4f})")
# Laser Power(mW)=0.8252*I(mA)+(-24.0509)
print(f"Diode Current(mA)={LinReg_PI.slope:.4f}*Laser Power(mW)+{LinReg_PI.intercept:.4f}")
# Diode Current(mA)=1.2118*Laser Power(mW)+29.1456

## Some test:
LaserI2P(158.8)
LaserI2P(30.4)

LaserP2I(1)
LaserP2I(107)

LaserP2I(LaserI2P(158.8)) # 158.79999959010303
LaserI2P(LaserP2I(107)) #106.99999965967962
