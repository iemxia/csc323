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



if __name__ == '__main__':
	unittest.main()

