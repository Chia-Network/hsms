import hashlib
import readline  # noqa
import json
import os
from pathlib import Path

from validation.consensus import (
    conditions_dict_for_coin_spend,
    hash_key_pairs_for_conditions_dict,
)

from bls12_381 import BLSPrivateKey

from .pst import PartiallySignedTransaction


def create_private_wallet(path, entropy_f):
    """
    Invoke the entropy function and create a new private wallet as a json
    file with the given path.
    """
    seed = hashlib.sha256(entropy_f()).digest()
    private_hd_key = BLSPrivateKey.from_seed(seed)
    d = dict(key=bytes(private_hd_key).hex())
    with open(path, "w") as f:
        json.dump(d, f)


def load_private_wallet(path):
    """
    Load a json file with the given path as a private wallet.
    """
    d = json.load(open(path))
    blob = bytes.fromhex(d["key"])
    return BLSPrivateKey.from_bytes(blob)


def default_entropy():
    """
    Call the os entropy function.
    """
    return os.urandom(1024)


def generate_signatures(pst, private_wallet):
    """
    For a given unfinalized SpendBundle, look at the hints to see if the given
    private wallet can generate any signatures, and generate them.
    """
    hd_hints = pst.get("hd_hints")
    sigs = {}
    private_fingerprint = private_wallet.fingerprint()

    for coin_solution in pst.get("coin_spends"):
        # run maximal_solution and get conditions
        conditions_dict = conditions_dict_for_coin_spend(coin_solution)
        # look for AGG_SIG conditions
        hkp_list = hash_key_pairs_for_conditions_dict(conditions_dict)
        # see if we have enough info to build signatures
        for aggsig_pair in hkp_list:
            pub_key = aggsig_pair.public_key
            message_hash = aggsig_pair.message_hash
            fp = pub_key.fingerprint()
            if fp in hd_hints:
                hint = hd_hints[fp]
                if private_fingerprint == hint.get("hd_fingerprint"):
                    private_key = private_wallet.private_child(hint.get("index"))
                    signature = private_key.sign(message_hash)
                    sigs[aggsig_pair] = signature
    return list(sigs.values())


def get_pst():
    """
    UI to accept an unfinalized SpendBundle, create signatures, and display them.
    """
    while True:
        pst_hex = input("enter partially-signed transaction hex> ")
        if len(pst_hex) == 0:
            return None
        try:
            blob = bytes.fromhex(pst_hex)
            return PartiallySignedTransaction.from_bytes(blob)
        except Exception as ex:
            print("exception %s" % ex)
        pst_hex = None


def main():
    wallet_name = input("wallet name> ")
    PATH = Path("private.%s.json" % wallet_name)
    if not PATH.exists():
        create_private_wallet(PATH, default_entropy)
    private_wallet = load_private_wallet(PATH)
    print("public hd is %s" % private_wallet.public_key())

    pst = get_pst()
    if pst:
        sigs = generate_signatures(pst, private_wallet)
        print("SIGNATURES:")
        for sig in sigs:
            print(bytes(sig).hex())


if __name__ == "__main__":
    main()
