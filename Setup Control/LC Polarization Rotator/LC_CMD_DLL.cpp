// LC_CMD_DLL.cpp : Defines the exported functions for the DLL to sending ASCII commands to LC controller.

// This code is modified from: 
/************************************************************************
*
*                               Meadowlark Optics
*                               Copyright (2006-2017)
*
* File name: usb_ver.cpp
*
* Description: This file contains sample source code that will initialize
*              a USB connection to a Meadowlark Optics D5020, send a
*              ver:? command and read the status response.
*
************************************************************************/

/************************************************************************
*
*								Modified by Yutong Wang
*
* File name: LC_CMD_DLL.cpp
*
* This is the first runnable version of LC command function. The function char* LCCMD(char* lcCmdStr) is defined based on the sample code from Meadowlark
* Optics for sending ASCII command to LC polarization retarder controller D5020 via USB connection.
*
* It enables conversion of string (or char array) to byte array which can be sent to LC device, and converstion of the returned byte array from the device to a string
* (or char array) as its output. The argument of function is a char array (or originally a string) which indicates the ASCII commands given in the device user manual.
* The code is then wrapped into the DLL file LC_CMD_DLL.dll and to be called in python via ctypes libraray.
*
* At 11:50 am on 2022/06/28
*************************************************************************/

/* Wrapping this code into a dll file is inspired from example code from MS c++ tutorial (MathLibrary.cpp : Defines the exported functions for the DLL.)*/

/*********** cpp script start from here ***********/

#include "pch.h" // use stdafx.h in Visual Studio 2017 and earlier
#include <utility>
#include "LC_CMD_DLL.h" //link to the header file of DLL source code: LC_CMD_DLL.cpp

#include <iostream>  // Original: #include <iostream.h> "That header doesn't exist in standard C++. It was part of some pre-1990s compilers"
#include <windows.h>
#include <string> // for using string
using namespace std; //solving “cout” "endl“: 未声明的标识符”

// Load LC controller's drivers:
#include "D:/MyDocs/PROG/VS/source/repos/LC_CMD_DLL/usbdrvd.h" 
#pragma comment(lib,"D:/MyDocs/PROG/VS/source/repos/LC_CMD_DLL/usbdrvd.lib") // use / instead of \ (show in win explorer)


// Define the function that Sending ASCII commands to LC controller and return its response:
// Send command e.g. "ver:?" as char array.

//string LCCMD(string lcCmdStr) // discarded previous implementation using std::string as input/output

