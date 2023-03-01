// LCcmdDll0Client0.cpp : This file contains the 'main' function. Program execution begins and ends there.
// need to place all required lib files in the "\repos\LC_CMD_DLL\x64\Debug" directory

#include <iostream>
#include <windows.h>
#include "LC_CMD_DLL.h"
#pragma comment(lib,"D:/MyDocs/PROG/VS/source/repos/LC_CMD_DLL/x64/Debug/LC_CMD_DLL.lib") // remember to put all related libraries include LC_CMD_DLL.h and usbdrvd.h in the working directory.
#include <string>
using namespace std;

void main()
{
	//string ans = LCcmd_ver();
	//int ans = LCcmd_ver();
	/*
	//string ans = LCCMD("ver:?");
	
	cout << "Return from LC:" << ans << endl;
	//cout << "Return from LC:" << LCCMD("ver:?") << endl;

	cout << "Return from LC:" << LCCMD("cyclp:1") << endl; //cyclp:1

	cout << "Return from LC:" << LCCMD("cycm:?") << endl;
	*/
	
	//char lcCmd[] = { 'v', 'e', 'r', ':', '?', '\n' };
	char lcCmdchar[] = "ver:?";
	cout << "lcCmd = " << lcCmdchar << endl;
	cout << "sizeof lcCmd = " << sizeof lcCmdchar << endl;

	//BYTE* ans = LCCMD(lcCmd);
	// convert return value to string and print it
	string ans = LCCMD(lcCmdchar);
	//char* ans = LCCMD(lcCmdchar);
	cout << "Return from LC#1:" << ans << endl;//Return from LC#1:ver:1.05 (c) 2013-2020 Meadowlark Optics,Inc.
	
	cout << "ans.length():" << ans.length() << endl;//statusStr.length() = 45 (not include null termination if it exists)
	//cout << "strlen(ans):" << strlen(ans) << endl;
	//cout << "Return from LC:" << LCCMD("ver:?") << endl;

	cout << "Return from LC#2:" << (string) LCCMD((char*) "cyclp:1") << endl; //Return from LC#2:cyclp:
	

	//char lcCmdchar1[] = "cycm:?";
	//cout << "Return from LC:" << LCCMD(lcCmdchar1) << endl;
	cout << "Return from LC#3:" << (const char*) LCCMD((char*)"cycm:?") << endl;//Return from LC#3:øÞo(


	/*
	string errorcmd = LCCMD("csssssyclp:0");
	cout << "Return from LC:" << errorcmd << endl;
	cout << "errorcmd.length() = " << errorcmd.length() << endl;
	*/
	char Buzzer = 7; // buzzer
	cout << Buzzer << endl;
	system("pause");
	SetLCCyclp1();
}


// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file

/*
// MathClientDLL0.cpp : Client app for MathLibrary DLL.
// #include "pch.h" Uncomment for Visual Studio 2017 and earlier
#include <iostream>
#include "MathLibraryDLL0.h"


int main()
{
	// Initialize a Fibonacci relation sequence.
	fibonacci_init(1, 1);
	// Write out the sequence values until overflow.
	do {
		std::cout << fibonacci_index() << ": "
			<< fibonacci_current() << std::endl;
	} while (fibonacci_next());
	// Report count of values written before overflow.
	std::cout << fibonacci_index() + 1 <<
		" Fibonacci sequence values fit in an " <<
		"unsigned 64-bit integer." << std::endl;
}
*/