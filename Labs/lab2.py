# use AES primitive, high crypto dome ?
# create AES object, specify mode (ECB), but only ever encrypt one block at a time
# never pass it more than one block at a time
# how to get parts and then change and submit, w3c site, do encoding correctly ('utf-8')


def pad(stream, block_size):
    pad_len = block_size - (len(stream) % block_size)  # get how many padding bytes we'll need
    return stream + bytes([pad_len] * pad_len)  # add that value as padding to end


def unpad(stream, block_size):
    if len(stream) % block_size != 0:
        raise ValueError('stream length invalid, must be multiple of block size')

    for i in range(block_size, 0, -1):
        guessed_padding = stream[-i:]
        padding_vals = set(guessed_padding)
        if len(padding_vals) == 1 and padding_vals.pop() == i:
            return stream[:-i]
    raise ValueError('No pad')



