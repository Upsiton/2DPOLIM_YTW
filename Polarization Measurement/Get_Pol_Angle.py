# -*- coding: utf-8 -*-
"""
Script for calculation of Angle of Polarization (AOP) in Polarization Measurement by Stepper-motor-driven Analyzer


This script is for running the power meter data with a rotating polarization analyzer to calculate the AOP. The file name of
data (.csv) is input in interactive way during running. The result (processed data, plottings) will be automatically saved in 
the current working directory with given folder name. It can run with several data files and save the whole result as well. 


Finished the beta version on March 2021
@author: Yutong
"""
#%% Initialization


import os

# Change the current working directory to specified path (e.g. location of sample data in folder "Samples").
os.chdir('D:\\MyDocs\\PROG\\GitHub\\2DPOLIM_YTW\\Samples') 


# ## Get path via input:
# workdir = input("Please input the path of folder which contains CSV files:\n...")
# os.chdir(workdir)

# cwd = os.getcwd() 
# print("Current working directory is:", cwd)
# ##

#Putting the imports at the top of the module: (Orininally in the Cell "Step 1")
import pandas as pd
import numpy as np

import time
from datetime import datetime, timedelta

# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

#*****************************************************************************#
#%% Step 1: Read out data in pandas only
#*****************************************************************************#
"""
Read out CSV file.
Remove header & trail.
Retrive date & time.
folder:D:\ProgramFiles1\Python38\MyPy\labwork\Power meter\Samples
"""
total_cycle = 10 # Total number of cycles. Every 180 degree = 1 cycle
r_spd = 90.00 # motor configuration of rotation speed in [degree/s]

# del file_name
if 'file_name' in locals(): #check if 'file_name' is aleady defined in previous running(local variable)
    while True: # Use an infinite loop to avoid an I/O error
        input_fnm = input("file_name already exists. Delete it and run a new file ([y]/n)?\nOr directly input the NEW file name here...")
        if input_fnm.upper() == "Y": 
            file_nameNew = input("Input the FULL name of CSV file(stored in current working directory):\n...")
            if os.path.isfile(file_nameNew): # if the file can be found:
                file_name = file_nameNew
                #del more variable like t0 tend:
                if 't_0_manu' in locals(): del t_0_manu
                if 't_end_manu' in locals(): del t_end_manu                
                print("NEW FILE NAME is accepted!")
                break # Loop ended.
            else: 
                print("ERROR: NO file founded! Try it again.")
            continue # stay in the loop and jump to the top
            
        elif input_fnm.upper() == "N":
            print("No action.")
            break
        elif os.path.isfile(input_fnm): # check if the file can be found in the CWD
            file_name = input_fnm
            if 't_0_manu' in locals(): del t_0_manu
            if 't_end_manu' in locals(): del t_end_manu
            print("NEW FILE NAME is accepted!")
            break
        else:
            print("ERROR: No operation matches the input! Try it again.")
            # continue
else:
    file_name = input("Please input the full name of CSV file(stored in current working directory):\n...")


### Retrieve info.(laser current/output power value, volt. of liquid crystal) from file name: (updated:2021/03/08, 21:44:30)
fileNmSplt = file_name.split("_") # works for file name like "PM_20210114_4_Laser_LC_56mA_2.45V_25s.csv"
print("\nInfo. from the file name:")
n=0 # for obtain index of values appear
laserCurrentVal=laserPowerVal=lcVoltVal=infoCode=np.nan # initialization(avoid the value keeps when running the next file)
for item in fileNmSplt:
    if ("mA" in item) and (item.find("mA") == len(item)-2): # Alternative: if "mA" in item; However, due to str.find() returning index, such expression can ensure "V", "mA", and "mW" appears in the end of string as a unit, not inside a certain word
        laserCurrentVal = float(item.replace("mA",""))
        print(f"Current of Laser: {laserCurrentVal}mA")
        # print("show n:",n)
        infoCode = "_".join(fileNmSplt[2:n]) # characters between date and laser config. value in the file name: "info. code", which contains info. of measurement.(e.g. 20210210_A2_Laser_LC_DC_Obj, 20210114_4_Laser_LC...)
        print(f"Info. code: {infoCode}")
    elif ("mW" in item) and (item.find("mW")  == len(item)-2): # 1st, make sure item contains "mW". 2nd, ensure "mW" appears in the end of the string
        laserPowerVal = float(item.replace("mW",""))
        print(f"Laser output power: {laserPowerVal}mW")
        # print("show n:",n)
        infoCode = "_".join(fileNmSplt[2:n])
        print(f"Info. code: {infoCode}")
    elif ("V" in item) and (item.find("V") == len(item)-1): 
        lcVoltVal = float(item.replace("V",""))
        print(f"Voltage of Liquid Crystal: {lcVoltVal}V")
    # print(n)
    n=n+1

### Load CSV file via Pandas
colnames=['Data'] 
dfPwData = pd.read_csv(file_name, names=colnames)#, header=None)
# Find(search for) header & tail in more general way (based on partial string search: .str.contain("")):

idx_header=dfPwData[dfPwData['Data'].str.contains('Time of day')].index[0] #find the index of the last line of header
idx_tail=dfPwData[dfPwData['Data'].str.contains('Last Power Reading')].index[0] #find the index of the first line  of header
dfPwData_header = dfPwData[0:idx_header+1].copy()
dfPwData_tail = dfPwData[idx_tail:].copy()

colnames=dfPwData.loc[idx_header]
powerdata = dfPwData[idx_header+1:idx_tail].copy() # clean data without header & tail: powerdata
powerdata.reset_index(drop=True, inplace=True) # reset index start from 0; drop the original index; change inplace(do operation on itself, no return)
powerdata=powerdata['Data'].str.split("; ", n=-1, expand=True) # split date&time and power according to delimiter;

#read out time

t_int = datetime.strptime(powerdata.iloc[0,0], "%m/%d/%Y;%H:%M:%S.%f")# in numpy; initial time of measurement
# Do it via ndarray, return t_sec, tim
tim = np.array([])
t_sec = np.array([])
for idx in range(len(powerdata)):# Later on use nditer(): Iterating Arrays Using nditer(). nditer is to visit every element of an array
    t_idx = datetime.strptime(powerdata.iloc[idx,0], "%m/%d/%Y;%H:%M:%S.%f")
    tim = np.append(tim, t_idx)
    #tim = np.append(tim, datetime.strptime(data[idx,0]+' '+data[idx,1], "%m/%d/%Y %H:%M:%S.%f")) # or write in a single line
    t_sec = np.append(t_sec,(t_idx - t_int).total_seconds())
t_total=t_sec[-1] # total measured time
print("Total second:{}".format((tim[-1]-tim[0]).total_seconds()))
# print(t_sec[-1] == (tim[-1]-tim[0]).total_seconds()) # Checked: True

powerdata.iloc[:,0] = tim # assign the result() to original Dataframe
powerdata["Time"]= t_sec # add a new col. labeled "Time" to store time in second
powerdata.iloc[:,1] = powerdata.iloc[:,1].astype(np.float).copy() # convert power data to numpy.float64
powerdata.rename(columns={0:"DateTime",1:"Power"},inplace=True) # assign col. names to first 2 col.

