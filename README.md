# Development and Deployment of UDP/IP OpenPMU Dashboard on AWS

![openpmu-dashboard](https://github.com/user-attachments/assets/eedc8188-a7f6-4740-8323-72f4a4aac7f5)

This application host a live data streaming dashboard using the openpmu realtime dataset. To clone this repository, run git clone https://github.com/Sleek-coder/openpmu-fullstack-dev.git on your command line and cd into openpmu-fullstack-dev folder. 

Run sudo python3 -m pip install --upgrade pip
Run sudo apt-get update
if in linux, run `source openpmu-env/bin/activate`
cd  into thesrc-frontendend
run npm start
Also , open a new directory , cd into  OpenPMU_XML_SV-Simulator 
Acyivate the virtualenv in this dir also 

sudo python3 StartOpenPMU_XML_SV_SimulatorGUI.py

in a new dir, cd  PhasorEst 
run python  StartPhasorEstimator.py

In the project directory . run Python3  manage.py runserver 

Also,  open a new dir 
run Python3 manage.py updatemodels
 Your fullstack  app is deployed 

Please find the written documentation
Download PDF here:
[openpmu_dashboard.pdf](https://github.com/user-attachments/files/16824073/openpmu_dashboard.pdf)
