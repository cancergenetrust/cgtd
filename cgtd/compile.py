from ethjsonrpc import EthJsonRpc

eth = EthJsonRpc("ethereum", 8545)

print "Balance:", eth.eth_getBalance()

with open("VarStore.sol") as f:
    contract = eth.eth_compileSolidity(f.read())

print "Contract:", contract

contract_tx = eth.create_contract(eth.eth_coinbase(),
                                  contract['VarStore']['code'], gas=300000)
print "Contract Tx:", contract_tx
