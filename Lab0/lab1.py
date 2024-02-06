from lab0 import bytesToBase64, base64ToBytes
import random
import time


class MersenneTwister:
    def __init__(self, c_seed=0, w=32, n=624, m=397, r=31, a=0x9908B0DF, u=11, d=0xFFFFFFFF, s=7, b=0x9D2C5680, t=15,
                 c=0xEFC60000, l=18, f=1812433253):
        self.w = w
        self.n = n
        self.m = m
        self.r = r
        self.a = a
        self.u = u
        self.d = d
        self.s = s
        self.b = b
        self.t = t
        self.c = c
        self.l = l
        self.f = f
        self.index = n + 1
        self.MT = [0] * n

        self.lower_mask = (1 << r) - 1
        self.upper_mask = (1 << w) - self.lower_mask
        self.c_seed = c_seed.to_bytes(4, 'big')

    def seed_mt(self, seed):
        self.index = self.n
        self.MT[0] = seed
        for i in range(1, self.n):
            temp = self.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (self.w - 2))) + i
            self.MT[i] = temp & 0xffffffff

    def extract_number(self):
        if self.index >= self.n:
            if self.index > self.n:
                raise ValueError("Generator was never seeded")
            self.twist()

        y = self.MT[self.index]
        y ^= (y >> self.u) & self.d
        y ^= (y << self.s) & self.b
        y ^= (y << self.t) & self.c
        y ^= y >> self.l

        self.index += 1
        return y & 0xffffffff

    def twist(self):
        for i in range(self.n):
            x = (self.MT[i] & self.upper_mask) + \
                (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if (x % 2) != 0:
                xA ^= self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def random(self):
        # return uniform distribution in [0,1)
        return self.extract_number() / 4294967296  # which is 2**w

    def randint(self, a, b):
        # return random int in [a, b)
        n = self.random()
        return int(n / (1 / (b - a)) + a)


def oracle():
    wait = random.randint(5, 60)
    print(f"waiting {wait} seconds")
    time.sleep(wait)
    seed = int(time.time())  # using current UNIX timestamp
    mt = MersenneTwister(seed)
    mt.seed_mt(seed)
    print("Actual seed: ", seed)
    wait2 = random.randint(5, 60)
    print(f"waiting {wait2} seconds")
    time.sleep(wait2)
    output = (mt.extract_number() & 0xFFFFFFFF).to_bytes(4, 'big')
    return bytesToBase64(output)


def mt19937TimeBreak(outputBase64):
    # decode base64 to bytes
    outputBytes = base64ToBytes(outputBase64)
    outputInt = int.from_bytes(outputBytes, byteorder='big')
    curTime = int(time.time())
    # go through all possible seeds btwn (current time - max sleep time) and (cur time - min sleep time)
    for seed in range(curTime - 60, curTime - 5):
        # seed with the key
        mt = MersenneTwister(seed)
        mt.seed_mt(seed)
        output = mt.extract_number() & 0xFFFFFFFF
        # find matching output and return the seed
        if output == outputInt:
            return seed
    print("no seed found")


def main():
    mt = MersenneTwister(123)
    mt.seed_mt(123)
    print(mt.random())
    print(mt.randint(1, 10))
    print(mt.randint(1, 10))
    print(mt.randint(1, 10))
    print(mt.randint(1, 10))

    print("seed w 123 again")
    mt2 = MersenneTwister(123)
    mt2.seed_mt(123)
    print(mt2.random())
    print(mt2.randint(1, 10))
    print(mt2.randint(1, 10))
    print(mt2.randint(1, 10))
    print(mt2.randint(1, 10))
    oracleOutput = oracle()
    print(oracleOutput)
    print("Guessed seed: ", mt19937TimeBreak(oracleOutput))


if __name__ == "__main__":
    main()
