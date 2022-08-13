# DDOS 

### Small test realization of services for DDOS attack 

***


## Description 

The attack is being run from multiple instances, so it has the host 
server that connects and manipulates the instances. Every instance 
connects to the server via WebSocket and waits for the command. <br />
The administrator of the server can command to start the attack on some 
target and the server will go through every connected instance to deploy 
the attack on the specified target. 

***


## Deployment 

##### Requirements 
```commandline
sudo apt install wrk                    // The workload generator
sudo apt install python3 python3-pip    // Python, language to run this script
                                        // and package manager to install libs
                                        
// Inside project directory
python3 -m pip install virtualenv   // Module to create virtual environment
python3 -m venv venv                // Create virtual environment
. ./venv/bin/activate               // Activate virtual environment

python3 -m pip install -r requirements.txt  // Install all the dependencies
```

### Host server 

First you will need a host server. This is a server which is a 
main machine to communicate with the clients that connect to this server 
receive the commands from it. 

##### Deploy host server
````commandline
// Inside project directory
. ./venv/bin/activate
python3 manage.py runserver -H <host> -p <port>
````

### Client server

Client connects to the host server and waits until the server gives the 
instructions to do.

##### Deploy client 
```commandline
// Inside project directory
. ./venv/bin/activate 
export PYTHONPATH=$(pwd)
python3 scripts/connect.py <host>:<port>
```

***

