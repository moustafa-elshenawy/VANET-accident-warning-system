import time
import json
from web3 import Web3

# --- CONFIGURATION ---
GANACHE_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x061689fE7534e4ec3dBfCC376c79D09F0fcCa29A" # UPDATE THIS IF REDEPLOYED

# 2. FULL ABI
CONTRACT_ABI = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{"indexed": True, "internalType": "uint256", "name": "id", "type": "uint256"},
			{"indexed": False, "internalType": "string", "name": "location", "type": "string"},
			{"indexed": True, "internalType": "address", "name": "reporter", "type": "address"},
			{"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
		],
		"name": "AccidentReported",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{"indexed": False, "internalType": "string", "name": "alertType", "type": "string"},
			{"indexed": True, "internalType": "address", "name": "attacker", "type": "address"}
		],
		"name": "SecurityAlert",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [{"indexed": True, "internalType": "address", "name": "vehicle", "type": "address"}],
		"name": "VehicleRegistered",
		"type": "event"
	},
	{
		"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
		"name": "accidentLog",
		"outputs": [
			{"internalType": "uint256", "name": "id", "type": "uint256"},
			{"internalType": "string", "name": "location", "type": "string"},
			{"internalType": "uint256", "name": "timestamp", "type": "uint256"},
			{"internalType": "address", "name": "reporter", "type": "address"}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "authorizedCount",
		"outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [{"internalType": "address", "name": "", "type": "address"}],
		"name": "authorizedVehicles",
		"outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAccidentCount",
		"outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAuthorizedVehicleCount",
		"outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [{"internalType": "address", "name": "_vehicle", "type": "address"}],
		"name": "registerVehicle",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{"internalType": "string", "name": "_location", "type": "string"},
			{"internalType": "uint256", "name": "_timeOfAccident", "type": "uint256"}
		],
		"name": "reportAccident",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "trafficAuthority",
		"outputs": [{"internalType": "address", "name": "", "type": "address"}],
		"stateMutability": "view",
		"type": "function"
	}
]

# --- CONNECT ---
try:
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Ganache.")
        exit()
    print(f"✅ Connected to Ganache at {GANACHE_URL}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
accounts = w3.eth.accounts

# --- DEFINE ROLES STRICTLY ---
# 1. Authority (Admin) - Usually Account 0
AUTHORITY = accounts[0] 

# 2. Car Node (Driver) - Usually Account 1
CAR_NODE = accounts[1]

# 3. Attacker - Usually Account 9
ATTACKER = accounts[9]

print("\n--- ROLE DEFINITIONS ---")
print(f"   [Admin]  Authority: {AUTHORITY}")
print(f"   [User]   Vehicle:   {CAR_NODE}")
print(f"   [Enemy]  Attacker:  {ATTACKER}")
print("------------------------")

# Verify Roles on Blockchain
try:
    real_auth_on_chain = contract.functions.trafficAuthority().call()
    if real_auth_on_chain != AUTHORITY:
        print(f"⚠️ WARNING: The deployed contract Authority is {real_auth_on_chain}, but Ganache Account 0 is {AUTHORITY}.")
        print("   Did you deploy with a different account? Logic might fail.")
        AUTHORITY = real_auth_on_chain # Update to match reality
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not read from contract at {CONTRACT_ADDRESS}")
    print("   The address might be wrong, or Ganache was restarted.")
    print("   Please REDEPLOY in Remix and update CONTRACT_ADDRESS in this script.")
    exit()

# --- HELPER FUNCTIONS ---
def send_tx(func_call, sender, expected_fail=False):
    try:
        # Simulate first
        try:
            func_call.call({'from': sender})
        except Exception as sim_error:
            error_str = str(sim_error)
            # Check for PUSH0 error
            if "invalid opcode" in error_str:
                print("❌ CRITICAL: Incompatible EVM Version. Recompile with 'Paris' version in Remix.")
                return False, 0
                
            reason = extract_reason(error_str)
            if expected_fail:
                 print(f"   🛡️ BLOCKING MECHANISM ACTIVE:")
                 print(f"      └── Result: ATTACK BLOCKED")
                 print(f"      └── Reason: {reason}")
            else:
                 print(f"   ❌ FAILED (Unexpected): {reason}")
            return False, 0

        # Send Real
        # Increased Gas Limit to 3,000,000 to avoid "Infinite Gas" errors
        tx_hash = func_call.transact({'from': sender, 'gas': 3000000})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] == 1:
            print(f"   ✅ Success! Gas Used: {receipt['gasUsed']}")
            return True, receipt['gasUsed']
        return False, 0
    except Exception as e:
        print(f"   ❌ Execution Error: {e}")
        return False, 0

def extract_reason(msg):
    if "revert" in msg:
        if "Access Denied" in msg: return "Impersonation (Not Authorized)"
        if "Replay Attack" in msg: return "Replay Attack (Old Timestamp)"
        if "Future time" in msg: return "Time Sync Error (Future Time)"
        if "Only Traffic Authority" in msg: return "Sybil Defense (Only Admin can Register)"
    return msg

