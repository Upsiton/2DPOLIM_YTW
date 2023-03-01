/************************************************************************

								Created by Yutong Wang

File name: LC_CMD_DLL.h
 - Contains declarations of LCCMD functions that the DLL exports.

This is the first runnable version of LC command function. The function char* LCCMD(char* lcCmdStr) is defined based on the sample code from Meadowlark
Optics for sending ASCII command to LC controller D5020 via USB connection.

It enables conversion of string (or char array) to byte array which can be sent to LC device, and converstion of the returned byte array from the device to a string
(or char array) as its output. The argument of function is a char array (or originally a string) which indicates the ASCII commands given in the device user manual.
The code is then wrapped into the DLL file LC_CMD_DLL.dll and to be called in python via ctypes libraray.

Require running in 64 bit system. 
At 11:50 am on 2022/06/28
************************************************************************/
// Code based on MS tutorial: MathLibraryDLL0.h - Contains declarations of math functions

#pragma once
//#include<string> // discarded std::string in latest implementation

// Preprocessor statements. PROJECTNAME_EXPORTS 
#ifdef LC_CMD_DLL_EXPORTS 
#define LC_CMD_DLL_API __declspec(dllexport)
#else
#define LC_CMD_DLL_API __declspec(dllimport)
#endif


//Declare the LCCMD functions in LC_CMD_DLL.cpp. For sending the ASCII command to LC and reading its response.
//Data type of both input & output: char*.

// extern "C" specifies that the function is defined elsewhere and uses the C-language calling convention. 

// Declare the function that Sending ASCII commands to LC controller and return its response:
extern "C" LC_CMD_DLL_API char* LCCMD(char* lcCmdStr);

// Declare the function that Directly initialize the LC controller into trigger pulse cycle mode before 2D POLIM measurement within c-programe without passing any argument from python:
extern "C" LC_CMD_DLL_API int SetLCCyclp1();

//extern "C" LC_CMD_DLL_API std::string LCCMD(std::string lcCmdStr);  // previous implementation

// Some functions for testing ctypes
// For testing passing char argument from python
extern "C" LC_CMD_DLL_API void display(char* str);
extern "C" LC_CMD_DLL_API void LCCMD1(char* lcCmdStr);