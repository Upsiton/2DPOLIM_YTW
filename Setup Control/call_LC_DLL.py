# -*- coding: utf-8 -*-
"""
Script to call the c-program wrapper "LC_CMD_DLL.dll" which contains functions 
to control the LC polarization retarder (Meadowlark Optics D5020) by sending 
ASCII commands. 

By using ctypes library, the ASCII commands (binary string in python) can be 
converted to C acceptable strings and passed to the function in c-program, and 
the returned data is passed back. 

Created on Fri Jul  8 15:07:24 2022

@author: Yutong Wang
"""

import ctypes

### Load my DLL into memory. LC controller driver: usbdrvd.dll needs to be in the same directory, too!
'''
# Both ctypes.WinDLL and ctypes.CDLL can work
# ctypes.CDLL - Instances of this class represent loaded shared libraries. 
Functions in these libraries use the standard C calling convention, and are 
assumed to return int.
'''
# locate the folder where the dll files are stored.

LC_CMD_DLL = ctypes.CDLL(r"D:\MyDocs\PROG\VS\source\repos\LC_CMD_DLL\files\LC_CMD_DLL.dll") 

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
    
    # or: LCResp = LC_CMD_DLL.LCCMD(ctypes.c_char_p(cmd)).decode("utf-8")
    
    print("LC returns:",LCResp)
    
    return LCResp


#%% Setting controller states in the Multi-state Switching Mode for 2D POLIM. !!!Uncomment and run it only if necessary!!!
'''
The LC controller D5020 is able to be switched between up to 16 states automatically or when receiving
a pulse on the I/O 1 connector. 
For 2D POLIM, each acquisition contains a scan of 6 polarization angles of excitation (0°, 30°, 60°, 90°, 120°, 150°), which corresponds to 6 states stored in the LC controller that has specific voltage setting.
The code in this cell aims to store the voltages and times of LC states. Apart from the mentioned 6 states, an additional NULL state which indicates 0 V is added to state 1. It is used to relax the LC from high voltage to low voltage and make it ready for the next cycle of scanning.

NOTE: This only needs to be done once!!! The controller will store the setting of states even be turned off. If any change is made in setting, run this part of code to re-set the states of LC controller.
'''

# test connection
PyLCCMD("ver:?")

# Firstly, setting voltages and delay times for state #1 - #7

''' # Discarded. Instead, use for loop to do the job in simpler way.
#set state 1 as 0V (NULL state). set voltage of state 1 of both channels to 0 mV
PyLCCMD("stv:1,0,0") 
PyLCCMD("stv:2,2090,0") # set channel 1 of state 2 as 2090 mV

#Query voltage for state 3
PyLCCMD("stv:1,?")

#Set delay time in 2000ms for a controller state to validate the state. Setting t = 0 disables the state.
PyLCCMD("stt:1,2000") 
#Query delay time for state 1
PyLCCMD("stv:1,?") 
'''

# Creat a list to store voltage of each LC state in mV unit.
# Each voltage corresponding to [NULL state (0V), 0 deg, 30 deg, 60 deg, 90 deg, 120 deg, 150 deg]
lcVoltList = ['0', '2090', '2310', '2560', '2880', '3320', '4030']

for i in range(7):
    
    print("Setting state #{}".format(i+1))
    # print(lcVoltList[i])
        
    # Setting voltage of state #i according to voltage list
    lcCmdV = "stv:{0},{1},0".format(str(i+1), lcVoltList[i])
    # print(lcCmdV)
    PyLCCMD(lcCmdV)
    
    # Query voltage of state i
    lcCmdV = "stv:{},?".format(str(i+1))
    # print(lcCmdV)
    PyLCCMD(lcCmdV)
    
    # Setting Delay time of state i to 2000ms
    lcCmdT = "stt:{},2000".format(str(i+1))
    # print(lcCmdT)
    PyLCCMD(lcCmdT)
    
    # Query Delay time of state i
    lcCmdT = "stt:{},?".format(str(i+1))
    # print(lcCmdT)
    PyLCCMD(lcCmdT)


# Secondly, disable the rest of un-used states #8 - 16 by setting delay time to 0s & voltage to 0V

# Using for loop to set multiple states

