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

hsm_test_spend -m 200 1.pub 2.pub > unsigned-test-spend.qri

echo $(cat unsigned-test-spend.qri) | hsms -y 1.se > sig.1
echo $(cat unsigned-test-spend.qri) | hsms -y 2.se > sig.2

hsmmerge unsigned-test-spend.qri $(cat sig.1) $(cat sig.2) > spendbundle.hex

hsm_dump_sb spendbundle.hex


