from web3 import Web3
import time

# Connect to Ganache
w3 = Web3(
    Web3.HTTPProvider(
        "http://127.0.0.1:7545"
    )
)

# First account
account = w3.eth.accounts[0]

# ---------------- STORE HASH
def store_on_blockchain(ipfs_hash):

    data = ipfs_hash + str(time.time())

    tx_hash = w3.eth.send_transaction({

        "from": account,
        "to": account,
        "value": 0,
        "data": w3.to_hex(text=data)

    })

    return tx_hash.hex()