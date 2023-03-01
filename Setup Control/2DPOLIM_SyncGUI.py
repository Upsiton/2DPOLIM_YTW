# -*- coding: utf-8 -*-
"""
File name: 2DPOLIM_SyncGUI_1.py
@author: Yutong Wang

Graphic User Interface (GUI) software for system control and image acquisition 
of 2DPOLIM setup. Functionalities are mostly adapted from PyArduino_2DPOLIM_Sync_0.py

Created on Sun Sep 18 15:25:54 2022

Key updates:
    - First complete design of frame @ 24/10/2022
    - Read/set Laser power feature @ ?
    - Enable/Disable certain buttons according to the connection state @ 16-18/01/2023
    - Implement LC Initialization in acquisition @ 18/01/2023 23:10
"""
# cd D:\\MyDocs\\PROG\\Python\\MyPy
# cd D:\\MyDocs\\PROG\\Python\\libs\\tkinter\\MariyaSha_Tutorial\\PDFextract_text-main\\finishedProject
# cd D:\\Research\\HeintzmannLab\\Programming\\DevCtrl\\2DPOLIM_GUI
# pwd
###

import tkinter as tk
from tkinter import ttk # contains Combobox
from PIL import Image, ImageTk

# import time
import serial
from serial import SerialException
from serial.tools import list_ports

# just for testing
# import random

root = tk.Tk() # Toplevel widget of Tk which represents mostly the main window of an application.
root.title("2DPOLIM Acquisition Software")

# set size of window
canvas = tk.Canvas(root, width=800, height=600)
canvas.grid(columnspan=7, rowspan=7) #Position a widget in the parent widget in a grid. Splits the canvas into 3 column , where elements can be put in.

################################## Template ################################## @ 04/10/2022
### Playground of GUI to try it out
#logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(row=4, column=5)#, sticky="E")

#instructions
instructions = tk.Label(root, text="2DPOLIM Acquisition Software\n by Yutong Wang", fg="purple", font=("Raleway",15))
instructions.grid(row=0, column=2) # columnspan=3,)  position of label
instructionTxt = """1. firstly click ‘Connect to Arduino’. If successful, click ‘Read Trigger Config’ to modify trigger parameters if necessary.
2. usually, only change ‘# of Repetition’ and ‘Exposure Pulse Width’. Don’t change the other settings unless you know what you’re doing. Click ‘Set Trigger Config’ to save changes.
3. (optional, connect to Laser is NOT necessary for acquisition) ‘Connect to Laser’ for setting/reading Laser Power. Select option in the combobox and click ‘Execute’
4. click ‘Check LC port’ to check connection of LC rotator.
5. once the Arduino and LC are correctly connected, ‘Start Acquisition’, ‘Start Infinite Trigger Mode’ buttons are available. 
6. set cameras into External Trigger Mode and start recording. Click ‘Start Acquisition’.
"""

# myLabel = tk.Label(root, text="Hello World!")  # does not fully overlap!! Use tk.StringVar() instead
myLabel0Text = tk.StringVar()
myLabel0 = tk.Label(root, textvariable = myLabel0Text)
myLabel0.grid(row=1,column=2)

# Button
def myClick():
    myLabel0Text.set("Hello World!")
    print("CNSL: Hello World!")
    
    # show text in main text box
    text_entry0 = entry0.get()
    # print(type(text_entry0)) #RTN: <class 'str'>
    main_text_box.insert('end', "Hello World! "+ text_entry0 + '\n') # show text by inserting; 'end' here is start at the end of the text. +'\n' to print new text in new line.
    global instructionTxt
    main_text_box.insert('end',instructionTxt+'\n')
    print(instructionTxt)
    # # text style conf.
    # main_text_box.tag_configure("center", justify="center")
    # main_text_box.tag_add("center", 1.0, "end")

myButton = tk.Button(root, text="Click me!", command=myClick, foreground="yellow", background="red")
# myButton.pack()
# myButton.grid(row=3,column=2)
myButton.grid(row=0,column=6)

# Print in MAIN text box
    # creat text box widget
main_text_box = tk.Text(root, height=20, width=50, padx=5, pady=5)
main_text_box.insert(1.0, "Show text here: "+'\n') # show text by inserting; The "1.0" here is the position where to insert the text, and can be read as "line 1, character 0". This refers to the first character of the first line
main_text_box.grid(row=4,column=2)  # position of text box

# Def a function to print sth in the main_text_box as a duplication of print() in the console
def TBOX_MN_print(text0='', text1='', text2='', text3=''): # in case of there's more arg. than 1
    text_to_print = str(text0)+str(text1)+str(text2)+str(text3)
    # print(text_to_print, type(text_to_print))
    main_text_box.insert('end', text_to_print +'\n') # show text by inserting
    # return text_to_print

# A Debug button for virtual switching ON/OFF of Laser & Arduino & LC; button with switch of text
# flags for connection states of devices
demo_flag = False
laserConnect_flag = False
arduinoConnect_flag = False
LCPortCheck_flag = False

