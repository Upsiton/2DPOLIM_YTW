Info. on codes in this folder
by Yutong

======== File name:
\2DPOLIM_GUI\2DPOLIM_SyncGUI.py

Description:
GUI software for 2D POLIM acquisition. Open and run it.

Change if needed at line 597: LC_CMD_DLL = ctypes.CDLL(r"D:\Research\HeintzmannLab\Programming\DevCtrl\code\mine\LC_CMD_DLL.dll")
with the correct directory of the file “LC_CMD_DLL.dll”.

======== File name:
\2DPOLIM_Sync_PyArdu\2DPOLIM_Sync_PyArdu.ino

Description:
The Arduino code. Use Arduino IDE 1.0/2.0 to upload the code to Arduino DUE if Arduino loses the code in its memory. 

======== File name:
\LC Polarization Rotator\LC_CMD_DLL.dll

Description:
The wrapped C++ code for controlling LC in Python. 

======== File name:
call_LC_DLL-Lab.py

Description:
Script to call the c-program wrapper "LC_CMD_DLL.dll" which contains functions to control the LC polarization retarder (Meadowlark Optics D5020) by sending ASCII commands. Only for advanced users. It can be used for re-assigning the pre-stored voltage states for 6 angles by running the whole script when needed. 

Change if needed at line 27: LC_CMD_DLL = ctypes.CDLL(r"D:\2DPOLIM\Setup\codes\LC_D5020_DLL\LC_CMD_DLL.dll")
with the correct directory of the file “LC_CMD_DLL.dll”.

======== File name:
PyArduino_2DPOLIM_Sync.py

Description:
Python script for controlling the Arduino for setup synchronization and image acquisition of 2DPOLIM setup. Only for advanced users. For normal users, use the GUI software by running \2DPOLIM_GUI\2DPOLIM_SyncGUI.py

======== File name:
PyCoboltLaser.py

Description:
Code for controlling the Cobolt laser in Python. Only for advanced users.

======== 
File name:
renameImgs_OldCam.py

Description:
Script for renaming the original images (raw data saved by cameras) of 2D POLIM from old Point Grey Grasshopper®3 cameras (model GS3-U3-23S6M-C). 
The renameImgs.py code has been adapted to the new PCO cameras.
