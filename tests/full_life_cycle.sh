#!/bin/sh

for N in 1 2
do
  if [ ! -f ${N}.se ]
  then
    hsmgen > ${N}.se
    rm -f ${N}.pub
  fi
  if [ ! -f ${N}.pub ]
  then
    hsmpk $(cat ${N}.se) > ${N}.pub
  fi
done

hsm_test_spend -m 200 $(cat 1.pub) $(cat 2.pub) > unsigned-test-spend.qri
hsm_test_spend -n -m 200 $(cat 1.pub) $(cat 2.pub) > unsigned-test-spend-unchunked.qri

cat unsigned-test-spend.qri | hsms -y 1.se > sig.1
cat unsigned-test-spend.qri | hsms -y 2.se > sig.2

hsmmerge unsigned-test-spend-unchunked.qri $(cat sig.1) $(cat sig.2) > spendbundle.hex

hsm_dump_sb spendbundle.hex


