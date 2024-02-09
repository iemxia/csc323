from lab0 import bytesToBase64, base64ToBytes
import random
import time


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
        # self.c_seed = c_seed.to_bytes(4, 'big')
        self.MT = [0] * MT19937.n
        self.cnt = 0
        self.seed_mt(seed)

    def seed_mt(self, seed):
        # self.index = self.n
        self.MT[0] = seed
        for i in range(1, self.n):
            self.MT[i] = (MT19937.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (MT19937.w - 2))) + i) & ((1 << MT19937.w) - 1)

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

    def random(self):
        # return uniform distribution in [0,1)
        return self.extract_number() / 4294967296  # which is 2**w

    def randint(self, a, b):
        # return random int in [a, b)
        n = self.random()
        return int(n / (1 / (b - a)) + a)


def oracle():
    wait = random.randint(5, 60)  # random wait time
    print(f"waiting {wait} seconds")
    time.sleep(wait)  # wait
    seed = int(time.time())  # using current UNIX timestamp
    mt = MT19937(seed)  # seed w/ MersenneTwister
    print("Actual seed: ", seed)
    wait2 = random.randint(5, 60)  # random wait time
    print(f"waiting {wait2} seconds")
    time.sleep(wait2)  # wait
    output = (mt.extract_number() & 0xFFFFFFFF).to_bytes(4, 'big')  # get number
    return bytesToBase64(output)  # return number base64 encoded


def mt19937TimeBreak(outputBase64):
    # decode base64 to bytes
    outputBytes = base64ToBytes(outputBase64)
    outputInt = int.from_bytes(outputBytes, byteorder='big')
    curTime = int(time.time())  # get current time
    # go through all possible seeds btwn (current time - max sleep time) and (cur time - min sleep time)
    for seed in range(curTime - 60, curTime - 5):
        # seed with the key
        mt = MT19937(seed)
        mt.seed_mt(seed)  # get output with every possible seed
        output = mt.extract_number() & 0xFFFFFFFF
        # find matching output and return the seed
        if output == outputInt:
            return seed
    print("no seed found")


def main():
    print("seed MT w 123")
    mt = MT19937(123)
    mt.seed_mt(123)
    print(mt.random())
    print(mt.randint(1, 10))
    print(mt.randint(1, 10))
    print(mt.randint(1, 10))
    print("seed w 123 again")
    mt2 = MT19937(123)
    mt2.seed_mt(123)
    print(mt2.random())
    print(mt2.randint(1, 10))
    print(mt2.randint(1, 10))
    print(mt2.randint(1, 10))
    # call oracle function
    oracleOutput = oracle()
    print(oracleOutput)
    # guess the seed
    print("Guessed seed: ", mt19937TimeBreak(oracleOutput))


if __name__ == "__main__":
    main()
