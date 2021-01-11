#!/bin/sh

set -e -v

if [ -n ${TRAVIS_SSH_SECRET} ]; then
    SSH_ID_ARG="-i ${HOME}/id_rsa"
    cat <<EOF | openssl enc -d -aes-256-cbc -pbkdf2 -pass env:TRAVIS_SSH_SECRET -a -out ~/id_rsa
U2FsdGVkX1+mQa03lh5LKvgKncOIy0gP3yYw+RY/J91NoVNQJPjGsKmm1AkK5v6b
j7Gn/upyr63LBjytCWbRZ/GW7B9TBu+w+mDYV1T01xo5HCD4kUPcN71oTgIz2lR5
I76Tsx5IZK3Q+DZkJZXPKkyoLUZPx6/+GZ58fi2Uo/Q3EopN1BjjCpGlkU34wJck
fWgbCC5oeBoFmiffuWzmRFHv8nUzh0pjNAVH1RFt+2Zm36btBnJG1UYRRb0RVHLx
h79LnnxU3tf5bHWGlZ4w7YOnmFiCW1l3EBFQLCP4AElG/Vo+SunG4O34G+cPGOp4
CG0FibyrtoJV5/4/jKpzkY+f6UJhRKdBZXGJprWlp2ZJ8tW0dvEgQ6MZO24ZWfUR
wlYjp9jrEf6/3b2i3y/wMqwde9r8uBdvXZiZTshm46h7KkSGD1CUKbLCTbgEZ719
mPDrjS4y4Gh/ooURmcjzyzkjS72lBgtzDtS2R7Em1bkI0f+QwE+NvknBT+uPFEL6
RtHPUEBo2wJJYHibn1X05Gqr6STkeqXx+FkTN2E80Ii30ixqp6F02y57eDESN7zQ
P9m9LBmv67Zf20IwizZHkw==
EOF
    chmod 600 ~/id_rsa
fi

ssh ${SSH_ID_ARG} -oStrictHostKeyChecking=no build@build.liqd.net deploy a4_kosmo master
