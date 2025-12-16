import argparse
import os
from pathlib import Path
import random
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

COMPARISONS = {
    "text_message": {
        "reference_g": 0.014,
        "unit": "text messages",
    },
    "web_search": {
        "reference_g": 0.5,   # midpoint of 0.2–0.7
        "unit": "web searches",
    },
    "spam_email": {
        "reference_g": 0.3,
        "unit": "spam emails",
    },
    "email": {
        "reference_g": 4,
        "unit": "proper emails",
    },
    "apple": {
        "reference_g": 10,
        "unit": "locally grown apples",
    },
    "plastic_bag": {
        "reference_g": 10,
        "unit": "plastic carrier bags",
    },
    "boil_water": {
        "reference_g": 70,
        "unit": "times boiling a quart of water",
    },
    "banana": {
        "reference_g": 80,
        "unit": "imported bananas",
    },
    "tv_hour": {
        "reference_g": 100,
        "unit": "hours of watching TV",
    },
    "shower_6min": {
        "reference_g": 550,
        "unit": "a 6-minute electrically powered shower",
    },
    "beer_pint": {
        "reference_g": 500,
        "unit": "pints of beer at a pub",
    },
    "toilet_paper": {
        "reference_g": 450,
        "unit": "rolls of recycled toilet paper",
    },
    "paperback_book": {
        "reference_g": 1000,
        "unit": "paperback books",
    },
    "newspaper": {
        "reference_g": 400,
        "unit": "weekday newspapers",
    },
    "bath_gas": {
        "reference_g": 1100,
        "unit": "warm baths (gas-heated)",
    },
    "pants_jeans": {
        "reference_g": 6000,
        "unit": "pairs of cotton jeans",
    },
    "shoes_leather": {
        "reference_g": 15000,
        "unit": "pairs of leather shoes",
    },
    "train_trip": {
        "reference_g": 120_000,
        "unit": "train trips from NYC to Niagara Falls and back",
    },
    "flight_europe": {
        "reference_g": 3_400_000,
        "unit": "return economy flights from Los Angeles to Barcelona",
    },
    "new_car": {
        "reference_g": 17_000_000,
        "unit": "new mid-size cars",
    },
}

def emission_comparisons(
    emissions_g,
    tolerance=(0.2, 10.0), # 1/5x to 10x higher
    max_results=1,
):
    def format_factor(f):
        if 0.8 <= f <= 1.25:
            return "equivalent to 1"
        elif f > 1:
            return f"equivalent to {f:.1f}"
        else:
            return f"equivalent to {1/f:.1f}"
    
    rendered = []

    for entry in COMPARISONS.values():
        ref = entry["reference_g"]
        units = entry["unit"]

        factor = emissions_g / ref

        if not (tolerance[0] <= factor <= tolerance[1]):
            continue

        relation = format_factor(factor)
        amount = emissions_g / ref

        rendered.append(
            f"{relation} {units}"
        )

    if not rendered:
        return None

    return random.sample(rendered, k=min(len(rendered), max_results))

def print_custom_paper_statement(methodology, hardware, consumed_energy, energy_unit="kWh", carbon_intensity=380):
    emissions = carbon_intensity * consumed_energy
    comps = emission_comparisons(emissions)
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
    
    if comps:
        output += f"\n\nFor comparison, this is {comps[0]}. Comparisons are based on ``How bad are bananas? The Carbon Footprint of everything'' by Mike Berners-Lee. Greystone Books 2011.\n" 
    
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