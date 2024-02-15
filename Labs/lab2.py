# use AES primitive, high crypto dome ?
# create AES object, specify mode (ECB), but only ever encrypt one block at a time
# never pass it more than one block at a time
# how to get parts and then change and submit, w3c site, do encoding correctly ('utf-8')
from Crypto.Cipher import AES
import base64

def pad(msg, block_size):
    pad_len = block_size - (len(msg) % block_size)  # get how many padding bytes we'll need
    return msg + bytes([pad_len] * pad_len)  # add that value as padding to end of msg


def unpad(msg, block_size):
    if len(msg) % block_size != 0:
        raise ValueError('stream length invalid, must be multiple of block size')
    pad_len = msg[-1]  # for a valid padding, the last byte value will be equal to the number of padding bytes
    # that exist
    for i in range(1, pad_len + 1):  # go through the msg backwards pad length positions
        # print(f'Stream byte: {msg[-i]} at pos: {-i}')
        pos_pad = msg[-i]  # get possible pos pad
        if pos_pad != pad_len:  # check that the byte is equal to the pad length number
            raise ValueError('invalid padding')
    msg = msg[:-i]  # cut the pad byte off
    return msg


def ecb_encrypt(key, plaintext):
    block_size = AES.block_size
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad(plaintext, block_size)
    ciphertext = cipher.encrypt(padded)
    return ciphertext


def ecb_decrypt(key, ciphertext, pad_scheme):
    block_size = AES.block_size
    if len(ciphertext) % block_size != 0:  # not a multiple of the block size
        raise ValueError("Must be multiple of block size")
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(ciphertext)
    if pad_scheme == "pkcs7":
        plaintext = unpad(decrypted, block_size)
    else:
        plaintext = ansi_x_unpad(decrypted, block_size)
    return plaintext


def ansi_x_unpad(msg, block_size):
    pad_len = msg[-1]
    if pad_len == 0 or pad_len > block_size:
        raise ValueErorr("Invalid Padding")
    for i in range(1, pad_len):
        if msg[-i -1] != 0:
            raise ValueError("Invalid padding")
    unpadded = msg[:-pad_len]
    return unpadded


def main():
    with open("Lab2.TaskII.A.txt", "r") as file:
        base64_ciphertext = file.read()

    ciphertext = base64.b64decode(base64_ciphertext)
    key = b'CALIFORNIA LOVE!'
    plaintext = ecb_decrypt(key, ciphertext, "pkcs7")
    plaintext_str = plaintext.decode('ascii')
    print("Decrypted plaintext: ", plaintext_str)


if __name__ == "__main__":
    main()
