# 2DPOLIM_YTW
The codes for my M.Sc. project "2D Polarization Fluorescence Imaging (2DPOLIM)". 

Folder: Polarization Measurement

Aiming for calculation in the polarization measurement.

The sample data (csv files) for running the "Get_Pol_Angle.py" is stored in the folder "Samples". "PM_20210114_4_Laser_LC_0mA_0V_Background_25s.csv" is the recorded background of the measurement. Others are data from polarization measurement. Put in the full file name (with .csv) of data when it is asked during running the script.

Folder: Setup Control

Contains home-created software for synchronization and system control of 2DPOLIM setup. 
Arduino is used as the trigger source for synchronizing the laser, LC polarization rotator, and two cameras. Arduino, laser, and LC are controlled in Python by USB connections to the PC. 
