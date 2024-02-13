def pad(stream, block_size):
    pad_len = block_size - (len(stream) % block_size)
    return stream + bytes([pad_len] * pad_len)


def unpad(stream, block_size):
    if len(stream) % block_size != 0:
        raise ValueError('stream length invalid, must be multiple of block size')

    for i in range(block_size, 0, -1):
        guessed_padding = stream[-i:]
        padding_vals = set(guessed_padding)
        if len(padding_vals) == 1 and padding_vals.pop() == i:
            return stream[:-i]
    raise ValueError('No pad')



