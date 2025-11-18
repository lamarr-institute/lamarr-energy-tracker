# Lamarr Energy Tracker

A simple wrapper around [CodeCarbon](https://mlco2.github.io/codecarbon/motivation.html) for tracking and reporting energy consumption from Python.

## Features

- 🧩 Simple extension to CodeCarbon
- 👨‍💻 Only three lines of code to report on environmental impacts of your research
- 💚 Help to make Lamarr Institute more resource-aware

## Installation

```bash
pip install lamarr-energy-tracker
```

## Usage

```python
from lamarr_energy_tracker import EnergyTracker

# Either use as a context manager
with EnergyTracker(project_name="your_research_project") as tracker:
    # Your code here
    pass

# Or manually
tracker = EnergyTracker(project_name="your_research_project")
tracker.start()
# Your resource-heavy code here
tracker.stop()
```

Once the tracker is stopped, it will print the energy consumption of your executed experiment as well as a summary statement that you can copy to your paper, describing the environmental impact of all your performed experiments for this project and hardware, for example:
```
Using CodeCarbon 3.0.8, the energy consumption of running all experiments on an Intel(R) Core(TM) i7-10610U CPU is estimated to 0.135 kWh.
This corresponds to estimated carbon emissions of 0.051 kg of CO2-equivalents, assuming a carbon intensity of 380 gCO2/kWh~\cite{lamarr_energy_tracker,codecarbon}.
Note that these numbers are underestimations of actual resource consumption and do not account for overhead factors or embodied impact~\cite{ai_energy_validation}.
```

Per default, the tracker stores data about tracked resource consumption in a central `emissions.csv` file, located in `~/.let/`. You can also provide a different `output_dir` or access the tracking results as follows (use arguments to only investigate specific projects):
```python
from lamarr_energy_tracker import load_summary, print_paper_statement, delete_results

# access a pandas dataframe with all tracked resource data
df = load_results()
# print the summary of all tracked resource data
print_paper_statement()
# delete the centrally stored resource data
delete_results()
```

You can also print the statement directly from the terminal:
```python
python -m lamarr_energy_tracker.print_paper_statement # Default arguments

python -m lamarr_energy_tracker.print_paper_statement --output_dir DIR --project_name NAME --hostname HOST # For additional filtering
```

While the tracker assumes deployment in Germany, you can also provide a different `country_iso_code` to change the [carbon intensity constant](https://github.com/mlco2/codecarbon/blob/master/codecarbon/data/private_infra/global_energy_mix.json).
For more information on the methodology behind the resource tracking, please refer to the [CodeCarbon documentation](https://mlco2.github.io/codecarbon/motivation.html).

## Collaborate
In order to become truly resource-aware, we hope to assemble impact reports about the resource consumption of research projects being conducted at Lamarr Institute.
Please send your `emissions.csv` files to [sebastian.buschjaeger@tu-dortmund.de](sebastian.buschjaeger@tu-dortmund.de), such that we can include your experiments in our reports.
Feel free to add additional information, such as a description of the project and a link to the paper or associated code repository. 

## Citing
If you use this tool to report your energy consumption, please cite the following literature, for example using the following bibtex entries:

```bibtex
@software{lamarr_energy_tracker,
  author = {Buschjäger, Sebastian and Fischer, Raphael},
  title  = {{Lamarr} {Energy} {Tracker}},
  year   = {2025},
  url    = {https://github.com/lamarr-institute/lamarr-energy-tracker},
}
```

```bibtex
@software{codecarbon,
  author    = {Courty, Benoît and
               Schmidt, Victor and
               Kamal, Goyal and
               others},
  title     = {mlco2/codecarbon: v3.0.8},
  year      = 2025,
  publisher = {Zenodo},
  version   = {v3.0.8},
  doi       = {10.5281/zenodo.17477894},
  url       = {https://doi.org/10.5281/zenodo.17477894},
}
```

```bibtex
@misc{ai_energy_validation,
  title  = {Ground-Truthing {AI} Energy Consumption: {Validating} {CodeCarbon} Against External Measurements}, 
  author = {Raphael Fischer},
  year   = {2025},
  doi    = {10.48550/arXiv.2509.22092},
  url    = {https://arxiv.org/abs/2509.22092}, 
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Copyright (c) Resource-Aware ML Research Team @ Lamarr Institute