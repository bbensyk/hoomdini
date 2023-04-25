import hoomd
import math
import numpy as np

'''=====================0 Exit Class0=======================0
 define a custom operation that will update us with the simulation status
0=====================0 Check State class 0======================='''

class hoomdini(hoomd.custom.Action):
    def __init__(self, numActive,numEscaped):
        self.numActive = numActive
        self.numEscaped = numEscaped 

    def act(self, timestep):
        snap = self._state.get_snapshot()
        locs = snap.particles.position[:]
        x_locs = locs[:,0] #the x value of every particle
        #print(np.asarray(x_locs[:] > 0.3).nonzero())
        snap.particles.position[np.asarray(x_locs[:] > 0.3).nonzero(),0] =22 # for any particle that has escape is put at x =22
        snap.particles.typeid[np.asarray(x_locs[:] > 0.3).nonzero()] = 2 #change particle type to 2, so it is no longer included in integrator
        self._state.set_snapshot(snap) #save updates to snapshot