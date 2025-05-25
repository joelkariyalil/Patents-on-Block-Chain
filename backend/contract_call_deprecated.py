import os
from dotenv import load_dotenv
from web3 import Web3
import json

load_dotenv()

RPC_URL = os.getenv("LOCAL_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Load ABI
with open("contract_abi.json") as f:
    abi = json.load(f)["abi"]

# Connect to local hardhat node
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def record_result(cid, score, decision):
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    txn = contract.functions.storeResult(cid, score, decision).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.to_wei("1", "gwei")
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return w3.to_hex(tx_hash)
