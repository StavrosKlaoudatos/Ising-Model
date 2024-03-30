import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter, FuncAnimation

def run_simulation(temperature=2.5, lattice_size=100, steps=100):
    lattice = np.random.choice([-1, 1], size=(lattice_size, lattice_size))

    def simulate_step(i):
        i, j = np.random.randint(0, lattice_size, size=2)
        S = lattice[i, j]
        nb = lattice[(i+1)%lattice_size, j] + lattice[i, (j+1)%lattice_size] + lattice[(i-1)%lattice_size, j] + lattice[i, (j-1)%lattice_size]
        dE = 2 * S * nb
        if dE < 0 or np.random.rand() < np.exp(-dE / temperature):
            lattice[i, j] *= -1

    fig, ax = plt.subplots()
    im = ax.imshow(lattice, cmap='viridis', interpolation='nearest')

    def update(frame):
        simulate_step(frame)
        im.set_data(lattice)
        return [im]

    ani = FuncAnimation(fig, update, frames=range(steps), blit=True)
    gif_path = "ising-model-webapp/static/images/simulation.gif"
    ani.save(gif_path, writer=PillowWriter(fps=10))

    # Simplify: Only save the final state for this example
    plt.imshow(lattice, cmap='viridis', interpolation='nearest')
    plt.title("Final State")
    final_state_path = "ising-model-webapp/static/images/final_state.png"
    plt.savefig(final_state_path)

    return gif_path, final_state_path

# Example usage (remove in actual app)
if __name__ == "__main__":
    run_simulation()
