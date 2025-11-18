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

def print_paper_statement(output_dir, project_name = None, user = None, hostname = None):
    """Prints a summary of all stored results"""
    results = load_results(output_dir, project_name, user, hostname)
    cc, hw, em, en, rate = format_summary(results)
    print(f"Using {cc}, the energy consumption of running all experiments on an {hw} is estimated to {en}. This corresponds to estimated carbon emissions of {em} of CO2-equivalents, assuming a carbon intensity of {rate}" + r"~\cite{lamarr_energy_tracker,codecarbon}. Note that these numbers are underestimations of actual resource consumption and do not account for overhead factors or embodied impact~\cite{ai_energy_validation}.")
    
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run foo.bar")

    parser.add_argument(
        "--output_dir",
        type=str,
        default=os.path.join(Path.home(), ".let"),
        help="Path to the output directory (default: ~/.let)"
    )
    parser.add_argument(
        "--project_name",
        type=str,
        default=None,
        help="Name of the project"
    )
    parser.add_argument(
        "--user",
        type=str,
        default=None,
        help="User name"
    )
    parser.add_argument(
        "--hostname",
        type=str,
        default=None,
        help="Hostname"
    )

    args = parser.parse_args()
    print_paper_statement(args.output_dir, args.project_name, args.user, args.hostname)