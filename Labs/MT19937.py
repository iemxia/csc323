# Mersenne Twister MT 19937
import time

import lab0
import base64


class MT19937:
	w, n = 32, 624
	f = 1812433253
	m, r = 397, 31
	a = 0x9908B0DF
	d, b, c = 0xFFFFFFFF, 0x9D2C5680, 0xEFC60000
	u, s, t, l = 11, 7, 15, 18

	def __init__(self, seed=0):
		# self.index = n + 1
		# self.MT = [0] * n
		#
		self.lower_mask = (1 << self.r) - 1
		self.upper_mask = (1 << self.w) - self.lower_mask
		self.MT = [0] * MT19937.n
		self.cnt = 0
		if isinstance(seed, bytes):
			seed = int.from_bytes(seed, "big")
		self.seed_mt(seed)

	def seed_mt(self, seed):
		# self.index = self.n
		self.MT[0] = seed
		for i in range(1, self.n):
			self.MT[i] = (MT19937.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (MT19937.w - 2))) + i) & (
					(1 << MT19937.w) - 1)

	def extract_number(self):
		if self.cnt >= self.n:
			if self.cnt > self.n:
				raise ValueError("Generator was never seeded")
			self.twist()

		y = self.MT[self.cnt]
		y ^= (y >> self.u)
		y ^= (y << self.s) & self.b
		y ^= (y << self.t) & self.c
		y ^= y >> self.l

		self.cnt += 1
		return y & 0xffffffff

	def twist(self):
		for i in range(self.n):
			x = (self.MT[i] & self.upper_mask) + \
			    (self.MT[(i + 1) % self.n] & self.lower_mask)
			xA = x >> 1
			if (x % 2) != 0:
				xA ^= self.a
			self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
		self.cnt = 0


rshift = lambda val, n: (val % 0x100000000) >> n


def inv_right(y, shiftlen):
	i = 0
	res = 0
	while i * shiftlen < 32:
		chunk = y & rshift(-1 << (32 - shiftlen), shiftlen * i)
		y ^= rshift(chunk, shiftlen)
		res |= chunk
		i += 1
	return res


def inv_left(y, shiftlen, mask):
	i = 0
	res = 0
	while i * shiftlen < 32:
		chunk = y & rshift(-1, 32 - shiftlen) << (shiftlen * i)
		y ^= (chunk << shiftlen) & mask
		res |= chunk
		i += 1
	return res


def unmix(x):
	x = inv_right(x, MT19937.l)
	x = inv_left(x, MT19937.t, MT19937.c)
	x = inv_left(x, MT19937.s, MT19937.b)
	x = inv_right(x, MT19937.u)
	return x


def compare_RNGs(r1, r2, lim=1000):
	for i in range(lim):
		if r1.extract_number() != r2.extract_number():
			print("RNGs not the same; stopped at index ", i)
			return
	print("From inspecting the first ", lim, " numbers, the two RNGs are the same.")


# function to take in file of tokens, decode them and split them, returns list of all tokens
def decodeTokens(file_path):
	alltokens = []
	with open("tokens.txt", "r") as file:
		for token in file:  # go through each line
			decodedToken8 = lab0.base64ToBytes(token)  # decode base64 string to bytes
			decodedToken8 = decodedToken8.decode('utf-8')  # back to string
			indivTokens = decodedToken8.split(":")  # split by colons
			for indivToken in indivTokens:
				alltokens.append(int(indivToken))
		return alltokens


def clone(MT):
	cloneMT = MT19937(0)
	for i in range(624):
		cloneMT.MT[i] = unmix(MT.extract_number())
	cloneMT.twist()
	return cloneMT


def compareMT(mt1, mt2, lim=624):
	for i in range(lim):
		if (mt1.extract_number() != mt2.extract_number()):
			print("Not the same, stopped at index ", i)
			return
	print("From inspecting the first ", lim, " numbers, the two RNGs are the same.")


def generate_next_token(MT):
	# Generate a 256-bit random number as our reset tokwn
	# by concatentating 8, 32-bit integers with colons
	token = str(MT.extract_number())
	for i in range(7):
		token += ":" + str(MT.extract_number())
	return (base64.b64encode(token.encode('utf-8'))).decode()


def main():
	# testing
	# testMT = MT19937(100)
	# cloneMT = clone(testMT)
	# compareMT(testMT, cloneMT)
	tokens = decodeTokens("tokens.txt")
	serverMT = MT19937(0)  # create MT object for server
	serverMT.MT = tokens
	cloneServer = clone(serverMT)
	nextTokens = 2
	predicted = []
	for i in range(nextTokens):
		predicted.append(generate_next_token(cloneServer))
	print(predicted)
	# reset string:
	# localhost:8080/reset?token=
if __name__ == '__main__':
	main()
