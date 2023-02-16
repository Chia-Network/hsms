import blspy


GROUP_ORDER = (
    52435875175126190479447740508185965837690552500527637822603658699938581184513
)


def private_key_from_int(secret_exponent: int) -> blspy.PrivateKey:
    secret_exponent %= GROUP_ORDER
    blob = secret_exponent.to_bytes(32, "big")
    return blspy.PrivateKey.from_bytes(blob)


def public_key_from_int(secret_exponent: int) -> blspy.G1Element:
    return private_key_from_int(secret_exponent).get_g1()
