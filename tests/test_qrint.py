from hsms.util.qrint_encoding import a2b_qrint, b2a_qrint, b2a_qrint_payload

from .generate import bytes32_generate

MAX_SIZE = 8192
BIG_BLOB = bytes([bytes32_generate(_)[0] for _ in range(MAX_SIZE)])


def check_b2a(data, expected_value=None):
    b = b2a_qrint(data)
    d = a2b_qrint(b)
    assert data == d
    if expected_value is not None:
        assert b == expected_value


def test_b2a_qrint():
    check_b2a(b"", "2")
    check_b2a(bytes([1]), "1002")
    check_b2a(bytes([2]), "1004")
    check_b2a(bytes([200]), "1620")
    check_b2a(bytes([1, 200]), "1003440")
    check_b2a(bytes([187, 200]), "1567440")
    check_b2a(
        b"the quick brown fox jumps over the lazy dogs",
        "339059973767614080397578834113941517634623454993421264001026867145388026209696872339324742682190340016362470400",
    )
    RANGE = list(range(0, 800)) + list(range(800, MAX_SIZE, 5))
    for size in RANGE:
        start = (MAX_SIZE - size) // 2
        blob = BIG_BLOB[start : start + size]
        check_b2a(blob)


def print_sizes():
    long_blob = bytes([_ % 256 for _ in range(4000)])
    d = []
    for size in range(2, 96):
        b = b2a_qrint_payload(long_blob, size)
        bits_used = ((len(b) + 2) // 3) * 10
        bytes_used = (bits_used + 7) // 8
        print(len(b), size)
        d.append((len(b), size, bytes_used))
    d.sort()
    print(d)
