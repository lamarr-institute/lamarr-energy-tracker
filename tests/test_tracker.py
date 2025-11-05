"""Unit tests for the EnergyTracker class"""
import os
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import socket
import getpass
from lamarr_energy_tracker import EnergyTracker

class TestEnergyTracker(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for test outputs"""
        self.temp_dir = tempfile.mkdtemp()
        self.default_project = "test_project"

    def tearDown(self):
        """Clean up temporary files"""
        for file in Path(self.temp_dir).glob("*.csv"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_creates_emissions_csv(self):
        """Test if emissions.csv is created in the specified directory"""
        with EnergyTracker(project_name=self.default_project, output_dir=self.temp_dir):
            pass  # Just testing the file creation
        
        emissions_file = Path(self.temp_dir) / "emissions.csv"
        self.assertTrue(emissions_file.exists(), "emissions.csv was not created")
        
        # Check if the file is a valid CSV with data
        df = pd.read_csv(emissions_file)
        self.assertGreater(len(df), 0, "emissions.csv is empty")

    def test_experiment_id_format(self):
        """Test if experiment_id follows the correct format"""
        with EnergyTracker(project_name=self.default_project, output_dir=self.temp_dir):
            pass

        emissions_file = Path(self.temp_dir) / "emissions.csv"
        df = pd.read_csv(emissions_file)
        
        # Get the expected experiment_id components
        expected_user = getpass.getuser()
        expected_host = socket.gethostname()
        
        # Check if experiment_id contains all components
        experiment_id = df['experiment_id'].iloc[0]
        self.assertIn(expected_user, experiment_id, "User not found in experiment_id")
        self.assertIn(expected_host, experiment_id, "Hostname not found in experiment_id")
        self.assertIn(self.default_project, experiment_id, "Project name not found in experiment_id")

    def test_custom_output_path(self):
        """Test if custom output path works correctly"""
        custom_dir = Path(self.temp_dir) / "custom_output"
        custom_dir.mkdir()
        
        with EnergyTracker(project_name=self.default_project, output_dir=str(custom_dir)):
            pass
        
        emissions_file = custom_dir / "emissions.csv"
        self.assertTrue(emissions_file.exists(), "emissions.csv not created in custom directory")

    def test_stop_return_format(self):
        """Test if stop() returns properly formatted emissions data"""
        tracker = EnergyTracker(project_name=self.default_project, output_dir=self.temp_dir)
        tracker.start()
        # Do some computation to ensure measurable energy consumption
        _ = [i**2 for i in range(10000)]
        emissions = tracker.stop()
        
        # Check if emissions is a float
        self.assertIsInstance(emissions, float, "Emissions should be a float")
        # Check if emissions is non-negative
        self.assertGreaterEqual(emissions, 0, "Emissions should be non-negative")

if __name__ == '__main__':
    unittest.main()