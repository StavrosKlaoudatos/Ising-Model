from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def ising_model_simulation(temperature, lattice_size, coupling_strength, magnetic_field, steps, frame_capture_rate=10):
    """
    Simulate the Ising model and capture the state of the lattice at intervals specified by frame_capture_rate.
    """
    lattice = np.random.choice([-1, 1], size=(lattice_size, lattice_size))
    frames = []  # To store captured frames

    for step in range(steps):
        # Simulation logic
        for _ in range(lattice_size * lattice_size):
            i, j = np.random.randint(0, lattice_size, size=2)
            spin = lattice[i, j]
            sum_neighbors = (
                lattice[(i + 1) % lattice_size, j] +
                lattice[(i - 1) % lattice_size, j] +
                lattice[i, (j + 1) % lattice_size] +
                lattice[i, (j - 1) % lattice_size]
            )
            delta_E = 2 * spin * (coupling_strength * sum_neighbors + magnetic_field)
            if delta_E < 0 or np.random.rand() < np.exp(-delta_E / temperature):
                lattice[i, j] = -spin

        # Capture frame
        if step % frame_capture_rate == 0:
            frames.append(lattice.copy().tolist())  # Append a copy of the current lattice state

    return frames

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    temperature = data['temperature']
    lattice_size = data['latticeSize']
    coupling_strength = data['couplingStrength']
    magnetic_field = data['magneticField']
    steps = data['steps']
    frame_capture_rate = data.get('frameCaptureRate', 2)  # Optional: Allow specifying capture rate

    frames = ising_model_simulation(temperature, lattice_size, coupling_strength, magnetic_field, steps, frame_capture_rate)
    return jsonify(frames)

if __name__ == '__main__':
    app.run(port=5100,debug=True)
