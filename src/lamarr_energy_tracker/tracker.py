"""
Main tracker module that wraps CodeCarbon functionality
"""
import os
from pathlib import Path
import getpass
import platform

from codecarbon import OfflineEmissionsTracker
import pandas as pd


def load_results(output_dir=None, project_name=None, user=None, hostname=None):
    """Retrieves a summary of all stored results"""
    if output_dir is None:
        output_dir = os.path.join(Path.home(), '.let')
    results = pd.read_csv(os.path.join(output_dir, 'emissions.csv'))
    # map project_name, user and hostname to individual columns
    for idx, field in enumerate(['project_name', 'user', 'hostname']):
        results[field] = results['experiment_id'].apply(lambda x: x.split('___')[idx])
    if project_name is not None:
        results = results[results['project_name'] == project_name]
    if user is not None:
        results = results[results['user'] == user]
    if hostname is not None:
        results = results[results['hostname'] == hostname]
    return results


def print_paper_statement(output_dir=None, project_name=None, user=None, hostname=None):
    """Prints a summary of all stored results"""
    results = load_results(output_dir, project_name, user, hostname)
    cc, hw, em, en, rate = format_summary(results)
    print(f"Using {cc}, the energy consumption of running all experiments on an {hw} is estimated to {en}. This corresponds to estimated carbon emissions of {em} of CO2-equivalents, assuming a carbon intensity of {rate}" + r"~\cite{lamarr_energy_tracker,codecarbon}.")
    
    
def format_summary(results):
    cc = f"CodeCarbon {results['codecarbon_version'].iloc[0]}"
    # get hardware info
    assert pd.unique(results['cpu_model']).size == 1, "Multiple CPU models found in results"
    assert pd.unique(results['gpu_model']).size == 1, "Multiple GPU models found in results"
    hw = results['cpu_model'].iloc[0].split(' @ ')[0]
    if not pd.isna(results['gpu_model'].iloc[0]):
        hw = hw + f" and {results['gpu_model'].iloc[0]}"
    # get emissions and energy
    em = f"{results['emissions'].sum():5.3f} kg" if results['emissions'].sum() > 0.1 else f"{results['emissions'].sum()*1000:5.3f} g"
    en = f"{results['energy_consumed'].sum():5.3f} kWh" if results['energy_consumed'].sum() > 0.1 else f"{results['energy_consumed'].sum()*1000:5.3f} Wh"
    rate = f"{int(results['emissions'].sum()/results['energy_consumed'].sum()*1000)} gCO2/kWh"
    return cc, hw, em, en, rate


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
        self.tracker = OfflineEmissionsTracker(
            experiment_id=experiment_id, output_dir=output_dir, country_iso_code=country_iso_code, log_level='error'
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