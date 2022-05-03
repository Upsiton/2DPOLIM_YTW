# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 14:13:24 2021
An alternative way to measure/cal. orientation angle of the polarization by the power obtained from 
two crossed direction of the analyzer. I_s & I_p (I_0 & I_90)
@author: Yuton
"""
import numpy as np
I_n = 0.006 #Noise [uW]
I_0 = 19.78 #Power of P(i.e. 0 degree) orientation of analyzer [uW]
I_90 = 0.017 #Power of S(i.e. 90 degree) orientation of analyzer [uW]
theta_0 =180/np.pi*np.arctan(((I_90-I_n)/(I_0-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 0 & 90 deg
print("Angle relative to 0 deg:", theta_0)

I_45 = 0.017 #Power of P(i.e. 0 degree) orientation of analyzer [uW]
I_135 = 9999999.78 #Power of S(i.e. 90 degree) orientation of analyzer [uW]
theta_45 =180/np.pi*np.arctan(((I_135-I_n)/(I_45-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 45 & 135 deg. Get angle relative to 45 deg
print("Angle relative to 45 deg:", " Shifted:",theta_45+45)


# implement in def function: finished on 2021.02.22 11:23pm
def cal_pol_4orient(I_0, I_45, I_90, I_135, I_n):
    # I_0=85.56
    # I_45=108.55
    # I_90=30.56
    # I_135=8.351
    # I_n=0.001
    if 'I_n' not in locals(): I_n = 0 # default noise=0 if not given
    if 'I_0' and 'I_90' in locals():
        print("I_0={}uW, I_90={}uW".format(I_0,I_90))
        theta_0 =180/np.pi*np.arctan(((I_90-I_n)/(I_0-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 0 & 90 deg
        print("Angle relative to 0 deg:", theta_0)
    else:
        print("'I_0' & 'I_90' are not both assigned!")

    if 'I_45' and 'I_135' in locals():
        print("I_45={}uW, I_135={}uW".format(I_45,I_135))
        if I_45 >= I_135:
            print("I_45 >= I_135 => theta_0 belongs to [0,90)")
        else:
            print("I_45 < I_135 => theta_0 belongs to [90,180)")
        theta_45 =180/np.pi*np.arctan(((I_135-I_n)/(I_45-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 45 & 135 deg. Get angle relative to 45 deg
        print("Angle relative to 45 deg:", theta_45)
    else:
        print("'I_0' & 'I_90' are not both assigned!")
        
    # transform of angle according to diff. cases:
    if (0<=theta_0<45) and (45>=theta_45>0):
        angle_0 = theta_0
        angle_45 = 45-theta_45
    elif (45<=theta_0<90) and (0<=theta_45<45):
        angle_0 = theta_0
        angle_45 = 45+theta_45
    elif (90>=theta_0>45) and (45<=theta_45<90):
        angle_0 = 180-theta_0 #=90+(90-theta_0)
        angle_45 = 45+theta_45
    elif (45>=theta_0>0) and (90>=theta_45>45):
        angle_0 = 180-theta_0 #=90+(90-theta_0)
        angle_45 = 225-theta_45 #=135+(90-theta_45)
    else:
        print("[ERROR!!!]This should not be seen. No condition fufilled.")
    print("angle_0 = ", angle_0)
    print("angle_45 = ", angle_45)
    # add auto select the angle:
    if abs(angle_0-0.)<=10 or abs(angle_0-180.)<=10 or abs(angle_0-90.)<=10: # don't forget the egde of 0/180
        print("angle_0 is close to the axis of 0/90 degree. Select the other value from 45/135 degree as result.")
        angleResult=round(angle_45,2)
    elif abs(angle_45-45.)<=10 or abs(angle_45-135.)<=10:
        print("angle_45 is close to the axis of 45/135 degree. Select the other value from 0/90 degree as result.")
        angleResult=round(angle_0,2)
    else:
        print("No angle is close to axes. Take mean value of both angles as result.")
        angleResult=round((angle_0+angle_45)/2,2)
        
    print("The result angle of pol. state is: {} deg".format(angleResult))
               
    return I_n, I_0, I_90, theta_0, I_45, I_135, theta_45, angle_0, angle_45, angleResult

# cal_pol_4orient(I_0=29.18, I_45=58.65, I_90=29.75, I_135=0.655, I_n=0.005)

#%% Automatically processing two angles and return the proper result:
theta_0 = 4.2576 # relative to 0 degree
theta_45 = 44.2566 # relative to 45 degree

angle_0 = 4.2576 # result from ref. axes of 0 & 90 deg
angle_45 = 45-44.2566 # result from ref. axes of 45 & 135 deg
angleBoth = np.array([angle_0,angle_45])
refAngle =  np.array([0., 45.]) # angles of two reference axes

# After the angle_0 & angle_45 is obtained, check if angle near to the axes. If so, exclude the result due to it's not accurate as the other one.
angle_0 = 4.2576 # result from ref. axes of 0 & 90 deg
angle_45 = 45-44.2566 # result from ref. axes of 45 & 135 deg

angle_0 = 44.2576 
angle_45 = 46.2566

angle_0 = 89.2576 
angle_45 = 91.2566

angle_0 = 134.2576 
angle_45 = 135.2566

angle_0 = 181.2576 
angle_45 = 179.2566

angle_0 = 23.2576 
angle_45 = 25.2566

if abs(angle_0-0.)<=10 or abs(angle_0-180.)<=10 or abs(angle_0-90.)<=10: # don't forget the egde of 0/180
    print("angle_0 is close to the axis of 0/90 degree. Select the other value from 45/135 degree as result.")
    angleResult=angle_45
elif abs(angle_45-45.)<=10 or abs(angle_45-135.)<=10:
    print("angle_45 is close to the axis of 45/135 degree. Select the other value from 0/90 degree as result.")
    angleResult=angle_0
else:
    print("No angle is close to axes. Take mean value of both angles as result.")
    angleResult=(angle_0+angle_45)/2
print("The result angle of pol. state is: {} deg".format(angleResult))
#%% Cleaned function for running:
import numpy as np
def cal_pol_4orient(I_0, I_45, I_90, I_135, I_n):
    if 'I_n' not in locals(): I_n = 0 # default noise=0 if not given
    if 'I_0' and 'I_90' in locals():
        print("I_0={}uW, I_90={}uW".format(I_0,I_90))
        theta_0 =180/np.pi*np.arctan(((I_90-I_n)/(I_0-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 0 & 90 deg
        print("Angle relative to 0 deg:", theta_0)
    else:
        print("'I_0' & 'I_90' are not both assigned!")

    if 'I_45' and 'I_135' in locals():
        print("I_45={}uW, I_135={}uW".format(I_45,I_135))
        if I_45 >= I_135:
            print("I_45 >= I_135 => theta_0 belongs to [0,90)")
        else:
            print("I_45 < I_135 => theta_0 belongs to [90,180)")
        theta_45 =180/np.pi*np.arctan(((I_135-I_n)/(I_45-I_n))**0.5) #cal. Pol. angle by power from two crossed orientations @ 45 & 135 deg. Get angle relative to 45 deg
        print("Angle relative to 45 deg:", theta_45)
    else:
        print("'I_0' & 'I_90' are not both assigned!")
        
    # transform of angle according to diff. cases:
    if (0<=theta_0<45) and (45>=theta_45>0):
        angle_0 = theta_0
        angle_45 = 45-theta_45
    elif (45<=theta_0<90) and (0<=theta_45<45):
        angle_0 = theta_0
        angle_45 = 45+theta_45
    elif (90>=theta_0>45) and (45<=theta_45<90):
        angle_0 = 180-theta_0 #=90+(90-theta_0)
        angle_45 = 45+theta_45
    elif (45>=theta_0>0) and (90>=theta_45>45):
        angle_0 = 180-theta_0 #=90+(90-theta_0)
        angle_45 = 225-theta_45 #=135+(90-theta_45)
    else:
        print("[ERROR!!!]This shouldn't be seen. No condition fufilled.")
    print("angle_0 = ", angle_0)
    print("angle_45 = ", angle_45)
    # add auto select the angle:
    if abs(angle_0-0.)<=10 or abs(angle_0-180.)<=10 or abs(angle_0-90.)<=10: # don't forget the egde of 0/180
        print("angle_0 is close to the axis of 0/90 degree. Select the other value from 45/135 degree as result.")
        angleResult=round(angle_45,2)
    elif abs(angle_45-45.)<=10 or abs(angle_45-135.)<=10:
        print("angle_45 is close to the axis of 45/135 degree. Select the other value from 0/90 degree as result.")
        angleResult=round(angle_0,2)
    else:
        print("No angle is close to axes. Take mean value of both angles as result.")
        angleResult=round((angle_0+angle_45)/2,2)
        
    print("The result angle of pol. state is: {} deg".format(angleResult))
               
    return I_n, I_0, I_90, theta_0, I_45, I_135, theta_45, angle_0, angle_45, angleResult
