# VANET-accident-warning-system
A Blockchain-based solution for Vehicular Ad-hoc Networks (VANETs) implementing secure vehicle authentication, trusted accident data recording, and defenses against Impersonation, Replay, and Sybil attacks using Solidity and Python.



🚗 Secure VANET Accident Warning System
A Blockchain-Based Approach for Secure Authentication and Trusted Data Recording in Vehicular Ad-Hoc Networks.

📖 Project Overview
This project addresses the critical security challenges in VANETs, specifically the issues of trust and data integrity in accident reporting. By leveraging Ethereum Smart Contracts, we created a decentralized "Root of Trust" that ensures only authorized vehicles can report accidents, preventing false alarms and traffic disruption caused by malicious actors.
Domain: Emerging Networks (VANET / IoT) Course: Blockchain Applications Status: Completed & Tested

🔑 Key Features

1.	Secure Authentication
Whitelisting Mechanism: Implements a strict access control model where a central Traffic Authority must register vehicles before they can interact with the network.
 	Defense: Neutralizes Sybil Attacks and Impersonation Attacks.

2.	Trusted Data Recording
Immutable Logging: Accident reports are stored as tamper-proof blockchain Events containing location data, reporter identity, and timestamps.
 	Defense: Prevents Modification Attacks (data cannot be altered once mined).

3.	Replay Attack Prevention
Freshness Check: The smart contract enforces a strict 5-minute time window for all reports.
 	Defense: Prevents hackers from capturing valid old messages and re-broadcasting them to confuse drivers.

🛠 Technology Stack
Smart Contract: Solidity (v0.8.0)
Blockchain Simulation: Ganache (Local Ethereum Blockchain)
Deployment: Remix IDE
 	Testing & Interaction: Python (Web3.py)

🚀 Installation & Usage

Prerequisites
1.	Node.js & Ganache: npm install -g ganache

2.	Python 3.x: pip install web3
 
Step 1: Start the Blockchain
Open your terminal and run a local Ganache instance:

ganache

Note the RPC Server URL (usually http://127.0.0.1:8545 ).

Step 2: Deploy the Contract
1.	Open Remix IDE.
2.	Upload VANETSafety.sol .
3.	Connect Remix to Dev - Ganache Provider (Port 8545).
4.	Deploy the contract.

Step 3: Run the Attack Simulation
1.	Copy the Contract Address from Remix.
2.	Update CONTRACT_ADDRESS in vanet_real_attack.py .
3.	Run the script:


python3 vanet_real_attack.py

🛡 Security Analysis (Threat Model)

We validated the system using a custom Python script that acts as both a legitimate user and a malicious attacker.

Attack Vector	  Defense Mechanism	  Simulation Result

Impersonation	  onlyAuthorized Modifier	  🛡 BLOCKED

Replay Attack	  Timestamp Freshness Logic	  🛡 BLOCKED

Sybil Attack	  Centralized Registration	  🛡 BLOCKED

Modification	  Blockchain Immutability	  🛡 BLOCKED

DoS Attack	  Gas Fee Economic Barrier	  Infeasible ($1.1M/hr cost)


Simulation Output
(Replace this with the screenshot of your terminal showing "ATTACK BLOCKED")

📊 Performance Evaluation

Gas Consumption Analysis:
 
Vehicle Registration: ~70,020 Gas

 	Accident Reporting: ~123,307 Gas Latency:
	
Simulation: < 50ms (Instant)

 	Mainnet Projection: ~12 seconds (1 Block Confirmation)

👥 Authors
[Moustafa Ahmed Elsayed Hosny]

[Hala Degol]

[Hagar Mahmoud]

📄 License
This project is open-source and available under the MIT License.
