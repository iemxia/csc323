from collections import namedtuple
from dataclasses import dataclass
Point = namedtuple("Point", "x y")
O = "Origin"
import random


@dataclass(frozen=True)
class Curve:
    a: int
    b: int
    field: int

    def __str__(self):
        return f"Curve: Y^2 = X^3 + {self.a}X + {self.b} over field {self.field}"


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
    while scalar > 0:
        if pow(int(scalar), 1, 2) == 1:
            R = ecc_add(R, P, curve)
        P = ecc_add(P, P, curve)
        scalar = scalar / 2
    return R


def is_quad_residue(n, p):
    # Euler's Criterion: n is a quadratic residue modulo p if n^((p-1)/2) ≡ 1 (mod p)
    return pow(n, (p-1) // 2, p) == 1


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

        b = pow(g, 2 ** (m - i - 1), p)
        r = pow((r * b), 1, p)
        c = pow((t * pow(r, 2, p)), 1, p)
        t = pow(r, 2, p)
        m = i

    return r


def gen_random_point(curve):
    while True:
        x = random.randint(0, curve.field -1)
        n = pow((pow(x, 3, curve.field) + curve.a * x + curve.b), 1, curve.field)
        y = tonelli_shanks(n, curve.field)
        if y is not None:
            return Point(x, y)