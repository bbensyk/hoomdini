import hoomd
import math
import numpy as np

'''The basic bias towards door'''

class reorient(hoomd.custom.Action):

    def __init__(self, numActive, cone,door):
        self.numActive = numActive #number of active particles
        self.cone = cone #random noise factor
        self.exitwidth = door #size of door

    def act(self, timestep):
        snap = self._state.get_snapshot() #access particle data
        for i in range(self.numActive):
            x = np.abs(snap.particles.position[i][0]) #since door is at x = 0, the door will be |x| away from the door
            y = -1*snap.particles.position[i][1] 
            mag = np.sqrt(x**2+y**2) #Distance to door
            theta_cur = np.arccos(snap.particles.orientation[i][0]) # the current direction the particle is facing
            if (y > -self.exitwidth/2-2) and (y < self.exitwidth/2+2): 
                theta_exit = 0
            else: 
                theta_exit =  np.arctan2(y,x) #finds angle to door
            theta = np.random.uniform(theta_exit-self.cone, theta_exit+self.cone+0.0001) #angle to door +noise
            snap.particles.orientation[i] = [np.cos(theta/2),0,0,np.sin(theta/2)] #changes the built in orientation of the particle
        self._state.set_snapshot(snap) # save snapshot with new orientation