## Processing the power measurements
# read out values
power_std=np.nanstd(powerdata.iloc[:,1]) #std of whole data; useless, only demo

print('Mean value of measurement/W: {0}.\nStandart deviation of measurement/W: {1}'.format(np.nanmean(powerdata.iloc[:,1]),power_std))
pw_tot_max = np.nanmax(powerdata.iloc[:,1])
pw_tot_min = np.nanmin(powerdata.iloc[:,1])
print('Maximum value of measurement/W: {}.\nMinimum value of measurement/W: {}.'.format(pw_tot_max,pw_tot_min))
print('Extinction ratio: {}'.format(pw_tot_max/pw_tot_min))

sampl, sampl_rate = len(powerdata), len(powerdata)/t_total
print("Total smapling: {} \nAverage sampling rate:{} Hz".format(sampl, "%.2f" % sampl_rate)) # ("%.2f" % sampl_rate) show 2 decimals

### Update: Add loading the background data to subtract noise [on 04.03.2021]
# Load CSV file of background measurement or specify the value of background
# Background is subtracted when cal.: pw_cycle_min_count_power, pw_cycle_max_count_power, DOP & anisotropy

# del bkgdMeanValue
while 'bkgdMeanValue' not in locals():
    inpBkgd = input("Load Background data of power measurement. Please either input the full name of a CSV file or specify a value by tying a number(unit: W):\n...")
    try: 
        bkgdMeanValue = float(inpBkgd) # directly assign when input is a number
        bkgdStd = np.nan
        bkgdChoice = 'specified'
        print("Background data is set:", bkgdMeanValue, 'W')
    except: # when input is not a number
        try:
            bkgdDf=pd.read_csv(inpBkgd, names=["Data"]) # load the file of input name
        except IOError:
            print("Error: you neither input an number nor file not found/fail in loading.")        
        else:
            bkgdDf = bkgdDf['Data'].str.split("; ", n=-1, expand=True) # Split CSV according to delimiter ;
            
            bkgdMeanValue = bkgdDf[bkgdDf.iloc[:,0].str.contains('Mean')][1] # Search for mean value
            bkgdMeanValue = pd.to_numeric(bkgdMeanValue.str.replace(' W','')).values[0] # delete " W" and convert object type to float64 via pd.to_numeric()
            
            bkgdStd = bkgdDf[bkgdDf.iloc[:,0].str.contains('Standard Deviation')][1] # Search for std value
            bkgdStd = pd.to_numeric(bkgdStd.str.replace(' W','')).values[0] # delete " W" and convert object type to float64 via pd.to_numeric()
            bkgdChoice = inpBkgd
            print("Background data is loaded.\nBackground of power data:\nmean:{} W; std:{} W\n".format(bkgdMeanValue,bkgdStd))

########*** Plot the Power-time ***########
### At first, creating new directory for saving results(plottings here); Copied this part to from step 3 
cwd = os.getcwd()
# dateStr = datetime.now().strftime("%x").replace("/","") #e.g.'030721'. Use it in the folder name for discriminating results from diff. dates
dateStr = datetime.now().strftime("%Y%m%d")[2:] # new expression for date refers to ISO 8601: '210308'; str[:] slicing strings
savePath = os.path.join(cwd, "pwResult_"+dateStr, file_name.replace(".csv", "")) # to save indv. results in a folder of its CSV file name; Need to create dir by os.mkdir(savePath) before df.to_csv()
# print(savePath)
try: 
    # os.mkdir(savePath) # creat new directory
    # Notice: A single call of os.mkdir(savePath) can only creating A Single Directory in the current working dir(like ...\Optical Power Monitor\pwResult_030721) without any sub-directories. To Create a Directory with Subdirectories using makedirs()
    os.makedirs(savePath) # use 'savePath' as path
except OSError as error: 
    print(error) 

### Plotting

# Plot from dataframe(Fig.1):
fig, pw_0 = plt.subplots(figsize=(16,9)) # figsize=1600*900 px
# fig, pw_0 = plt.subplots(figsize=(8,6)) # figsize=1600*900 px
plt.subplots_adjust(top=0.961,bottom=0.065,left=0.058,right=0.991,hspace=0.2,wspace=0.2) # Adjust the subplot layout parameters
pw_0.scatter(powerdata.iloc[:,2], powerdata.iloc[:,1], s=2, marker='o', color='b', label=r'Power') # s=size(diameter) of marker

pw_0.set_title('Raw Data: Power vs. Time (under original timeline)', fontsize=20)
pw_0.set_xlabel('Time/s', fontsize=18)
# Make a plot with major ticks that are multiples of 1. and minor ticks that are multiples of 0.5. Label major ticks with '%d' formatting but don't label them
pw_0.xaxis.set_major_locator(MultipleLocator(1))
pw_0.xaxis.set_minor_locator(MultipleLocator(0.2))

plt.ylabel('Power/W', fontsize=18)
plt.legend(fontsize=14)
pw_0.grid()
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig1.png")) # save fig as png and pdf/svg format in "savePath"
plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig1.svg"))
plt.show()

#####****** Loarding process finished ******######

#*****************************************************************************#
### Step 2.1: Locating the initial time of rotation (through standard deviation)
#*****************************************************************************#
# Do rolling standard deviation in pandas.DataFrame

window = 10 # from test of a data, 5 is optimal to distinguish t_0 from other. (use 10 in LC-chara.)
power_rol_mean = powerdata.iloc[:,1].rolling(window).mean()
power_rol_std = powerdata.iloc[:,1].rolling(window).std() # do rolling std with a window
power_rol_std_2 = power_rol_std.rolling(3).std()
power_rol_std_2_1 = power_rol_std.rolling(2).std()
print(f'The window of rolling standard deviation: {window} data')

# time rolling std
window1 = 3 
time_rol_std = powerdata.iloc[:,2].rolling(window1).std() # rolling std of time
factor_F = 2.2 # set criteria for setting the starting time (power_rol_std[idx]/ref_std >= factor_F); this value can be around 2.0 (1.9~2.5); e.g.2.2 for LC; 1.5 for direct laser source

    # real code:
win_sec = [1.0, 2.0] # set the window for reference (criteria); (start, end) in second
win_ref = np.arange(win_sec[0]*sampl_rate,win_sec[1]*sampl_rate) # cal. the index range of selected window
ref_std = np.nanstd(powerdata.iloc[win_ref,1])
print(f'The reference value/W (the std of an window of {win_sec} second): {ref_std}')
ratio_ref = power_rol_std[:]/ref_std # show ratio of reference value/std. of values; for set good criteria
for idx in range(int(0.0*sampl_rate),len(powerdata)): # scan range start form an offset(optional): (certain second*sampl_rate) to avoid the fluctuation in the beginning
    if power_rol_std[idx]/ref_std >= factor_F: break # set criteria for setting the starting time; this value can be around 2.0 (1.9~2.5); e.g.2.2 for LC; 1.5 for direct laser source
t_0_auto_idx = idx+1 # select one point before the value jump as the begining time. Original:idx+1; Updated:idx-1(due to acceleration, time during is prefered to be a bit smaller than real value)

