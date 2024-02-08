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


def get_bit(x, i):
    return x & (1 << (MT19937.w - i - 1))


def reverse_bits(x):
    rev = 0
    for i in range(MT19937.w):
        rev = (rev << 1)
        if x > 0:
            if x & 1 == 1:
                rev = (rev ^ 1)
            x = (x >> 1)
    return rev


def inv_left(y, a, b):
    return reverse_bits(inv_right(reverse_bits(y), a, reverse_bits(b)))


def inv_right(y, a, b):
    x = 0
    for i in range(MT19937.w):
        if i < a:
            x |= get_bit(y, i)
        else:
            x |= (get_bit(y, i) ^ ((get_bit(x, i - a) >> a) & get_bit(b, i)))
    return x


def unmix(y):
    x = y
    x = inv_right(x, MT19937.l, ((1 << MT19937.w) - 1))
    x = inv_left(x, MT19937.t, MT19937.c)
    x = inv_left(x, MT19937.s, MT19937.b)
    x = inv_right(x, MT19937.u, MT19937.d)
    return x


def compare_RNGs(r1, r2, lim=1000):
    for i in range(lim):
        if r1.extract_number() != r2.extract_number():
            print("RNGs not the same; stopped at index ", i)
            return
    print("From inspecting the first ", lim, " numbers, the two RNGs are the same.")


def main():
    rng1 = MT19937(0)
    rng2 = MT19937(1)
    for i in range(MT19937.n):
        rng2.MT[i] = unmix(rng1.extract_number())
    rng2.twist()
    compare_RNGs(rng1, rng2)


if __name__ == '__main__':
    main()
