HSMS: hardware security module software/simulator

This project is intended to run on an air-gapped computer to sign chia spends using bls12_381 keys.


Install
-------

`$ pip install -e .`

If on windows, you need one extra package:

`$ pip install pyreadline`


Tools
-----

Command-line tools installed include:

- `hsms` - HSM sim that accepts `UnsignedSpend` objects and produces signatures, full or partial
- `hsmgen` - generate secret keys
- `hsmpk` - show public keys for secret keys
- `hsmmerge` - merge signatures for a multisig spend
- `qrint` - convert binary to/from qrint ascii

For testing & debugging:

- `hsm_test_spend` - create a simple test `UnsignedSpend` multisig spend
- `hsm_dump_sb` - debug utility to dump information about a `SpendBundle`
