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
		self.w_bit_mask = (1 << self.w) - 1
		self.lower_mask = (1 << self.r) - 1
		self.upper_mask = (1 << self.w) - self.lower_mask
		self.MT = [0] * MT19937.n
		self.cnt = 0
		if isinstance(seed, bytes):
			seed = int.from_bytes(seed, "big")
		self.seed_mt(seed)

	def init_from_state(self, state):
		self.MT = state
		self.cnt = self.n
		return self

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
		y ^= (y >> self.u) & self.d
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


def bitlistToInt(bit_list):
	# converts list of bits to an integer
	# iterate through list and shift current integer left by 1 pos and then perform XOR w current bit
	out = 0
	for bit in bit_list:
		out = (out << 1) | bit
	return out


def intToBitlist(num):
	# converts integer into list of bits
	# convert integer num into binary string of length 32
	return [1 if digit == '1' else 0 for digit in format(num, '032b')]


def inv_right(y, shift):
	# inverse right shift on int y by specified number shift
	out = intToBitlist(y)  # first convert integer y into list of bits
	for idx in range(shift, 32):  # go through all 32 positions
		out[idx] = out[idx] ^ out[idx - shift]  # perform XOR btwn each bit and the corresponding bit 'shift' # of
	# positions to the left
	return bitlistToInt(out)


def inv_left(y, shift, mask):
	# performs inverse left shift on y and specified # of positions 'shift', using bitmask 'mask'
	mask = intToBitlist(mask)
	out = intToBitlist(y)
	# goes through bits from pos 32 - shift - 1 to pos 0 (basically in reverse)
	for idx in range(32 - shift - 1, -1, -1):
		# do XOR between each bit and (corresponding bit 'shift' positions to the right ANDed w/ corresponding bit of
		# the mask)
		out[idx] = out[idx] ^ (out[idx + shift] & mask[idx])
	return bitlistToInt(out)


def unmix(x):
	# call helper function to do the extract_number fcn in reverse
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
def decodeTokens():
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
	state = []
	for i in range(624):
		orig = MT.extract_number()
		unmixed = unmix(orig)
		state.append(unmixed)
	cloneMT = MT19937()
	cloneMT.MT = state
	print("Cloned state: ", cloneMT.MT)
	cloneMT.twist()
	return cloneMT


def compareMT(mt1, mt2, lim=624):
	for i in range(lim):
		if mt1.extract_number() != mt2.extract_number():
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
	testMT = MT19937(100)
	print("original state: ", testMT.MT)
	cloneMT = clone(testMT)
	print("next orig num: ", testMT.extract_number())
	print("next clone orig num: ", cloneMT.extract_number())
	compareMT(testMT, cloneMT)
	tokens = decodeTokens()  # all 624 tokens from the server Mersenne Twister output
	print("Tokens: ", tokens)
	state = [0] * 624  # state variable to hold all the new states
	for i in range(len(tokens)):
		state[i] = unmix(tokens[i])
	print("State: ", state)
	cloneServer = MT19937()
	cloneServer.MT = state  # set clone's state
	for keyNum in range(79):  # generate all the keys that we had before, plus ONE (for admin)
		key = generate_next_token(cloneServer)
		if keyNum == 78:
			print(f"Key {keyNum + 1}: {key}")


# reset string:
# localhost:8080/reset?token=
if __name__ == '__main__':
	main()
