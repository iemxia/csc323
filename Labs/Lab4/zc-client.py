import sys, time, json, os, hashlib
from ecdsa import VerifyingKey, SigningKey
from Crypto.Cipher import AES
from Crypto import Random
import random
from ecdsa.util import string_to_number
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
                if data['type'] == self.TRANSACTION:
                    self.utx.append(data)
                elif data['type'] == self.BLOCKCHAIN:
                    self.blockchain = data['blockchain']
                elif data['type'] == self.UTXPOOL:
                    self.utx = data['utxpool']
            # TODO: Validate blocks

    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")


def add_coin_base_tx(tx):
    coin_base_tx = {
        'value': COINBASE,
        'pub_key': my_pub_key
    }
    tx['output'].append(coin_base_tx)


def verify_transaction(tx, blockchain):
    if confirm_utx_format(tx):  # is correct format
        # Check if transaction is of correct type
        if tx['type'] != BLOCK:
            print("Error: Invalid transaction type")
            return False

        # Check if transaction input refers to a valid block
        input_block_id = tx['input']['id']
        input_block_n = tx['input']['n']
        found_block = False
        for block in blockchain:
            if block['id'] == input_block_id:
                found_block = True
                if input_block_n >= len(block['tx']):
                    print("Error: Invalid transaction input")
                    return False
                else:
                    input_tx = block['tx'][input_block_n]
                    break

        if not found_block:
            print("Error: Invalid transaction input block")
            return False

        # Verify ECDSA signature
        input_tx_pub_key = input_tx['output'][0]['pub_key']
        input_tx_sig = tx['sig']
        vk_input_tx_pub_key = VerifyingKey.from_string(bytes.fromhex(input_tx_pub_key))
        try:
            assert vk_input_tx_pub_key.verify(bytes.fromhex(input_tx_sig), bytes(str(input_tx['output'])))
        except Exception as e:
            print("Error verifying transaction signature:", e)
            return False

        # Check if the sum of outputs equals the total input
        total_output = sum(out['value'] for out in tx['output'])
        input_amount = input_tx['output'][0]['value']
        if total_output != input_amount:
            print("Error: Outputs do not match input amount")
            return False

        # Check for invalid values and ensure only two outputs
        if len(tx['output']) > 2 or len(tx['output']) < 1:
            print("Error: Invalid number of transaction outputs")
            return False

        for out in tx['output']:
            if out['value'] <= 0:
                print("Error: Invalid transaction output value")
                return False

        return True
    return False


def confirm_utx_format(utx):
    # Check if all required keys are present
    required_keys = ['type', 'input', 'sig', 'output']
    for key in required_keys:
        if key not in utx:
            print(f"Error: Key '{key}' is missing in the utx transaction")
            return False

    # Check the data types and structure of the transaction
    if not isinstance(utx['type'], int):
        print("Error: 'type' must be an integer")
        return False

    if not isinstance(utx['input'], dict) or 'id' not in utx['input'] or 'n' not in utx['input']:
        print("Error: 'input' must be a dictionary containing 'id' and 'n'")
        return False

    if not isinstance(utx['sig'], str):
        print("Error: 'sig' must be a string")
        return False

    if not isinstance(utx['output'], list) or len(utx['output']) < 1 or len(utx['output']) > 2:
        print("Error: 'output' must be a list with 1 or 2 elements")
        return False

    for output in utx['output']:
        if not isinstance(output, dict) or 'value' not in output or 'pub_key' not in output:
            print("Error: Each 'output' element must be a dictionary containing 'value' and 'pub_key'")
            return False

        if not isinstance(output['value'], int) or output['value'] <= 0:
            print("Error: 'value' must be a positive integer")
            return False

        if not isinstance(output['pub_key'], str):
            print("Error: 'pub_key' must be a string")
            return False

    return True


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

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        slogan = " You can't spell \"It's a Ponzi scheme!\" without \"ZachCoin\" "
        print("=" * (int(len(slogan) / 2) - int(len(' ZachCoin™') / 2)), 'ZachCoin™',
              "=" * (int(len(slogan) / 2) - int(len('ZachCoin™ ') / 2)))
        print(slogan)
        print("=" * len(slogan), '\n')
        x = input("\t0: Print keys\n\t1: Print blockchain\n\t2: Print UTX pool\n\nEnter your choice -> ")
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
            utx_index = random.randint(0, len(client.utx) - 1)
            tx = client.utx[utx_index]
            if verify_transaction(tx, client.blockchain):
                add_coin_base_tx(tx)  # add coinbase tx
                pow, nonce = mine_transaction(tx, client.blockchain[-1])  # try to mine it
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
                

        # as well as any other additional features

        input()


if __name__ == "__main__":
    main()
