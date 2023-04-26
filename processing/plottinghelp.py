'''imports'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from scipy.interpolate import make_interp_spline
'''read in your csvs'''
vals = (np.array(pd.read_csv('your.csv'))[:,2]*100)
t = (np.array(pd.read_csv('your.csv'))[:,1]*100)
'''While not necesary, it may be helpful to add more (0,0) values to insure the graph starts from orgin'''
T= np.zeros(len(t)+5)
V = np.zeros(len(t)+5)
T[5:] = t
V[5:] = vals

'''Plot the values'''
colors = ["lightsteelblue","cornflowerblue", "dodgerblue","blue","navy"] 
plt.plot(T, V, color = colors[0] ,label = "your label")
plt.legend()
plt.xlabel("time", fontsize =15)
plt.xlim(0,6000)
plt.ylim(0)
plt.ylabel("Percent Escaped", fontsize =15)
plt.title("Percent escaped vs Time at an Activity of 100", fontsize =18)
plt.show()

'''Find time to escape'''
escT = np.zeros((n,m)) #array of escape times for each density and magnitude
for i in range(m):
    Et_V = np.asarray(V[i] ==100).nonzero()
    if np.shape(Et_V)== (1,0):
        escT[0,i] = np.log10(t[-1])
        print("didn't escape")
    else:
        escT[0,i] = np.log10(t[Et_V[0][0]]) #save the first time value when percent escape > 100

'''Example Heat Map'''
x = densities
y = magnitudes
z = escT
X, Y = np.meshgrid(x, y)
fig, ax = plt.subplots(width_ratios = [1], height_ratios =[1])
cs = ax.pcolormesh(X, Y, z, cmap=cm.viridis)
#clb=plt.colorbar(cs, orientation='horizontal',shrink = 0.5,anchor = (0.5, 0.75))
clb=plt.colorbar(cs, shrink = 0.5)
clb.ax.tick_params(labelsize=8) 
clb.set_label('Log of Equiliberation Time', loc = 'center',fontsize=8)
plt.xlabel("Density of Particles", fontsize = 18)
plt.ylabel("Velocity", fontsize = 18)
plt.title("How do Density and Speed Affect Escape Time", fontsize = 20)
plt.show()
