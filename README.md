# LET - Lamarr Energy Tracker
<div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
  <div>
    <img src="logo.png" alt="Lamarr Energy Tracker logo" style="width:100px; height:auto; display:block;" />
  </div>
  <div style="flex:1; min-width:240px;">
A simple wrapper around <a href="https://mlco2.github.io/codecarbon/motivation.html">CodeCarbon</a> for tracking and reporting local energy consumption from Python.
  </div>
</div>

## Features
- 🧩 Simple extension to CodeCarbon software
- 👨‍💻 Three lines of code to report on environmental impacts of your research experiments
- 💚 Help to make Lamarr Institute more resource-aware

## Installation

As a Python library, you can simply install it by running

```bash
pip install lamarr-energy-tracker
```

## Usage

LET should only be used for local setups without available energy monitoring.
If you use the [Lamarr Cluster](https://gitlab.tu-dortmund.de/lamarr/lamarr-public/cluster), your resource consumption will be automatically tracked soon, so you do not need to run LET.
The following gives an idea of how LET can be included in your Python code:


```python
from lamarr_energy_tracker import EnergyTracker

# Either use as a context manager
with EnergyTracker(project_name="your_research_project") as tracker:
    # Your resource-heavy code here
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

While the tracker assumes code is executed in Germany, you can also provide a different `country_iso_code` to change the [carbon intensity constant](https://github.com/mlco2/codecarbon/blob/master/codecarbon/data/private_infra/global_energy_mix.json).
For more information on the methodology behind the tracker, please refer to the [CodeCarbon documentation](https://mlco2.github.io/codecarbon/motivation.html).

## Collaborate
In order to become truly resource-aware, we hope to assemble impact reports about the resource consumption of research projects being conducted at Lamarr Institute.
Please send your `emissions.csv` files to [sebastian.buschjaeger@tu-dortmund.de](sebastian.buschjaeger@tu-dortmund.de), such that we can include your experiments in our reports.
Feel free to add additional information, such as a description of the project and a link to the paper or associated code repository. 

## Citing
If you use this tool to report your energy consumption, please cite the following literature:

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