# -*- coding: utf-8 -*-
"""
Script for renaming the original images (raw data saved by cameras) from 2DPOLIM.

Add some strings indicating the channel of camera and corresponding polarization state of excitation in the file name. 

How to run it:
    
1.Run the script. 
2.When the program asks for input in the Console. Copy and paste the path of the folder which contains images acquired by both 
cameras (#213 & #214). 
3.Input the format (suffix) of the image (including '.') when asked. For example:.tif    
4.Wait until finish. The renamed files will be copied to a new folder called "Renamed" in the current folder.     

Explanation of strings in file name:
    _cam0-90_     ---   images taken from camera of 0 & 90 degree channel of detection
    _cam45-135_   ---   images taken from camera of 45 & 135 degree channel of detection
    _ExPol-0deg   ---   polarization orientation of excitation light in this image is 0 degree
    _ExPol-NULL   ---   a NULL state which applies 0V to LC at the end of each full scan. It is used to avoid the drawbacks of slow relaxation of LC from high to low voltage.
    _Cycle1       ---   number of cycles (full scan of all 6 angles) that the image belongs to
    
    
Inspired by online resources:
    https://zhuanlan.zhihu.com/p/281097068
    https://zhuanlan.zhihu.com/p/35032919
    https://www.runoob.com/note/27030

Created on Fri May 20 14:51:27 2022

@author: Yutong
"""

# Import os library
import os
import shutil

# [***Modify HERE***] Specify the path of acquired images here. Remeber to use r"", otherwise use \\ instead of \ 
# path = r"D:\Research\Data\FlyCap\AM callibration" 


# Or do it interactively
path = input(r"Type the path of folder which sotres images captured by cameras (Do NOT use '\\' in the path. Example: D:\Research\Data\FlyCap\AM callibration):")
path = path.strip() # s.strip() for removing possible spaces

if os.path.isdir(path): # check if path exist and is a directory
    # Creat a new folder called "Renamed" in the current directory for storing renamed images
    newPath = path + r'\Renamed'
    if not os.path.exists(newPath): 
        os.mkdir(newPath)
else:
    print("ERROR: cannot find the folder. Please check the 'path'.")
    
# Creat a new folder called "Renamed" in the current directory for storing renamed images
newPath = path + r'\Renamed'
if not os.path.exists(newPath): 
    os.mkdir(newPath)
    
    
# [***Modify HERE***] Specify the format of image (.tif/.jpg):
# imgFormat = ".jpg" 

# Or do it interactively
imgFormat = input("Type the formate of the acquired images including '.' (Example:.tif):")
imgFormat = imgFormat.strip()

        
# Scan all the files in the path
count = 0
folderCount = 0
otherFilesCount = 0

fileList = os.listdir(path) # List all files (including names of subfolders) in the path
# file = fileList[3]

for file in fileList:
    oldDir = os.path.join(path,file) # get old file's directory
    if os.path.isdir(oldDir): # skip if it is a folder instead of a file   
        folderCount+=1
        continue
    
    filename = os.path.splitext(file)[0] # file name
    filetype = os.path.splitext(file)[1] # file type (suffix)
    
    # Skip if the type of file is not the specified type
    if (filetype.upper() != imgFormat.upper()):
        otherFilesCount+=1
        continue
    
    # fileNmSplt = file.split('.')
    #fileName = fileNmSplt[-2] + '.'+fileNmSplt[-1]
    
    # Identify which camera by finding 'Cam213' or 'Cam214'
    if ('cam214'.upper() in filename.upper()):
        filename = filename.replace('214', '0-90')  # Is camera of 0/90 deg. Replace 'Cam214' with 'Cam0-90'
    elif ('cam213'.upper() in filename.upper()):
        filename = filename.replace('213', '45-135')    # Is camera of 45/135 deg. Replace 'Cam213' with 'Cam45-135'

    # Identify the Polarization Orentation Angle from the sequence number of file name:
    
    numImag = int(filename.split('-')[-1])
    
    if (numImag % 7 == 0): 
        strExcPol = '_ExPol-0deg'
    elif (numImag % 7 == 1): 
        strExcPol = '_ExPol-30deg'
    elif (numImag % 7 == 2): 
        strExcPol = '_ExPol-60deg'
    elif (numImag % 7 == 3): 
        strExcPol = '_ExPol-90deg'
    elif (numImag % 7 == 4): 
        strExcPol = '_ExPol-120deg'
    elif (numImag % 7 == 5): 
        strExcPol = '_ExPol-150deg'
    elif (numImag % 7 == 6): 
        strExcPol = '_ExPol-NULL'
    # print(strExcPol)
    
    # get the number of scanning cycles
    numCycle = numImag // 7 + 1
    numCycleStr = '_Cycle'+str(numCycle)
    # print(numCycleStr)
    
    # Create new name that contains info of Polarization Angle of Excitation of each image according to sequence number.
    FileNameNew = filename + numCycleStr + strExcPol + filetype 
    print("New file name:\n"+FileNameNew)
    newDir = os.path.join(newPath, FileNameNew)
        
    # Rename and copy the file into a new folder "Renamed" at current folder.
    # os.rename(os.path.join(path,file), os.path.join(path,FileNameNew)) # only rename
    shutil.copy(oldDir, newDir) # able to copy & rename 
    
    count+=1
    print(f'#{count}')

print(f"Done.\n{count} files are renamed and copied to the sub-folder 'Renamed'.")

# Show info of skipped files/folders
if (folderCount != 0):
    print(f"{folderCount} subfolders are found and skipped!")
    
if (otherFilesCount != 0):
    print(f"{otherFilesCount} files do not match the specified format ({imgFormat}) are found and skipped!!!")