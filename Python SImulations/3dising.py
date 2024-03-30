import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import ipywidgets as widgets
from IPython.display import display

class IsingModel3DSphere:
    def __init__(self, N, R, T, steps=500):
        self.N = N  # Grid size
        self.R = R  # Radius for spherical boundary
        self.T = T  # Temperature
        self.steps = steps  # Number of simulation steps
        self.spins, self.surface_indices = self.initialize_spins_with_surface()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

    def initialize_spins_with_surface(self):
        spins = np.zeros((self.N, self.N, self.N), dtype=int)
        surface_indices = []
        center = self.N // 2
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    dist = (x - center) ** 2 + (y - center) ** 2 + (z - center) ** 2
                    if dist <= self.R ** 2:
                        spins[x, y, z] = np.random.choice([-1, 1])
                        if dist > (self.R-1) ** 2:  # Consider only surface for visualization
                            surface_indices.append((x, y, z))
        return spins, np.array(surface_indices)

    def delta_E(self, x, y, z):
        s = self.spins[x, y, z]
        neighbors = sum([self.spins[(x+1)%self.N, y, z], self.spins[(x-1)%self.N, y, z],
                         self.spins[x, (y+1)%self.N, z], self.spins[x, (y-1)%self.N, z],
                         self.spins[x, y, (z+1)%self.N], self.spins[x, y, (z-1)%self.N]])
        return 2 * s * neighbors

    def monte_carlo_step(self):
        for _ in range(len(self.surface_indices)):
            i = np.random.randint(len(self.surface_indices))
            x, y, z = self.surface_indices[i]
            dE = self.delta_E(x, y, z)
            if dE < 0 or np.random.rand() < np.exp(-dE / self.T):
                self.spins[x, y, z] *= -1

    def update(self, frame):
        self.monte_carlo_step()
        self.ax.clear()
        self.ax.set_xlim(0, self.N)
        self.ax.set_ylim(0, self.N)
        self.ax.set_zlim(0, self.N)
        pos = self.surface_indices[self.spins[self.surface_indices[:,0], self.surface_indices[:,1], self.surface_indices[:,2]] > 0]
        neg = self.surface_indices[self.spins[self.surface_indices[:,0], self.surface_indices[:,1], self.surface_indices[:,2]] < 0]
        self.ax.scatter(pos[:,0], pos[:,1], pos[:,2], color='red', s=1)
        self.ax.scatter(neg[:,0], neg[:,1], neg[:,2], color='blue', s=1)

    def animate(self):
        anim = FuncAnimation(self.fig, self.update, frames=np.arange(0, self.steps), repeat=False)
        plt.show()

# Running the simulation with 3D visualization
N = 200 # Use a smaller grid for better performance
R = 20
T = 0.2
steps = 300
model = IsingModel3DSphere(N, R, T, steps)
model.animate()
