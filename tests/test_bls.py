from hashlib import sha256

import pytest

from hsms.bls12_381 import BLSPublicKey, BLSSecretExponent, BLSSignature


def try_stuff(g):

    m1 = g + g
    m2 = m1 * 2
    assert m2 == m1 + m1
    assert m2 == 2 * m1
    h2 = m2 * 1
    assert bytes(m2) == bytes(h2)
    assert h2 == 1 * m2
    assert m2 * 0 == BLSPublicKey.zero()
    assert 0 * m2 == BLSPublicKey.zero()

    m4 = m2 + m2
    m9 = m4 + m4 + m1
    assert m1 * 9 == m9
    assert 9 * m1 == m9
    m3 = m2 + m1
    assert m9 == m3 + m3 + m3

    for s in [m1, m2, m3, m4, m9]:
        b = s.as_bech32m()
        assert s == BLSPublicKey.from_bech32m(b)


def test_bls_public_key():
    gen = BLSPublicKey.generator()
    assert bytes(gen).hex() == (
        "97f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a1"
        "4e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb"
    )
    zero = BLSPublicKey.zero()
    assert bytes(zero).hex() == "c" + ("0" * 95)

    # when we multiply by the generator, we use a different code path
    # to make it hard to shoot yourself in the timing-attack food

    # so we test with a generator a few non-generators
    try_stuff(gen)

    my_generator = gen + gen
    try_stuff(my_generator)

    for s in (2, 7**35, 11**135, 13**912):
        try_stuff(gen * s)

    with pytest.raises(ValueError):
        BLSPublicKey.from_bech32m("foo")


def test_bls_secret_exponent():
    se_m = BLSSecretExponent.from_seed(b"foo")
    ev = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
    assert bytes(se_m).hex() == ev

    se5 = BLSSecretExponent.from_int(5)
    assert int(se5) == 5
    k = int(se_m)
    assert k == int(ev, 16)
    assert se5 + se_m == k + 5

    zero = BLSSecretExponent.zero()
    assert int(zero) == 0
    assert se_m + zero == se_m

    for s in [se_m, se5, zero]:
        b = s.as_bech32m()
        assert s == BLSSecretExponent.from_bech32m(b)

    ev = "31f6283bc95a37bee2053ab2b57a88606b948aea646adb47dc463fd8f465e9a7"
    child = se5.child(10)
    assert bytes(child).hex() == ev

    # check that derivation works before casting to pubkey or after
    pse5 = se5.public_key()
    p_child = pse5.child(10)
    assert p_child == child.public_key()

    ev = "49a56bb020d2879c50f7f88de1b511e0bb6eeaa1c160dd5e61f4d281af5a0a9c"
    child = se5.hardened_child(10)
    assert bytes(child).hex() == ev

    ev = 768461592
    assert se5.fingerprint() == ev
    assert se5.public_key().fingerprint() == ev

    with pytest.raises(ValueError):
        BLSSecretExponent.from_bech32m("foo")


def test_bls_signature():
    se5 = BLSSecretExponent.from_int(5)
    message_hash = sha256(b"foo").digest()
    sig = se5.sign(message_hash)
    ev = (
        "8af37ffbe5be8977c8a02c492ef242d4b911f1cefdbbe20560908b6e9aaf6ee39c1e9f64b838c1ccbe45d5f88f9a190a"
        "001613eafc47ed2a6a4abeb3791d861796a6b493c7b7d6bdfa5b5e97fbf4d4389101a0fedb23385fe42fa1d0865c4d0f"
    )
    assert bytes(sig).hex() == ev

    p5 = se5.public_key()
    aggsig_pair = BLSSignature.aggsig_pair(p5, message_hash)
    assert sig.validate([aggsig_pair])

    zero = BLSSignature.zero()
    assert sig + zero == sig

    se7 = BLSSecretExponent.from_int(7)
    se12 = BLSSecretExponent.from_int(12)

    p12 = se12.public_key()

    # do some fancy signing
    sig5 = se5.sign(message_hash, final_public_key=p12)
    sig7 = se7.sign(message_hash, final_public_key=p12)
    sig12 = se12.sign(message_hash)
    assert sig5 + sig7 == sig12

    ev = (
        "93e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e"
        "024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb8"
    )
    assert bytes(BLSSignature.generator()).hex() == ev