print("{time of rotation Begins} The index of break:", t_0_auto_idx)
print("{time of rotation Begins} The time of break:", powerdata.iloc[t_0_auto_idx,0], ". In second:", powerdata.iloc[t_0_auto_idx,2], "s")
# up to now: new condition based on std is done. @ 2021.01.06 3:47AM
t_0_auto = powerdata.iloc[t_0_auto_idx,2] # set the initial time

# Find the end time of rotation for velocity correction:
for idx in range(len(powerdata),0,-1): # scan range from the end to the beginning
    if power_rol_std[idx-1]/ref_std >= factor_F: break # idx-1 for reversed scaning, otherwise idx exceed the last element ;set criteria for setting the starting time; this value can be around 2.0 (1.9~2.5)
t_end_auto_idx = idx-1-window # Subtract window value & select one point before the value jump as the begining time. Original:idx+1-window

print("{time of rotation Ends} The index of break:", t_end_auto_idx)
print("{time of rotation Ends} The time of break:", powerdata.iloc[t_end_auto_idx,0], ". In second:", powerdata.iloc[t_end_auto_idx,2], "s")
t_end_auto = powerdata.iloc[t_end_auto_idx,2] # set the end time
print(f"Total rotation time given by auto selection: {round(t_end_auto-t_0_auto, 3)} s")
print("Rotation speed cal. by auto values: {} deg/s".format(round(180*total_cycle/(t_end_auto-t_0_auto),3)))



## Plot from dataframe with mark on new origin point(t_0_auto)(Fig.2):
fig, pw_1 = plt.subplots(figsize=(16,9)) # figsize=1600*900 px
plt.subplots_adjust(top=0.961,bottom=0.065,left=0.058,right=0.991,hspace=0.2,wspace=0.2) # Adjust the subplot layout parameters
pw_1.scatter(powerdata.iloc[:,2], powerdata.iloc[:,1], s=2, marker='o', color='b', label=r'Power') # s=size(diameter) of marker
pw_1.set_title('Preview: Power vs. Time (under original timeline)', fontsize=20)
pw_1.set_xlabel('Time/s', fontsize=18)
# Make a plot with major ticks that are multiples of 1. and minor ticks that are multiples of 0.5. Label major ticks with '%d' formatting but don't label them
pw_1.xaxis.set_major_locator(MultipleLocator(1))
pw_1.xaxis.set_minor_locator(MultipleLocator(0.2))

plt.ylabel('Power/W', fontsize=18)
plt.legend(fontsize=14)
pw_1.grid()
plt.plot(powerdata.iloc[t_0_auto_idx,2], powerdata.iloc[t_0_auto_idx,1], 'r*', powerdata.iloc[t_end_auto_idx,2], powerdata.iloc[t_end_auto_idx,1], 'r*') # mark the t_0_auto & t_end_auto

pw_1.axvline(powerdata.iloc[t_0_auto_idx,2], linestyle='--', color='y') # vertical lines
pw_1.axvline(powerdata.iloc[t_end_auto_idx,2], linestyle='--', color='y')

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig2.png")) # save fig as png and pdf/svg format in "savePath"
plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig2.svg")) # 
plt.show()

#*****************************************************************************#
#%% Step 2.2 & 3: Input & Processing
#*****************************************************************************#

### Step2.2: Manually check & input:

    ## Set the inertial time t_0:
#t_0_manu = 2.9051
#del t_0_manu
if 't_0_manu' in locals():
    input01 = input("The 't_0_manu' has already been set. Do you want to delete it and try it again? \nType 'D' or 'd' to delete it, type any other key to skip:\n...")
    if input01.upper() == "D": 
        del t_0_manu
        print("'t_0_manu' has been deleted.")
    else:
        print("No action.")

inpT0Msg = f"The calculation suggests the intial time of rotation t_0: {t_0_auto} s.\n\
For accepting the auto value, please input 'Y' or 'y'. Any other letter: error & stop. \n\
For giving an value manually, please input a number here:\n..."

if 't_0_manu' not in locals(): #check if 't_0_manu' is defined (local variable)
    inpT0 = input(inpT0Msg)
    if inpT0.upper() == "Y": # accept the auto value
        t_0_idx = t_0_auto_idx # assign the auto value for following processing
        #t_0 = powerdata.iloc[t_0_idx,2] # set the initial time
        t_0Choice = "auto" # mark down the choice of t_0
        print("Auto value is accepted!")
    else: 
        try: # if no error then do following, otherwiese do except and return error message.
            t_0_manu = float(inpT0)
            # print(type(inpT0))
            t_0Choice = "manual"
            print("Your input value is: t_0_manu = ", t_0_manu)
            t_0_manu_df = powerdata[abs(powerdata["Time"]-t_0_manu) <= 3/sampl_rate] # Firstly, find the neighborhood of given t_0 by eyes and retrieve info
            #t_0_manu_df
            t_0_manu_idx = abs(t_0_manu_df["Time"]-t_0_manu).idxmin() # Secondly, finds the closest point to the manually input t_0 value.
            t_0_idx = t_0_manu_idx
#powerdata.iloc[abs(t_0_manu_df["Time"]-t_0_manu).idxmin(),:]
        except ValueError:
            print("<!!!You break the script by neither inputing 'Y'/'y', nor a number!!!>")

# t_0_idx should be set up to here.
t_0 = powerdata.iloc[t_0_idx,2] # set the initial time
print(f"[The initial time of rotation has been set!\n\
 Index: {t_0_idx};   DateTime: {powerdata.iloc[t_0_idx,0]};   In second: {powerdata.iloc[t_0_idx,2]} s]")

      
    ## Set the end time t_end:
if 't_end_manu' in locals():
    input01 = input("The 't_end_manu' has already been set. Do you want to delete it and try it again? \nType 'D' or 'd' to delete it, type any other key to skip:\n...")
    if input01.upper() == "D": 
        del t_end_manu
        print("'t_end_manu' has been deleted.")
    else:
        print("No action.")

inpTEndMsg = f"The calculation suggests the stop time of rotation t_end: {t_end_auto} s.\n\
Accepting the auto value, please input 'Y' or 'y'; Any other letter: error & stop. \n\
Giving an value manually, please input a number here:\n..."
   
if 't_end_manu' not in locals(): #check if 't_end_manu' is defined (local variable)
    inpTEnd = input(inpTEndMsg)
    if inpTEnd.upper() == "Y": # accept the auto value
        t_end_idx = t_end_auto_idx # assign the auto value for following processing
        t_endChoice = "auto" # mark down the choice of t_end
        #t_end = powerdata.iloc[t_end_idx,2] # set the initial time
        print("Auto value is accepted!")
    else: 
        try: # if no error then do following, otherwiese do except and return error message.
            t_end_manu = float(inpTEnd)
            # print(type(inpTEnd))
            t_endChoice = "manual"
            print("Your input value is: t_end_manu = ", t_end_manu)
            t_end_manu_df = powerdata[abs(powerdata["Time"]-t_end_manu) <= 3/sampl_rate] # Firstly, find the neighborhood of given t_end by eyes and retrieve info
            # t_end_manu_df
            t_end_manu_idx = abs(t_end_manu_df["Time"]-t_end_manu).idxmin() # Secondly, finds the closest point to the manually input t_end value.
            t_end_idx = t_end_manu_idx
#powerdata.iloc[abs(t_end_manu_df["Time"]-t_end_manu).idxmin(),:]
        except ValueError:
            print("<!!!You break the script by neither inputing 'Y'/'y', nor a number!!!>")

