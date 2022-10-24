# -*- coding: utf-8 -*-
"""
File name: 2DPOLIM_SyncGUI_0.py
@author: Yutong

Graphic User Interface (GUI) software for system control and image acquisition 
of 2DPOLIM setup. Functionalities are mostly adapted from PyArduino_2DPOLIM_Sync_0.py

Created on Sun Sep 18 15:25:54 2022

Key updates:
    - First complete design of frame @ 2022/10/24
"""
# cd D:\\MyDocs\\PROG\\Python\\MyPy
# cd D:\\MyDocs\\PROG\\Python\\libs\\tkinter\\MariyaSha_Tutorial\\PDFextract_text-main\\finishedProject
# cd D:\\Research\\HeintzmannLab\\Programming\\DevCtrl\\2DPOLIM_GUI
# pwd
###

import tkinter as tk
from tkinter import ttk # contains Combobox
from PIL import Image, ImageTk

import time
import serial
from serial import SerialException
from serial.tools import list_ports

# just for testing
import random

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

# button with switch of text
buttonSwitch_flag = 0

def buttonSwitch():
    global buttonSwitch_flag
    flag = random.randint(1,11)
    if flag <=5:
        buttonSwitch_flag = 0
    else:
        buttonSwitch_flag = 1
      
    if buttonSwitch_flag == 0:
        switch_btn_Text.set("Switch ON")
        buttonSwitch_text = "Hello!"
        # Change the text variable of label widget:
        myLabel0Text.set("Hello!")
        # Change the color config. of the label widget:
        myLabel0.config(bg = "yellow", fg = "red")
    else:
        switch_btn_Text.set("Switch OFF")
        buttonSwitch_text = "Bye bye!"
        # Change the text variable of label widget:
        myLabel0Text.set("Bye bye!")
        # Change the color config. of the label widget:
        myLabel0.config(bg = "green", fg = "yellow")
        
    main_text_box.insert('end', buttonSwitch_text + '\n')
    # switch button
switch_btn_Text = tk.StringVar()
switch_btn = tk.Button(root, textvariable=switch_btn_Text, command=lambda:buttonSwitch(), font="Raleway", bg="#20bebe", fg="white", height=2, width=15)

if buttonSwitch_flag == 0:
    switch_btn_Text.set("Switch ON")
else:
    switch_btn_Text.set("Switch OFF")
    
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
                TBOX_MN_print("Connect to Arduino at port:",portNoArduino)
            except Exception as error:
                raise SerialException (f'{portNoArduino} not accesible. Error: {error}')
        elif open_flag==True:
            print("Arduino is already opened at port:",portNoArduino)
            TBOX_MN_print("Arduino is already opened at port:",portNoArduino)
        else:
            try: arduino_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Arduino Devices Present.")
            TBOX_MN_print("No Arduino Devices Present.")

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
            except Exception as error:
                raise SerialException (f'{portNoLaser} not accesible. Error: {error}')
        elif open_flag==True:
            print("Cobolt 06-MLD 488nm Laseris already opened at port:",portNoLaser)
            TBOX_MN_print("Cobolt 06-MLD 488nm Laseris already opened at port:",portNoLaser)
        else:
            try: laser488_Serial.__del__() # try to close the port if it is still hooked.
            except:
                pass
            print("No Cobolt 06-MLD 488nm Laser Presents.")
            TBOX_MN_print("No Cobolt 06-MLD 488nm Laser Presents.")
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

def openSerialPort_Laser():
    TBOX_MN_print("Open Laser's Serial Port...")
    openSerialPort("laser")
    print("CNSL: openSerialPort_Laser")
    # text_response = str(openSerialPort("laser"))
    # # show text in main text box
    # main_text_box.insert('end', text_response +'\n') # show text by inserting

def closeSerialPort_Laser_Arduino():
    TBOX_MN_print("Close Serial Port of Laser/Arduino...")
    print("CNSL: closeSerialPort_Laser and Arduino")

    try:
        arduino_Serial.__del__()
    except:
        pass
        print("Error in disconnecting Arduino!")
        TBOX_MN_print("Error in disconnecting Arduino!")
        
    try:
        laser488_Serial.__del__()
    except:
        pass
        print("Error in disconnecting Laser!")
        TBOX_MN_print("Error in disconnecting Laser!")

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

## B2: Laser config. (!!!Funcionality is Unfinished!!!)
# Read laser power
laserPowerConfig_Label = tk.Label(root, text="Laser Power (mW): ")
laserPowerConfig_Label.grid(row=2,column=5, sticky="E")

# Input box
laserPowerConfig_Entry = tk.Entry(root, width=6)
laserPowerConfig_Entry.grid(row=2,column=6, sticky="W")
laserPowerConfig_Entry.insert(0, "click")

pass

# Combobox to select read/set value
laserPowerConfig_Combobox = ttk.Combobox(root, width = 14) # Combobox is in ttk
laserPowerConfig_Combobox['value'] = ("Read Laser Power","Set Laser Power") # set manu of combobox
laserPowerConfig_Combobox.current(0) # set default selection of the first item
laserPowerConfig_Combobox.grid(row=2,column=7, sticky="W", padx=5)

pass

# Button for executing read/set value
laserPowerConfig_btn = tk.Button(root, text="Execute",fg="red", bg="light yellow")
laserPowerConfig_btn.grid(row=2,column=8,sticky="W")
 
