# Network Slicing in SDN

<div>
        <img src="https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54" alt="Python"/>
        <img src="https://img.shields.io/badge/shell_script-%23121011.svg?style=flat&logo=gnu-bash&logoColor=white" alt="Shell Script"/>
</div>

## Table of contents

- [Introduction](#introduction)
- [Setup the virtual machine](#Setup-the-virtual-machine)
- [Run the demo](#Run-the-demo)
- [Other resources](#Other-resources)



# Introduction

The goal of this project is to develop, starting from a dense network, a program that allows flexible activation and deactivation of flows between nodes, through a commandline program that guides the user.


The network is composed of 5 switches and 7 hosts, the white numbers rappresent the link capacities in Mbps, the capacities between host and switch are supposed to be infinite, here is the topology:


<img src="Topology (2).jpg" alt="width" style="width:80%;" />


The user can choose the source, the destination hosts and the bandwidth to allocate.
Then the software trys to find the shortest available path with the highest bandwidth given the previous inputs.
It is also possible to delete previous created flows.













# Setup the virtual machine

1. follow the instruction here to install mininet on a virtual machine: https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs
2. Clone the repository in the virtual machine:
```bash
git clone https://github.com/Federico467/NextGenerationNetworks
```




# Run the demo


To run this demo, follow these steps:

1. go to the NextGenerationNetworks folder and start first the controller and then the network:
```bash
cd NextGenerationNetworks
ryu-manager Controller.py
sudo python3 Network.py
```
2. Open a new terminal and run the software:
```bash
cd NextGenerationNetworks
sudo python3 Software.py
```
3. Now you can add flows and remove them, simply following the commandline questions



# Other resources

https://cs.stackexchange.com/questions/1591/finding-the-maximum-bandwidth-along-a-single-path-in-a-network/1639#1639