def buttonSwitch():
    global demo_flag, laserConnect_flag, arduinoConnect_flag, LCPortCheck_flag
    ## Randomly set button flag value
    # flag = random.randint(1,11)
    # if flag <=5:
    #     demo_flag = False
    # else:
    #     demo_flag = True
    
    ## Switch on each click 
    if demo_flag == False:
        demo_flag = True
    else:
        demo_flag = False
      
    if demo_flag == True: # ON state
        switch_btn_Text.set("Switch OFF") # re-set the shown text on the button
        demo_text = "[Demo] Hello! I'm ON."
        # Change the text variable of label widget:
        myLabel0Text.set("[Demo] Hello! I'm ON.")
        # Change the color config. of the label widget:
        myLabel0.config(bg = "yellow", fg = "red")
        
        # Virtually switch ON Laser & Arduino & LC (set the flag to ON state)
        laserConnect_flag = True # Enable Laser buttons:
        # laserPowerConfig_btn.config(state=tk.NORMAL) # set button state to "NORMAL" when device is connected
        # laserON_btn.config(state=tk.NORMAL)
        # laserOFF_btn.config(state=tk.NORMAL)
        # ### !!!idea!!! put above part in a function. Call it at the end of some related button to refresh the state of other buttons. DONE @ 2023.01.18
        arduinoConnect_flag = True
        LCPortCheck_flag = True
    else:
        switch_btn_Text.set("Switch ON")
        demo_text = "[Demo] I'm OFF. Bye bye!"
        # Change the text variable of label widget:
        myLabel0Text.set("[Demo] I'm OFF. Bye bye!")
        # Change the color config. of the label widget:
        myLabel0.config(bg = "green", fg = "yellow")
        # Virtually switch OFF Laser & Arduino & LC (set the flag to OFF state)
        laserConnect_flag = False # Disable Laser buttons:        
        arduinoConnect_flag = False
        LCPortCheck_flag = False
    # Refresh the button state
    buttonStateRefresh()
    main_text_box.insert('end', demo_text + '\n')
    # switch button
switch_btn_Text = tk.StringVar()
switch_btn_Text.set("[Demo]")
switch_btn = tk.Button(root, textvariable=switch_btn_Text, command=lambda:buttonSwitch(), font="Raleway", bg="#20bebe", fg="white", height=2, width=15)

# if demo_flag == False:
#     switch_btn_Text.set("Switch ON")
# else:
#     switch_btn_Text.set("Switch OFF")
    
# switch_btn.grid(column=2, row=2)
switch_btn.grid(row=0, column=5)

# Input boxes (fields, Entry) for Changing config.
entry0 = tk.Entry(root, width=15)
entry0.insert(0, "Enter something:")
entry0.grid(column=4, row=0)

################################## 2DPOLIM Control ##################################
## A. Open serial port of Laser/ Arduino /Lc

## A1&2: open serial port of Arduino and Laser

