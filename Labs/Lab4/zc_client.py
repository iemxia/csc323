import sys, time, json, os, hashlib
from ecdsa import VerifyingKey, SigningKey
from Crypto.Cipher import AES
from Crypto import Random
import random
from p2pnetwork.node import Node

SERVER_ADDR = "zachcoin.net"
SERVER_PORT = 9067

# ZachCoin Constants
BLOCK = 0
TRANSACTION = 1
BLOCKCHAIN = 2
UTXPOOL = 3
COINBASE = 50
DIFFICULTY = 0x0000007FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
my_pub_key = "0ca98e3b9b1229284510e493a34ed4b38c8a14c6226b4aef682edf0ac1014d4d015555eb372fdf907e121ccbb954c3ab"


class ZachCoinClient(Node):
    # Hardcoded gensis block
    blockchain = [
        {
            "type": BLOCK,
            "id": "b4b9b8f78ab3dc70833a19bf7f2a0226885ae2416d41f4f0f798762560b81b60",
            "nonce": "1950b006f9203221515467fe14765720",
            "pow": "00000027e2eb250f341b05ffe24f43adae3b8181739cd976ea263a4ae0ff8eb7",
            "prev": "b4b9b8f78ab3dc70833a19bf7f2a0226885ae2416d41f4f0f798762560b81b60",
            "tx": {
                "type": TRANSACTION,
                "input": {
                    "id": "0000000000000000000000000000000000000000000000000000000000000000",
                    "n": 0
                },
                "sig": "adf494f10d30814fd26c6f0e1b2893d0fb3d037b341210bf23ef9705479c7e90879f794a29960d3ff13b50ecd780c872",
                "output": [
                    {
                        "value": 50,
                        "pub_key": "c26cfef538dd15b6f52593262403de16fa2dc7acb21284d71bf0a28f5792581b4a6be89d2a7ec1d4f7849832fe7b4daa"
                    }
                ]
            }
        }
    ]
    utx = []

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(ZachCoinClient, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)

    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        # print("node_message from " + connected_node.id + ": " + json.dumps(data,indent=2))
        print("node_message from " + connected_node.id)

        if data != None:
            if 'type' in data:
                if data['type'] == TRANSACTION: #1
                    self.utx.append(data)
                elif data['type'] == BLOCKCHAIN: #2
                    self.blockchain = data['blockchain']
                elif data['type'] == UTXPOOL:  #3
                    self.utx = data['utxpool']
                elif data['type'] == BLOCK:  #0
                    # TODO: Validate blocks
                    print("user submitted block")
                    if verify_block(data, self, -1, False):  # index should be the last block exist
                        self.blockchain.append(data)
                        print(data["tx"]["output"][1]["pub_key"])
                        print("Block verified, added to blockchain")
                    else:
                        print("block did not pass verification")
                else:
                    print("someone submitted something weird")

    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")


def verify_block(block, client, prev_index, existing_tf):
    # verifying block contains all required fields
    required_fields = ['type', 'id', 'nonce', 'pow', 'prev', 'tx']
    for field in required_fields:
        if field not in block:
            print(f"Error: Missing field '{field}' in the block")
            return False
    # type field is the value BLOCK
    if block['type'] != BLOCK:
        print("Invalid block type")
        return False
    # block ID computed correctly
    exp_id = hashlib.sha256(json.dumps(block['tx'], sort_keys=True).encode('utf8')).hexdigest()
    if block['id'] != exp_id:
        print("Incorrect block ID")
        return False
    # prev block id is correct
    prev_exp_id = client.blockchain[prev_index]["id"]
    if block['prev'] != prev_exp_id:
        print("Invalid prev Block ID")
        return False
    # validate pow is less than difficulty and pow is correctly calculated from Nonce
    nonce = block["nonce"]
    prev = client.blockchain[prev_index]["id"]
    utx = block['tx']
    if hashlib.sha256(json.dumps(utx, sort_keys=True).encode('utf8') + prev.encode('utf-8') + nonce.encode('utf-8')).hexdigest() != block['pow']:
        print("Nonce does not calculate to given pow")
        return False
    if int(block['pow'], 16) > DIFFICULTY:
        print("Pow > Difficulty")
        return False
    if not verify_transaction(utx, client.blockchain, existing_tf, True):
        print("Invalid transaction")
        return False
    return True  # passes all checks and is a valid black