# t_end_idx should be set up to here.
t_end = powerdata.iloc[t_end_idx,2] # set the stop time of rotation
print(f"[The STOP time of rotation has been set!\n\
 Index: {t_end_idx};   DateTime: {powerdata.iloc[t_end_idx,0]};   In second: {powerdata.iloc[t_end_idx,2]} s]")
t_total_rot = t_end-t_0 # the total rotation time given by selection the t_0 and t_end
print(f"Total rotation time given by selection: {t_total_rot} s")

      
### Step 3: Cal. angle from the given initial time of rotation:
# total_cycle = 10 # Total number of cycles. Every 180 degree = 1 cycle
# r_spd = 90.00 # rotation speed in [degree/s]
# r_spd_correct = 0 #-0.55456#-0.05621 #-0.25 # delta_velocity if needed to correct the set velocity
# r_spd = r_spd + r_spd_correct # corrected velocity
# r_spd_dev = 1800/20.1214 - r_spd

r_spd_correct = round(180*total_cycle/t_total_rot,3) # corrected velocity; round to 3 decimal points
r_spd_dev = round(r_spd_correct - r_spd,3) # delta_velocity if needed to correct the set velocity
#print(r_spd_correct)

inpSpdMsg = f"Rotation velocity: r_spd={r_spd} degree/s\n\
Recommended correction of rotation velocity: \n\
\Delta r_spd ={r_spd_dev} degree/s.\n\
Corrected rotation velocity: r_spd_correct = {r_spd_correct}\n\
For accepting the corrected value, please input 'Y' or 'y'. Any other letter: keeps the original value has been set. \n\
For giving an value manually, please input a number here:\n..."

inpSpd = input(inpSpdMsg)
if inpSpd.upper() == "Y": # accept the auto value
    r_spd = r_spd_correct # assign the corrected value
    r_spdChoice = "corrected" # mark down the choice of speed
    print("Corrected value has been accepted!")
else: 
    try: # if no error then do following, otherwiese do except and return error message.
        r_spd = float(inpSpd)
        r_spdChoice = "specified"
    except:
        print("keeps the original value has been set.")
        r_spdChoice = "original"
        #r_spd
print("Roataion velocity has been finally set to:\n r_spd = ",r_spd," degree/s.")

## the following block only for testing:
if 't_0' not in locals(): #check if 't_0' is defined (local variable)
    t_0 = float(input("The intial time of rotation t_0 is not defined. Please input a value here:\n..."))

# new time line:
t_relv = t_sec - t_0 # cal. relatvie time based on t_0 (start rotation)
# powerdata_1 = np.column_stack([powerdata,t_relv]) # add relative time to powerdata
powerdata["Relative time"]= t_relv # add a new col. labeled "Relative Time" to powerdata
powerdata["Rotation angle"]= np.around(t_relv*r_spd, decimals=3) # add a new col. labeled "Rotation angle" to powerdata
# powerdata.drop(columns=["Relative time","Rotation angle"], inplace=True) # Remove rows or columns; do operation inplace


### Find max and min

# Real code
# Find the "phase" (theta_0) of the initial position: a rough estimation of pol. angle
theta_0_1 = (180/np.pi)*np.arccos(((powerdata.iloc[t_0_idx,1]-pw_tot_min)/pw_tot_max)**0.5) # by fitting the cos function from max. & min. values. T01:12.790
theta_0_2 = 180/np.pi*np.arctan(((powerdata.loc[abs(powerdata['Rotation angle']-90).idxmin()]["Power"])/(powerdata[powerdata['Rotation angle']==0]["Power"].iloc[0]))**0.5) #Another way to cal. Pol. angle by power from two crossed orientations @ 0 & 90 deg
# theta_0 = [np.nanmean([theta_0_1, theta_0_2]),np.nanstd([theta_0_1, theta_0_2])]
theta_0 = np.nanmean([theta_0_1, theta_0_2])
theta_0_std = np.nanstd([theta_0_1, theta_0_2])
print("The rough estimation of polarization angle is: {} degree (unreliable).".format(round(theta_0,2)))
#p_t = pw_tot_min + pw_tot_max*(np.cos(20/180*np.pi))**2 # to see the power value if theta_crt (shifting criterion) set to 20 degree; T01:6.196500804367459e-06

# decide do shift or not:
# if 20<theta_0<70) do not shift; otherwise theta_0 is in 0+/-20 degree or 90+/-20 degree, do shift of 45 degree of subsection

if (20<theta_0<70): # do not shift; {This part is mostly done on 2021.01.02}
    ## split original data into 10 cycles (180deg each) and store in a list "pw_cycles"; each element in the list is DataFrame-type and is a subsection of powerdata within a cycle. 
    pw_cycle=[]
    for i in range(total_cycle):
        pw_cycle.append(powerdata[(powerdata["Rotation angle"]>=0+180*i) & (powerdata["Rotation angle"]<180+180*i)]) #equal to above; 
    
    ## find local mix/min values in each cycle & its indices in "Power"
    ## cal. from max
    pw_cycle_max_idx=[] 
    for i in range(total_cycle):
        pw_cycle_max_idx.append(pw_cycle[i]["Power"].idxmax())
    pw_cycle_max = powerdata.iloc[pw_cycle_max_idx,:].copy() # stored max in each cycle; use.cpy() to avoid "SettingWithCopyWarning" due to potential Chained assignment problem
    pw_pol_angle_max = pw_cycle_max.loc[:,["Rotation angle"]] % 180 # cal. "Rotation angle" by  remainder of the division rot.angle/180
    pw_cycle_max["Pol. angle"] = pw_pol_angle_max # add a new col. labeled "Rotation angle" to powerdata
    # pw_cycle_max.drop(columns="Pol. angle", inplace=True)

    
    ## cal. from min
    pw_cycle_min_idx=[] 
    for i in range(total_cycle):
        pw_cycle_min_idx.append(pw_cycle[i]["Power"].idxmin())
    pw_cycle_min = powerdata.iloc[pw_cycle_min_idx,:].copy() # stored min in each cycle; use.cpy() to avoid "SettingWithCopyWarning" due to potential Chained assignment problem
    
    ## cal. "Rotation angle" by  remainder of the division rot.angle/180 +/- 90 due to min refering to perpendicular orientation:
    #Can do above stuff in just one line: (by just +90 firstly. Sequence is important! Sth can be easily done by just reverse the sequence!)
    pw_pol_angle_min = (pw_cycle_min.loc[:,["Rotation angle"]]+90)%180
    
    pw_cycle_min["Pol. angle"] = pw_pol_angle_min # add a new col. labeled "Rotation angle" to powerdata
    #print("The polarization angles given by min. power: ", pw_pol_angle_min)
    
   
    # if no offset in sectioning, count all min/max:
    pw_pol_angle_all = np.append(pw_cycle_min.loc[:,'Pol. angle'].values, pw_cycle_max.loc[:,'Pol. angle'].values) # store all obtained Pol. angles from both min & max.; can add selection of range (exclude first & last element)
    #pw_pol_angle_min_mean = round(np.nanmean(pw_pol_angle_all[0:total_cycle]),2)
    pw_pol_angle_min_count = pw_pol_angle_all[0:total_cycle] # the angles of min that take into count in cal. statistics
    pw_pol_angle_max_count = pw_pol_angle_all[total_cycle:] # the angles of max that take into count in cal. statistics
    # The new in v0.85: Cal. the mean & std or power value at peak or valley. Or can copy the whole volumes instead of only copy angle values. For power calc. 

    # Creat new df to store counted result
    pw_cycle_min_count = pw_cycle_min.iloc[0:total_cycle,:].copy()
    pw_cycle_min_count["Category"] = "min"
    pw_cycle_max_count = pw_cycle_max.iloc[0:total_cycle,:].copy()
    pw_cycle_max_count["Category"] = "Max"

