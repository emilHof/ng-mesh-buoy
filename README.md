## Buoy Mesh Network - JMU Engineering

A common code base for mesh network ready buoys.\
This repository is undergoing a constant stream of updates. Feel free to check
out a branch and jump right into building with us!

## How to contribute?
Clone the repository or any branch of the repository by typing:

```
git clone https://github.com/emilHof/ng-mesh-buoy.git
```

to check out the main branch or,

```
git clone --branch <branch_name> https://github.com/emilHof/ng-mesh-buoy.git
```

to check out a specific branch.\
For example, checking out the **section3-comms-dev** branch would look like this:

```
git clone --branch section3-comms-dev https://github.com/emilHof/ng-mesh-buoy.git
```


**Have fun making!**

## Architecture
```mermaid
graph LR;
  A[Remote Xbee] -- Msg -->B[RadioInterface</font>];
  B-- Puts recieved msgs in the in_queue -->C(In_Queue);
  C-- Reads items from the in_queue -->D[MessageHandler];
  D-- Puts alt-adressed msg in the dep_queue -->E(Dep_Queue);
  D-- Executes any query cmds found in the msg -->F[DBInterface];
  D-- Executes any location cmds found in the msg -->G[GPSInterface];
  F-- Returns query data -->D;
  G-- Returns location data -->D;
  H[RFIDInterface]-- Logs data to the db -->F;
  D-- Puts return msg into the dep_queue -->E;
  E-- Reads msgs from the dep_queue -->B;
  B-- Broadcasts all msgs -->A;
```