def verify_transaction(tx, blockchain, existing_block, adding_new):
    # Check if all required keys are present
    required_keys = ['type', 'input', 'sig', 'output']
    for key in required_keys:
        if key not in tx:
            print(f"Error: Key '{key}' is missing in the utx transaction")
            return False

    # check type is correct
    if tx['type'] != TRANSACTION:
        print("Invalid transaction type")
        return False

    # Ensure valid number of outputs
    if existing_block:
        if len(tx['output']) > 3 or len(tx['output']) < 1:
            print(len(tx["output"]))
            print("Invalid number of transaction outputs (existing block)")
            return False
    else:
        if len(tx['output']) > 2 or len(tx['output']) < 1:
            print(len(tx["output"]))
            print("Invalid number of transaction outputs (utx)")
            return False

    # Check if transaction input refers to a valid block
    input_block_id = tx['input']['id']
    input_block_n = tx['input']['n']  # index of the output tx in block it's referring to (payment to the spender that they're now spending)
    found_block = False
    input_tx = None  # set variable for place where coins are coming from
    for i in range(len(blockchain)):  # go through all blocks in existing blockchain
        if existing_block is False:  # for testing valid blocks that don't exist already, for testing pre-existing blocks for debugging
            if blockchain[i]["tx"]["input"]["id"] == input_block_id and blockchain[i]["tx"]["input"]["n"] == tx["input"]["n"]:  # check if any block already in blockchain spent it already
                print("Input is already spent")  # go through all unverfified transactions check if their input refers to an output, list of unspent
                return False
        if blockchain[i]['id'] == input_block_id:  # find the block it's referring to
            found_block = True  # block exists
            if input_block_n >= len(blockchain[i]['tx']):  # transaction index is valid
                print("Error: Invalid transaction index")
                return False
            input_tx = blockchain[i]['tx']['output'][input_block_n]  # set where the coins to be paid are coming from
            break

    if not found_block:
        print("Error: Could not find input block in blockchain")
        return False

    total_output = 0
    if adding_new:  # verifying transaction in block
        for i in range(len(tx["output"])-1):  # don't include coinbase value
            total_output += tx['output'][i]['value']  # coins being paid out, don't include coinbase part
    else:  # verifying transaction alone
        for i in range(len(tx["output"])):
            total_output += tx['output'][i]['value']
    # verify coinbase output
    if adding_new:
        coinbase_output = tx['output'][-1]['value']
        if coinbase_output != COINBASE:
            print("Incorrect coinbase value")
            return False

    if int(total_output) <= 0 or not isinstance(total_output, int):  # non zero, non negative, integer output value
        print("Zero/negative or non integer output value")
        return False

    input_amount = input_tx['value']
    if total_output != input_amount:
        print("Error: Output does not match input amount")
        print(f"total output {total_output}, input amt: {input_amount}")
        return False

    # Verify ECDSA signature
    input_tx_pub_key = input_tx['pub_key']
    input_tx_sig = tx['sig']
    vk_input_tx_pub_key = VerifyingKey.from_string(bytes.fromhex(input_tx_pub_key))
    try:
        assert vk_input_tx_pub_key.verify(bytes.fromhex(input_tx_sig), json.dumps(tx['input'], sort_keys=True).encode('utf8'))
    except Exception as e:
        print("Invalid transaction signature:", e)
        return False
    return True  # PASSED ALL CHECKSSSS, valid


def add_coin_base_tx(tx):
    coin_base_tx = {
        'value': COINBASE,
        'pub_key': my_pub_key
    }
    tx['output'].append(coin_base_tx)
    return tx


def mine_transaction(utx, prev):
    nonce = Random.new().read(AES.block_size).hex()
    while (int(hashlib.sha256(
            json.dumps(utx, sort_keys=True).encode('utf8') + prev.encode('utf-8') + nonce.encode('utf-8')).hexdigest(),
               16) > DIFFICULTY):
        nonce = Random.new().read(AES.block_size).hex()
    pow = hashlib.sha256(
        json.dumps(utx, sort_keys=True).encode('utf8') + prev.encode('utf-8') + nonce.encode('utf-8')).hexdigest()
    return pow, nonce


