"""Unit tests for the EnergyTracker class"""
import os
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import socket
import getpass
from io import StringIO
import sys
from lamarr_energy_tracker import EnergyTracker
from lamarr_energy_tracker.print_paper_statement import print_custom_paper_statement

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
        proj, user, host = experiment_id.split("___")
        self.assertEqual(expected_user, user, "User not found in experiment_id")
        self.assertEqual(expected_host, host, "Hostname not found in experiment_id")
        self.assertEqual(self.default_project, proj, "Project name not found in experiment_id")

    def test_custom_output_path(self):
        """Test if custom output path works correctly"""
        custom_dir = Path(self.temp_dir) / "custom_output"
        custom_dir.mkdir()
        
        with EnergyTracker(project_name=self.default_project, output_dir=str(custom_dir)):
            pass
        
        emissions_file = custom_dir / "emissions.csv"
        self.assertTrue(emissions_file.exists(), "emissions.csv not created in custom directory")
        os.remove(emissions_file)
        os.rmdir(custom_dir)

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


class TestPaperStatementOutput(unittest.TestCase):
    """Test cases for print_custom_paper_statement output formatting"""
    
    def _capture_statement_output(self, methodology, hardware, consumed_energy, energy_unit="kWh", carbon_intensity=380):
        """Helper method to capture print output"""
        captured_output = StringIO()
        sys.stdout = captured_output
        try:
            print_custom_paper_statement(methodology, hardware, consumed_energy, energy_unit, carbon_intensity)
            sys.stdout = sys.__stdout__
            return captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__
    
    def test_statement_output_contains_information(self):
        """Test that output contains the information provided"""
        methodology, hardware, energy = "CO2 Impact Calculator", "NVIDIA GTX 1080 GPU", 0.15
        output = self._capture_statement_output(methodology, hardware, energy)
        for info in [methodology, hardware, f"{energy:5.3f}"]:
            self.assertIn(info, output, f"{info} not found in output")
    
    def test_statement_output_small_emissions_in_g(self):
        """Test that small emissions are displayed in gCO2-equivalents"""
        output = self._capture_statement_output("CodeCarbon 3.0.8", "Intel CPU", 0.05, "Wh")
        self.assertNotIn(" kWh", output, "Default energy unit should not be included")
        self.assertIn("Wh", output, "Custom energy unit should be included")
        self.assertIn("gCO2-equivalents", output, "Small emissions should be in gCO2-equivalents")
    
    def test_statement_output_contains_carbon_intensity(self):
        """Test that carbon intensity is included in output"""
        carbon_intensity = 450
        output = self._capture_statement_output("CodeCarbon 3.0.8", "Intel CPU", 0.1, carbon_intensity=carbon_intensity)
        self.assertIn("450", output, "Carbon intensity not found in output")
        self.assertIn("gCO2/kWh", output, "Carbon intensity unit not found")
    
    def test_statement_output_contains_citations(self):
        """Test that output contains proper citation markers"""
        output = self._capture_statement_output("CodeCarbon 3.0.8", "Intel CPU", 0.05)
        self.assertIn(r"\cite{lamarr_energy_tracker,codecarbon}", output, "Missing LaTeX citation for lamarr_energy_tracker and codecarbon")
        self.assertIn(r"\cite{ai_energy_validation}", output, "Missing LaTeX citation for ai_energy_validation")

if __name__ == '__main__':
    unittest.main()