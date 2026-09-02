#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "ket-lang",
# ]
# ///

from math import pi, sqrt
from typing import Callable, Iterator

from ket import (
    Process, Quant,
    H, X, ctrl, measure,
)


def bit_iter(target: int) -> Iterator[bool]:
    mask: int = 1 << target.bit_length() - 1
    while mask:
        yield bool(target & mask)
        mask >>= 1


def big_Z(qubits: Quant) -> None:
    *controls, target = qubits
    H(target)
    if controls:
        ctrl(controls, X)(target)
    else:
        X(target)
    H(target)


def phase_oracle(target: int) -> Callable[[Quant], None]:
    def _phase_oracle(qubits: Quant) -> None:
        for qubit, bit in zip(qubits, bit_iter(target)):
            if not bit:
                X(qubit)

        big_Z(qubits)

        for qubit, bit in zip(qubits, bit_iter(target)):
            if not bit:
                X(qubit)

    return _phase_oracle


def diffuser(qubits: Quant) -> None:
    H(qubits)
    X(qubits)
    big_Z(qubits)
    X(qubits)
    H(qubits)


def grover(phase_oracle: Callable[[Quant], None], num_qubits: int) -> int:
    process: Process = Process()
    qubits: Quant = process.alloc(num_qubits)
    H(qubits)
    for _ in range(int(sqrt(2 ** num_qubits) * pi / 4)):
        phase_oracle(qubits)
        diffuser(qubits)
    return measure(qubits).get()


def main() -> None:
    target: int = int(input("Enter target (binary): "), 2)
    print(f"Grover's algorithm found {
        bin(grover(phase_oracle(target), target.bit_length()))[2:]
    }")


if __name__ == "__main__":
    main()
