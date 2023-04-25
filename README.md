# hoomdini
HOOMD3 simulations of escape panic in a 2D box.

### Cabilities of the code contained within this repository: 
- Varied particle types
  - Purely Brownian Particles 
  - Active Brownian Particles
  - Active Brownian with Bias towards exit 
- Customizable particle starting locations based on density for both square and hexagonal packing
- Placement of static particles to be used as either doors or obsticals
- Exclusion of particles that have escaped through the walls
- Tracks the number of escaped particles over time and saves into a .csv 
- Tracks the avergae local density of active particles over time and saves to a .csv

### WIPs:
- The density tracker currently requires a large amount of memory. Other density trackers are possible, but the simulations take longer to run
- The hexagonal packing module is only set up for the highest density. Further work needs to be preformed to make it variable
- I worked on creating a vision based bias for module which is about 80% complete but needs further work
- For now the bias operator uses a for loop which is discuraged for the HOOMD custom operators due to time it takes to run. Needs optimization.


# Code Structure
I have attempted to keep my code heavily commented and have included a quick break down of the structure. 

![HoomdiniBreakdown](HoomdiniBreakdown.png)
