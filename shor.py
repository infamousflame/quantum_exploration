#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "ket-lang",
# ]
# ///

"""The real Shor's algorithm."""

from fractions import Fraction
from math import gcd
from random import randint

from ket import (
    Process, Quant,
    H, QFT, X, sample,
)
from ket.qulib.oracle import xor_oracle


def find_order(x: int, n: int) -> int | None:
    """Finds the order of x modulo n the quantum way.

    Args:
        x (int): The base.
        n (int): The modulus.

    Returns:
        int | None: The order of x modulo n, or None if no order is found.
    """
    l: int = n.bit_length()
    t: int = l << 1
    process: Process = Process()
    exponent: Quant = process.alloc(t)
    target: Quant = process.alloc(l)

    H(exponent[:l])
    X(target[0])
    xor_oracle(lambda e: pow(x, e, n))(exponent, target)
    QFT(exponent)
    values: int = sample(exponent).value
    for y in values:
        if y == 0:
            continue
        fraction: Fraction = Fraction(y, 1 << t).limit_denominator(n)
        order: int = fraction.denominator
        if order > 0 and pow(x, order, n) == 1:
            return order
    return None

def is_perfect_power(n: int) -> int | None:
    """Checks if n is a perfect power.

    Args:
        n (int): The number to check.

    Returns:
        int | None: The base if n is a perfect power, None otherwise.
    """
    for exp in range(2, n.bit_length() + 1):
        lo, hi = 2, n
        while lo <= hi:
            mid = lo + hi >> 1
            power: int = pow(mid, exp)
            if power == n:
                return mid
            elif power < n:
                lo = mid + 1
            else:
                hi = mid - 1
    return None


def shor(n: int, max_attempts: int = 1) -> int:
    """Factors an integer using Shor's algorithm.

    Args:
        n (int): The integer to factor.
        max_attempts (int): The maximum number of attempts to find a factor.

    Returns:
        int: A factor of n.
    """
    if n < 2:
        return 1
    if not n & 1:
        return 2
    if (base := is_perfect_power(n)) is not None:
        return base

    for _ in range(max_attempts):
        x: int = randint(2, n - 1)
        g: int = gcd(x, n)
        if g != 1:
            return g
        r: int = find_order(x, n)
        if r is None or r & 1:
            continue
        half_power: int = pow(x, r >> 1, n)
        if half_power == n - 1:
            continue
        for x in (1, -1):
            if (factor := gcd(half_power + x, n)) not in (1, n):
                return factor
    return 1


def main() -> None:
    large_num: int = int(input("Enter large integer to factor: "))
    factor: int = shor(large_num, 5)
    print(f"Shor's algorithm found a factor: {factor}")
    print(f"{large_num} = {factor} * {large_num // factor} is {large_num % factor == 0},")
    print(
        "we have indeed found a nontrivial factor!"
        if large_num % factor == 0 and factor != 1 else
        "we have not found a nontrivial factor yet."
    )


if __name__ == "__main__":
    main()
