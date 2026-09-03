#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "ket-lang",
# ]
# ///

"""The order finding subroutine from Shor's algorithm."""

from fractions import Fraction

from ket import (
    Process, Quant,
    H, QFT, measure, sample,
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
    t: int = 2 * l + 3
    process: Process = Process()
    exponent: Quant = process.alloc(t)
    target: Quant = process.alloc(l)

    H(exponent)
    xor_oracle(lambda e: pow(x, e, n))(exponent, target)
    _ = measure(target)
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


def main() -> None:
    x: int = int(input("Enter x: "))
    n: int = int(input("Enter n: "))
    order: int | None = find_order(x, n)
    if order is None:
        print("No order found.")
        return
    print(f"{x}^{order} mod {n} = 1 is {pow(x, order, n) == 1}.")


if __name__ == "__main__":
    main()
