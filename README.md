
#                                            CODRUG VERSION 2025.1.0:                                            #
This is a tool applied to QSAR analysis using machine learning (ML) models. Its design includes everything from the preparation of labeled internal datasets, preprocessing, exploratory and statistical analysis, generation of molecular descriptors and feature engineering, construction and validation of regression models, classification and clustering, cross-validation, hyperparameter optimization, and prediction of classes or bioactivities in external databases. This interface guides users through complex processes, reducing the need for programming knowledge and IDE use. It was developed in Python 3.10.12 using the PyQt5/Qt 5.15.14 framework, with an intuitive and modular graphical interface organized into sequential tabs. The main libraries integrated into this tool were ChEMBL Web Client, Pandas, Numpy, Matplotlib, RDKit, PaDEL-Descriptor, TensorFlow, PyTorch, Pycaret, and Scikitlearn.


#                                        **INSTALLATION INSTRUCTIONS**:                                     #


**Download the compressed file from the link:**
https://github.com/moimaian/CODRUG/archive/refs/heads/main.zip

** Extract the file to a working folder, for example, "$HOME/CODRUG":**
This can be done graphically in a file manager such as Nemo
- Extract the contents of the CODRUG-main.zip file to your system's home folder, creating the folder $HOME/CODRUG (remove -main from the name)
It is also possible to extract and rename the folder by opening a terminal window in the Downloads folder and executing the commands:
sudo apt-get install unzip # If you have not installed
unzip CODRUG-main.zip
mv $HOME/Downloads/CODRUG-main $HOME/CODRUG

** Still in the terminal, run the CODRUG.py file using the command:**
cd $HOME/CODRUG && python3 ./CODRUG.py

Use the following command if you do not have python3 on your system:
sudo apt update
sudo apt install python3 -y

A window will then appear describing the requirements that are not installed in the environment so that the user knows what needs to be installed beforehand. This installation can be done through the interface itself, which will open automatically, or with the module_requirements.py file in the MODULES folder.
In this first run, the Python virtual environment will be created in $HOME/.venv/CODRUG, where the program packages that are dependencies for running CODRUG will be installed (see topic 3).

For installations via the terminal, this environment can be activated with the command:
source $HOME/.venv/CODRUG/bin/activate

# **PREREQUISITES:**
All prerequisites must be installed by clicking the "Installation Requirements" button in the HOME tab. However, if it is necessary to reinstall one or more, these can be selected in the checklist.
The prerequisites are:
- Python version: 3.10.12
- matplotlib: 3.10.5
- Numpy: 1.26.4
- Pandas: 2.1.4
- PyCaret: 3.3.2
- RDKit: 2024.03.5
- Joblib: 1.3.2
- Scikit-learn: 1.4.2
- Chembl Web Resource Client: 0.10.9
- Padelpy: 0.1.13
- Seaborn: 0.13.2

THIS APPLICATION WAS DEVELOPED AND TESTED ONLY ON LINUX MINT 21.3 WITH KERNEL 5.15.0 AND CUDA-TOOLKIT 12.4. 
IT WILL PROBABLY WORK WELL ON UBUNTU LINUX AND ITS FLAVORS, BUT I DO NOT GUARANTEE IT FOR OTHER LINUX DISTROS!

#                                     **MORE INFORMATIONS:**:                                  #
See User Manual.

Ready! Enjoy! I hope it is useful in your work!

## License

CODRUG is free software and is distributed under the terms of the
GNU General Public License v3.0 or later (GPL-3.0-or-later).

Copyright (C) 2024–2026 Moisés Maia.

The software is registered as a computer program at the
Instituto Nacional da Propriedade Industrial (INPI), Brazil.

See the LICENSE file for details.


