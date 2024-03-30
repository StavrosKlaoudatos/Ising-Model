import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib
from tempfile import NamedTemporaryFile
import zipfile
import os

matplotlib.use("TkAgg")  # Use the TkAgg backend for Matplotlib within Tkinter

class IsingModelSimulator:
    def __init__(self, temperature=1.0, lattice_size=100, coupling_strength=1.0, magnetic_field=0.0, steps=100):
        self.temperature = temperature
        self.lattice_size = lattice_size
        self.coupling_strength = coupling_strength
        self.magnetic_field = magnetic_field
        self.steps = steps
        self.lattice = np.random.choice([-1, 1], size=(lattice_size, lattice_size))
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.lattice, cmap='viridis', interpolation='nearest')
        self.energy_data = []
        self.spin_data = []
        self.ani = None  # Animation object, initially None

    def calculate_total_energy(self):
        energy = 0
        for i in range(self.lattice_size):
            for j in range(self.lattice_size):
                S = self.lattice[i, j]
                nb = self.lattice[(i+1) % self.lattice_size, j] + \
                     self.lattice[i, (j+1) % self.lattice_size] + \
                     self.lattice[(i-1) % self.lattice_size, j] + \
                     self.lattice[i, (j-1) % self.lattice_size]
                energy += -self.coupling_strength * S * nb
        return energy / 2.0  # Each pair is counted twice

    def delta_energy(self, i, j):
        S = self.lattice[i, j]
        nb = self.lattice[(i+1) % self.lattice_size, j] + \
             self.lattice[i, (j+1) % self.lattice_size] + \
             self.lattice[(i-1) % self.lattice_size, j] + \
             self.lattice[i, (j-1) % self.lattice_size]
        return 2 * S * nb * self.coupling_strength

    def simulate_step(self, frame):
        for _ in range(self.lattice_size ** 2):
            i, j = np.random.randint(0, self.lattice_size, size=2)
            dE = self.delta_energy(i, j)
            if dE < 0 or np.random.rand() < np.exp(-dE / self.temperature):
                self.lattice[i, j] *= -1  # Flip the spin
        self.energy_data.append(self.calculate_total_energy())  # Track energy after each step
        self.spin_data.append(np.mean(self.lattice))  # Track average spin after each step
        self.im.set_data(self.lattice)
        return self.im,

    def start_simulation(self):
        self.ani = FuncAnimation(self.fig, self.simulate_step, frames=range(self.steps), interval=50, blit=True, repeat=False)

    def perform_analysis(self):
        # Analysis generates plots for Total Energy and Average Spin
        figures = []
        steps = np.arange(len(self.energy_data))  # Use recorded data length
        fig_energy, ax_energy = plt.subplots()
        ax_energy.plot(steps, self.energy_data, label="Total Energy", color='red')
        ax_energy.set_title("Total Energy Over Time")
        ax_energy.set_xlabel("Step")
        ax_energy.set_ylabel("Energy")
        figures.append(fig_energy)

        fig_spin, ax_spin = plt.subplots()
        ax_spin.plot(steps, self.spin_data, label="Average Spin", color='blue')
        ax_spin.set_title("Average Spin Over Time")
        ax_spin.set_xlabel("Step")
        ax_spin.set_ylabel("Spin")
        figures.append(fig_spin)

        return figures

class IsingModelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2D Ising Model Simulator")
        self.geometry("800x600")
        self.simulator = None
        self.figures = []  # To hold analysis figures
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Define parameter inputs and labels
        self.temperature = tk.DoubleVar(value=2.5)
        self.lattice_size = tk.IntVar(value=100)
        self.coupling_strength = tk.DoubleVar(value=1.0)
        self.magnetic_field = tk.DoubleVar(value=0.0)
        self.steps = tk.IntVar(value=100)

        fields = [
            ("Temperature (T):", self.temperature),
            ("Lattice Size (N):", self.lattice_size),
            ("Coupling Strength (J):", self.coupling_strength),
            ("Magnetic Field (h):", self.magnetic_field),
            ("Steps:", self.steps)
        ]
        for label, var in fields:
            ttk.Label(frame, text=label).pack(fill='x', expand=True)
            ttk.Entry(frame, textvariable=var).pack(fill='x', expand=True)

        ttk.Button(frame, text="Start Simulation", command=self.start_simulation).pack(pady=5)

    def start_simulation(self):
        # Ensure no ongoing animation before starting a new one
        if self.simulator and self.simulator.ani:
            try:
                self.simulator.ani.event_source.stop()  # Attempt to stop the existing animation
            except AttributeError:
                pass  # If ani or event_source does not exist, ignore the error
            plt.close(self.simulator.fig)  # Close the existing figure

        # Initialize a new simulator instance and start the simulation
        self.simulator = IsingModelSimulator(
            temperature=self.temperature.get(),
            lattice_size=self.lattice_size.get(),
            coupling_strength=self.coupling_strength.get(),
            magnetic_field=self.magnetic_field.get(),
            steps=self.steps.get()
        )
        self.simulator.start_simulation()
        messagebox.showinfo("Simulation", "Simulation started. Please wait for completion.")

        # Delayed call to display analysis to ensure it runs after the simulation
        self.after(100 + self.simulator.steps * 50, self.display_analysis)

    def display_analysis(self):
        # Perform and display analysis after simulation
        self.figures = self.simulator.perform_analysis()
        for fig in self.figures:
            fig.show()
        self.ask_save_results()

    def ask_save_results(self):
        # Prompt user to save results after analysis
        if messagebox.askyesno("Save Results", "Simulation completed. Would you like to save the results?"):
            self.save_results()

    def save_results(self):
        # Save simulation animation and analysis plots in a ZIP file
        save_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if save_path:
            with zipfile.ZipFile(save_path, 'w') as zipf:
                with NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
                    self.simulator.ani.save(tmpfile.name, writer='ffmpeg', dpi=200)
                    zipf.write(tmpfile.name, arcname="simulation.mp4")
                    os.unlink(tmpfile.name)  # Remove temporary file after saving
                for i, fig in enumerate(self.figures, start=1):
                    with NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                        fig.savefig(tmpfile.name)
                        zipf.write(tmpfile.name, arcname=f"figure_{i}.png")
                        os.unlink(tmpfile.name)  # Remove temporary file after saving

if __name__ == "__main__":
    app = IsingModelApp()
    app.mainloop()
