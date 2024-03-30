document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('simulationForm');
    const resultContainer = document.getElementById('result');
    const slider = document.getElementById('frame-slider');
    const frameNumberDisplay = document.getElementById('frame-number');
    const totalFramesDisplay = document.getElementById('total-frames');
    

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Reset UI elements for a new simulation
        resultContainer.innerHTML = 'Running simulation...';
        slider.value = 0; // Reset the slider
        frameNumberDisplay.textContent = '0'; // Reset the frame number display
        totalFramesDisplay.textContent = ''; // Clear total frames until new data is loaded

        const postData = {
            temperature: parseFloat(document.getElementById('temperature').value),
            latticeSize: parseInt(document.getElementById('latticeSize').value, 10),
            couplingStrength: parseFloat(document.getElementById('couplingStrength').value),
            magneticField: parseFloat(document.getElementById('magneticField').value),
            steps: parseInt(document.getElementById('steps').value, 10)
        };

        fetch('http://localhost:5100/simulate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(postData),
        })
        .then(response => response.json())
        .then(data => {
            const { frames, energies } = data;
            Plotly.purge('result'); // Clear any existing plots
            resultContainer.innerHTML = ''; // Clear the "Running simulation..." message
            slider.max = frames.length - 1; // Update slider range based on new data
            totalFramesDisplay.textContent = frames.length-1; // Display total frames for new simulation
            updatePlot(frames[0]); // Display the first frame of the new simulation
            
            slider.oninput = function() {
                const frameIndex = parseInt(this.value);
                frameNumberDisplay.textContent = frameIndex;
                updatePlot(frames[frameIndex]);
            };
            plotEnergyData(energies);
        })
        .catch(error => {
            console.error('Error:', error);
            resultContainer.innerHTML = `Error running simulation: ${error.message}`;
        });
    });

    function updatePlot(frameData) {
        Plotly.react('result', [{
            z: frameData,
            type: 'heatmap',
            colorscale: 'Viridis',
            showscale: false
        }], {
            title: 'Ising Model Simulation'
        });
    }

    function plotEnergyData(energies) {
        const steps = Array.from({ length: energies.length }, (_, i) => i + 1); // Create an array [1, 2, ..., N]
        const energyTrace = {
            x: steps,
            y: energies,
            mode: 'lines+markers',
            name: 'Total Energy',
            marker: { color: 'blue' }
        };

        const layout = {
            title: 'Total Energy per Step',
            xaxis: { title: 'Step' },
            yaxis: { title: 'Total Energy' }
        };

        Plotly.newPlot('energy-plot', [energyTrace], layout);
    }
});
