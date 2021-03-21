#!/usr/bin/env bash
echo "Creating conda environment..."
conda create -n tf1 python=3.6 tensorflow=1.15 -y
conda activate tf1
echo "Created tf1 environment. Installing IBM FL..."
cd /mydata/ && git clone https://github.com/IBM/federated-learning-lib
cd /mydata/federated-learning-lib/federated-learning-lib && pip install ./federated_learning_lib-1.0.4-py3-none-any.whl
echo "Installed IBM FL. Installing Jupyter Notebook..."
conda install -c conda-forge notebook -y
jupyter notebook --generate-config
echo "c.NotebookApp.allow_origin = '*'" >> ~/.jupyter/jupyter_notebook_config.py
echo "c.NotebookApp.ip = '0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py
ufw allow 8888
echo "Installed Jupyter Notebook"
