# openpmu-fullstack-dev
This app host a live data streaming dashboard using the openpmu realtime dataset
sudo python3 -m pip install --upgrade pip
sudo apt-get update

python3 -m venv openpmu-env
`source openpmu-env/bin/activate`

sudo python3 -m pip install pyqt5
cd into  openpmu-fullstack-dev directory
cd  into thesrc-frontendend
run npm start
Also , open a new directory , cd into  OpenPMU_XML_SV-Simulator 
Acyivate the virtualenv ein this dir also 

sudo python3 StartOpenPMU_XML_SV_SimulatorGUI.py

in a new dir, cd  PhasorEst 
run python  StartPhasorEstimator.py

In the project directory . run Python3  manage.py runserver 

Also,  open a new dir 
run Python3 manage.py updatemodels
 Your fullstack  app is deployed 
