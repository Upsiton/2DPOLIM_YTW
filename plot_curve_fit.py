"""
===============
Curve fitting of power meter data in Angle of Polarization measurement

Inspired by: 1.6.12.8. Curve fitting — Scipy lecture notes
https://scipy-lectures.org/intro/scipy/auto_examples/plot_curve_fit.html#sphx-glr-download-intro-scipy-auto-examples-plot-curve-fit-py
on 25.02.2021
===============
"""

# Fit the Power v.s. Angle curve. Run this script after running "Get_Pol_Angle.py".

import numpy as np

# read power data of measurement (Y data) (when rotating):
y_data1 = powerdata.iloc[t_0_idx:t_end_idx+1,1].to_numpy()

# read angles (X data) (when rotating):
x_data1 = powerdata.iloc[t_0_idx:t_end_idx+1,4].to_numpy()

# And plot the original data
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.scatter(x_data1, y_data1, s=8, marker='o',)

# Now fit the cos**2 function (Malus's law) to data 
from scipy import optimize

def fit_power_angle_func(x, a, b, c, d):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2+d
    # return a*(np.cos(b*x+c))**2 # in [deg]
    
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[0.015, 1, -45, 0.001]) # guess of parameters

print(params)

r_spd_fit = round(90/params[1], 3) # rotation speed from fitting
theta_0_fit = round(params[2], 3) # AOP (initial phase) result from fitting

print("theta_0 by fitting: {} degree\nr_spd by fitting: {} degree/s".format([theta_0_fit,90+theta_0_fit],r_spd_fit))

print("\ntheta_0 by localization of Max./min.: {} degree\nr_spd by localization of Max./min.: {} degree/s".format([pw_pol_angle_min_mean,pw_pol_angle_max_mean,pw_pol_angle_all_count_mean],r_spd))
print("\ntheta_0 by estimation of inertial phase angle: {} degree\n".format(round(theta_0,3)))

############################################################
# And plot the resulting curve on the data
plt.figure(figsize=(6,4))
plt.scatter(x_data1, y_data1, s=8, marker='o', label="Raw data")
plt.plot(x_data1, fit_power_angle_func(x_data1, params[0], params[1], params[2], params[3]), 
         "r",label="Fitted function")

plt.legend(loc="best")
plt.show()

############################################################


    
    
##################### Some tests ############
# def fit_power_angle_func(x, a, b, c):
#     return a/2+a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)
#     # return a*(np.cos(b*x+c))**2

# params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
#                                                p0=[0.015, 1, -45])

# def fit_power_angle_func(x, a, b, c, d):
#     return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2+d
#     # return a*(np.cos(b*x+c))**2
# params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
#                                                p0=[0.015, 1, -45, 0.001])

########################

#raise RuntimeError("Optimal parameters not found: " + errmsg)
#RuntimeError: Optimal parameters not found: Number of calls to function has reached maxfev = 800.

