import hoomd
import gsd.hoomd
import numpy as np
import particlePlacer
import datetime
import pandas as pd
import trampling
import matplotlib
import freud
import placer
pE = [] #number of escaped particles
t = [] #time

'''=====================0 System Parameters 0=======================0
 1: establish the basics of the simulations for the integrator
0=====================0 System Parameters 0======================='''
p_diameter = 1 # particle diameter
D = p_diameter*1.25
dt = 0.0001   #timestep(0.0001)
mag = 5
cone = 0.01 
cell = hoomd.md.nlist.Cell(buffer = D) 
exit_width = p_diameter*2.83
kt = 1
density = 0.9

'''=====================0 Box Parameters 0=======================0
 1:Create world box with Width, Height, Length,xo,yo,zo [2d in this sim]
 2:Add walls to world box so particles don't escape
 3:Creater smaller box for particle placement 
0=====================0 Box Parameters 0======================='''
L = 50
box = [L,L,0,0,0,0] # Width, Height, Length, x0, y0, z0 world box
bounds = [hoomd.wall.Plane(origin=(-L/2,0,0), normal=(1,0,0)),
                 hoomd.wall.Plane(origin=(L/2,0,0), normal=(-1,0,0)),
                 hoomd.wall.Plane(origin=(0,L/2,0), normal=(0,-1,0)),
                 hoomd.wall.Plane(origin=(0,-L/2,0), normal=(0,1,0))]  # HOOMD planar walls 
part_box = [-L/7, L/2.3, -L/2.3, -L/2.3]  # top left X, top left Y, bottom left X, bottom left Y
walls = [(-0.5, L/2, 0, exit_width/2), (-0.5, -exit_width/2, 0, -L/2),(-4,exit_width/2+0.5,-3,exit_width/2-0.5)]  # [(startX, startY, endX, endY)] of the particle based walls and obstical

'''=====================0 Simulation Setup 0=======================0
 1:Place Particles
 2:Add random orientations
 3:Create snapshot
0=====================0 Simulation Setup 0======================='''
N = (25**2*density)/(np.pi*(p_diameter/2)**2)
L = np.abs(part_box[0]-part_box[2])
W = np.abs(part_box[1]-part_box[3])
print("length =",L,"width =",W,"area =",L*W)
print(N)
root = L*W/N
print(np.sqrt(root))
x = np.sqrt(root)
print(x)
if x < p_diameter:
    print("Too dense for chosen measuremnts")
    x = p_diameter
if density < 0.8: 
    part_coords = \
        particlePlacer.createCoordinates(*part_box, spaceBetween=x)
else: 
    part_coords = \
        placer.HexCoords(*part_box)
nA = len(part_coords)

wall_coords= []
for w in walls:
    wall_coords += particlePlacer.createCoordinates(*w, spaceBetween=p_diameter)
nW = len(wall_coords)

nE = 0

s = gsd.hoomd.Frame()
s.particles.N = nA + nW
s.particles.position = part_coords + wall_coords
#s.particles.orientation = orient
s.particles.typeid = ([0] * nA) + ([1] * nW) +([2] * nE)
s.particles.types = ["A", "W","E"]
s.configuration.box = box
s.configuration.dimensions = 2

print(f"IC:\n\tActiveParticles: {nA}\n\tWallParticles: {nW}")

with gsd.hoomd.open(name='sim.gsd', mode='wb') as f:
    f.append(s)

'''=====================0 Add Forces 0=======================0
Lennard-Jones between pair interactions and walls 
0=====================0 Add Forces 0======================='''
eps=1.0
lj = hoomd.md.pair.ForceShiftedLJ(nlist=cell, default_r_cut=p_diameter)
lj_bounds = hoomd.md.external.wall.ForceShiftedLJ(walls=bounds)

