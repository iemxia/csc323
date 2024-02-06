# Mersenne Twister MT 19937
import self as self


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
            self.MT[i] = (MT19937.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (MT19937.w - 2))) + i) & ((1 << MT19937.w) - 1)

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