# Disable state 8 - 16:
for i in range(8,17):
    
    print("Setting state #{}".format(i))
    
    # Setting voltage of state i to 0V
    lcCmdV = "stv:" + str(i) + ",0,0" # or lcCmdV = "stv:{},0,0".format(str(i))
    # print(lcCmdV)
    PyLCCMD(lcCmdV)
    
    # Query voltage of state i
    lcCmdV = "stv:" + str(i) + ",?"
    # print(lcCmdV)
    PyLCCMD(lcCmdV)
    
    # Setting Delay time of state i to 0ms
    lcCmdT = "stt:" + str(i) + ",0"
    # print(lcCmdT)
    PyLCCMD(lcCmdT)
    
    # Query Delay time of state i
    # lcCmdT = "stt:" + str(i) + ",?"
    lcCmdV = "stt:{},?".format(str(i))
    # print(lcCmdT)
    PyLCCMD(lcCmdT)
    

#%%
##### Initialize the LC controller into trigger pulse cycle mode before 2D POLIM measurement:
    
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

##### More tests
'''
print("Return from LC:", LC_CMD_DLL.LCCMD(ctypes.c_char_p(b"stv:3,2310,0")).decode("utf-8")) # set voltage of state 3 in channel 1 to 2310 mV
print("Return from LC:", LC_CMD_DLL.LCCMD(ctypes.c_char_p(b"stv:3,?")).decode("utf-8")) # Query voltage for state 3

print("Return from LC:", LC_CMD_DLL.LCCMD(ctypes.c_char_p(b"sttaaa:3,2000")).decode("utf-8")) # Wrong cmd returns: error:
print("Return from LC:", LC_CMD_DLL.LCCMD(ctypes.c_char_p(b"stt:3,2000")).decode("utf-8")) # Set delay time 2000 ms for a controller state.
print("Return from LC:", LC_CMD_DLL.LCCMD(ctypes.c_char_p(b"stt:3,?")).decode("utf-8")) # Query delay time for state n.

# Alternative implementation by using string buffer
cmd1 = ctypes.create_string_buffer(b"ver:?")
print("Return from LC:", LC_CMD_DLL.LCCMD(cmd1).decode("utf-8"))
'''
#%% Some commands

# # Go to certain state of LC
# PyLCCMD('state:3')

# # Query current state
# PyLCCMD('state:?')

# # Go to multi-state cycling mode
# PyLCCMD("cyclp:1")

#%% For Demonstration in the Thesis

# """
# Script to call the c-program wrapper "LC_CMD_DLL.dll" which contains functions 
# to control the LC polarization retarder (Meadowlark Optics D5020) by sending 
# ASCII commands. 

# By using ctypes library, the ASCII commands (binary string in python) can be 
# converted to C acceptable strings and passed to the function in c-program, and 
# the returned data is passed back. 

# Created on Fri Jul  8 15:07:24 2022

# @author: Yutong Wang
# """

# import ctypes
# """
# Script to call the c-program wrapper "LC_CMD_DLL.dll" which contains functions 
# to control the LC polarization retarder controller (Meadowlark Optics D5020) by 
# sending ASCII commands. 
# """
# # Load the DLL files (LC_CMD_DLL.dll and usbdrvd.dll) are stored:
# LC_CMD_DLL = ctypes.CDLL(r"D:\MyDocs\PROG\VS\source\repos\LC_CMD_DLL\files\LC_CMD_DLL.dll") 

# # Acquire the function signature of C++ function: "char* LCCMD(char* lcCmdStr)" in LC_CMD_DLL.dll
# try:
#     LC_CMD_DLL.LCCMD # access to the C++ function
# except:
#     print("Error in calling C++ function in LC_CMD_DLL.dll!!!")
    
# ## Define ctypes data types of argument & return:
# # Specify the data type (char * (NUL terminated)) of argument for the foreign C++ function. 
# LC_CMD_DLL.LCCMD.argtypes = [ctypes.c_char_p] 
# # Specify the data type (char * (NUL terminated)) of return for the foreign C++ function. 
# LC_CMD_DLL.LCCMD.restype = ctypes.c_char_p 

# ## Define a function to sending ASCII command to LC controller (calling LC_CMD_DLL.LCCMD in C++ program LC_CMD_DLL.dll)
# def PyLCCMD(cmd):
#     """
#     Input: cmd - a string of ASCII command. e.g. "ver:?"
#     Returns: a string of response from LC controller
#     """
#     print("Send command:",cmd)
#     # Encode the string to bytes which is C-acceptable. i.e. "ver:?" to b"ver:?"
#     cmd = cmd.encode() 
#     # Send arguement cmd to function "char* LCCMD(char* lcCmdStr)" in c-program, and convert returned bytes to string
#     LCResp = LC_CMD_DLL.LCCMD(ctypes.c_char_p(cmd)).decode("utf-8")
    
#     print("LC returns:",LCResp)
#     return LCResp

# # Run the function by sending command "ver:?" to query firmware version.
# print("Return from LC:", PyLCCMD("ver:?"))
