HSMS: hardware security module software/simulator

This project is intended to run on an air-gapped computer to sign chia spends using bls12_381 keys.


Install
-------

`$ pip install -e .`


enscons
-------

This package uses [enscons](https://github.com/dholth/enscons)
which uses [SCons](https://scons.org/) to build rather than the commonly used `setuptools`.
