#!/usr/bin/env python3

import hashlib
from typing import Tuple

import utils
from fastecdsa.point import Point
from fastecdsa.curve import Curve


class CryptoError(Exception):
    pass


SecureCurve = Curve(
    p  = 0xa0fca03a870f6e3fc52aeef0d61f198fddc7a2c6bd414b3e5a1afc5a4a82009d,
    a  = 0x3458be7671950c6b01bed2734056c9217012fd1f07ee085afd504b412061e63c,
    b  = 0x0,
    q  = 0xa0fca03a870f6e3fc52aeef0d61f19915ca241a1b2e1cb33cb1434415514a902,
    gx = 0x6a0ea6b596c2adb773a821e9c6799a0e8ab03e355560a64ac1eecb6df8bd92ba,
    gy = 0x9e337b7d04c686771d18cd12a9b5174cb5b134be7ab09176c418bce4ff265de9,
    oid = b's\xee\xccur\xee',
    name = 'SecureCurve',
)


def hash(data: bytes) -> int:
    return int.from_bytes(hashlib.sha3_256(data).digest(), 'big')


def generate_keypair() -> Tuple[str, str]:
    d = utils.generate_random_number(1, SecureCurve.q - 1)
    Q = d * SecureCurve.G

    return (
        utils.serialize_number(d),
        utils.serialize_numbers_sequence(Q.x, Q.y),
    )


def get_public_key(private_key: str) -> str:
    try:
        d = utils.deserialize_number(private_key)
    except utils.SerializationError as e:
        raise CryptoError(f'invalid private key: {e}')

    Q = d * SecureCurve.G

    return utils.serialize_numbers_sequence(Q.x, Q.y)


def sign(message: bytes, private_key: str) -> str:
    try:
        d = utils.deserialize_number(private_key)
    except utils.SerializationError as e:
        raise CryptoError(f'invalid private key: {e}')

    k = utils.generate_random_number(1, SecureCurve.q - 1)
    r = (k * SecureCurve.G).x
    h = hash(utils.int_to_bytes(r) + message)
    s = k - h * d

    return utils.serialize_numbers_sequence(r, s)


def verify(message: bytes, public_key: str, signature: str) -> bool:
    try:
        r, s = utils.deserialize_numbers_sequence(signature)
    except utils.SerializationError:
        return False

    try:
        x, y = utils.deserialize_numbers_sequence(public_key)
        Q = Point(x, y, curve=SecureCurve)
    except utils.SerializationError as e:
        raise CryptoError(f'invalid public key: {e}')

    h = hash(utils.int_to_bytes(r) + message)
    u = h * Q + s * SecureCurve.G

    return u.x == r
