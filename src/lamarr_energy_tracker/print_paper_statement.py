import argparse
import os
from pathlib import Path
import pandas as pd

def load_results(output_dir = os.path.join(Path.home(), '.let'), project_name = None, user = None, hostname = None):
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

def print_paper_statement(output_dir, project_name=None, user=None, hostname=None):
    """Prints a summary of all stored results"""
    results = load_results(output_dir, project_name, user, hostname)
    cc, hw, en, rate = format_summary(results)
    energy, energy_unit = en.split(" ")
    print_custom_paper_statement(cc, hw, float(energy), energy_unit, rate)

def print_custom_paper_statement(methodology, hardware, consumed_energy, energy_unit="kWh", carbon_intensity=380):
    emissions = carbon_intensity * consumed_energy
    if energy_unit == "Wh":
        emissions = emissions / 1000  # convert Wh to kWh
    if emissions >= 10:
        emissions = emissions / 1000
        emissions_unit = "kgCO2-equivalents"
    else:
        emissions_unit = "gCO2-equivalents"
    output = f"Using {methodology}, the energy consumption of running all experiments on an {hardware} is estimated to {consumed_energy:5.3f} {energy_unit}." \
          + f"This corresponds to estimated carbon emissions of {emissions:5.3f} {emissions_unit}, assuming a carbon intensity of {carbon_intensity} gCO2/kWh" \
          + r"~\cite{lamarr_energy_tracker,codecarbon}. Note that these numbers are underestimations of actual resource consumption and do not account for overhead factors or embodied impacts~\cite{ai_energy_validation}."
    print("\n" + output + "\n")
    return output
    
def format_summary(results):
    cc = f"CodeCarbon {results['codecarbon_version'].iloc[0]}"
    # get hardware info
    assert pd.unique(results['cpu_model']).size == 1, "Multiple CPU models found in results"
    assert pd.unique(results['gpu_model']).size == 1, "Multiple GPU models found in results"
    hw = results['cpu_model'].iloc[0].split(' @ ')[0]
    if not pd.isna(results['gpu_model'].iloc[0]):
        hw = hw + f" and {results['gpu_model'].iloc[0]}"
    # get emissions and energy
    en = f"{results['energy_consumed'].sum():5.3f} kWh" if results['energy_consumed'].sum() > 0.1 else f"{results['energy_consumed'].sum()*1000:5.3f} Wh"
    rate = int(results['emissions'].sum()/results['energy_consumed'].sum()*1000) # gCO2/kWh
    return cc, hw, en, rate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print a paper statement summarizing energy and carbon emissions of tracked experiments. You can either use logs from the tracker, or provide custom information (pass values for methodology, hardware, and energy).")

    parser.add_argument("--output_dir", type=str, default=os.path.join(Path.home(), ".let"), help="Path to the output directory (default: ~/.let)")
    parser.add_argument("--project_name", type=str, default=None, help="Name of the project")
    parser.add_argument("--user", type=str, default=None, help="User name")
    parser.add_argument("--hostname", type=str, default=None, help="Hostname")
    parser.add_argument("--methodology", type=str, default=None, help="Methodology for energy estimation (e.g., CodeCarbon 3.0.8 or ML Impact Calculator)")
    parser.add_argument("--hardware", type=str, default=None, help="Information on experiment hardware (e.g., CPU or GPU type)")
    parser.add_argument("--consumed_energy", type=float, default=None, help="Information on consumed energy (in kWh)")
    parser.add_argument("--carbon_intensity", type=int, default=380, help="Information on carbon intensity (in gCO2/kWh)")

    args = parser.parse_args()
    if args.methodology is not None and args.hardware is not None and args.consumed_energy is not None:
        print_custom_paper_statement(args.methodology, args.hardware, args.consumed_energy, carbon_intensity=args.carbon_intensity)
    else:
        print_paper_statement(args.output_dir, args.project_name, args.user, args.hostname)