else:
    theta_offset = 45
    print(f"The theta_0 is {round(theta_0, ndigits=2)} degree. Thus, introduce angle offset of {theta_offset} degree for sectioning!")
            ## split original data into 10 cycles (180deg each) and store in a list "pw_cycles"; each element in the list is DataFrame-type and is a subsection of powerdata within a cycle. 
    pw_cycle=[]
    for i in range(total_cycle):
        pw_cycle.append(powerdata[(powerdata["Rotation angle"]>=0+theta_offset+180*i) & (powerdata["Rotation angle"]<180+theta_offset+180*i)]) #equal to above; 
    
    ## find local mix/min values in each cycle & its indices in "Power"
    ## cal. from max
    pw_cycle_max_idx=[] 
    for i in range(total_cycle):
        pw_cycle_max_idx.append(pw_cycle[i]["Power"].idxmax())
    pw_cycle_max = powerdata.iloc[pw_cycle_max_idx,:].copy() # stored max in each cycle; use.cpy() to avoid "SettingWithCopyWarning" due to potential Chained assignment problem
    pw_pol_angle_max = pw_cycle_max.loc[:,["Rotation angle"]] % 180 # cal. "Rotation angle" by  remainder of the division rot.angle/180
    pw_cycle_max["Pol. angle"] = pw_pol_angle_max # add a new col. labeled "Rotation angle" to powerdata
    
    ## cal. from min
    pw_cycle_min_idx=[] 
    for i in range(total_cycle):
        pw_cycle_min_idx.append(pw_cycle[i]["Power"].idxmin())
    pw_cycle_min = powerdata.iloc[pw_cycle_min_idx,:].copy() # stored min in each cycle; use.cpy() to avoid "SettingWithCopyWarning" due to potential Chained assignment problem
    
    ## cal. "Rotation angle" by remainder of the division rot.angle/180 +/- 90 due to min refering to perpendicular orientation:

    #Can do above stuff in just one line: (by just +90 firstly. Sequence is important! Sth can be easily done by just reverse the sequence!)
    pw_pol_angle_min = (pw_cycle_min.loc[:,["Rotation angle"]]+90)%180
    
    pw_cycle_min["Pol. angle"] = pw_pol_angle_min # add a new col. labeled "Rotation angle" to powerdata
    # print("The polarization angles given by min. power: ", pw_pol_angle_min)
    
    # if add offset in sectioning, drop the min/max from 1st and last cycle: 
    pw_pol_angle_all = np.append(pw_cycle_min.loc[:,'Pol. angle'].values, pw_cycle_max.loc[:,'Pol. angle'].values) # store all obtained Pol. angles from both min & max.; can add selection of range (exclude first & last element)
    pw_pol_angle_min_count = pw_pol_angle_all[1:total_cycle-1] # the angles of min that take into count in cal. statistics. i.e. neglect the fiest & last term
    pw_pol_angle_max_count = pw_pol_angle_all[total_cycle+1:-1] # the angles of max that take into count in cal. statistics i.e. neglect the fiest & last term
    
    # statistics of Max./min. power values

        # Creat new df to store counted result
    pw_cycle_min_count = pw_cycle_min.iloc[1:total_cycle-1,:].copy()
    pw_cycle_min_count["Category"] = "min"
    pw_cycle_max_count = pw_cycle_max.iloc[1:total_cycle-1,:].copy()
    pw_cycle_max_count["Category"] = "Max"


#Add the offset of -180 deg around 0/180 border here: # on 2021.02.09
#due to reference mechanism, changing in "pw_pol_angle_all" will change "pw_pol_angle_min_count" & "pw_pol_angle_max_count" as well. So, only need a single manipulation here

if (True in (pw_pol_angle_all>=170)) and (True in (pw_pol_angle_all<=10)): # need to test two conditions, otherwise always get problem at border. Cuz only for angles crossing the border
    for i in range(len(pw_pol_angle_all)):

        pw_pol_angle_all[i] = pw_pol_angle_all[i]-180 if pw_pol_angle_all[i]>=170 else pw_pol_angle_all[i]


print("\nThe polarization angles given by min. power: ", pw_pol_angle_min)    
print("The polarization angles given by max. power: ", pw_pol_angle_max)
    
# up to here, finding max/min now works @ 2021.01.03 03:24

# Statistics of result:

pw_cycle_min_count_power = [np.nanmean(pw_cycle_min_count.iloc[:,1]-bkgdMeanValue),np.nanstd(pw_cycle_min_count.iloc[:,1])] # [mean, std] of power values of min. unit:W; Considering and substrating background: bkgdMeanValue
pw_cycle_max_count_power = [np.nanmean(pw_cycle_max_count.iloc[:,1]-bkgdMeanValue),np.nanstd(pw_cycle_max_count.iloc[:,1])] # [mean, std] of power values of max. unit:W; Considering and substrating background: bkgdMeanValue
print("\nStatistics of Power/W:\n@ Max. [mean, std]:{}\n@ min. [mean, std]:{}\n".format(pw_cycle_max_count_power,pw_cycle_min_count_power))
P_paral = pw_cycle_max_count_power[0] # I_parallel: "Intensity" from analyzer to parallel orientation
P_perpen = pw_cycle_min_count_power[0] # I_perpendicular: "Intensity" from analyzer to parallel orientation
# Degree of polarization(DOP); Background value(bkgdMeanValue) is subtracted
P_DOP = round((P_paral-P_perpen)/(P_paral+P_perpen-2*bkgdMeanValue),5)
print("Degree of polarization(DOP): P = ", P_DOP)
# Anisotropy; Background value(bkgdMeanValue) is subtracted
r_anisotropy = round((P_paral-P_perpen)/(P_paral+2*P_perpen-3*bkgdMeanValue),5)
print("Anisotropy: r = ", r_anisotropy, "\n")


    # Stats. of Angles:
    # Direct take values form pw_cycle_min/max

    # After defined pw_cycle_min/max_count in both case, then cal. only once here:
pw_pol_angle_min_mean = round(np.nanmean(pw_pol_angle_min_count),2)
pw_pol_angle_min_std = round(np.nanstd(pw_pol_angle_min_count),2)

pw_pol_angle_max_mean = round(np.nanmean(pw_pol_angle_max_count),2)
pw_pol_angle_max_std = round(np.nanstd(pw_pol_angle_max_count),2)

print("Counted angles cal. from min. power:", pw_pol_angle_min_count)
print("pw_pol_angle_min_mean =",pw_pol_angle_min_mean)
print("pw_pol_angle_min_std =",pw_pol_angle_min_std,"\n")

