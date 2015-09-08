Project: Distributed monitor

Author: Florin Cotoranu

Email: florincotoranu@yahoo.com

Date: 09/08/2015

This project was done as an assignment proposed by Cloudbase Solutions:

=========================================================================
Your task is to build a system that would be used to monitor different 
statistics from multiple nodes. Example: free/used memory, cpu usage, 
network usage, disk IOps.

The system will be distributed, it should have a controller that recives
periodic updates from agents running on different machines. You should 
use AMQP for communication. All the gathered statistics should be stored
in a database of your choice.

The application should be written in Python and should run on Windows. 
The required information should be gathered using WMI.

The project should be unit tested.

Bonus: The agents retrieving the statistics should be able to run on Linux
as well.

Notes: your work is individual

==========================================================================

A. OVERVIEW
==========================================================================

The system was implemented in Python and is split into two components.
The components communicate using AMQP messages through a RabbitMQ server.

1. Controller
A controller runs on a Windows, and sends requests to 
multiple agents(nodes) for different system statistics:
- CPU usage (percentage)
- Total and available virtual memory
- Disk writes/reads per second
- Network bytes read/written

The requests are sent cyclically in 4 phases:
1. CPU usage request sent to all agents
2. Memory information request to all agents
3. Disc IOps request sent to all agents
4. Network usage request sent to all agents

The statistics received as response are stored into a SQLite database.

2. Agent
An agent may run on a Windows or Linux platform and forwards the 
system statistics to the controller when requested.
Statistics are gathered using WMI on Windows systems and psutil on 
Linux systems.


B. CONFIGURATION
==========================================================================
	
1. Agents
Each agent must be configured in agent/config.py before being used:
 - OS: used operating system on node: 'Windows'/'Linux'
 - LABEL: unique label used to identify an agent.
 - USER_CFG: RabbitMQ username 
 - PASW_CFG: RabbitMQ password
 - IP_CFG: RabbitMQ server ip address
 - PORT_CFG: RabbitMQ port number
 
2. Controller
The controller is configured in controller/config.py:
 - LABEL_LIST: list containing all agent labels
 - MAX_RETRY_COUNTER_CFG: Maximum number of times a request is retried
 in case an agent goes into timeout
 - LOOP_PERIOD_CFG: time, in seconds, between two request phases 
 - TIMEOUT_VAL_CFG: maximum allowed time, in seconds, between a request
 is sent to an agent and a reply is received. If this time passes without
 any reply, the communication with the agent enters timeout.
 - USER_CFG: RabbitMQ username 
 - PASW_CFG: RabbitMQ password
 - IP_CFG: RabbitMQ server ip address
 - PORT_CFG: RabbitMQ port number
 - _DALECT_CFG: database dialect
 - _FILENAME_CFG = database location and filename


C. USAGE
==========================================================================
	
1. Agents
After an agent is configured, it may be started by running agent/main.py.
Once an agent is running, it waits for AMQP from the controller.
To stop an agent, press CTRL+C.

2. Controller
Before running the controller, all configured agents should already be running.
To start the controller, run controller/main.py. To stop it, press CTRL+C.


D. TESTING
==========================================================================
	
Both, the controller and agent, have been unit tested. Test scripts can be found
in agent/unit_test.py and controller/unit_test.py.
Also, target tests have been performed in the following configuration:
- 1 controller running on Windows
- 1 agent running on Windows
- 1 agent running on Linux


E. CONCLUSION AND PERSONAL OPINION
==========================================================================
	
I have to mention that before this project, I had no prior knowledge of Python,
AMQP and other involved technologies. As expected, it took longer than originally
planned to develop this project due to the learning process involved. 
I had moments of satisfaction and also moments of frustration, but in the end, the
gathered knowledge and skill makes up for everything and I am grateful for this
oportunity. I look forward to receiving technical feedback for this project,
and I hope we will colaborate in the future. Thanks!
