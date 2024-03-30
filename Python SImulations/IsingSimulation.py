import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use("TkAgg")  # Ensure that the Tk backend is used for matplotlib

class IsingModelSimulator:
    def __init__(self, temperature=1.0, lattice_size=100, coupling_strength=1.0, magnetic_field=0.0, steps=1000):
        self.temperature = temperature
        self.lattice_size = lattice_size
        self.coupling_strength = coupling_strength
        self.magnetic_field = magnetic_field
        self.steps = steps
        self.lattice = np.random.choice([-1, 1], size=(lattice_size, lattice_size))
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.lattice, cmap='viridis', interpolation='nearest')
        self.ani = None

    def delta_energy(self, i, j):
        spin = self.lattice[i, j]
        sum_neighbors = (
            self.lattice[(i + 1) % self.lattice_size, j] +
            self.lattice[(i - 1) % self.lattice_size, j] +
            self.lattice[i, (j + 1) % self.lattice_size] +
            self.lattice[i, (j - 1) % self.lattice_size]
        )
        return 2 * spin * (self.coupling_strength * sum_neighbors + self.magnetic_field)

    def simulate_step(self, *args):
        for _ in range(self.lattice_size ** 2):
            i, j = np.random.randint(0, self.lattice_size, size=2)
            delta_E = self.delta_energy(i, j)
            if delta_E < 0 or np.random.rand() < np.exp(-delta_E / self.temperature):
                self.lattice[i, j] *= -1
        self.im.set_data(self.lattice)
        return self.im,

    def start_simulation(self):
        self.ani = FuncAnimation(self.fig, self.simulate_step, frames=self.steps, interval=50, blit=True, repeat=False)

    def record_simulation(self, filepath):
        # Ensure ani is not None and has a save method
        if self.ani and hasattr(self.ani, 'save'):
            self.ani.save(filepath, writer='ffmpeg')

class IsingModelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2D Ising Model Simulator")
        self.geometry("400x300")
        self.simulator = None
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Define parameter inputs
        self.temperature = tk.DoubleVar(value=1.0)
        self.lattice_size = tk.IntVar(value=100)
        self.coupling_strength = tk.DoubleVar(value=1.0)
        self.magnetic_field = tk.DoubleVar(value=0.0)

        # Add input fields and labels
        fields = [
            ("Temperature (T):", self.temperature),
            ("Lattice Size (N):", self.lattice_size),
            ("Coupling Strength (J):", self.coupling_strength),
            ("Magnetic Field (h):", self.magnetic_field),
        ]
        for label, var in fields:
            ttk.Label(frame, text=label).pack(fill='x', expand=True)
            ttk.Entry(frame, textvariable=var).pack(fill='x', expand=True)

        # Control buttons
        ttk.Button(frame, text="Start Simulation", command=self.start_simulation).pack(pady=5)
        ttk.Button(frame, text="Record Animation", command=self.record_animation).pack(pady=5)
        ttk.Button(frame, text="Terminate", command=self.terminate).pack(pady=5)

    def prepare_simulation(self):
        if self.simulator and self.simulator.ani:
            self.simulator.ani.event_source.stop()
            plt.close(self.simulator.fig)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.simulator = IsingModelSimulator(
            temperature=self.temperature.get(),
            lattice_size=self.lattice_size.get(),
            coupling_strength=self.coupling_strength.get(),
            magnetic_field=self.magnetic_field.get(),
        )
        self.canvas = FigureCanvasTkAgg(self.simulator.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def start_simulation(self):
        self.prepare_simulation()
        self.simulator.start_simulation()

    def record_animation(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All Files", "*.*")],
        )
        if filepath:
            self.prepare_simulation()
            self.simulator.start_simulation()
            self.simulator.record_simulation(filepath)
            print(f"Animation saved to {filepath}")

    def terminate(self):
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = IsingModelApp()
    app.mainloop()
