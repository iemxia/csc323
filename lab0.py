import codecs
import base64
import string
import binascii


# Task 1
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


# Task 2
def xorTwoByteStrings(input_str, key):
    # make the key and input into bytes
    input_str = bytes.fromhex(input_str)
    # key = bytes.fromhex(key)
    # repeat key so that it matches the length of the input string
    # question: is it a string of actual bytes? what does it mean may or may not be in the ASCII space?
    new_key = (key * (len(input_str) // len(key) + 1))[:len(input_str)]
    # use zip with for loop to create tuple of bits x and y from input string and key and do the XOR
    result = bytes(x ^ y for x, y in zip(input_str, new_key))
    # convert result to hex encoded string
    #result_hex = result.hex()
    return result


def englishAnalysis(text):
    # English letter frequencies pulled from Wikipedia
    frequencies = {
        'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51,
        'i': 6.97, 'n': 6.75, 's': 6.33, 'h': 6.09,
        'r': 5.99, 'd': 4.25, 'l': 4.03, 'c': 2.78,
        'u': 2.76, 'm': 2.41, 'w': 2.36, 'f': 2.23,
        'g': 2.02, 'y': 1.97, 'p': 1.93, 'b': 1.29,
        'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15,
        'q': 0.10, 'z': 0.07
    }
    # make lowercase
    text = text.lower()
    # Get obs letter frequencies
    obs_freq = {char: text.count(char) / len(text) for char in string.ascii_lowercase}
    # Get the sum of squared differences between obs and exp frequencies (Chi squared method statistics)
    score = sum((obs_freq[char] - frequencies[char])**2 for char in string.ascii_lowercase)
    return score


def findMessage(file_path):
    with open(file_path, 'r') as file:
        for hex_string in file:  # go through file line by line
            # hex_string = hex_string.strip()  # remove leading/trailing white space

            for key in range(256):  # try all possible keys (2^8)
                xorResult = xorTwoByteStrings(hex_string, key.to_bytes(1, 'big'))  # xor with the key
                # decrypted = stringBytesToHexASCII(xorResult)  # turn bytes to hex ASCII
                try:
                    decoded = xorResult.decode('utf-8')  # decode
                except UnicodeDecodeError:
                    continue
                score = englishAnalysis(decoded)  # score each

                if score < 651:  # if score is less than 10, print out that decrypted message
                    print(f"Key: {key.to_bytes(1, 'big')}, Decrypted Text: {decoded}")

                # Key: b'\x7f', Decrypted Text: Out on bail, fresh out of jail, California dreaming
                # Soon as I step on the scene, I'm hearing ladies screaming


def main():
    findMessage('Lab0.TaskII.B.txt')


if __name__ == "__main__":
    main()
