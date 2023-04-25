import hoomd
import math
import numpy as np

'''Attempt at adding vision to particle bias'''

class reorient(hoomd.custom.Action):

    def __init__(self, numActive, cone,door):
        self.numActive = numActive #number of active particles
        self.cone = cone #noise factor
        self.exitwidth = door #size of door
    
    def check_sight(self, theta_cur, theta_exit, y): #attempt to insure that the particle is facing the door. 1.2 rads is a human's field of view
        check = True
        if y > 0:
            if (np.sin(theta_cur) < np.sin(theta_exit + 0.6)) and (np.sin(theta_cur) > np.sin(theta_exit - 0.6)): check = False
        else: 
            if (np.sin(theta_cur) > np.sin(theta_exit + 0.6)) and (np.sin(theta_cur) < np.sin(theta_exit - 0.6)): check = False
        return check
    
    def check_dist(self, mag): #check to insure that the particle is with a certain distance to the door
        if mag > 15: check = True
        else: check = False
        return check
        
    def angle(self, theta_cur, theta_exit, y, x, mag): #picks an angle
        if self.check_sight(theta_cur,theta_exit,y) or self.check_dist(mag):
            max_rand = 15**2*self.cone #max randomness
            new_theta = np.random.uniform(theta_cur-max_rand, theta_cur+max_rand+0.0001)
        else: 
            rand = mag**2*self.cone #Luminosity drops off as 1/r^2, so noise factor scales as r^2
            new_theta = np.random.uniform(theta_exit-rand, theta_exit+rand+0.0001)
        return new_theta

    def act(self, timestep):
        snap = self._state.get_snapshot()
        for i in range(self.numActive):
            x = np.abs(snap.particles.position[i][0])
            y = -1*snap.particles.position[i][1]
            mag = np.sqrt(x**2+y**2) #Distance to door
            theta_cur = np.arccos(snap.particles.orientation[i][0]) # the current direction the particle is facing
            if (y > -self.exitwidth/2-2) and (y < self.exitwidth/2+2): 
                theta_exit = 0
            else: 
                theta_exit =  np.arctan2(y,x)
            theta = self.angle(self, theta_cur, theta_exit, y, x, mag)
            snap.particles.orientation[i] = [np.cos(theta/2),0,0,np.sin(theta/2)]
        self._state.set_snapshot(snap)