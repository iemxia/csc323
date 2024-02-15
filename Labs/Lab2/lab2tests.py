import unittest
from lab2 import *


class MyTestCase(unittest.TestCase):
	def test_pad(self):
		msg = b'Hello'
		block_size = 8
		expected = b'Hello\x03\x03\x03'
		self.assertEqual(pad(msg, block_size), expected)

	def test_pad_fullmsg(self):
		msg = b'12345678'
		block_size = 8
		expected = b'12345678\x08\x08\x08\x08\x08\x08\x08\x08'
		self.assertEqual(pad(msg, block_size), expected)

	def test_unpad(self):
		to_unpad = b'Hello\x03\x03\x03'
		block_size = 8
		msg = b'Hello'
		self.assertEqual(unpad(to_unpad, block_size), msg)

	def test_unpad_wrongsize(self):
		to_unpad = b'Hello'
		block_size = 8
		with self.assertRaises(ValueError):
			unpad(to_unpad, block_size)

	def test_unpad_weirdpadding(self):
		to_unpad = b'Hello\x03\x02\x01'
		block_size = 8
		msg = b'Hello\x03\x02'
		self.assertEqual(unpad(to_unpad, block_size), msg)

	def test_unpadweird(self):
		to_unpad = b'Hell\x03\x03\x03\x03'
		block_size = 8
		msg = b'Hell\x03'
		self.assertEqual(unpad(to_unpad, block_size), msg)

	def test_unpadfullmsg(self):
		msg = b'12345678'
		block_size = 8
		to_unpad = b'12345678\x08\x08\x08\x08\x08\x08\x08\x08'
		self.assertEqual(unpad(to_unpad, block_size), msg)


if __name__ == '__main__':
	unittest.main()
