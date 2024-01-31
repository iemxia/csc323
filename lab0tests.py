import unittest
from lab0 import *

class testLab1(unittest.TestCase):
	def testBytesToHexASCII(self):
		testString = b'foo'
		expString = '666f6f'
		self.assertEqual(expString, stringBytesToHexASCII(testString))

	def testBytesToHexASCII2(self):
		testString = b'Our string'
		expString = '4f757220737472696e67'
		self.assertEqual(expString, stringBytesToHexASCII(testString))

	def testBytesToHexASCII3(self):
		testString = bytes([0b111101])
		expString = '3d'
		self.assertEqual(expString, stringBytesToHexASCII(testString))

	def testHextoBytes(self):
		hex_string = 'deadbeef'
		exp_string = b'\xde\xad\xbe\xef'
		self.assertEqual(exp_string, hexASCIItoBytes(hex_string))

	def testHextoBytes2(self):
		hex_string = '01020e0f0f'
		exp_string = b'\x01\x02\x0e\x0f\x0f'
		self.assertEqual(exp_string, hexASCIItoBytes(hex_string))

	def testBase64toBytes(self):
		base64_string = 'aGVsbG8='
		exp_string = b'hello'
		self.assertEqual(exp_string, base64ToBytes(base64_string))

	def testBase64toBytes2(self):
		base64_string = 'Y3NjIDMyMyBsYWIgMQ=='
		exp_string = b'csc 323 lab 1'
		self.assertEqual(exp_string, base64ToBytes(base64_string))

	def testBytestoBase64(self):
		input_bytes = b'xia websterrrr'
		exp_string = 'eGlhIHdlYnN0ZXJycnI='
		self.assertEqual(exp_string, bytesToBase64(input_bytes))

	def testBytestoBase642(self):
		input_bytes = b'today is january 24 2024'
		exp_string = 'dG9kYXkgaXMgamFudWFyeSAyNCAyMDI0'
		self.assertEqual(exp_string, bytesToBase64(input_bytes))

	def testXORsamelength(self):
		input_str = b'0100100'
		key = b'1001010'
		exp_res = b'\x01\x01\x00\x01\x01\x01\x00'
		# exp_res = b'1101110'  says it should be hexadecimal bytes? I just want it to be normal binary bytes? which is right?
		self.assertEqual(exp_res, xorTwoByteStrings(input_str, key))

	def testSplitBins(self):
		keyLen = 5
		ciphertext = '12345123451234512345'
		bins = splitBins(ciphertext, keyLen)
		for i, bin in enumerate(bins):
			print(f'Bin {i+1}: {bin}')

if __name__ == '__main__':
	unittest.main()

