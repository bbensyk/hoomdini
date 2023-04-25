import hoomd
import math
import numpy as np
import freud
import matplotlib

'''=====================0 Trampling Class 0=======================0
Tracks the local density and positions of too high density marked as trampling
0=====================0 Trampling class 0======================='''

class density(hoomd.custom.Action):

    def __init__(self, numActive, r,D,L,N):
        self.numActive = numActive
        self.r = r
        #appends the density and locations of extra high density
        self.D = D
        self.L = L
        self.N = N
        
    def density(self, syst):
        voro = freud.locality.Voronoi()
        cell_A = voro.compute(system = syst).volumes
        A = cell_A[np.asarray(syst.particles.typeid==0).nonzero()] #Only the active particles
        MA = np.mean(A)
        p_A = np.pi*self.r**2
        mean = p_A/MA
        return p_A/A, mean
    
    def trample(self, rho):
        return np.asarray(rho<3).nonzero()

    def act(self, timestep):
        snap = self._state.get_snapshot()
        loc_density,mean = self.density(snap)
        high = self.trample(loc_density)
        zones = snap.particles.position[high]
        self.D.append(mean)
        self.L.append(zones)
        self.N = len(zones[:,0])
        #print("local density has a shape", np.shape(loc_density))
        #print("Total density has shape", np.shape(self.D))
        #print("There are",np.shape(zones),"trampling occurances")
        #print("Trampling has shape", np.shape(self.L))
        
        