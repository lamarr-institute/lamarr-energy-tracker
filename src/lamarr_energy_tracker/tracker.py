"""
Main tracker module that wraps CodeCarbon functionality
"""
from codecarbon import EmissionsTracker

class EnergyTracker:
    """A wrapper class for CodeCarbon's EmissionsTracker with simplified interface"""
    
    def __init__(self, project_name=None, output_dir=None):
        """
        Initialize the energy tracker
        
        Args:
            project_name (str, optional): Name of the project being tracked
            output_dir (str, optional): Directory to save the emissions data
        """
        self.tracker = EmissionsTracker(
            project_name=project_name,
            output_dir=output_dir
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
        
    def stop(self):
        """Stop tracking and return the total energy consumed in kWh"""
        return self.tracker.stop()
        
    @property
    def emissions(self):
        """Get the current CO2 emissions in kg"""
        return self.tracker.emissions