print("Counted angles cal. from Max. power:", pw_pol_angle_max_count)
print("pw_pol_angle_max_mean =",pw_pol_angle_max_mean)
print("pw_pol_angle_max_std =",pw_pol_angle_max_std,"\n")


pw_pol_angle_all_count = np.append(pw_pol_angle_min_count, pw_pol_angle_max_count)
pw_cycle_all_count = pd.concat([pw_cycle_max_count,pw_cycle_min_count])# Concatenating objects by pd.concat()
print("All the Pol. angle that are counted:", pw_pol_angle_all_count)
pw_pol_angle_all_count_mean = round(np.nanmean(pw_pol_angle_all_count),2)
pw_pol_angle_all_count_std = round(np.nanstd(pw_pol_angle_all_count),2)
print('Mean angle of all counted:', pw_pol_angle_all_count_mean) 
print('Std of all counted:', pw_pol_angle_all_count_std,"\n")


########################################
### Plot new Power curve(Fig.3)
# Plot [Time-Power curve] with new timeline:
# fig, pw_1t = plt.subplots(figsize=(16,9)) # figsize=(8,6) means: 800*600 pxs
fig, pw_1t = plt.subplots(figsize=(16,9)) # figsize=1600*900 px
plt.subplots_adjust(top=0.961,bottom=0.065,left=0.058,right=0.991,hspace=0.2,wspace=0.2) # Adjust the subplot layout parameters
pw_1t.scatter(powerdata.iloc[:,3], powerdata.iloc[:,1], s=2, marker='o', color='b', label=r'Power') # s=size(diameter) of marker
#plt.plot(stock_df['daily_return'], label='Daily Return')
#plt.plot(stock_df['expand_mean'], label='Expanding Mean')
#plt.plot(stock_df['roll_mean_3'], label = 'Rolling Mean')
pw_1t.set_title('Power vs. Time (with new timeline)', fontsize=20)
pw_1t.set_xlabel('Time/s', fontsize=18)
pw_1t.xaxis.set_major_locator(MultipleLocator(1)) # major ticks that are multiples of 1
#pw_1t.xaxis.set_major_formatter(FormatStrFormatter('%d'))
pw_1t.xaxis.set_minor_locator(MultipleLocator(0.2)) # minor ticks that are multiples of 0.2

plt.ylabel('Power/W', fontsize=18)
plt.legend(fontsize=14)
pw_1t.grid()
# plt.show()
plt.plot(0.0, powerdata[powerdata["Relative time"]==0].loc[:,["Power"]].values, 'r*') # mark the origin point
plt.plot(powerdata.loc[t_end_idx,["Relative time"]], powerdata.loc[t_end_idx,["Power"]], 'r*')  # mark the stop point
plt.plot(pw_cycle_max.loc[:,["Relative time"]].values, pw_cycle_max.loc[:,["Power"]].values, 'ro') # highlight max/min point
plt.plot(pw_cycle_min.loc[:,["Relative time"]].values, pw_cycle_min.loc[:,["Power"]].values, 'ro') # highlight max/min point
# pw_1t.axvline(powerdata.iloc[t_0_auto_idx,2], linestyle='--', color='y') # vertical lines
# try for loop to get break points of sectioning
#n=0
pw_cycle_break=[]
for ele in range(len(pw_cycle)):
    #n=n+1
    #print(n)
    #print(pw_cycle[ele].head(1)["Time"])
    pw_cycle_break.append(pw_cycle[ele].head(1)["Relative time"].values[0])
    pw_1t.axvline(pw_cycle[ele].head(1)["Relative time"].values[0], linestyle='--', color='y')
pw_cycle_break.append(pw_cycle[total_cycle-1].tail(1)["Relative time"].values[0]) # obtains full break points of sectioning
pw_1t.axvline(pw_cycle[total_cycle-1].tail(1)["Relative time"].values[0], linestyle='--', color='y')
# pw_cycle_break 
# pw_1t.axvline(pw_cycle_break, linestyle='--', color='y')

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig3_tmPw.png")) # save fig as png and pdf/svg format in "savePath"
plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig3_tmPw_power.svg"))
plt.show()

## Plot the [Rotation Angle-Power curve](Fig.4)

fig, pw_2ang = plt.subplots(figsize=(16,9)) # figsize=1600*900 px
plt.subplots_adjust(top=0.961,bottom=0.065,left=0.058,right=0.991,hspace=0.2,wspace=0.2) # Adjust the subplot layout parameters
pw_2ang.scatter(powerdata.iloc[:,3]*r_spd, powerdata.iloc[:,1], s=2, marker='o', color='b', label=r'Power') # s=size(diameter) of marker

pw_2ang.set_title('Power vs. Rotation Angle', fontsize=20)
pw_2ang.set_xlabel('Rotation Angle/Degree', fontsize=18)
pw_2ang.xaxis.set_major_locator(MultipleLocator(90.)) # major ticks that are multiples of 90
#pw_2ang.xaxis.set_major_formatter(FormatStrFormatter('%d'))
pw_2ang.xaxis.set_minor_locator(MultipleLocator(30.)) # minor ticks that are multiples of 30

plt.ylabel('Power/W', fontsize=18)
pw_2ang.grid()
plt.legend(fontsize=14)
# plt.show()
#plt.plot(x[1:], y[1:], 'ro') # highlight specific points in plot
# plt.plot(powerdata.iloc[pw_cycle_max_idx,4], powerdata.iloc[pw_cycle_max_idx,1], 'ro')
plt.plot(0.0, powerdata[powerdata["Rotation angle"]==0].loc[:,["Power"]].values, 'r*') # mark the origin point

plt.plot(powerdata.loc[t_end_idx,["Rotation angle"]], powerdata.loc[t_end_idx,["Power"]], 'r*')  # mark the stop point
 # plt.plot(powerdata.iloc[t_0_auto_idx,2], powerdata.iloc[t_0_auto_idx,1], 'r*', powerdata.iloc[t_end_idx,2], powerdata.iloc[t_end_auto_idx,1], 'r*') # mark the t_0_auto & t_end_auto
plt.plot(pw_cycle_max.loc[:,["Rotation angle"]].values, pw_cycle_max.loc[:,["Power"]].values, 'ro') # highlight max/min point
plt.plot(pw_cycle_min.loc[:,["Rotation angle"]].values, pw_cycle_min.loc[:,["Power"]].values, 'ro') # highlight max/min point
# draw grid of sectioning:
pw_cycle[0].tail(1)["Time"]
pw_cycle[1].head(1)["Time"]
# try for loop to get break points of sectioning
# pw_cycle_break=[]
for ele in range(len(pw_cycle)):
    # pw_cycle_break.append(pw_cycle[ele].head(1)["Relative time"].values[0])
    pw_2ang.axvline(pw_cycle[ele].head(1)["Rotation angle"].values[0], linestyle='--', color='y')
#pw_cycle_break.append(pw_cycle[total_cycle-1].tail(1)["Relative time"].values[0]) # obtains full break points of sectioning
pw_2ang.axvline(pw_cycle[total_cycle-1].tail(1)["Rotation angle"].values[0], linestyle='--', color='y')
# pw_cycle_break 
# pw_1t.axvline(pw_cycle_break, linestyle='--', color='y')

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig4_aglPw.png")) # save fig as png and pdf/svg format in "savePath"
plt.savefig(savePath+"/"+file_name.replace(".csv", "_fig4_aglPw.svg")) 
plt.show()


