class MersenneTwister:
    def __init__(self, seed, w=32, n=624, m=397, r=31, a=0x9908B0DF, u=11, d=0xFFFFFFFF, s=7, b=0x9D2C5680, t=15, c=0xEFC60000, l=18):
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

        self.index = n
        self.MT = [0] * n

        self.lower_mask = (1 << r) - 1
        self.upper_mask = (1 << w) - self.lower_mask

        self.seed_mt(seed)

    def seed_mt(self, seed):
        self.index = self.n
        self.MT[0] = seed
        for i in range(1, self.n):
            self.MT[i] = (self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w-2))) + i) & ((1 << self.w) - 1)

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
        return y & ((1 << self.w) - 1)

    def twist(self):
        for i in range(self.n):
            x = (self.MT[i] & self.upper_mask) | (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x % 2 != 0:
                xA ^= self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0


# Example Usage:
# Initialize the Mersenne Twister with a seed
mt = MersenneTwister(seed=5489)

# Generate random numbers
for _ in range(10):
    print(mt.extract_number())