char* LCCMD(char* lcCmdStr)
{
	cout << "********************************* Communication Start *********************************" << endl;
#define  flagsandattrs  0x40000000

	/* // Just for debugging
	//printf("%s", lcCmdStr);
	cout << "lcCmdStr: " << lcCmdStr << endl;
	cout << "*lcCmdStr: " << *lcCmdStr << endl;
	cout << "sizeof lcCmdStr = " << sizeof * lcCmdStr << endl;
	cout << "strlen(lcCmdStr) = " << strlen(lcCmdStr) << endl;
	cout << "Type of lcCmdStr: " << typeid(*lcCmdStr).name() << endl;
	cout << "lcCmdStr[1] = " << lcCmdStr[1] << endl;
	*/
	cout << "Send command: " << lcCmdStr << endl;

	// Firstly, convert char array to BYTE (const char) which can be read by device. lcCmd will be sent to the device.
	BYTE* lcCmd = (BYTE*) lcCmdStr;

	//BYTE* lcCmd = (BYTE*)lcCmdStr.c_str(); //Discarded. string to byte pointer: (@2022-06-27 4:22 pm)

	/* // Just for debugging
	//BYTE lcCmd[] = { 'v', 'e', 'r', ':', '?', '\n' }; // cmd "ver:?<CR>" gives the version info. of device.
	//BYTE lcCmd[] = { 'i', 'n', 'v',':','1',',', '1','0','0','0', '\n'}; //"inv:n, v1"

	cout << "lcCmd: " << lcCmd << endl;
	cout << "sizeof lcCmd = " << sizeof lcCmd << endl;
	cout << "Type of lcCmd: " << typeid(lcCmd).name() << endl;
	cout << "lcCmd[5] = " << lcCmd[5] << endl;

	//INT lcCmd_size = 6; //The size of the byte array of the command. 6 for "ver:?<CR>"
	//INT lcCmd_size = sizeof lcCmd; // or use (sizeof lcCmd) / (sizeof * lcCmd);
	//INT lcCmd_size = (INT)lcCmdStr.length() + 1; // +1 to include null termination '\n'
	//INT lcCmd_size = (INT) sizeof lcCmd;

	cout << "Type of strlen(lcCmdStr): " << typeid(strlen(lcCmdStr)).name() << endl;
	//cout << "strlen(lcCMDStr1) = " << strlen(lcCMDStr1) << endl;
	cout << " Real sizeof lcCmd = " << lcCmd_size << endl;
	*/


	INT lcCmd_size = (INT)strlen(lcCmdStr) + 1; // add 1 to the length for including the null termination '\n'

	// Declare buffer to save response value from device:
	BYTE status[64]; // receiving response data from device
	char * statusChar; // convert response data to char as output of function
	//string statusStr; // Discarded.

	HANDLE dev1, pipe0, pipe1;

	UINT devcnt, i;
	UINT USB_PID;
	UINT pipeCount;

	// GUID:'Globally Unique Identifier'. USB_GUID; The GUID_DEVINTERFACE_USB_DEVICE device interface class is defined for USB devices that are attached to a USB hub. Requires <windows.h>
	GUID  theGUID; 

	theGUID.Data1 = 0xa22b5b8b;
	theGUID.Data2 = 0xc670;
	theGUID.Data3 = 0x4198;
	theGUID.Data4[0] = 0x93;
	theGUID.Data4[1] = 0x85;
	theGUID.Data4[2] = 0xaa;
	theGUID.Data4[3] = 0xba;
	theGUID.Data4[4] = 0x9d;
	theGUID.Data4[5] = 0xfc;
	theGUID.Data4[6] = 0x7d;
	theGUID.Data4[7] = 0x2b;

	//cout << "&theGUID=" << &theGUID << endl;//RTN:

	USB_PID = 0x139C; //PID for the D5020.

	// Detect the LC D5020 device:
	devcnt = USBDRVD_GetDevCount(USB_PID); /*USBDRVD_API UINT      USBDRVD_CALL USBDRVD_GetDevCount(DWORD USB_PID);*/
	cout << "Number of connected devices： " << devcnt << endl; //RTN:devcnt=1 if connected correctly.

	if (devcnt == 0) 
	{	
		// Device is not found.

		/*  // Discarded: Return string
		statusStr = "No Meadowlark Optics USB Devices Present.";
		cout << statusStr << endl;
		*/
		statusChar = (char *) "No Meadowlark Optics USB Devices Present.";
		cout << statusChar << endl;
	}
	else
	{
		/* open device and pipes */
		dev1 = USBDRVD_OpenDevice(1, flagsandattrs, USB_PID);
		//USBDRVD_OpenDevice and USB_CloseDevice are deprecated in version 1.1 onward
		/*USBDRVD_API HANDLE    USBDRVD_CALL USBDRVD_OpenDevice(UINT deviceNumber, DWORD attributes, DWORD USB_PID);*/

		//cout << "flagsandattrs=" << flagsandattrs << endl; //RTN:flagsandattrs = 1073741824
		//cout << "dev1=" << dev1 << endl; //dev1 = 000002897F5C6BC0, 000001AE1F256BC0, 0000023FE45F6BC0, 000001ED7C3C6BC0

		/* Try GetPipeCount // USBDRVD_API UINT      USBDRVD_CALL USBDRVD_GetPipeCount(HANDLE device);
		pipeCount = USBDRVD_GetPipeCount(dev1);
		cout << "pipeCount=" << pipeCount << endl;//RTN:pipeCount=2
		*/
		

		/*USBDRVD_API HANDLE    USBDRVD_CALL USBDRVD_PipeOpen(UINT deviceNumber, UINT pipe, DWORD attributes, const GUID *USB_GUID);*/
		pipe0 = USBDRVD_PipeOpen(1, 0, flagsandattrs, &theGUID); // Might be: pipe (endpoint?) for reading. GUID:'Globally Unique Identifier'
		pipe1 = USBDRVD_PipeOpen(1, 1, flagsandattrs, &theGUID); // Might be: pipe (endpoint?) for writing
		

		/* //print out the variables to see their values 
		cout << "&theGUID=" << &theGUID << endl;//RTN:&theGUID=0000006FC917F858, 0000002215B4FB08
		cout << "pipe0=" << pipe0 << endl;//RTN:pipe0=0000000000000000
		cout << "pipe1=" << pipe1 << endl;//RTN:pipe1=0000000000000000 
		*/

			/* send ASCII command */
		USBDRVD_BulkWrite(dev1, 1, lcCmd, lcCmd_size);	/* USBDRVD_API ULONG     USBDRVD_CALL USBDRVD_BulkWrite(HANDLE device, ULONG pipe, BYTE *buffer, ULONG count);*/

			/* read status response */
		USBDRVD_BulkRead(dev1, 0, status, 64); //read 64 bytes back and store in "status".	/* USBDRVD_API ULONG     USBDRVD_CALL USBDRVD_BulkRead(HANDLE device, ULONG pipe, BYTE *buffer, ULONG count)*/

		/* output status until a <CR> is found */
		cout << "LC returns: ";

		int sizeStatus = 0;
		for (i = 0; status[i] != 0xd; i++) /* <CR> is 0xd  CR (carriage return) being 0xD, and LF (Line finish, aka newline) being 0xA.*/
		{
			cout << status[i];
			sizeStatus++; // counting number of elements
		}
		
		cout << endl; //print below in new line:
		/*
		cout << status << endl;
		cout << endl << "sizeof(status) = " << sizeof(status) << " sizeStatus = " << sizeStatus << endl; // to get the size of status (returned value) without counting '\n'. //sizeof(status) = 64 sizeStatus = 45
		*/

		/* close device and pipes */
		USBDRVD_PipeClose(pipe0);
		USBDRVD_PipeClose(pipe1);
		USBDRVD_CloseDevice(dev1); //USBDRVD_OpenDevice and USB_CloseDevice are deprecated in version 1.1 onward


		// Convert byte array to string: (covert to char array is done on 2022-06-24)
		// Firstly convert byte array to char array
		char statusCharTemp[sizeof(status) + 1];
		memcpy(statusCharTemp, status, sizeStatus);
		statusCharTemp[sizeStatus] = '\0'; // add null termination to the end of returned data
	
		statusChar = statusCharTemp; // assign the response data to returned variable 'statusChar'

		/* // print the varaible
		cout << "statusCharTemp: " << statusCharTemp << endl;//statusCharTemp: ver:1.05 (c) 2013-2020 Meadowlark Optics,Inc.
		cout << "Type of statusCharTemp: " << typeid(statusCharTemp).name() << endl;// Type of statusCharTemp: char [65]
		cout << "strlen(statusCharTemp) = " << strlen(statusCharTemp) << endl;//strlen(statusCharTemp) = 45

		// second, convert char array to string and assign to the return variable.
		statusStr = statusCharTemp; // convert char array to string
		cout << "statusStr: " << statusStr << endl;//statusStr: ver:1.05 (c) 2013-2020 Meadowlark Optics,Inc.
		cout << "Type of statusStr: " << typeid(statusStr).name() << endl;// Type of statusStr: char [65]
		cout << "statusStr.length() = " << statusStr.length() << endl;//strlen(statusStr) = 45
		*/
	}
	cout << "********************************** Communication End **********************************" << endl;
	

	/* // Print out return value 
	cout << "statusChar: " << statusChar << endl;//
	cout << "Type of statusChar: " << typeid(statusChar).name() << endl;// 
	cout << "sizeof statusChar = " << sizeof statusChar << endl;//trlen(statusChar)
	*/
	return (char*)statusChar;
}