#*****************************************************************************#
#%% Save & export result
#start on 25.02.2021
#*****************************************************************************#
# SAVE whole info of each measurement into one single dataframe: allResult

#Check the variable, ask for save or not
...
while input("Save the result? ([y]/n)\n...").upper() != "Y": # Just a double-check to avoid mistaken running
    print("Do not save!(you need to terminate maually)")

# del powerdata_allResult
if 'powerdata_allResult' not in locals():
    # creat the dataframe, give column names
    powerdata_allResult = pd.DataFrame(columns=['#',"File Name","Info. Code","LD Current/mA","Laser Power/mW","LC Voltage/V","Repeat #","Polarization Angle","Angle std","Result Choice",
                                 "Speed","Speed Choice","t_0","t_end","t_0 Choice","t_end Choice",
                                 "Max Power","Min Power", "Degree of Pol.(DOP)", "Anisotropy", 
                                 "Result_All","Result_min","Result_Max","Angles_min","Angles_Max","Background"])
idx_rslt = len(powerdata_allResult)
# Check Repeat Result:

if file_name in powerdata_allResult.loc[:,"File Name"].to_list():  # Alt: if True in (powerdata_allResult["File Name"]==file_name): #(but 3 times slower)
    inpRepeat=""
    while inpRepeat.upper() != "Y":
        inpRepeat=input("[WARNING]Result with the file name '{}' already exist!!! Insert a new row and SAVE the result? (typing [y]) Otherwise do not save(need to nterrupt maually). Input:\n...".format(file_name))
    
    # if inpRepeat.upper() == "Y":
    print("Save the result to the next row.")  
    
    ## Assign the repeat series number to column "Repeat #" in each result of the same file name
    ## Alt, do above 6 lines via mask/index instead of loop:
    repeatMask = powerdata_allResult["File Name"] == file_name
    numOfRepeat = len(powerdata_allResult[repeatMask])
    print("Number of already existing result with the same file name:",numOfRepeat)
    powerdata_allResult.loc[repeatMask,"Repeat #"] = range(numOfRepeat) # assign all series # to "Repeat #" to all already existing 'same' result at once via indexing
    powerdata_allResult.at[idx_rslt,"Repeat #"] = numOfRepeat # assign the current result's series # 
    
    
    # ADD here: insert a new row at under the last row with the same file name:
    
    
### Assign each of the results:
# using DataFrame.at or DataFrame.iat :Access a single value for a row/column label pair/ integer position.
# idx_rslt = len(powerdata_allResult)
powerdata_allResult.at[idx_rslt,"#"] = idx_rslt
powerdata_allResult.at[idx_rslt,"File Name"] = file_name

# assign:"Info. Code","LD Current/mA","Laser Power/mW","LC Voltage/V"
try:
    powerdata_allResult.at[idx_rslt,"Info. Code"] = infoCode
except:
    powerdata_allResult.at[idx_rslt,"Info. Code"] = np.nan
try:
    powerdata_allResult.at[idx_rslt,"LD Current/mA"] = laserCurrentVal
except:
    powerdata_allResult.at[idx_rslt,"LD Current/mA"] = np.nan
try:
    powerdata_allResult.at[idx_rslt,"Laser Power/mW"] = laserPowerVal
except:
    powerdata_allResult.at[idx_rslt,"Laser Power/mW"] = np.nan
try:
    powerdata_allResult.at[idx_rslt,"LC Voltage/V"] = lcVoltVal
except:
    powerdata_allResult.at[idx_rslt,"LC Voltage/V"] = np.nan

    
###% Ask for pol. angle selection & save it:
inpPolRsltSelectMsg= f"Save Polarization Angle. Indicate which result should be saved:\n\
    -'all': save result cal. from both Max. & min. {pw_pol_angle_all_count_mean, pw_pol_angle_all_count_std};\n\
    -'min': save result cal. from min. only.       {pw_pol_angle_min_mean, pw_pol_angle_min_std};\n\
    -'max': save result cal. from Max. only.       {pw_pol_angle_max_mean, pw_pol_angle_max_std};\n\
    -'nan': do not save the result.\n\
Input the kay words here:..."

inpPolRsltSelect = ""
while inpPolRsltSelect.upper() not in ["ALL","MIN","MAX","NAN"]:
    print("[ERROR]Your input cannot match any KEY words. Please input the KEY words correctly. Otherwise interrupt the running maually")
    inpPolRsltSelect = input(inpPolRsltSelectMsg)
    
if inpPolRsltSelect.upper()=="ALL":
    powerdata_allResult.at[idx_rslt,"Polarization Angle"] = pw_pol_angle_all_count_mean
    powerdata_allResult.at[idx_rslt,"Angle std"] = pw_pol_angle_all_count_std
    powerdata_allResult.at[idx_rslt,"Result Choice"] = "all"
    print("Pol. angle result of 'all' is saved!")
elif inpPolRsltSelect.upper()=="MIN":
    powerdata_allResult.at[idx_rslt,"Polarization Angle"] = pw_pol_angle_min_mean
    powerdata_allResult.at[idx_rslt,"Angle std"] = pw_pol_angle_min_std
    powerdata_allResult.at[idx_rslt,"Result Choice"] = "min"
    print("Pol. angle result of 'min' is saved!")
elif inpPolRsltSelect.upper()=="MAX":
    powerdata_allResult.at[idx_rslt,"Polarization Angle"] = pw_pol_angle_max_mean
    powerdata_allResult.at[idx_rslt,"Angle std"] = pw_pol_angle_max_std
    powerdata_allResult.at[idx_rslt,"Result Choice"] = "Max"
    print("Pol. angle result of 'Max' is saved!")
elif inpPolRsltSelect.upper()=="NAN":
    powerdata_allResult.at[idx_rslt,"Polarization Angle"] = float('nan')
    powerdata_allResult.at[idx_rslt,"Angle std"] = float('nan')
    powerdata_allResult.at[idx_rslt,"Result Choice"] = "NaN"
    print("NO(nan) Pol. angle result is saved!")

###% Save Speed & its selection:
powerdata_allResult.at[idx_rslt,"Speed"] = r_spd # assign the speed
# Save the source of speed value: original/auto corrected/specified
# Update: make it easy by puting a new variable r_spdChoice in the above if syntax to mark down the choice. Now only need to assign this variable
powerdata_allResult.at[idx_rslt,"Speed Choice"] = r_spdChoice
print("\nRoataion Speed is saved as:",powerdata_allResult.at[idx_rslt,"Speed"],";",powerdata_allResult.loc[idx_rslt,"Speed Choice"])

###% Save t_0, t_end and their selection:
# t_0:
powerdata_allResult.at[idx_rslt,"t_0"] = t_0

powerdata_allResult.at[idx_rslt,"t_0 Choice"] = t_0Choice
print("t_0 is saved as:",powerdata_allResult.at[idx_rslt,"t_0"],";",powerdata_allResult.loc[idx_rslt,"t_0 Choice"])

# t_end:
powerdata_allResult.at[idx_rslt,"t_end"] = t_end

