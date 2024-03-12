from collections import namedtuple
from dataclasses import dataclass
Point = namedtuple("Point", "x y")
O = "Origin"


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
