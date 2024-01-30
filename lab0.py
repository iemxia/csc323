import codecs
import base64

def stringBytesToHexASCII(byteString):
    # converts string of bytes to hex-encoded ASCII string
    hexString = codecs.encode(byteString, "hex")
    return hexString.decode('UTF-8')


def hexASCIItoBytes(hexASCIIString):
    # decodes hex-encoded ASCII string back to bytes
    return bytes.fromhex(hexASCIIString)


def base64ToBytes(base64String):
    # convert base64-encoded string to bytes
    base64_bytes = base64String.encode('utf-8')  # convert base64 string into bytes-like object
    res = base64.decodebytes(base64_bytes)  # base64 decode the data
    return res


def bytesToBase64(byte):
    # convert bytes to basde64-encoded string
    encoded = base64.b64encode(byte)  # base 64 encode the bytes
    res = encoded.decode('utf-8')  # decode to get the base64 encoded data using human-readable characters
    return res

