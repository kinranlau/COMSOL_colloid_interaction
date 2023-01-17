# COMSOL simulation of colloidal interactions

See the original paper: 

*A Multi-Parameter Study of the Colloidal Interaction between Au and TiO<sub>2</sub>: The Role of Surface Potential, Concentration and Defects*

<br></br>
**There are 2 main components in this repository:**
1. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kinranlau/COMSOL_colloid_interaction/blob/main/SVM_prediction/%5BGUI%5D_Predict_colloid_interaction_SVM.ipynb) A **SVM model** for predicting whether a particular interaction is favorable, available with GUI in a Google Colab notebook
2. [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kinranlau/COMSOL_colloid_interaction/HEAD?urlpath=%2Fproxy%2F5006%2Fbokeh-app) An **interactive energy plot** for exploring the simulated data, visualized by Bokeh and hosted on Binder
---

## SVM for predicting the interaction outcome [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kinranlau/COMSOL_colloid_interaction/blob/main/SVM_prediction/%5BGUI%5D_Predict_colloid_interaction_SVM.ipynb)
- The model considers the interaction between a negative particle (e.g. Au) and a negative surface with positive defects (e.g. TiO<sub>2</sub>) in water

- Given a particular combination of these 7 parameters, the model will predict whether this interaction is favorable or not
  - $V_{Part}:$ Particle potential
  - $V_{Surf}:$ Surface potential
  - $V_{Def}:$ Defect potential
  - $DD:$ Defect density
  - $Conc:$ Concentration
  - $R:$ Particle radius
  - $A_H:$ Hamaker constant

- The data used for training the SVM is available at `/SVM_prediction/results_varyvdw_SVM.csv`


## Interactive visualization of the energy plots [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kinranlau/COMSOL_colloid_interaction/HEAD?urlpath=%2Fproxy%2F5006%2Fbokeh-app)
- A total of 5040 conditions were simulated by varying $V_{Part}$, $V_{Surf}$, $V_{Def}$, $DD$, $Conc$, $R$
- The van der Waals contribution can also be varied by changing $A_H$
- Upon a change in the parameters, the corresponding energy curves will be updated interactively
- The raw data can be found in `/bokeh-app/results.csv` and the headers in `/bokeh-app/headers.py`
- Apart from running it on Binder, the visualization can also be run locally by cloning this repository, navigating into the directory `/bokeh-app/` which is where the Bokeh server file `main.py` is located
- The Bokeh server can be started in the terminal by `bokeh serve --show main.py`, provided that python and Bokeh are properly installed (see dependencies in `environment.yml`)