# --- EXECUTION ---
def run_strict_demo():
    
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 1: AUTHORITY REGISTERS VEHICLE")
    print("Logic: Authority (Acc 0) grants access to Car (Acc 1)")
    print("="*60)
    # ---------------------------------------------------------
    
    # Check if already registered
    if contract.functions.authorizedVehicles(CAR_NODE).call():
        print(f"   [Info] Vehicle {CAR_NODE} is already authorized.")
    else:
        print(f"   [Action] Authority registering {CAR_NODE}...")
        # Note: Sender is AUTHORITY
        send_tx(contract.functions.registerVehicle(CAR_NODE), AUTHORITY)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 2: VEHICLE REPORTS ACCIDENT")
    print("Logic: Car (Acc 1) reports valid data.")
    print("="*60)
    # ---------------------------------------------------------
    
    # Check Authorization before proceeding to prevent Infinite Gas (Revert)
    if not contract.functions.authorizedVehicles(CAR_NODE).call():
        print("❌ ERROR: Car Node is NOT authorized. Scenario 2 will revert.")
        print("   Fix: Ensure AUTHORITY account matches the contract deployer.")
        return

    # Get Blockchain Time
    block_time = w3.eth.get_block('latest')['timestamp']
    print(f"   [Info] Using Blockchain Time: {block_time}")
    
    # Note: Sender is CAR_NODE
    success_valid, valid_gas = send_tx(contract.functions.reportAccident("Crash Hwy 1", block_time), CAR_NODE)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 3: IMPERSONATION ATTACK")
    print("Logic: Attacker (Acc 9) tries to report.")
    print("="*60)
    # ---------------------------------------------------------
    print(f"   [!] ATTACKER ADDRESS: {ATTACKER}")
    print(f"   [!] ATTACK TYPE:      Unauthorized Injection (Spoofing)")
    print(f"   [!] DEFENSE:          Whitelist Check (onlyAuthorized)")
    print("   --------------------------------------------------------")
    print("   [Hacker] Attacker sending report...")
    send_tx(contract.functions.reportAccident("Fake Crash", block_time), ATTACKER, expected_fail=True)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 4: REPLAY ATTACK")
    print("Logic: Car (Acc 1) sends OLD data (10 mins ago).")
    print("="*60)
    # ---------------------------------------------------------
    old_time = block_time - 600
    print(f"   [!] REPLAYER ADDRESS: {CAR_NODE} (Compromised/Replaying)")
    print(f"   [!] ATTACK TYPE:      Replaying Stale Data (10 mins old)")
    print(f"   [!] DEFENSE:          Freshness Check (timestamp window)")
    print("   --------------------------------------------------------")
    print(f"   [Hacker] Replaying report from time {old_time}...")
    send_tx(contract.functions.reportAccident("Crash Hwy 1", old_time), CAR_NODE, expected_fail=True)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 5: SYBIL ATTACK")
    print("Logic: Attacker (Acc 9) tries to register a fake car.")
    print("="*60)
    # ---------------------------------------------------------
    print(f"   [!] ATTACKER ADDRESS: {ATTACKER}")
    print(f"   [!] ATTACK TYPE:      Fake Identity Registration")
    print(f"   [!] DEFENSE:          Centralized Authority (onlyAuthority)")
    print("   --------------------------------------------------------")
    print("   [Hacker] Attacker trying to register Account 8...")
    send_tx(contract.functions.registerVehicle(accounts[8]), ATTACKER, expected_fail=True)

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("SCENARIO 6: DoS COST ANALYSIS")
    print("="*60)
    # ---------------------------------------------------------
    print(f"   [!] ATTACKER ADDRESS: {ATTACKER}")
    print(f"   [!] ATTACK TYPE:      Spamming / Network Flooding")
    print(f"   [!] DEFENSE:          Gas Fees (Economic Deterrence)")
    print("   --------------------------------------------------------")
    if success_valid:
        # Assumptions for Economic Analysis
        BLOCK_GAS_LIMIT = 30_000_000
        GAS_PRICE_GWEI = 50 # High traffic price assumption
        ETH_PRICE_USD = 2500 # Approx current price assumption
        
        txs_per_block = int(BLOCK_GAS_LIMIT / valid_gas)
        cost_per_tx_eth = valid_gas * GAS_PRICE_GWEI * 1e-9
        cost_per_block_eth = txs_per_block * cost_per_tx_eth
        cost_per_hour_usd = cost_per_block_eth * ETH_PRICE_USD * (3600/12) # ~300 blocks/hr

        print(f"   [Analysis] Gas per valid Report:      {valid_gas} units")
        print(f"   [Analysis] Max Throughput per Block:  {txs_per_block} transactions")
        print(f"   [Analysis] Cost to Fill 1 Block:      {cost_per_block_eth:.4f} ETH")
        print(f"   [Analysis] Cost to Sustain (1 Hour):  ${cost_per_hour_usd:,.2f} USD")
        print(f"   [Result]   ATTACK BLOCKED (Economically Infeasible)")
    else:
        print("   ⚠️ Cannot calculate (Scenario 2 failed).")

    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("FINAL SYSTEM STATUS CHECK")
    print("="*60)
    # ---------------------------------------------------------
    count = contract.functions.getAccidentCount().call()
    print(f"Total Accidents Recorded: {count}")
    if count == 1:
        print("✅ PERFECT RESULT (1 Valid, 0 Fakes)")
    else:
        print(f"⚠️ Check Logic (Count is {count})")

if __name__ == "__main__":
    run_strict_demo()
