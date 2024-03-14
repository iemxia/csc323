from __future__ import annotations
import os
from dataclasses import dataclass
from Crypto.Hash import HMAC, SHA256


@dataclass(frozen=True)
class Curve:
    a: int
    b: int
    field: int

    def __str__(self):
        return f"Curve: Y^2 = X^3 + {self.a}X + {self.b} over field {self.field}"


@dataclass(frozen=True)
class EccPoint:
    curve: Curve

    def __add__(self: EccPoint, p: EccPoint) -> EccPoint:
        match self:
            case EccInfPoint():
                return p
            case EccAlgPoint():
                pass
            case _:
                raise TypeError(f"Attempting to add a non-point: {p}")
        # If we're here, self must be an EccAlgPoint
        match p:
            case EccInfPoint():
                return self
            case EccAlgPoint():
                f = self.curve.field
                if self.x == p.x and pow(self.y + p.y, 1, f) == 0:
                    return EccInfPoint(self.curve)
                if self.x == p.x and self.y == p.y:
                    m = (3 * pow(self.x, 2, f) + self.curve.a) * pow(2 * self.y, -1, f)
                else:
                    m = (p.y - self.y) * pow(p.x - self.x, -1, f)
                m = pow(m, 1, f)
                nx = pow((pow(m, 2, f) - self.x - p.x), 1, f)
                ny = pow(m * (self.x - nx) - self.y, 1, f)
                return EccAlgPoint(self.curve, x=nx, y=ny)
            case _:
                raise TypeError(f"Attempting to add a non-point: {p}")

    def __mul__(self: EccPoint, scalar: int) -> EccPoint:
        if not isinstance(scalar, int):
            raise TypeError(f"Attempting to multiply a point by a non-int: {scalar = }")
        if scalar < 0:
            raise ValueError(f"Attempting to multiply point by a negative value: {scalar = }")
        res = EccInfPoint(self.curve)
        p = self
        for b in bits(scalar):
            if b:  # odd
                res += p
            p = p + p
        return res

    def __rmul__(self: EccPoint, scalar: int) -> EccPoint:
        return self.__mul__(scalar)


class EccInfPoint(EccPoint):
    def __str__(self):
        return "Origin"

    def is_inf(self):
        return True


@dataclass(frozen=True)
class EccAlgPoint(EccPoint):
    x: int  # Second positional argument
    y: int  # Third positional argument

    def __str__(self):
        return f"({self.x}, {self.y})"

    def is_inf(self):
        return False


curve = Curve(a=-95051, b=11279326, field=233970423115425145524320034830162017933)
base_point = EccAlgPoint(curve=curve, x=182, y=85518893674295321206118380980485522083)
# Base point order
bp_order = 29246302889428143187362802287225875743


def gen_keys() -> (int, EccPoint):
    secret = pow(int.from_bytes(os.urandom(20), "little"), 1, bp_order)
    public = base_point * secret
    return (secret, public)


def get_shared_key(pub_key: EccPoint, s_key: int) -> EccPoint:
    return pub_key * s_key


def calculate_hmac(msg: str, key: EccPoint) -> HMAC.HMAC:
    h = HMAC.new(str(key).encode(), digestmod=SHA256)
    h.update(msg.encode())
    return h


def verify_msg(msg: str, hmac: str, pub_key: EccPoint, s_key: int) -> bool:
    shared_key = get_shared_key(pub_key, s_key)
    print("shared key: ", shared_key)
    print("Verifying msg: ", msg)
    h = calculate_hmac(msg, shared_key)
    print("Expected hmac: ", h.hexdigest())
    try:
        h.hexverify(hmac)
        return True
    except ValueError:
        return False


def bits(n):
    while n:
        yield n & 1
        n >>= 1
