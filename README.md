NGMesh API
========

The NGMesh API solves the problem of integrating Arduino based water quality sensors into
a Python based mesh network. This is done by utilizing a number of unidirectional and bidirectional
serial port interfaces. These are coordinated with the builtin [Asyncio](https://docs.python.org/3/library/asyncio.html)
library to enable simultaneous acquisition and transaction of local data.

**To get started:**
1. Clone the repository ------`git clone https://github.com/emilHof/ng-mesh-buoy.git`
2. Install the requirements - `pip install -r requirements.txt`
3. Set up your ports --------- `port = *your-port*, rate=*your-rate*`
4. Launch the cli ------------- `python3 cli.py`

## Features
Clone the repository or any branch of the repository by typing:

`git clone https://github.com/emilHof/ng-mesh-buoy.git`

to check out the main branch or,

`git clone --branch <branch_name> https://github.com/emilHof/ng-mesh-buoy.git`

to check out a specific branch.\
For example, checking out the **section3-comms-dev** branch would look like this:

`git clone --branch section3-comms-dev https://github.com/emilHof/ng-mesh-buoy.git`


**Have fun making!**
