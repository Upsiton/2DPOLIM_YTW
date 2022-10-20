# -*- coding: utf-8 -*-
"""

Script for Four-directional Measurement of Angle of Polarization (AOP).

An alternative way to measure/cal. orientation of the polarization by the power 
obtained from the analyzer oriented at two sets of orthogonal directions. (I_0 & I_90, I_45 & I_135)

I_0, I_90 are the averaged value from power meter when analyzer orients at 0 or 90 degree, respectively. 
I_45, I_135 corresponds to 45 and 135 degree. 
I_n is the measured background noise.

Created on Wed Feb 17 14:13:24 2021
@author: Yutong

"""
 
import numpy as np

def cal_pol_4orient(I_0, I_45, I_90, I_135, I_n):
    '''
    Parameters
    ------------
    I_0 ... measured power at 0 degree
    I_45 ... measured power at 45 degree    
    I_90 ... measured power at 90 degree
    I_135 ... measured power at 135 degree
    I_n ... background noise
    
    Returns
    ------------
    I_n, I_0, I_90 ... 
    theta_0 ... result of arctan(((I_90-I_n)/(I_0-I_n))**0.5)
    I_45, I_135 ... 
    theta_45 ... result of arctan(((I_135-I_n)/(I_45-I_n))**0.5)
    
    angle_0 ... AOP calculated from measurement at 0 & 90 degree
    angle_45 ... AOP calculated from measurement at 45 & 135 degree
    angleResult ... final result of AOP. Either choose one from angle_0 and angle_45, or take the average according to the condition
       
    '''
    
    if 'I_n' not in locals(): I_n = 0 # Default set noise I_n=0 if it's not given
    
    # cal. Pol. angle by power from two crossed orientations @ 0 & 90 deg. Get angle relative to axis of 45 deg
    if 'I_0' and 'I_90' in locals():
        print("I_0 = {} uW, I_90 = {} uW".format(I_0,I_90))
        theta_0 = 180/np.pi*np.arctan(((I_90-I_n)/(I_0-I_n))**0.5)
        theta_0 = round(theta_0, 2)
        print("Angle relative to 0 deg: ", theta_0)
    else:
        print("[ERROR!!!] 'I_0' & 'I_90' are not both assigned!")

    # cal. Pol. angle by power from two crossed orientations @ 45 & 135 deg. Get angle relative to axis of 45 deg
    if 'I_45' and 'I_135' in locals():
        print("I_45 = {} uW, I_135 = {} uW".format(I_45,I_135))
        if I_45 >= I_135:
            print("I_45 >= I_135 => theta_0 belongs to [0,90)")
        else:
            print("I_45 < I_135 => theta_0 belongs to [90,180)")
        theta_45 = 180/np.pi*np.arctan(((I_135-I_n)/(I_45-I_n))**0.5)
        theta_45 = round(theta_45, 2)
        print("Angle relative to 45 deg: ", theta_45, " degree")
    else:
        print("[ERROR!!!] 'I_0' & 'I_90' are not both assigned!")
        
    # transform of angle relative to axis of 0 degree according to diff. cases:
    if (0<=theta_0<45) and (45>=theta_45>0):
        angle_0 = theta_0
        angle_45 = 45-theta_45
    elif (45<=theta_0<90) and (0<=theta_45<45):
        angle_0 = theta_0
        angle_45 = 45+theta_45
    elif (90>=theta_0>45) and (45<=theta_45<90):
        angle_0 = 180-theta_0 # = 90+(90-theta_0)
        angle_45 = 45+theta_45
    elif (45>=theta_0>0) and (90>=theta_45>45):
        angle_0 = 180-theta_0 # = 90+(90-theta_0)
        angle_45 = 225-theta_45 # = 135+(90-theta_45)
    else:
        print("[ERROR!!!] This shouldn't be seen. No condition fufilled.")
    print("angle_0 = ", angle_0, " degree")
    print("angle_45 = ", angle_45, " degree")
    
    # Automatic selection of the angles among angle_0 and angle_45 and return the proper result:
    # check if angle angle_0 is near the axes of 0/180/90 deg. If so, exclude the result due to it's not accurate due to limited extinction ratio of analyzer.    
    if abs(angle_0-0.)<=10 or abs(angle_0-180.)<=10 or abs(angle_0-90.)<=10: # don't forget the egde of 0/180
        print("angle_0 is close to the axis of 0/90 degree. Select the other value from 45/135 degree as AOP result.")
        angleResult=round(angle_45,2)
    
    # check if angle angle_45 is near the axes of 45/135 deg. If so, exclude the result due to it's not accurate due to limited extinction ratio of analyzer.
    elif abs(angle_45-45.)<=10 or abs(angle_45-135.)<=10: 
        print("angle_45 is close to the axis of 45/135 degree. Select the other value from 0/90 degree as AOP result.")
        angleResult=round(angle_0,2)
        
    else:
        print("No angle is close to axes. Take mean value of both angles as AOP result.")
        angleResult=round((angle_0+angle_45)/2,2)
        
    print("The Angle of Polarization (AOP) result is: {} deg".format(angleResult))
               
    return I_n, I_0, I_90, theta_0, I_45, I_135, theta_45, angle_0, angle_45, angleResult

#%% Running

# some examples of measured data:
cal_pol_4orient(I_0=1.1537E-04, I_45=5.9604E-05, I_90=6.5840E-07, I_135=5.9104E-05, I_n=8.4088E-10) # AOP = 0.12 deg
cal_pol_4orient(I_0=8.7185E-05, I_45=1.0947E-04, I_90=3.0078E-05, I_135=9.1932E-06, I_n=8.4088E-10) # AOP = 29.64 deg
cal_pol_4orient(I_0=5.8063E-05, I_45=1.1677E-04, I_90=5.9051E-05, I_135=1.4660E-06, I_n=8.4088E-10) # AOP = 45.24 deg
cal_pol_4orient(I_0=5.5429E-07, I_45=5.7024E-05, I_90=1.1737E-04, I_135=5.9888E-05, I_n=8.4088E-10) # AOP = 90.7 deg
cal_pol_4orient(I_0=3.0838E-05, I_45=8.2852E-06, I_90=8.8310E-05, I_135=1.1011E-04, I_n=8.4088E-10) # AOP = 120.12 deg
cal_pol_4orient(I_0=6.0888E-05, I_45=1.3078E-06, I_90=5.8016E-05, I_135=1.1749E-04, I_n=8.4088E-10) # AOP = 135.69 deg

