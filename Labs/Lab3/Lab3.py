import random
import crypto
import requests
from collections import namedtuple
from dataclasses import dataclass
from Crypto.Hash import HMAC, SHA256


# Point = namedtuple("Point", "x y")


class Point(namedtuple('Point', ['x', 'y'])):
	def __str__(self):
		return f"({self.x}, {self.y})"


@dataclass(frozen=True)
class Curve:
	a: int
	b: int
	field: int

	def __str__(self):
		return f"Curve: Y^2 = X^3 + {self.a}X + {self.b} over field {self.field}"


O = "Origin"


def ec_inv(P, curve):
	# Fcn to return inverse of point P on curve
	if P == O:
		return P
	return Point(P.x, pow((-P.y), 1, curve.field))


def ecc_add(P, Q, curve):
	if P == O:
		res = Q
	elif Q == O:
		res = P
	elif Q == ec_inv(P, curve):
		res = O
	else:
		# no origin stuff
		if P == Q:
			dydx = (3 * pow(P.x, 2, curve.field) + curve.a) * pow(2 * P.y, -1, curve.field)
		else:
			dydx = (Q.y - P.y) * pow(Q.x - P.x, -1, curve.field)
		dydx = pow(dydx, 1, curve.field)
		x = pow((pow(dydx, 2, curve.field) - P.x - Q.x), 1, curve.field)
		y = pow((dydx * (P.x - x) - P.y), 1, curve.field)
		res = Point(x, y)
	return res


def ecc_multiply(P, scalar, curve):
	R = O
	for b in crypto.bits(scalar):
		if b:
			R = ecc_add(R, P, curve)
		P = ecc_add(P, P, curve)
	return R


def is_quad_residue(n, p):
	# Euler's Criterion: n is a quadratic residue modulo p if n^((p-1)/2) ≡ 1 (mod p)
	return pow(n, (p - 1) // 2, p) == 1


def tonelli_shanks(n, p):
	# check if n is a quadratic residue modulo p
	if not is_quad_residue(n, p):
		return None
	q = p - 1
	s = 0
	while pow(q, 1, 2) == 0:
		q //= 2
		s += 1
	h = 2
	# Find non residue h mod p
	while is_quad_residue(h, p):
		h += 1
	g = pow(h, q, p)
	r = pow(n, (q + 1) // 2, p)
	c = pow(n, q, p)
	t = pow(n, q, p)
	m = s
	while c != 1:
		for i in range(1, m):
			if pow(c, 2 ** i, p) == 1:
				break

		b = pow(g, 2 ** (m - i - 1), int(p))
		r = pow((r * b), 1, int(p))
		c = pow((t * pow(r, 2, p)), 1, int(p))
		t = pow(r, 2, int(p))
		m = i
	return r


def gen_random_point(curve):
	while True:
		x = random.randint(0, curve.field - 1)
		n = pow((pow(x, 3, curve.field) + curve.a * x + curve.b), 1, curve.field)
		y = tonelli_shanks(n, curve.field)
		if y is not None:
			return Point(x, y)


def find_order(curve, curve_order, desired_order):
	while True:
		# get random point
		# Multiply the random point by curve order / desired order
		# make sure x,y != 0, and it is not the origin
		# check that that point * desired order is the Origin
		point = gen_random_point(curve)
		point2 = ecc_multiply(point, curve_order / desired_order)
		if point2.x != 0 and point2.y != 0 and point2 != "Origin" and (ecc_multiply(point2, desired_order) == "Origin"):
			return point2


# Admin	(96165014455133451299602130519484332678, 168520299563844318262710184803285423050)
admin_pkey = Point(96165014455133451299602130519484332678, 168520299563844318262710184803285423050)
# Bob	(177257703850715743761420820441156309751, 202681454021723094555650780401482249868)
bob_pkey = Point(177257703850715743761420820441156309751, 202681454021723094555650780401482249868)
# Curve
# Curve: Y^2 = X^3 + -95051X + 11279326 over field 233970423115425145524320034830162017933
chat_curve = Curve(a=-95051, b=11279326, field=233970423115425145524320034830162017933)
# Base Point
# (182, 85518893674295321206118380980485522083)
chat_bp = Point(182, 85518893674295321206118380980485522083)
# Base Point Order
# 29246302889428143187362802287225875743
chat_bp_order = 29246302889428143187362802287225875743
my_secret_key = random.randint(1, chat_bp_order - 1)  # generate secret key
my_public_key = ecc_multiply(chat_bp, my_secret_key, chat_curve)


def calculate_hmac(msg: str, key: Point) -> HMAC.HMAC:
	h = HMAC.new(str(key).encode(), digestmod=SHA256)
	h.update(msg.encode())
	return h


def send_msg(rec_pkey):
	s = requests.Session()
	print("My public key: ", my_public_key)
	msg = "Hi"
	shared_key = ecc_multiply(rec_pkey, my_secret_key, chat_curve)
	# binary_shared_key = str.encode(shared_key_string)
	hmac = calculate_hmac(msg, shared_key)
	url = "http://localhost:8080/submit"
	form_data = {
		'recipient': 'Bob',  #
		'message': msg,  # Your message
		'hmac': hmac,
		'pkey_x': my_public_key.x,  # Your public key X coordinate
		'pkey_y': my_public_key.y  # Your public key Y coordinate
	}
	response = s.post(url, data=form_data)
	print(response.content)


# part 4: n is b, pick curves with same a as the server code
# write own function to find prime divisors of those curves
# stole create_hmac function from crypto
# find key mod, test every number in that range, then calculate HMAC of the msg of hmac not working

if __name__ == '__main__':
	send_msg(bob_pkey)
