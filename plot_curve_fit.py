"""
===============
Curve fitting

source: 1.6.12.8. Curve fitting — Scipy lecture notes
https://scipy-lectures.org/intro/scipy/auto_examples/plot_curve_fit.html#sphx-glr-download-intro-scipy-auto-examples-plot-curve-fit-py
on 25.02.2021
===============

Demos a simple curve fitting
"""

############################################################
# First generate some data
import numpy as np

# Seed the random number generator for reproducibility
np.random.seed(0)

# x_data = np.linspace(-5, 5, num=50)
# y_data = 2.9 * np.sin(1.5 * x_data) + np.random.normal(size=50)

#Alt: common cos curve
x_data = np.linspace(0, 360, num=360)
y_data = 2.5*np.cos(np.pi/180*x_data+np.pi/180*(-45))+2.5# + np.random.normal(size=360) #np.pi/180=0.017453292519943295

# And plot it
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.scatter(x_data, y_data)

############################################################
# Now fit a simple sine function to the data
from scipy import optimize

def test_func(x, a, b, c, d):
    return a * np.cos(b * x + c) + d

params, params_covariance = optimize.curve_fit(test_func, x_data, y_data,
                                               p0=[2, 0.015, 0, 1])

print(params)

############################################################
# And plot the resulting curve on the data

plt.figure(figsize=(6, 4))
plt.scatter(x_data, y_data, label='Data')
plt.plot(x_data, test_func(x_data, params[0], params[1], params[2], params[3]),
         'r', label='Fitted function')

plt.legend(loc='best')

plt.show()


#%% ###########################################################
# apply to power-angle curve. Do it after run cal. script
import numpy as np
# power of measurement (when rotating):
y_data1 = powerdata.iloc[t_0_idx:t_end_idx+1,1].to_numpy()
# angle (when rotating):
x_data1 = powerdata.iloc[t_0_idx:t_end_idx+1,4].to_numpy()
# And plot it
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.scatter(x_data1, y_data1, s=8, marker='o',)

# Now fit a simple sine function to the data
from scipy import optimize
def fit_power_angle_func(x, a, b, c, d):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2+d
    # return a*(np.cos(b*x+c))**2 # in [deg]
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[0.015, 1, -45, 0.001])

print(params)

r_spd_fit = round(90/params[1], 3)
theta_0_fit = round(params[2], 3)
print("theta_0 by fitting: {} degree\nr_spd by fitting: {} degree/s".format([theta_0_fit,90+theta_0_fit],r_spd_fit))

print("\ntheta_0 by localization of Max./min.: {} degree\nr_spd by localization of Max./min.: {} degree/s".format([pw_pol_angle_min_mean,pw_pol_angle_max_mean,pw_pol_angle_all_count_mean],r_spd))
print("\ntheta_0 by estimation of inertial phase angle: {} degree\n".format(round(theta_0,3)))
# fit_power_angle_func(x, params[0], params[1], params[2], params[3])
############################################################
# And plot the resulting curve on the data
plt.figure(figsize=(6,4))
plt.scatter(x_data1, y_data1, s=8, marker='o', label="Raw data")
plt.plot(x_data1, fit_power_angle_func(x_data1, params[0], params[1], params[2], params[3]), 
         "r",label="Fitted function")

plt.legend(loc="best")
plt.show()

############################## Results:
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

#%% ###########################################################
# Test of fitting 4 channel images
x_data1 = np.array([0,45,90,135])
y_data1 = np.array([17.04, 9.93, 59.11, 10.34]) #np.array([136.54, 57.23, 46.84, 51.16])
# And plot it
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.scatter(x_data1, y_data1, s=8, marker='o',)

# Now fit a simple sine function to the data without offset of y value
from scipy import optimize
def fit_power_angle_func(x, a, b, c):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2
    # return a*(np.cos(b*x+c))**2 # in [deg]
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[120, 1.0, 1.0])

print(params)

# Now fit a simple sine function to the data WITH offset d if y value
from scipy import optimize
def fit_power_angle_func(x, a, b, c, d):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2+d
    # return a*(np.cos(b*x+c))**2 # in [deg]
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[50, 1, 50, 10])
# good guessing e.g. [0.015, 1, -45, 0.001], [100, 1, 45, 10]

print(params)


# And plot the resulting curve on the data
plt.figure(figsize=(6,4))
plt.scatter(x_data1, y_data1, s=8, marker='o', label="Raw data")
x_data0 = np.linspace(0, 360, num=360)
# if fit 4 arg
plt.plot(x_data0, fit_power_angle_func(x_data0, params[0], params[1], params[2], params[3]), 
         "r",label="Fitted function")
# # if fit 3 arg
# plt.plot(x_data0, fit_power_angle_func(x_data0, params[0], params[1], params[2])#, params[3]), 
#          "r",label="Fitted function")

plt.legend(loc="best")
plt.show()




######################### For internship ###################################
# First generate some data
import numpy as np

# Test of fitting 16 angles for pulse energy values
x_data1 = np.array([5.10,4.95,4.75,4.60,4.40,4.15,4.00,3.85,3.75,3.60,3.50,3.35,3.20,3.05,2.90,2.70])
y_data1 = np.array([250,230,210,190,170,150,140,130,120,110,100,90,80,70,60,50]) #np.array([136.54, 57.23, 46.84, 51.16])
# And plot it
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.scatter(x_data1, y_data1, s=8, marker='o',)

# Now fit a simple sine function to the data without offset of y value
from scipy import optimize
def fit_power_angle_func(x, a, b, c):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2
    # return a*(np.cos(b*x+c))**2 # in [deg]
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[250, 1.0, 1.0])

print(params)

# Now fit a simple sine function to the data WITH offset d of y value
from scipy import optimize
def fit_power_angle_func(x, a, b, c, d):
    return a/2*np.cos(2*b*(np.pi/180)*x+2*(np.pi/180)*c)+a/2+d
    # return a*(np.cos(b*x+c))**2 # in [deg]
params, params_covariance = optimize.curve_fit(fit_power_angle_func, x_data1, y_data1, 
                                               p0=[1000, 1, 0, 10])
# good guessing e.g. [0.015, 1, -45, 0.001], [100, 1, 45, 10]

print(params)


# And plot the resulting curve on the data
plt.figure(figsize=(6,4))
plt.scatter(x_data1, y_data1, s=8, marker='o', label="Raw data")
x_data0 = np.linspace(0, 360, num=360)
# if fit 4 arg
plt.plot(x_data0, fit_power_angle_func(x_data0, params[0], params[1], params[2], params[3]), 
         "r",label="Fitted function")
# # if fit 3 arg
# plt.plot(x_data0, fit_power_angle_func(x_data0, params[0], params[1], params[2])#, params[3]), 
#          "r",label="Fitted function")

plt.legend(loc="best")
plt.show()