#======== Auxiliary Functions Starts Here ========
########## Connect to port by searching key words. Done @ 2022.08.14 @PyArduino_2DPOLIM_Sync_0.py

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
        DESCRIPTION. A list of COM port number of Arduino and Cobolt 06-MLD 488nm Laser if they are found. Otherwise, return a list element of empty string ''.

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
                TBOX_MN_print("Found Arduino at port:",portNoArduino)
            
            if ("VID:PID=25DC:0006" in device.hwid):
                portNoLaser = device.device
                print("Found Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
                TBOX_MN_print("Found Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
    # Second, connect to the port specified by the function argument  
    if dev == "None":
        pass # By default: Only returns port number of found devices, without connecting to the devices.
    elif dev == "arduino":
        global arduino_Serial, arduinoConnect_flag, laserConnect_flag
        open_flag=False
        try: open_flag = arduino_Serial.is_open # Check open state in order to Skip if the port is already opened to avoid PermissionError(13, 'Access is denied.', None, 5)
        except:
            pass
        # print(open_flag)
        
        if (portNoArduino !='' and open_flag==False):
            try:
                arduino_Serial = serial.Serial(portNoArduino, baudrate=115200, timeout=1)
                print("Connect to Arduino at port:",portNoArduino)
                TBOX_MN_print("Connect to Arduino at port:",portNoArduino)
                arduinoConnect_flag = True # assign True state to the arduino connection flag
            except Exception as error:
                raise SerialException (f'{portNoArduino} not accesible. Error: {error}')
                arduinoConnect_flag = False
        elif open_flag==True:
            print("Arduino is already opened at port:",portNoArduino)
            TBOX_MN_print("Arduino is already opened at port:",portNoArduino)
            arduinoConnect_flag = True
        else:
            try: arduino_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Arduino Devices Present.")
            TBOX_MN_print("No Arduino Devices Present.")
            arduinoConnect_flag = False

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
                TBOX_MN_print("Connect to Cobolt 06-MLD 488nm Laser at port:", portNoLaser)
                laserConnect_flag = True # assign True state to the laser connection flag
            except Exception as error:
                raise SerialException (f'{portNoLaser} not accesible. Error: {error}')
                laserConnect_flag = False
        elif open_flag==True:
            print("Cobolt 06-MLD 488nm Laseris already opened at port:",portNoLaser)
            TBOX_MN_print("Cobolt 06-MLD 488nm Laseris already opened at port:",portNoLaser)
            laserConnect_flag = True
        else:
            try: laser488_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Cobolt 06-MLD 488nm Laser Presents.")
            TBOX_MN_print("No Cobolt 06-MLD 488nm Laser Presents.")
            laserConnect_flag = False
    else:
        print("Wrong function argument.")
        TBOX_MN_print("Wrong function argument.")
        
    
    # Last, return port of devices for further use
    return [portNoArduino, portNoLaser]

# openSerialPort()
# openSerialPort("arduino")
# openSerialPort("laser")
# openSerialPort("lc")

# arduino_Serial.__del__()
# laser488_Serial.__del__()
########## end of cell @PyArduino_2DPOLIM_Sync_0.py
#======== Auxiliary Functions Ends Here ========

# Buttons
def openSerialPort_Arduino():
    TBOX_MN_print("Open Arduino's Serial Port...")
    openSerialPort("arduino")
    print("CNSL: openSerialPort_Arduino")
    # text_response = str(openSerialPort("arduino"))
    # show text in main text box
    # main_text_box.insert('end', text_response +'\n') # show text by inserting
    # Refresh the button state
    buttonStateRefresh()

def openSerialPort_Laser():
    TBOX_MN_print("Open Laser's Serial Port...")
    openSerialPort("laser")
    print("CNSL: openSerialPort_Laser")
    # text_response = str(openSerialPort("laser"))
    # # show text in main text box
    # main_text_box.insert('end', text_response +'\n') # show text by inserting
    # Refresh the button state
    buttonStateRefresh()

def closeSerialPort_Laser_Arduino():
    TBOX_MN_print("Close Serial Port of Laser & Arduino...")
    print("CNSL: closeSerialPort_Laser and Arduino")
    
    global arduinoConnect_flag, laserConnect_flag

    try:
        arduino_Serial.__del__()
        print("Arduino is disconnected!")
        TBOX_MN_print("Arduino is disconnected!")
        arduinoConnect_flag = False
    except:
        pass
        print("Error in disconnecting Arduino!")
        TBOX_MN_print("Error in disconnecting Arduino!")
        
    try:
        laser488_Serial.__del__()
        print("Laser is disconnected!")
        TBOX_MN_print("Laser is disconnected!")
        laserConnect_flag = False
    except:
        pass
        print("Error in disconnecting Laser!")
        TBOX_MN_print("Error in disconnecting Laser!")
    # Refresh the button state
    buttonStateRefresh()

#create action buttons & 
openSerialPort_Arduino_btn = tk.Button(root, text="Connect to Arduino", command=lambda:openSerialPort_Arduino(), foreground="white", background="lime green")
openSerialPort_Laser_btn = tk.Button(root, text="Connect to Laser", command=lambda:openSerialPort_Laser(), foreground="white", background="lime green")
openSerialPort_Close_btn = tk.Button(root, text="Close ALL Serial Ports", command=lambda:closeSerialPort_Laser_Arduino(), foreground="black", background="white")

#place buttons on grid
openSerialPort_Arduino_btn.grid(row=1, column=3, pady=10)
openSerialPort_Laser_btn.grid(row=1, column=4)
openSerialPort_Close_btn.grid(row=1, column=5)

## Section B: Laser ON/OFF and configuration of Both Arduino and laser
## B1: Laser ON/OFF

# laser ON in CW trigger
def laserTriggerOn(if_ON):
    if if_ON == 1:
        myLabel0Text.set("Laser is ON! (CW mode)")
        TBOX_MN_print("Laser is ON! (CW mode)")
        print("CNSL: Laser is ON! (CW mode)")
        PyArduinoCMD("cwm1")
    elif if_ON ==0:
        myLabel0Text.set("Laser is OFF! (CW mode)")
        TBOX_MN_print("Laser is OFF! (CW mode)")
        print("CNSL: Laser is OFF! (CW mode)")
        PyArduinoCMD("cwm0")
        
laserON_btn = tk.Button(root, text="Laser ON!", command=lambda:laserTriggerOn(1), foreground="yellow", background="red")
# PyArduinoCMD("cwm1") #issue: the cam cannot work in cw mode. need to turn off trigger in cam setting manually
laserON_btn.grid(row=3,column=6)

# laser OFF in CW trigger
laserOFF_btn = tk.Button(root, text="Laser OFF", command=lambda:laserTriggerOn(0), foreground="yellow", background="green")
# PyArduinoCMD("cwm0") #issue: the cam cannot work in cw mode. need to turn off trigger in cam setting manually
laserOFF_btn.grid(row=3,column=7)

## B2: Laser config. (Done on 2022.12.01)
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

# Read laser power
laserPowerConfig_Label = tk.Label(root, text="Laser Power (mW): ")
laserPowerConfig_Label.grid(row=2,column=5, sticky="E")

# Input box
laserPowerConfig_Entry = tk.Entry(root, width=6)
laserPowerConfig_Entry.grid(row=2,column=6, sticky="W")
laserPowerConfig_Entry.insert(0, "select...")

# Combobox to select read/set value
laserPowerConfig_Combobox = ttk.Combobox(root, width = 14) # Combobox is in ttk
laserPowerConfig_Combobox['value'] = ("Read Laser Power","Set Laser Power") # set manu of combobox
laserPowerConfig_Combobox.current(0) # set default selection of the first item
laserPowerConfig_Combobox.grid(row=2,column=7, sticky="W", padx=5)

# Button for executing read/set value
laserPowerConfig_btn = tk.Button(root, text="Execute", command=lambda:laserPowerConfigButton(), fg="red", bg="light yellow")
laserPowerConfig_btn.grid(row=2,column=8,sticky="W")


# Function of executing combobox selection: read/set laser power in modulation mode.
def laserPowerConfigButton():
    # .get() to obtain value of combobox selection
    cmbox = laserPowerConfig_Combobox.get()
    print(cmbox," ", type(cmbox))

    if cmbox == "Read Laser Power":
        try:
            laserPower = PyLaserCMD("glmp?") ## "glmp?" Get laser modulation power set point. Return: str(Float) (mW)
        except: 
            print("Error: something wrong during getting Power Setting from Cobolt Laser.")
            TBOX_MN_print("Error: something wrong during getting Power Setting from Cobolt Laser.")
            
        # Assign value to input box: laserPowerConfig_Entry
        laserPowerConfig_Entry.delete(0, 'end')
        laserPowerConfig_Entry.insert(0, laserPower)
        print("Read Laser Power: ", laserPower, "mW")
        TBOX_MN_print("Read Laser Power: ", laserPower, "mW")
        
    elif cmbox == "Set Laser Power":
        ### Assign laser power of modulation mode to Cobolt laser
        # First, Get value from input boxe: laserPowerConfig_Entry, and convert to float
        try:
            laserPower_Set = float(laserPowerConfig_Entry.get())
        except: 
            print("Error: something wrong during getting values from input box.")
            TBOX_MN_print("Error: something wrong during getting values from input box.")
        print(laserPower_Set)
        
        # Second, set power to Cobolt laser by cmd
        # print("slmp {}".format(laserPower_Set))
        laserPower_Set_IsOK = PyLaserCMD("slmp {}".format(laserPower_Set)) # Set laser modulation power to xx mW
        
        if laserPower_Set_IsOK == "OK":
            print("Set Laser Power to: ", laserPower_Set, "mW")
            TBOX_MN_print("Set Laser Power to: ", laserPower_Set, "mW")
        else:
            print("Error: something wrong during setting Power to Cobolt Laser.")
            TBOX_MN_print("Error: something wrong during setting Power to Cobolt Laser.")

"""
##########################  Example: write value from input box
    # Readout LCWaitTime:
    findSub = "LCWaitTime = "
    LCWaitTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
    LCWaitTimeVal = int(LCWaitTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(LCWaitTimeVal)
    # Assign value to input box
    entry3_lcwait.delete(0, 'end')
    entry3_lcwait.insert(0, str(LCWaitTimeVal))
##########################  Example ends
##########################  Example: read value from input box
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

########################## Example ends

    
###### Used for GUI laser power setting
PyLaserCMD("slmp 30.56") # Set laser modulation power to 30 mW
#RTN: Send command to laser: slmp 30.56
#RTN: Laser returns: OK
#RTN: Out[24]: 'OK'

PyLaserCMD("glmp?") ## "glmp?" Get laser modulation power set point. Return: Float (mW)
#RTN: Send command to laser: glmp?
#RTN: Laser returns: 30.6
#RTN: Out[25]: '30.6'
######
"""
## A3: Test LC communication (!!!Funcionality is Unfinished!!!): still missing: sending cmd to LC to initiate cycle mode/re-set cycling states. 
# Implemented on 2022/11/02
# A changable Label to show status of LC port test
''' Example:
myLabel0Text = tk.StringVar()
myLabel0 = tk.Label(root, textvariable = myLabel0Text)

myLabel0Text.set("Bye bye!")
# Change the color config. of the label widget:
myLabel0.config(bg = "green", fg = "yellow")
'''
LCPortCheckLabel0 = tk.Label(root, text = "LC Port Status:")
LCPortCheckLabel0.grid(row=3, column=3, sticky="E")

LCPortCheckText = tk.StringVar()
LCPortCheckLabel = tk.Label(root, textvariable = LCPortCheckText)
LCPortCheckLabel.grid(row=3, column=4, sticky="W")
# Inertial text:
LCPortCheckText.set("Undetected")
LCPortCheckLabel.config(bg = "yellow", fg = "red")

# Button to check LC communication:
LCPortCheck_btn = tk.Button(root, text="Check LC Port", command=lambda:LCPortCheck(), foreground="white", background="lime green")
LCPortCheck_btn.grid(row=3,column=5,sticky="W")

### LC control
"""
Script to call the c-program wrapper "LC_CMD_DLL.dll" which contains functions 
to control the LC polarization retarder (Meadowlark Optics D5020) by sending 
ASCII commands. 

By using ctypes library, the ASCII commands (binary string in python) can be 
converted to C acceptable strings and passed to the function in c-program, and 
the returned data is passed back. 

Created on Fri Jul  8 15:07:24 2022

@author: Yutong
"""

import ctypes

### Load my DLL into memory.
'''
# Both ctypes.WinDLL and ctypes.CDLL can work
# ctypes.CDLL - Instances of this class represent loaded shared libraries. 
Functions in these libraries use the standard C calling convention, and are 
assumed to return int.
'''
# LC_CMD_DLL = ctypes.WinDLL(r"D:\MyDocs\PROG\VS\source\repos\LC_CMD_DLL\x64\Debug\LC_CMD_DLL.dll")
#LC_CMD_DLL = ctypes.CDLL(r"D:\MyDocs\PROG\VS\source\repos\LC_CMD_DLL\x64\Debug\LC_CMD_DLL.dll") 
LC_CMD_DLL = ctypes.CDLL(r"D:\Research\HeintzmannLab\Programming\DevCtrl\code\mine\LC_CMD_DLL.dll") #Laptop

#LC_CMD_DLL = ctypes.CDLL(r"D:\2DPOLIM\Setup\codes\LC_D5020_DLL\LC_CMD_DLL.dll")  # (Lab PC) locate the folder where the dll files are stored.

# Acquire the function signature of C function: "char* LCCMD(char* lcCmdStr)" in LC_CMD_DLL.dll
CppLCCMD = LC_CMD_DLL.LCCMD 

### Define ctypes data types of argument & return value in advance @ 2022.07.07

# ctypes.c_char_p related to char * (NUL terminated) in C and bytes object or None in Python
CppLCCMD.argtypes = [ctypes.c_char_p] #Assign a tuple of ctypes types to specify the argument types that the function accepts.
CppLCCMD.restype = ctypes.c_char_p #Assign a ctypes type to specify the result type of the foreign function. 


### Define a function to sending ASCII command to LC controller (via calling LC_CMD_DLL.LCCMD in c-program)
def PyLCCMD(cmd):
    """
    Input: cmd - a string of ASCII command. e.g. "ver:?"

    Returns: a string of response from LC controller

    """
    print("Send command:",cmd)
    
    # Encode the string to bytes which is C-acceptable. i.e. "ver:?" to b"ver:?"
    cmd = cmd.encode() 
    
    # Send arguement cmd to function "char* LCCMD(char* lcCmdStr)" in c-program, and convert returned bytes to string
    LCResp = CppLCCMD(ctypes.c_char_p(cmd)).decode("utf-8")
    
    print("LC returns:",LCResp)
    
    return LCResp

'''
###### (!!!Half-Done!!!): sending cmd to LC to initiate cycle mode/re-set cycling states. 
# Need more buttons for it (optional)

#### Initialize the LC controller into trigger pulse cycle mode before 2D POLIM measurement:
    
#Send 1st command "ver:?":
#Description: Query firmware version. Controller returns firmware version and copyright string.This is used to test communication with the PC.
# print("Return from LC:", PyLCCMD("ver:?")) # null termination '\0' is not necessary
PyLCCMD("ver:?")    # if connected, returns 'ver:1.05 (c) 2013-2020 Meadowlark Optics,Inc.'

#Send 2nd command "cyclp:1":
#Description: Tells the controller to cycle through all valid states (7 states corresponding to 6 polarization angles and a NULL state of 0V). State change occurs only when a trigger pulse is detected on the controller’s trigger input. "1" in the command starts cycling, while "0" stops cycling.
# print("Return from LC:", PyLCCMD("cyclp:1"))
PyLCCMD("cyclp:1")

#Send 3rd command "cycm:?":
#Description: Queries the current cycling mode of the controller. Result indicates command being executed. 1 = constant state; 2 = cyc; 3 = cycl; 4 = cycp; 5 = cyclp; 6 =rand. “cycm:5” will be returned if everything is correct.
# print("Return from LC:", PyLCCMD("cycm:?"))
LCCycmStat = PyLCCMD("cycm:?")

if (LCCycmStat=="cycm:5"):
    print("Initialized the LC controller into trigger pulse cycle mode.")
else:
    print("Error occurs! Do NOT run 2D POLIM before the LC controller is correctly initialized.")

### Or directly call the defined function "SetLCCyclp1()" in LC_CMD_DLL.dll for doing the same thing without passing arguement from Python to C:
# LC_CMD_DLL.SetLCCyclp1()
# print("Initialized the LC controller into trigger pulse cycle mode.")
'''
# LCPortCheck_flag = False
def LCPortCheck():
    # Do LC port check by sending a command
    global LCPortCheck_flag
    
    #Description: Query firmware version. Controller returns firmware version and copyright string.This is used to test communication with the PC.
    LCDataStr = PyLCCMD("ver:?")    # if connected, returns 'ver:1.05 (c) 2013-2020 Meadowlark Optics,Inc.'
    if ('ver:' in LCDataStr):
        LCPortCheck_flag = True
        print("LC communication test: PASS.")
        TBOX_MN_print("LC communication test: PASS.")
    else:
        LCPortCheck_flag = False
        print("LC communication test: FAIL.")
        TBOX_MN_print("LC communication test: FAIL.")
    
    # Show the port test result 
    if LCPortCheck_flag == True or demo_flag == True:  # demo_flag == True is just for demo. when without LC at around.
        LCPortCheckText.set("Ready")
        LCPortCheckLabel.config(bg = "green", fg = "yellow")
        LCPortCheck_flag = True
    else:
        LCPortCheckText.set("FAILED")
        LCPortCheckLabel.config(bg = "yellow", fg = "red")
    
    # Refresh the button state
    buttonStateRefresh()
    

## Section C: 2DPOLIM Acquisition: Arduino configuration and control
########## first part @PyArduino_2DPOLIM_Sync_0.py

#======== Auxiliary Functions Starts Here ========
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
            TBOX_MN_print(arduinoDataPacket)

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

#======== Auxiliary Functions Ends Here ========

### C1: Parameter Configuration (readout & set) of Arduino
# done @ 0:40 2022/10/18 

# Readout current config. of Arduino. on 2022/10/16-17

triggerConfigLabel = tk.Label(root, text="Trigger Timing\nConfiguration (unit: ms):", fg="blue") #, font="Raleway")
triggerConfigLabel.grid(column=0, row=0, sticky="NE")#, columnspan=3) # position of label

# Input fields (Entry) and their labels for Changing config.
# entry1. # of Repetition(var:numScan)
entry1_nscan_Label = tk.Label(root, text="# of Repetition =", fg="red")
entry1_nscan_Label.grid(column=0, row=1, sticky="E")

entry1_nscan = tk.Entry(root, width=6)
entry1_nscan.grid(column=1, row=1, padx=10, sticky="W") # padx: add space between the adjacent widget of xx px.
entry1_nscan.insert(0, "click 'Show Parameters'")
# entry1_nscan.delete(0,'end') # or entry1_nscan.delete(0, tk.END) ; tk.END='end'

# entry2. LC Pulse Width(var:triggerPulseWidthLC)
entry1_nscan_Label = tk.Label(root, text="LC Pulse Width =")
entry1_nscan_Label.grid(column=0, row=2, sticky="E")

entry2_lcpt = tk.Entry(root, width=6)
entry2_lcpt.grid(column=1, row=2, padx=10, sticky="W")
entry2_lcpt.insert(0, "click 'Show Parameters'")

# entry3. LC Wait Time(var:LCWaitTime) 
entry3_lcwait_Label = tk.Label(root, text="LC Wait Time =")
entry3_lcwait_Label.grid(column=0, row=3, sticky="E")

entry3_lcwait = tk.Entry(root, width=6)
entry3_lcwait.grid(column=1, row=3, padx=10, sticky="W")
entry3_lcwait.insert(0, "click 'Show Parameters'")

# entry4. Exposure Pulse Width(var:triggerPulseWidthMain)
entry4_mnpt_Label = tk.Label(root, text="Exposure Pulse Width =", fg="red")
entry4_mnpt_Label.grid(column=0, row=4, sticky="NE")

entry4_mnpt = tk.Entry(root, width=6)
entry4_mnpt.grid(column=1, row=4, padx=10, sticky="NW")
entry4_mnpt.insert(0, "click 'Show Parameters'")

# entry5. Interval between Repetitions(var:triggerDelayTime)
entry5_pdly_Label = tk.Label(root, text="Interval between Repetitions =")
entry5_pdly_Label.grid(column=0, row=5, sticky="NE")

entry5_pdly = tk.Entry(root, width=6)
entry5_pdly.grid(column=1, row=5, padx=10, sticky="NW")
entry5_pdly.insert(0, "click 'Show Parameters'")

# Read and Show current config.
def getArduinoConfig():
    CurrentArduinoConfigList = PyArduinoCMD("parm?", if_return = True)
    
    # Readout numScan(# of Repetition):
    findSub = "# of Repetition(var:numScan) = "
    # locate substring in the list
    numScanVal = [i for i in CurrentArduinoConfigList if findSub in i] #RTN:['numScan = 5']
    # Retrive the value of config. and convert it into int
    numScanVal = int(numScanVal[0].split("= ")[-1])
    print(numScanVal)
    # Assign value to input box
    entry1_nscan.delete(0, 'end')
    entry1_nscan.insert(0, str(numScanVal))
    
    # Readout triggerPulseWidthLC(LC Pulse Width):
    findSub = "LC Pulse Width(var:triggerPulseWidthLC) = "
    triggerPulseWidthLCVal = [i for i in CurrentArduinoConfigList if findSub in i]
    triggerPulseWidthLCVal = int(triggerPulseWidthLCVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(triggerPulseWidthLCVal)
    # Assign value to input box
    entry2_lcpt.delete(0, 'end')
    entry2_lcpt.insert(0, str(triggerPulseWidthLCVal))
    
    # Readout LCWaitTime(LC Wait Time):
    findSub = "LC Wait Time(var:LCWaitTime) = "
    LCWaitTimeVal = [i for i in CurrentArduinoConfigList if findSub in i]
    LCWaitTimeVal = int(LCWaitTimeVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(LCWaitTimeVal)
    # Assign value to input box
    entry3_lcwait.delete(0, 'end')
    entry3_lcwait.insert(0, str(LCWaitTimeVal))
    
    # Readout triggerPulseWidthMain(Exposure Pulse Width):
    findSub = "Exposure Pulse Width(var:triggerPulseWidthMain) = "
    triggerPulseWidthMainVal = [i for i in CurrentArduinoConfigList if findSub in i]
    triggerPulseWidthMainVal = int(triggerPulseWidthMainVal[0].split("= ")[-1][:-2]) # '5ms': [:-2] for removing 'ms'
    print(triggerPulseWidthMainVal)
    # Assign value to input box
    entry4_mnpt.delete(0, 'end')
    entry4_mnpt.insert(0, str(triggerPulseWidthMainVal))
    
    # Readout triggerDelayTime(Interval between Repetitions):
    findSub = "Interval between Repetitions(var:triggerDelayTime) = "
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


## Implement GUI Widgets 
showArduinoConfig_btn = tk.Button(root, text="Read Trigger Config", command=lambda:getArduinoConfig(), foreground="white", background="#20bebe")
showArduinoConfig_btn.grid(row=2, column=3, padx=10, pady=10)

setArduinoConfig_btn = tk.Button(root, text="Set Trigger Config", command=lambda:setArduinoConfig(), foreground="red", background="yellow")
setArduinoConfig_btn.grid(row=2, column=4, padx=10, pady=10)

    
## C2: Operation Modes of Arduino 
## Start @ 05/10/2022 0:10
## Implement LC Initialization in acquisition @ 18/01/2023 23:00

# 1. Acquisition mode
def PyArduinoCMD_acqm():
    myLabel0Text.set("Start Acquisition!")
    print("CNSL: PyArduinoCMD_acqm")
    
    # text_response = "Start acquisition!"
    # main_text_box.insert('end', text_response +'\n') # show text by inserting
    TBOX_MN_print("Start Acquisition!")
    
    # Action:
    # PyArduinoCMD("acqm")
    
    # Step 1. Initialize the LC to cycle mode:
    #Send command "cyclp:1" to set LC into cycle mode
    #Description: Tells the controller to cycle through all valid states (7 states corresponding to 6 polarization angles and a NULL state of 0V). State change occurs only when a trigger pulse is detected on the controller’s trigger input. "1" in the command starts cycling, while "0" stops cycling.
    # print("Return from LC:", PyLCCMD("cyclp:1"))
    PyLCCMD("cyclp:1")
    
    #Send command "cycm:?" for checking current mode of LC:
    #Description: Queries the current cycling mode of the controller. Result indicates command being executed. 1 = constant state; 2 = cyc; 3 = cycl; 4 = cycp; 5 = cyclp; 6 =rand. “cycm:5” will be returned if everything is correct.
    # print("Return from LC:", PyLCCMD("cycm:?"))
    LCCycmStat = PyLCCMD("cycm:?")

    if LCCycmStat=="cycm:5":
        print("Initialized the LC controller into trigger pulse cycle mode.")
        TBOX_MN_print("Initialized the LC controller into trigger pulse cycle mode.")
        
        # Step 2. Arduino start triggering: 
        PyArduinoCMD("acqm")
        # text_response = "Acquisition is done!"
        # main_text_box.insert('end', text_response +'\n') # show text by inserting
        TBOX_MN_print("Acquisition is done!")
        print("Acquisition is done!")
        myLabel0Text.set("Acquisition is done!")
        
    elif demo_flag == True:
        myLabel0Text.set("[Demo]Start Acquisition!")
        print("[Demo]CNSL: PyArduinoCMD_acqm")
        TBOX_MN_print("[Demo]Start Acquisition!")
        print("!!!NOTICE: This is a Demo, NOT a real acquisition!!!")
        TBOX_MN_print("!!!NOTICE: This is a Demo, NOT a real acquisition!!!")
        
        # Step 2. Arduino start triggering: 
        PyArduinoCMD("acqm")
        TBOX_MN_print("[Demo]Acquisition is done!", "\n","!!!NOTICE: This is a Demo, NOT a real acquisition!!!")
        print("[Demo]Acquisition is done!", "\n","!!!NOTICE: This is a Demo, NOT a real acquisition!!!")
        myLabel0Text.set("[Demo]Acquisition is done!")
    
    else:
        print("Error occurs! Do NOT run 2D POLIM UNLESS the LC controller is correctly initialized.")
        TBOX_MN_print("Error occurs! Do NOT run 2D POLIM UNLESS the LC controller is correctly initialized.")
    

startAcquisitionMode_btn = tk.Button(root, text="Start Acquisition!", command=lambda:PyArduinoCMD_acqm(), foreground="yellow", background="red")
startAcquisitionMode_btn.grid(row=4, column=3)

# 2. Infinite triggering mode (!!!Funcionality is Unfinished!!!)
'''
PyArduinoCMD("infm")

PyArduinoCMD("infm0")
'''
def PyArduinoCMD_infm():
    myLabel0Text.set("Start Infinite Trigger Mode!")
    print("CNSL: PyArduinoCMD_infm")
    
    TBOX_MN_print("Start Infinite Trigger Mode!")
    
    # Action:
    #Initialize the LC to cycle mode:
    PyLCCMD("cyclp:1")
    
    PyArduinoCMD("infm")
    
    TBOX_MN_print("Infinite Trigger Mode is on! Click 'Stop Infinite Trigger Mode' to termninate.")

startInfiniteMode_btn = tk.Button(root, text="Start Infinite\nTrigger Mode", command=lambda:PyArduinoCMD_infm(), fg="red", bg="light yellow")
startInfiniteMode_btn.grid(row=4, column=4)

def PyArduinoCMD_infm0():
    myLabel0Text.set("Stop Infinite Trigger Mode!")
    print("CNSL: PyArduinoCMD_infm0")
    
    TBOX_MN_print("Stop Infinite Trigger Mode!")
    
    # Action:
    PyArduinoCMD("infm0")
    
    TBOX_MN_print("Infinite Trigger Mode is terminated!")

stopInfiniteMode_btn = tk.Button(root, text="Stop Infinite\nTrigger Mode", command=lambda:PyArduinoCMD_infm0(), fg="light yellow", bg="#20bebe")
stopInfiniteMode_btn.grid(row=5, column=4, sticky="N")

### Some ending code:

# Activate/disable Button based on the value of connection flag. Implement @ 2023.01.16
'''
3 flags of connection of devices:
laserConnect_flag = False
arduinoConnect_flag = False
LCPortCheck_flag = False
'''
def buttonStateRefresh():
    '''
    Refresh the state of buttons. Check the related flag value and set the button state between "NORMAL" and "DISABLED"
    
    Returns
    -------
    None.
    '''
    global demo_flag, laserConnect_flag, arduinoConnect_flag, LCPortCheck_flag
    # 1. Laser related buttons: when laserConnect_flag == True
    if laserConnect_flag == True:
        laserPowerConfig_btn.config(state=tk.NORMAL) # set button state to "NORMAL" when device is connected
        laserON_btn.config(state=tk.NORMAL)
        laserOFF_btn.config(state=tk.NORMAL)
    else: 
        laserPowerConfig_btn.config(state=tk.DISABLED) # set button state to "DISABLED" when device is connected
        laserON_btn.config(state=tk.DISABLED)
        laserOFF_btn.config(state=tk.DISABLED)
        
    # 2. Arduino related buttons: when arduinoConnect_flag == True
    if arduinoConnect_flag == True:
        showArduinoConfig_btn.config(state=tk.NORMAL) # set button state to "NORMAL" when device is connected
        setArduinoConfig_btn.config(state=tk.NORMAL)
    else: 
        showArduinoConfig_btn.config(state=tk.DISABLED) # set button state to "DISABLED" when device is connected
        setArduinoConfig_btn.config(state=tk.DISABLED)
        
    # 3. Acquisition buttons: when arduinoConnect_flag == True and LCPortCheck_flag == True
    if arduinoConnect_flag == True and LCPortCheck_flag == True:
        startAcquisitionMode_btn.config(state=tk.NORMAL) # set button state to "NORMAL" when device is connected
        startInfiniteMode_btn.config(state=tk.NORMAL)
        stopInfiniteMode_btn.config(state=tk.NORMAL)
    else:
        startAcquisitionMode_btn.config(state=tk.DISABLED) # set button state to "DISABLED" when device is connected
        startInfiniteMode_btn.config(state=tk.DISABLED)
        stopInfiniteMode_btn.config(state=tk.DISABLED)
    
# Done: add flags to certain buttons, and using buttonStateRefresh() for certain functions.
buttonStateRefresh()

# end of main window
root.mainloop()
