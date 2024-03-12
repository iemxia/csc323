import unittest
from Lab3 import *

class MyTestCase(unittest.TestCase):
	def test_ec_add(self):
		curve = Curve(a=3, b=8, field=13)
		P = Point(9, 7)
		Q = Point(1, 8)
		R = ecc_add(P, Q, curve)
		self.assertEqual(R, Point(2, 10))

	def test_ec_add2(self):
		curve = Curve(a=3, b=8, field=13)
		P = Point(9, 7)
		Q = Point(9, 7)
		R = ecc_add(P, Q, curve)
		self.assertEqual(R, Point(9, 6))

	def test_ec_add3(self):
		curve = Curve(a=3, b=8, field=13)
		P = Point(12, 11)
		Q = Point(12, 2)
		R = ecc_add(P, Q, curve)
		self.assertEqual(R, "Origin")

	def test_ec_mul(self):
		curve = Curve(a=3, b=8, field=13)
		P = Point(12, 11)
		scalar = 3
		R = ecc_multiply(P, scalar, curve)
		self.assertEqual(R, Point(9, 6))

	def test_ec_mul2(self):
		curve = Curve(a=3, b=8, field=13)
		P = Point(9, 6)
		scalar = 5
		R = ecc_multiply(P, scalar, curve)
		self.assertEqual(R, Point(9, 7))


if __name__ == '__main__':
	unittest.main()
