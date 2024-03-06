from collections import namedtuple
Point = namedtuple("Point", "x y")
O = 'Origin'


def inv_mod_p(x, curve):
    # Return inverse for x mod curve.field, assuming x not divisble by the field
    if pow(x, 1, curve.field) == 0:
        raise ZeroDivisionError("Cannot inverse")
    return pow(x, curve.field - 2, curve.field)

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
    elif Q == ec_inv(P):
        res = O
    else:
        # no origin stuff
        if P == Q:
            dydx = (3 * P.x ** 2 + curve.a) * inv_mod_p(2 * P.y)
        else:
            dydx = (Q.y - P.y) * inv_mod_p(Q.x - P.x)
        x = pow((dydx ** 2 - P.x - Q.x), 1, curve.field)
        y = pow((dydx * (P.x - x) - P.y), 1, curve.field)
        result = Point(x, y)
    return result

class Curve:
    a: int
    b: int
    field: int

    def __str__(self):
        return f"Curve: Y^2 = X^3 + {self.a}X + {self.b} over field {self.field}"

