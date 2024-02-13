# use AES primitive, high crypto dome ?
# create AES object, specify mode (ECB), but only ever encrypt one block at a time
# never pass it more than one block at a time
# how to get parts and then change and submit, w3c site, do encoding correctly ('utf-8')


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


