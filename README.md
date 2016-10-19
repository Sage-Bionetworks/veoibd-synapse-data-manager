veoibd-synapse-data-manager
==============================

Admin related logistics regarding uploading and annotating data to Synapse for members of the VEOIBD consortium.

# Getting Started

## Registering with [Synapse](https://www.synapse.org/)

1. Create an account at [Synapse](https://www.synapse.org/)
2. You will need to register and become a [certified user](http://docs.synapse.org/articles/getting_started.html#becoming-a-certified-user).

## Installing

Download this project repository:

Using git...

```
git clone https://github.com/ScottSnapperLab/veoibd-synapse-data-manager.git
```

Using your web browser...

1. Click [here](https://github.com/ScottSnapperLab/veoibd-synapse-data-manager/releases) to see a list of releases.
2. Download and unzip.
3. Navigate into the project folder.

## Configuring

The `configs` folder contains an example configuration file. Copy this example file. Modify the values to fit your site's information.

## Running commands

Still to come...

Project Organization
------------
```
├── configs
├── data
│   ├── external           <- Data from third party sources
│   ├── interim            <- Intermediate data that has been transformed.
│   ├── processed          <- The final, canonical data sets for modeling.
│   └── raw                <- The original, immutable data dump.
├── docs                   <- A default Sphinx project; see sphinx-doc.org for details
├── github                 <- Contains a script for creating and pushing to github
├── LICENSE
├── Makefile               <- Makefile with commands to provision a Conda environment and register
│                             the environment's kernel with Jupyter
├── models                 <- Trained and serialized models, model predictions, or model summaries
├── notebooks              <- Jupyter notebooks. Naming convention is a date and title
│                             (`2016-07-28__initial_exploration.ipynb`)
├── README.md              <- The top-level README for developers using this project.
├── references             <- Data dictionaries, manuals, and all other explanatory materials.
├── reports                <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures            <- Generated graphics and figures to be used in reporting
├── requirements.txt       <- The requirements file for reproducing the analysis environment.
├── setup.py               <- Allows installing this project's python code for Notebook importation
├── Snakefile              <- Snakemake file for reproducing a full pipeline
├── src                    <- Source code for use in this project.
│   ├── python
│   │   ├── data           <- Code to download or generate data
│   │   ├── features       <- Code to turn raw data into features for modeling
│   │   ├── models         <- Code to train models and then use trained models to make
│   │   ├── rules          <- Scripts meant to be plugged in as Snakemake Rules
│   │   └── visualization  <- Code to create exploratory and results oriented visualizations
│   └── R
│       └── rules          <- Scripts meant to be plugged in as Snakemake Rules
└── tox.ini
```
