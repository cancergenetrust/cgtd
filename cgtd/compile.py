import json
from ethjsonrpc import EthJsonRpc

eth = EthJsonRpc("ethereum", 8545)

with open("VarStore.sol") as f:
    contract = eth.eth_compileSolidity(f.read())
transaction = eth.create_contract(eth.eth_coinbase(),
                                  contract['VarStore']['code'], gas=300000)
contract["transaction"] = transaction
contract["account"] = eth.eth_coinbase()
print json.dumps(contract)
