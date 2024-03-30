from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def calculate_total_energy(lattice, coupling_strength, magnetic_field):
    energy = 0
    lattice_size = len(lattice)
    for i in range(lattice_size):
        for j in range(lattice_size):
            spin = lattice[i][j]
            # Sum over nearest neighbors using periodic boundary conditions
            sum_neighbors = lattice[(i-1) % lattice_size][j] + lattice[(i+1) % lattice_size][j] + lattice[i][(j-1) % lattice_size] + lattice[i][(j+1) % lattice_size]
            energy += -coupling_strength * spin * sum_neighbors - magnetic_field * spin
    return energy / 2  # Each pair is counted twice

def ising_model_simulation(temperature, lattice_size, coupling_strength, magnetic_field, steps, frame_capture_rate=10):
    lattice = np.random.choice([-1, 1], size=(lattice_size, lattice_size))
    frames = []
    energies = []

    average_spin = []

    for step in range(steps):
        for _ in range(lattice_size * lattice_size):
            i, j = np.random.randint(0, lattice_size, size=2)
            spin = lattice[i, j]
            sum_neighbors = lattice[(i + 1) % lattice_size, j] + lattice[(i - 1) % lattice_size, j] + lattice[i, (j + 1) % lattice_size] + lattice[i, (j - 1) % lattice_size]
            delta_E = 2 * spin * (coupling_strength * sum_neighbors + magnetic_field)
            if delta_E < 0 or np.random.rand() < np.exp(-delta_E / temperature):
                lattice[i, j] = -spin

        if step % frame_capture_rate == 0:
            frames.append(lattice.copy().tolist())
            energies.append(calculate_total_energy(lattice, coupling_strength, magnetic_field))
            average_spin.append(np.mean(lattice))

    return frames, energies, average_spin

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    temperature = data['temperature']
    lattice_size = data['latticeSize']
    coupling_strength = data['couplingStrength']
    magnetic_field = data['magneticField']
    steps = data['steps']
    frame_capture_rate = data.get('frameCaptureRate', 2)

    frames, energies, average_spin = ising_model_simulation(temperature, lattice_size, coupling_strength, magnetic_field, steps, frame_capture_rate)
    return jsonify({"frames": frames, "energies": energies, "average_spin":average_spin})

if __name__ == '__main__':
    app.run(port=5100,debug=True)