lj.params[('A', 'A')] = dict(epsilon=eps, sigma=p_diameter) # pair interactions between same type
lj.params[('A', 'W')] = dict(epsilon=eps, sigma=p_diameter) # particle interactins with fake walls
#all other forces are 0 
lj.params[('W', 'W')] = dict(epsilon=0, sigma=p_diameter)
lj.r_cut[('W', 'W')] = 0
lj.params[('E', 'E')] = dict(epsilon=0, sigma=p_diameter)
lj.r_cut[('E', 'E')] = 0
lj.params[('E', 'W')] = dict(epsilon=0, sigma=p_diameter)
lj.r_cut[('E', 'W')] = 0
lj.params[('A', 'E')] = dict(epsilon=0, sigma=p_diameter)
lj.r_cut[('A', 'E')] = 0

#interactions between particle and walls 
lj_bounds.params['A'] = dict(epsilon=5, sigma=p_diameter, r_cut=D)
lj_bounds.params['W'] = dict(epsilon=0, sigma=p_diameter, r_cut=0)
lj_bounds.params['E'] = dict(epsilon=0, sigma=p_diameter, r_cut=0)
'''=====================0 Initializing 0=======================0
Brownian integrator populated with consants and forces
0=====================0 Initializing 0======================='''

computer = hoomd.device.auto_select()
sim = hoomd.Simulation(device=computer, seed=1)
sim.create_state_from_gsd(filename='sim.gsd')

integrator = hoomd.md.Integrator(dt)
noise = hoomd.md.methods.Brownian(filter=hoomd.filter.Type('A'), kT=kt, alpha =1.0)
integrator.methods.append(noise)

integrator.forces.append(lj)
integrator.forces.append(lj_bounds)

sim.operations.integrator = integrator

'''=====================0 Check State class 0=======================0
 define a custom operation that will update us with the simulation status
0=====================0 Check State class 0======================='''
class printSimState(hoomd.custom.Action):
    global pE
    global t
    def __init__(self, numActive,numWalls):
        self.numActive = numActive
        self.numWalls = numWalls #particle positions actually counterintuitively start with wall positions 

    def act(self, timestep):
        print('Status')
        escaped = 0 
        with self._state.cpu_local_snapshot as snap:
            locs = snap.particles.position[:]
            x_locs = locs[:,0]
            escaped = len(x_locs[np.asarray(x_locs[:] > 0.3).nonzero()])
        esc_per = escaped/self.numActive*100
        pE.append(escaped/self.numActive)
        t.append(timestep*0.0001)
        try:
            secRemaining = int((self._state._simulation.final_timestep - timestep) / self._state._simulation.tps)
        except ZeroDivisionError:
            secRemaining = 0
        print(
            "Time step:", timestep*0.0001,"s", 
            "| # Step:", timestep,
            "| ETR:", str(datetime.timedelta(seconds=secRemaining)))
        print(
            "Escaped:", escaped,
            "| Total Particles:", self.numActive,
            "| Percent:", round(esc_per,3),'%'
        )
        
'''=====================0 Running 0=======================0
Run program
0=====================0 Running 0======================='''
'''trample = trampling.density(numActive = nA, r = p_diameter/2,D=[],L=[],N =0) #track local density
trample_op = hoomd.update.CustomUpdater(
    action=trample, 
    trigger=hoomd.trigger.Periodic(int(100)))'''

status = printSimState(numActive = nA, numWalls =nW) #print status of simulation
status_op = hoomd.write.CustomWriter(
    action=status,
    trigger=hoomd.trigger.Periodic(int(5000))) # every 100,000 steps

sim.operations.writers.append(status_op)
#sim.operations += trample_op


gsd_writer = hoomd.write.GSD(filename='runSim.gsd',
                             trigger=hoomd.trigger.Periodic(100), #every 10_000
                             mode='wb',
                             filter=hoomd.filter.All())
sim.operations.writers.append(gsd_writer)


sim.run(500_000) #10>15 Million seem best
dict1 = {"Time": t, "Percent": pE}
df1 = pd.DataFrame(dict1)
df1.to_csv('brownian.csv')