pass




## A3: Test LC communication (!!!Funcionality is Unfinished!!!)
# A changable Label to show status of LC port test
''' Example:
myLabel0Text = tk.StringVar()
myLabel0 = tk.Label(root, textvariable = myLabel0Text)

myLabel0Text.set("Bye bye!")
# Change the color config. of the label widget:
myLabel0.config(bg = "green", fg = "yellow")
'''
LCPortCkeckLabel0 = tk.Label(root, text = "LC Port Status:")
LCPortCkeckLabel0.grid(row=3, column=3, sticky="E")

LCPortCkeckText = tk.StringVar()
LCPortCkeckLabel = tk.Label(root, textvariable = LCPortCkeckText)
LCPortCkeckLabel.grid(row=3, column=4, sticky="W")
# Inertial text:
LCPortCkeckText.set("Undetected")
LCPortCkeckLabel.config(bg = "yellow", fg = "red")

# Button to check LC communication:
LCPortCkeck_btn = tk.Button(root, text="Check LC Port", command=lambda:LCPortCkeck(), foreground="white", background="lime green")
LCPortCkeck_btn.grid(row=3,column=5,sticky="W")

pass
def LCPortCkeck():
    if buttonSwitch_flag == 1:
        LCPortCkeckText.set("Ready")
        LCPortCkeckLabel.config(bg = "green", fg = "yellow")
    else:
        LCPortCkeckText.set("FAILED")
        LCPortCkeckLabel.config(bg = "yellow", fg = "red")
    



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

triggerConfigLabel = tk.Label(root, text="Trigger Timing\n Configuration:", fg="blue") #, font="Raleway")
triggerConfigLabel.grid(column=0, row=0, sticky="E")#, columnspan=3) # position of label

# Input fields (Entry) and their labels for Changing config.
# entry1. # of Full Scan
entry1_nscan_Label = tk.Label(root, text="# of Full Scan =")
entry1_nscan_Label.grid(column=0, row=1, sticky="E")

entry1_nscan = tk.Entry(root, width=6)
entry1_nscan.grid(column=1, row=1, padx=10, sticky="W") # padx: add space between the adjacent widget of xx px.
entry1_nscan.insert(0, "click 'Show Parameters'")
# entry1_nscan.delete(0,'end') # or entry1_nscan.delete(0, tk.END) ; tk.END='end'

# entry2. triggerPulseWidthLC 
entry1_nscan_Label = tk.Label(root, text="triggerPulseWidthLC =")
entry1_nscan_Label.grid(column=0, row=2, sticky="E")

entry2_lcpt = tk.Entry(root, width=6)
entry2_lcpt.grid(column=1, row=2, padx=10, sticky="W")
entry2_lcpt.insert(0, "click 'Show Parameters'")

# entry3. LCWaitTime = 
entry3_lcwait_Label = tk.Label(root, text="LCWaitTime =")
entry3_lcwait_Label.grid(column=0, row=3, sticky="E")

entry3_lcwait = tk.Entry(root, width=6)
entry3_lcwait.grid(column=1, row=3, padx=10, sticky="W")
entry3_lcwait.insert(0, "click 'Show Parameters'")

# entry4. triggerPulseWidthMain =
entry4_mnpt_Label = tk.Label(root, text="triggerPulseWidthMain =")
entry4_mnpt_Label.grid(column=0, row=4, sticky="NE")

entry4_mnpt = tk.Entry(root, width=6)
entry4_mnpt.grid(column=1, row=4, padx=10, sticky="NW")
entry4_mnpt.insert(0, "click 'Show Parameters'")

# entry5. triggerDelayTime =
entry5_pdly_Label = tk.Label(root, text="triggerDelayTime =")
entry5_pdly_Label.grid(column=0, row=5, sticky="NE")

entry5_pdly = tk.Entry(root, width=6)
entry5_pdly.grid(column=1, row=5, padx=10, sticky="NW")
entry5_pdly.insert(0, "click 'Show Parameters'")

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


## Implement GUI Widgets 
showArduinoConfig_btn = tk.Button(root, text="Read Trigger Config", command=lambda:getArduinoConfig(), foreground="white", background="#20bebe")
showArduinoConfig_btn.grid(row=2, column=3, padx=10, pady=10)

setArduinoConfig_btn = tk.Button(root, text="Set Trigger Config", command=lambda:setArduinoConfig(), foreground="red", background="yellow")
setArduinoConfig_btn.grid(row=2, column=4, padx=10, pady=10)



## C2: Operation Modes of Arduino 
## Start @ 05/10/2022 0:10

# 1. Acquisition mode
def PyArduinoCMD_acqm():
    myLabel0Text.set("Start Acquisition!")
    print("CNSL: PyArduinoCMD_acqm")
    
    # text_response = "Start acquisition!"
    # main_text_box.insert('end', text_response +'\n') # show text by inserting
    TBOX_MN_print("Start Acquisition!")
    
    # Action:
    PyArduinoCMD("acqm")
    
    # text_response = "Acquisition is done!"
    # main_text_box.insert('end', text_response +'\n') # show text by inserting
    TBOX_MN_print("Acquisition is done!")

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

# end of main window
root.mainloop()
