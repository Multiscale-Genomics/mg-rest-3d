# mg-rest-3d

[![Documentation Status](https://readthedocs.org/projects/mg-rest-3d/badge/?version=latest)](http://mg-rest-3d.readthedocs.io/en/latest/?badge=latest)

RESTful API for TADbit generated 3D coordinates

# Requirements
- Mongo DB 3.2
- Python 2.7.10+
- pyenv
- pyenv virtualenv
- Python Modules:
  - h5py
  - numpy
  - DMP
  - Flask
  - Flask-Restful
  - Waitress

# Installation
Cloneing from GitHub:
```
git clone https://github.com/Multiscale-Genomics/mg-rest-3d.git
```
To get this to be picked up by pip if part of a webserver then:
```
pip install --editable .
pip install -r requirements.txt
```
This should install the required packages listed in the `setup.py` script.


Installation via pip:
```
pip install git+https://github.com/Multiscale-Genomics/mg-rest-3d.git
```

# Configuration files
Requires a file with the name `mongodb.cnf` with the following parameters to define the MongoDB server:
```
[dmp]
host = localhost
port = 27017
user = testuser
pass = test123
db = dmp
ftp_root = ftp://ftp.multiscalegenomics.eu/test
```

# Setting up a server
```
git clone https://github.com/Multiscale-Genomics/mg-rest-dm.git

cd mg-rest-3d
pyenv virtualenv 2.7.12 mg-rest-3d
pyenv activate mg-rest-3d
pip install git+https://github.com/Multiscale-Genomics/mg-dm-api.git
pip install -e .
pip deactivate
```
Starting the service:
```
nohup ${PATH_2_PYENV}/versions/2.7.12/envs/mg-rest-3d/bin/waitress-serve --listen=127.0.0.1:5003 rest.app:app &
```

# Generating test data
Run the following script:
```
python scripts/GenerateSampleCoords.py
```

# Testing the performance of the API
Run the test script:
```
 python -m scripts.test_regions_models
```
