"""
Main tracker module that wraps CodeCarbon functionality
"""
from codecarbon import OfflineEmissionsTracker
import os
from pathlib import Path
import getpass
import platform

class EnergyTracker:
    """A wrapper class for CodeCarbon's EmissionsTracker with simplified interface"""
    
    def __init__(self, project_name="default", output_dir=None):
        """
        Initialize the energy tracker
        
        Args:
            project_name (str, optional): Name of the project being tracked
            output_dir (str, optional): Directory to save the CodeCarbon logs
        """
        if output_dir is None:
            output_dir = os.path.join(Path.home(), '.let')
        os.makedirs(output_dir, exist_ok=True)
        current_user = getpass.getuser()
        hostname = platform.node()
        experiment_id = f"{project_name}___{current_user}___{hostname}"
        self.tracker = OfflineEmissionsTracker(
            experiment_id=experiment_id, output_dir=output_dir, log_level='error'
        )
        
    def __enter__(self):
        """Start tracking when used as a context manager"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracking when exiting the context manager"""
        self.stop()
        
    def start(self):
        """Start tracking energy consumption"""
        self.tracker.start()
        
    def stop(self, print_summary=True):
        """Stop tracking and return the total energy consumed in kWh"""
        result = self.tracker.stop()

        if print_summary:
            with open(os.path.join(self.tracker._output_dir, self.tracker._output_file), 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_line = lines[-1]
                    print("Energy Consumption Summary:")
                    print(last_line.strip())

        return result
