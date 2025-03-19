# CGE

This repository contains a computational general equilibrium (CGE) model for policy analysis. The model based off of the simplest CGE model presented [Hosoe, Gawana, and Hashimoto (2010)](https://www.amazon.com/Textbook-Computable-General-Equilibrium-Modeling/dp/0230248144) and the source code is written in Python.

## Installing and Running CGE from this GitHub repository

* Install the [Anaconda distribution](https://www.anaconda.com/distribution/) of Python
* Clone this repository to a directory on your computer
* From the terminal (or Conda command prompt), navigate to the directory to which you cloned this repository and run `conda env create -f environment.yml`
* Then, `conda activate cge_env`
* Then install by `pip install -e .`
* Navigate to `./open_cge`
* Run the model with an example calibration by typing `python execute.py`

## Working with existing environment

* `$cd C:\Users\D.Zhussupova\Documents\zhus_dika\CGE_projects\CGE`

* `$conda activate cge_env`

* `$cd .\open_cge\`

* `$python .\execute.py`
