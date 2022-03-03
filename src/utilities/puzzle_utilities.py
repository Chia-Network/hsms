from binascii import hexlify
import string
from chiasim.hashable import ProgramHash, BLSPublicKey, BLSSignature


def pubkey_format(pubkey):
    if isinstance(pubkey, str):
        if len(pubkey) == 96:
            if not check_string_is_hex(pubkey):
                raise ValueError
            ret = "0x" + pubkey
        elif len(pubkey) == 98:
            if not check_string_is_hex(pubkey[2:95]):
                raise ValueError
            if not pubkey[0:2] == "0x":
                raise ValueError
            ret = pubkey
        else:
            raise ValueError
    elif hasattr(pubkey, 'decode'):  # check if serialized
        ret = serialized_key_to_string(pubkey)
    elif isinstance(pubkey, BLSPublicKey):
        ret = serialized_key_to_string(bytes(pubkey))
    return ret


def secret_hash_format(secret_hash):
    if isinstance(secret_hash, str):
        if len(secret_hash) == 64:
            if not check_string_is_hex(secret_hash):
                raise ValueError
            ret = "0x" + secret_hash
        elif len(secret_hash) == 66:
            if not check_string_is_hex(secret_hash[2:67]):
                raise ValueError
            if not secret_hash[0:2] == "0x":
                raise ValueError
            ret = secret_hash
        else:
            raise ValueError
    return ret


def serialized_key_to_string(pubkey):
    return "0x%s" % hexlify(pubkey).decode('ascii')


def check_string_is_hex(value):
    for letter in value:
        if letter not in string.hexdigits:
            return False
    return True


def puzzlehash_from_string(puzhash):
    if hasattr(puzhash, 'decode'):  # check if serialized
        puz = puzhash.decode("utf-8")
    else:
        puz = puzhash
    try:
        ret = ProgramHash(bytes.fromhex(puz))
    except Exception:
        raise Exception
    return ret


def pubkey_from_string(pubkey):
    try:
        ret = PublicKey.from_bytes(bytes.fromhex(pubkey))
    except Exception:
        raise Exception
    return ret


def signature_from_string(signature):
    try:
        sig = BLSSignature.from_bytes(bytes.fromhex(signature))
    except Exception:
        raise Exception
    return sig


def BLSSignature_from_string(signature):
    try:
        sig = BLSSignature(bytes.fromhex(signature))
    except Exception:
        raise Exception
    return sig


"""
Copyright 2018 Chia Network Inc
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
