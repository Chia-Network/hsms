import math

from typing import List, Tuple


def b2a_chunks(blob: bytes, bytes_per_chunk: int) -> List[bytes]:
    total_len = len(blob)

    bytes_per_chunk -= 2
    num_chunks = math.ceil(total_len / bytes_per_chunk)
    if num_chunks > 256:
        raise ValueError("Cannot chunk a blob into more than 256 chunks")

    bundle_chunks = [
        blob[i : min(i + bytes_per_chunk, total_len)]
        + bytes(
            [int(i / bytes_per_chunk), num_chunks - 1]
        )  # Indication of the order of the blocks
        for i in range(0, total_len, bytes_per_chunk)
    ]

    return bundle_chunks


def a2b_chunks(chunks: List[bytes]) -> bytes:
    sorted_chunks = sorted(chunks, key=lambda c: c[-2])
    bare_chunks = [c[:-2] for c in sorted_chunks]
    return b"".join(bare_chunks)


class ChunkAssembler:
    chunks: List[bytes]

    def __init__(self):
        self.chunks = []

    def add_chunk(self, chunk: bytes):
        if chunk in self.chunks:
            return
        if len(self.chunks) > 0 and self.chunks[0][-1] != chunk[-1]:
            raise ValueError("chunk is part of a different set")
        indexes_seen = [c[-2] for c in self.chunks]
        if chunk[-2] in indexes_seen:
            raise ValueError("chunk conflicts with already added chunk")
        else:
            self.chunks.append(chunk)
            return

    def is_assembled(self) -> bool:
        if len(self.chunks) > 0 and self.chunks[0][-1] == len(self.chunks) - 1:
            return True
        else:
            return False

    def status(self) -> Tuple[int, int]:
        """Returns: (amount of chunks we have, amount of chunks total)"""
        if len(self.chunks) == 0:
            return 0, 0
        else:
            return len(self.chunks), self.chunks[0][-1] + 1

    def assemble(self) -> bytes:
        return a2b_chunks(self.chunks)