// Alternative: Define the function that Directly initialize the LC controller into trigger pulse cycle mode before 2D POLIM measurement within c-programe without passing any argument from python:
int SetLCCyclp1()
{
	// v1.0: char as return

	// Send 1st command "ver:?":
	// Description: Query firmware version. Controller returns firmware version and copyright string.This is used to test communication with the PC.
	char lcCmd[] = "ver:?";
	string ans = LCCMD(lcCmd); // convert char to string for printing
	cout << "Return from LC: " << ans << endl;

	// Send 2nd command "cyclp:1":
	// Description: Tells the controller to cycle through all valid states (7 states corresponding to 6 polarization angles and a NULL state of 0V). State change occurs only when a trigger pulse is detected on the controller’s trigger input. "1" in the command starts cycling, while "0" stops cycling.
	cout << "Return from LC: " << (string)LCCMD((char*) "cyclp:1") << endl; //Return from LC#2:cyclp:

	// Send 3rd command "cycm:?":
	// Description: Queries the current cycling mode of the controller. Result indicates command being executed. 1 = constant state; 2 = cyc; 3 = cycl; 4 = cycp; 5 = cyclp; 6 =rand. “cycm:5” will be returned if everything is correct.
	cout << "Return from LC: " << (string)LCCMD((char*) "cycm:?") << endl;

	//system("pause");
	return 1;
}

// Some functions for testing ctypes:
void display(char* str) {
	printf("%s", str);
	cout << &str << endl;
	cout << *str << endl;
}

void LCCMD1(char* lcCmdStr)
{
	printf("%s", lcCmdStr);
	cout << endl;
	cout << "lcCmdStr: " << *lcCmdStr << endl;
	cout << "sizeof lcCmdStr = " << sizeof * lcCmdStr << endl;
	cout << "strlen(lcCmdStr) = " << strlen(lcCmdStr) << endl;
	cout << "Type of lcCmdStr: " << typeid(*lcCmdStr).name() << endl;
	cout << "lcCmdStr[1] = " << lcCmdStr[1] << endl;
}