def main():
    if len(sys.argv) < 3:
        print("Usage: python3", sys.argv[0], "CLIENTNAME PORT")
        quit()

    # Load keys, or create them if they do not yet exist
    keypath = './' + sys.argv[1] + '.key'
    if not os.path.exists(keypath):
        sk = SigningKey.generate()
        vk = sk.verifying_key
        with open(keypath, 'w') as f:
            f.write(sk.to_string().hex())
            f.close()
    else:
        with open(keypath) as f:
            try:
                sk = SigningKey.from_string(bytes.fromhex(f.read()))
                vk = sk.verifying_key
            except Exception as e:
                print("Couldn't read key file", e)

    # Create a client object
    client = ZachCoinClient("127.0.0.1", int(sys.argv[2]), sys.argv[1])
    client.debug = False

    time.sleep(1)

    client.start()

    time.sleep(1)

    # Connect to server
    client.connect_with_node(SERVER_ADDR, SERVER_PORT)
    print("Starting ZachCoin™ Client:", sys.argv[1])
    time.sleep(2)
    my_block = None
    my_tx_idx = 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        slogan = " You can't spell \"It's a Ponzi scheme!\" without \"ZachCoin\" "
        print("=" * (int(len(slogan) / 2) - int(len(' ZachCoin™') / 2)), 'ZachCoin™',
              "=" * (int(len(slogan) / 2) - int(len('ZachCoin™ ') / 2)))
        print(slogan)
        print("=" * len(slogan), '\n')
        x = input("\t0: Print keys\n\t1: Print blockchain\n\t2: Print UTX pool\n\t3: Mine\n\t4: verify existing block\n\t5: print my tx\n\nEnter your choice -> ")
        try:
            x = int(x)
        except:
            print("Error: Invalid menu option.")
            input()
            continue
        if x == 0:
            print("sk: ", sk.to_string().hex())
            print("vk: ", vk.to_string().hex())
        elif x == 1:
            print(json.dumps(client.blockchain, indent=1))
        elif x == 2:
            print(json.dumps(client.utx, indent=1))
        # TODO: Add options for creating and mining transactions
        elif x == 3:  # verifying a utx and try to mine
            not_mined = True
            while not_mined:  # keep trying to find a transaction that will verify
                print("finding valid transaction")
                utx_index = random.randint(0, len(client.utx) - 1)
                tx = client.utx[utx_index]
                if verify_transaction(tx, client.blockchain, False):  # once valid transaction found
                    print("valid transaction found")
                    tx = add_coin_base_tx(tx)  # add coinbase tx
                    print(f"starting to mine tx at index {utx_index}")
                    pow, nonce = mine_transaction(tx, client.blockchain[-1]["id"])  # try to mine it
                    block_id = hashlib.sha256(json.dumps(tx, sort_keys=True).encode('utf8')).hexdigest()
                    prev_id = client.blockchain[-1]["id"]
                    # tx is the same
                    zc_block = {
                        "type": BLOCK,
                        "id": block_id,
                        "nonce": nonce,
                        "pow": pow,
                        "prev": prev_id,
                        "tx": tx
                    }
                    client.send_to_nodes(zc_block)  # try to send to server if block is mined and created
                    # not_mined = False
                    print("Block mined")
        elif x == 4:  # test my verify block fcn verifies a block that should be verified
            utx_index = random.randint(1, len(client.blockchain) - 1)
            block_to_test = client.blockchain[utx_index]
            print(json.dumps(block_to_test,indent=2))
            if verify_block(block_to_test, client, utx_index-1, True):
                print("block verified")
            else:
                print("something's wrong in ur code, fix it lols")
        elif x == 5:  # print my transaction block
            print("My 25 coins block: ", client.blockchain[273])
            my_block = client.blockchain[273]
        elif x == 6:  # find block with my public key as an output in a transaction
            found = False
            for i in range(1, len(client.blockchain)):
                for j in range(len(client.blockchain[i]["tx"]["output"])):
                    if client.blockchain[i]["tx"]["output"][j]["pub_key"] == my_pub_key:
                        found = True
                        print(f"Found proof of block paying to me at index {i}", json.dumps(client.blockchain[i], indent=2))
            if found is False:
                print("Did not find block")
        elif x == 7: # submit my own transaction
            input_tx = {
                "id": my_block["id"],
                "n": 0
            }
            sig = sk.sign(json.dumps(input_tx, sort_keys=True).encode('utf8')).hex()
            tx = {
                "type": TRANSACTION,
                "input": input_tx,
                "sig": sig,
                "output": [
                    {
                        "value": 10,
                        "pub_key": "81124c3b51a23e43c5480dc7987369a591862f451ecc6b8312923761f15528054a20a8047a7ff6f8878161af5eeced39"
                    },
                    {
                        "value": 15,
                        "pub_key": my_pub_key
                    }
                ]
            }
            client.send_to_nodes(tx)
            my_tx_idx = len(client.utx) - 1
            print("my utx at index ", my_tx_idx)
        elif x == 8:  # mine my own transaction
            tx = client.utx[856]
            if verify_transaction(tx, client.blockchain, False):  # once valid transaction found
                print("valid transaction found")
                tx = add_coin_base_tx(tx)  # add coinbase tx
                print(f"starting to mine tx at index 856")
                pow, nonce = mine_transaction(tx, client.blockchain[-1]["id"])  # try to mine it
                block_id = hashlib.sha256(json.dumps(tx, sort_keys=True).encode('utf8')).hexdigest()
                prev_id = client.blockchain[-1]["id"]
                # tx is the same
                zc_block = {
                    "type": BLOCK,
                    "id": block_id,
                    "nonce": nonce,
                    "pow": pow,
                    "prev": prev_id,
                    "tx": tx
                }
                print(zc_block)
                client.send_to_nodes(zc_block)  # try to send to server if block is mined and created
                # not_mined = False
                print("Block mined")

        #     pass
        input()


if __name__ == "__main__":
    main()
