from dataclasses import dataclass
from typing import List, Optional

from clvm.casts import int_from_bytes

from hsms.streamables import bytes32, Program
from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent
from hsms.util.clvm_serialization import (
    transform_list,
    transform_dict,
    transform_dict_by_key,
)


@dataclass
class PathHint:
    fingerprint: bytes  # length == 4
    path: List[int]

    def to_clvm(self) -> Program:
        program_pairs = (self.fingerprint, self.path)
        return Program.to(program_pairs)

    @classmethod
    def from_clvm(cls, program: Program) -> "PathHint":
        fingerprint = int_from_bytes(program.pair[0].atom)
        path = transform_list(program.pair[1], lambda x: int_from_bytes(x.atom))
        return cls(fingerprint, path)


SR_TRANSFORMS = dict(
    m=lambda x: bytes32(x.atom),
    p=lambda x: BLSPublicKey.from_bytes(x.atom),
    h=lambda x: PathHint.from_clvm(x),
    f=lambda x: BLSPublicKey.from_bytes(x.atom),
)


@dataclass
class SigningRequest:
    message: bytes32
    partial_pubkey: BLSPublicKey
    final_pubkey: Optional[BLSPublicKey]
    path_hints: List[PathHint]

    @classmethod
    def from_bytes(cls, blob: bytes) -> bytes:
        return cls.from_clvm(Program.from_bytes(blob))

    def __bytes__(self) -> bytes:
        return bytes(Program.to(self.to_clvm()))

    def to_clvm(self) -> Program:
        program_pairs = [
            ("m", self.message),
            ("p", bytes(self.partial_pubkey)),
            ("h", self.path_hints.to_clvm()),
        ]
        if self.final_pubkey:
            program_pairs.append(("f", bytes(self.final_pubkey)))
        return Program.to([list(_) for _ in program_pairs])

    @classmethod
    def from_clvm(cls, program: Program) -> "SigningRequest":
        d = transform_dict(program, transform_dict_by_key(SR_TRANSFORMS))
        return cls(d["m"], d["p"], d.get("f"), d["h"])
