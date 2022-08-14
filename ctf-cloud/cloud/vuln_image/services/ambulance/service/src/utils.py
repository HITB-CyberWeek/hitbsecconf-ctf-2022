#!/usr/bin/env python3

import os
import base64
from typing import List

import gmpy2


class SerializationError(Exception):
    pass


def b64encode(data: bytes) -> str:
    return base64.b64encode(data, b'_.').strip(b'=').decode()


def b64decode(data: str) -> bytes:
    try:
        return base64.b64decode(data + '=' * 8, b'_.')
    except Exception as e:
        raise SerializationError(f'failed to decode base64: {e}')


def int_to_bytes(number: int) -> bytes:
    return gmpy2.to_binary(gmpy2.mpz(number))


def bytes_to_int(data: bytes) -> int:
    try:
        return int(gmpy2.from_binary(data))
    except Exception as e:
        raise SerializationError(f'failed to parse int: {e}')


def generate_random_number(lower: int, upper: int) -> int:
    if lower == upper:
        return lower

    if lower > upper:
        lower, upper = upper, lower

    range = upper - lower + 1
    random_bytes = os.urandom(1 + range.bit_length() // 8)
    random_number = int.from_bytes(random_bytes, 'big')
    
    return lower + random_number % range


def serialize_numbers_sequence(*numbers: int) -> str:
    parts = []

    for number in numbers:
        data = int_to_bytes(number)
        length_data = len(data).to_bytes(2, 'big')

        parts.append(length_data)
        parts.append(data)

    return b64encode(b''.join(parts))


def deserialize_numbers_sequence(data: str) -> List[int]:
    data = b64decode(data)
    numbers = []

    while len(data) > 0:
        length_data, data = data[:2], data[2:]

        if len(length_data) != 2:
            raise SerializationError("length is too short")

        length = int.from_bytes(length_data, 'big')

        if len(data) < length:
            raise SerializationError("data is too short")

        number_data, data = data[:length], data[length:]

        number = bytes_to_int(number_data)
        numbers.append(number)

    return numbers


def serialize_number(number: int) -> str:
    return serialize_numbers_sequence(number)


def deserialize_number(data: str) -> int:
    if len(data) == 0:
        raise SerializationError("data is empty")

    return deserialize_numbers_sequence(data)[0]