powerdata_allResult.at[idx_rslt,"t_end Choice"] = t_endChoice
print("t_end is saved as:",powerdata_allResult.at[idx_rslt,"t_end"],";",powerdata_allResult.loc[idx_rslt,"t_end Choice"])

###% Save power values of Max. & min. ([mean, std] of power values. unit:W):

powerdata_allResult.at[idx_rslt,"Max Power"] = pw_cycle_max_count_power # [mean, std] of power values of max. unit:W
powerdata_allResult.at[idx_rslt,"Min Power"] = pw_cycle_min_count_power # [mean, std] of power values of min. unit:W
print("Statistics of Power/W:\n@ Max. [mean, std]:{}\n@ min. [mean, std]:{}\n".format(pw_cycle_max_count_power,pw_cycle_min_count_power))
powerdata_allResult.at[idx_rslt,"Degree of Pol.(DOP)"] = P_DOP
print("Degree of polarization(DOP): P = ", P_DOP)
powerdata_allResult.at[idx_rslt,"Anisotropy"] = r_anisotropy
print("Anisotropy: r = ", r_anisotropy, "\n")

### Save the whole result of Polarization Angle
# "Result_All","Result_min","Result_Max","Angles_min","Angles_Max"
powerdata_allResult.at[idx_rslt,"Result_All"] = [pw_pol_angle_all_count_mean,pw_pol_angle_all_count_std]
powerdata_allResult.at[idx_rslt,"Result_min"] = [pw_pol_angle_min_mean,pw_pol_angle_min_std]
powerdata_allResult.at[idx_rslt,"Result_Max"] = [pw_pol_angle_max_mean,pw_pol_angle_max_std]
powerdata_allResult.at[idx_rslt,"Angles_min"] = pw_pol_angle_min_count
powerdata_allResult.at[idx_rslt,"Angles_Max"] = pw_pol_angle_max_count
### Save Background info
powerdata_allResult.at[idx_rslt,"Background"] = [bkgdMeanValue, bkgdStd, bkgdChoice]

# print(powerdata_allResult.iloc[idx_rslt]) # In the end, print the current row
print("Current result saved!")
# done at 2:50AM March 1st, 2021

################################
### Save & Export individual result of each file
powerdata_indvResult = powerdata_allResult.iloc[idx_rslt].copy() # copy current row of powerdata_allResult
powerdata_indvResult["Unit"] = "Time: Second; Power: Watt"

## Export DataFrame variables as CSV files
# creat new directory for saving results; Copy this part to step 2 after loading the CSV file for saving plottings
cwd = os.getcwd()
# dateStr = datetime.now().strftime("%x").replace("/","") #e.g.'030721'. Use it in the folder name for discriminating results from diff. dates
dateStr = datetime.now().strftime("%Y%m%d")[2:] # new expression for date refers to ISO 8601: '210308'; str[:] slicing strings
savePath = os.path.join(cwd, "pwResult_"+dateStr, file_name.replace(".csv", "")) # to save indv. results in a folder of its CSV file name; Need to create dir by os.mkdir(savePath) before df.to_csv()
# print(savePath)
if os.path.isdir(savePath) == False:
    try: 
        # os.mkdir(savePath) # creat new directory
        # Notice: A single call of os.mkdir(savePath) can only creating A Single Directory in the current working dir(like ...\Optical Power Monitor\pwResult_030721) without any sub-directories. To Create a Directory with Subdirectories using makedirs()
        os.makedirs(savePath)
    except OSError as error: 
        print(error)   

powerdata_indvResult.to_csv(savePath+"/"+file_name.replace(".csv", "_indvResult.csv"), index=True, na_rep="NaN")
powerdata.to_csv(savePath+"/"+file_name.replace(".csv", "_DATA.csv"), index=False, na_rep="NaN")
pw_cycle_all_count.to_csv(savePath+"/"+file_name.replace(".csv", "_cyclesResult.csv"), index=False, na_rep="NaN")
print("\nIndividual results of '{}' exported successfully! (dir: {})".format(file_name,savePath))

dfPwData.to_csv(savePath+"/"+file_name, index=False, header=False) # In the end, save Original data as a copy to indvResult folder; without index nor column name

plt.close('all') # all open plots are closed
# Updated: 11:30PM March 7, 2021; Complete plotting adjustment, save fig, and copy orig. data
 
################################
### For dropping results in DataFrame. Uncomment it and run:
# powerdata_allResult.drop(powerdata_allResult.index[-1], inplace=True) # drop the last(current) row in powerdata_allResult; 
# dropIdx = # drop any given row in powerdata_allResult; 
# powerdata_allResult.drop(powerdata_allResult.index[dropIdx], inplace=True) 

# del powerdata_indvResult

################################

#%% Export the DataFrame: powerdata_allResult as a CSV file
'''
Run this cell AFTER processing all the files. The DataFrame type variable 
"powerdata_allResult" will be saved as a CSV file in the working folder.
'''
cwd = os.getcwd()
# dateStr = datetime.now().strftime("%x").replace("/","") #e.g.'030721'. Use it in the folder name for discriminating results from diff. dates
dateStr = datetime.now().strftime("%Y%m%d")[2:] # new expression for date refers to ISO 8601: '210308'; str[:] slicing strings
savePath = os.path.join(cwd, "pwResult_"+dateStr) 
# print(savePath)
if os.path.isdir(savePath) == False:
    try: 
        os.makedirs(savePath) # creat new directory
    except OSError as error: 
        print(error)

allResultFilePath = savePath+'/'+'powerdata_allResult_'+dateStr+'.csv'
inpAllRsltOverwrite = ""
if os.path.isfile(allResultFilePath): # check if the file already exist. If so, ask for overwrite or not
    while inpAllRsltOverwrite not in ["Y","N","R"]: # Keep in the loop if not answer correctly
        inpAllRsltOverwrite = input("The CSV file already exists, input: 'y' for overwriting; 'n' for not exporting; 'r' for rename the file.\n...").upper()
        if inpAllRsltOverwrite == "Y":
            powerdata_allResult.to_csv(allResultFilePath, index=False, na_rep="NaN")
            print("\nComplete result exported successfully! ({})".format(allResultFilePath))
        elif inpAllRsltOverwrite == "N": 
            print("Do not export!")
        elif inpAllRsltOverwrite == "R": # re-name the file and export
            allResultFileName = input("Type a new name(other than '{}') for exporting Complete Result:".format('powerdata_allResult_'+dateStr+'.csv'))
            allResultFilePath = savePath+'\\'+allResultFileName+'.csv'
            powerdata_allResult.to_csv(allResultFilePath, index=False, na_rep="NaN", mode="x") #  mode="x" will raise an exception if the target file still exists
            print("\nComplete result exported successfully! ({})".format(allResultFilePath))
        else:
            print("WARNING: No option matches your input! Choose again.")
else: # if no file exists, export
    powerdata_allResult.to_csv(allResultFilePath, index=False, na_rep="NaN", mode="x")
    print("\nComplete result exported successfully! ({})".format(allResultFilePath))

powerdata_allResultRead = pd.read_csv(allResultFilePath)
powerdata_allResultRead = pd.read_csv("D:\Yuton\Documents\Thorlabs\Optical Power Monitor\\2021011415\pwResult_210315\powerdata_allResult_210315.csv")

#*****************************************************************************#
