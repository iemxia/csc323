import codecs


def stringBytesToHexASCII(byteString):
	hex = codecs.encode(byteString, "hex")
	return hex.decode('UTF-8')


def hexASCIItoBytes(hexASCIIstring):
	return 0


def base64ToBytes(base64String):
	return 0


def bytesToBase64(bytes):
	return 0
