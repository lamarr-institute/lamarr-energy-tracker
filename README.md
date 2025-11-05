# Lamarr Energy Tracker

A simple wrapper around CodeCarbon for tracking and reporting energy consumption from Python.

## Installation

```bash
pip install lamarr-energy-tracker
```

## Usage

```python
from lamarr_energy_tracker import EnergyTracker

# Using as a context manager
with EnergyTracker(project_name="my_project") as tracker:
    # Your code here
    pass

# Or manually
tracker = EnergyTracker(project_name="my_project")
tracker.start()
# Your code here
emissions = tracker.stop()
print(f"CO2 emissions: {emissions} kg")
```

## Features

- Simple interface to CodeCarbon
- Context manager support
- Easy access to emissions data
- Automatic tracking and reporting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Copyright (c) Resource-Aware ML Research Team @ Lamarr Institute