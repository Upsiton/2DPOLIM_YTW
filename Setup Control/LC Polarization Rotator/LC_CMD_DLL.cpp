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
*								Modified by Yutong
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
	cout << "Send command: " << lcCmdStr << endl;

	// Firstly, convert char array to BYTE (const char) which can be read by device. lcCmd will be sent to the device.
	BYTE* lcCmd = (BYTE*) lcCmdStr;

	//BYTE* lcCmd = (BYTE*)lcCmdStr.c_str(); //Discarded. string to byte pointer: (@2022-06-27 4:22 pm)

	INT lcCmd_size = (INT)strlen(lcCmdStr) + 1; // add 1 to the length for including the null termination '\n'

	// Declare buffer to save response value from device:
	BYTE status[64]; // receiving response data from device
	char * statusChar; // convert response data to char as output of function
	//string statusStr; // Discarded.

	/********  
	*
	*
	*
	*
	* The detail of the code is not shown here due to the copyright issue.
	*
	*
	*
	*
	*
	********/

		// Convert byte array to string: (covert to char array is done on 2022-06-24)
		// Firstly convert byte array to char array
		char statusCharTemp[sizeof(status) + 1];
		memcpy(statusCharTemp, status, sizeStatus);
		statusCharTemp[sizeStatus] = '\0'; // add null termination to the end of returned data
	
		statusChar = statusCharTemp; // assign the response data to returned variable 'statusChar'
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
