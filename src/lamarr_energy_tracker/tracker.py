"""
Main tracker module that wraps CodeCarbon functionality
"""
import logging
import os
from pathlib import Path
import getpass
import platform

from codecarbon import OfflineEmissionsTracker
from codecarbon.external.logger import set_logger_level
import pandas as pd

from lamarr_energy_tracker.print_paper_statement import format_summary, load_results, print_paper_statement

def delete_results(output_dir=None):
    os.remove(os.path.join(output_dir, 'emissions.csv'))

class EnergyTracker:
    """A wrapper class for CodeCarbon's EmissionsTracker with simplified interface"""
    
    def __init__(self, project_name="default", country_iso_code="DEU", output_dir=None):
        """
        Initialize the energy tracker
        
        Args:
            project_name (str, optional): Name of the project being tracked
            output_dir (str, optional): Directory to save the CodeCarbon logs
        """
        self.project_name = project_name
        if output_dir is None:
            output_dir = os.path.join(Path.home(), '.let')
        os.makedirs(output_dir, exist_ok=True)
        self.user = getpass.getuser()
        self.hostname = platform.node()
        experiment_id = f"{self.project_name}___{self.user}___{self.hostname}"

        # Set the log_level here already otherwise we get stuff like 
        # [codecarbon INFO @ 12:21:08] offline tracker init
        # [codecarbon WARNING @ 12:21:08] Multiple instances of codecarbon are allowed to run at the same time.
        set_logger_level(level="error")

        # Additional, set the log_level=error here as well, otherwise this 
        # instances overrides our previous level with "" (aka level="info")
        self.tracker = OfflineEmissionsTracker(
            experiment_id=experiment_id, output_dir=output_dir, country_iso_code=country_iso_code, log_level="error"
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
        self.tracker.stop()
        result = self.last_result

        if print_summary:
            _, _, _, en, _ = format_summary(pd.DataFrame([result]))
            print(f"\nTracker stopped - this experiment consumed {en}.\n")
            print_paper_statement(output_dir=self.tracker._output_dir, project_name=self.project_name, user=self.user, hostname=self.hostname)
        return result['energy_consumed']
    
    @property
    def results(self):
        """Get all stored results"""
        results = load_results(output_dir=self.tracker._output_dir, project_name=self.project_name, user=self.user, hostname=self.hostname)
        return results
    
    @property
    def last_result(self):
        """Get the last stored result"""
        result = self.results.iloc[-1]
        return result

if __name__ == "__main__":
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    
    # Example usage with context manager
    with EnergyTracker(project_name="example_project", output_dir=temp_dir) as tracker:
        # Simulate some computation
        total = sum(i * i for i in range(10000))

    # Example usage with explicit start/stop
    tracker = EnergyTracker(project_name="example_project_explicit", output_dir=temp_dir)
    tracker.start()
    total = sum(i * i for i in range(10000))
    # Simulate some computation
    energy_used = tracker.stop()
    print(f"Energy consumed (explicit): {energy_used} kWh")

    shutil.rmtree(temp_dir)