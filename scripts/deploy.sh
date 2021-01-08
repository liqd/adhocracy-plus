#!/bin/sh

set -e -v

if [ -n ${TRAVIS_SSH_SECRET} ]; then
    SSH_ID_ARG="-i ${HOME}/id_rsa"
    cat <<EOF | openssl enc -d -aes-256-cbc -pbkdf2 -pass env:TRAVIS_SSH_SECRET -a -out ~/id_rsa
U2FsdGVkX18DO2nMk3k0/oPRl+o9zuQe/XY0LKPQlXbNPIEtKdv43u9fCUqd5xwW
kS4zYEkLLTHeqKv8H2SH9zQ8IvZyXg7CVmkzXbxXkp1kWU/p/O1CP7eAJr8cdlg/
TwXwHFw03QsszK764lq8SRTpRxsLJBw5bhO5oDD2/oVD4hZi14IURez1TeRj3+sP
dPN/Ix25iK8kWFXMDyfbZbNdH3DwN5bP/MqCSAYFe8xZSxLBtHYY+AxaDnkHXvYS
i9tiejUL3QH9+Lazn5PQFs06Wc+A11TGKkusKv9GbRdF8RzpYsTospjN1H2P61sp
JV4fgPuVclGgBgRZ2m3Htw/P+PoJDcbP4YiG/ITLIHrg5AnpyPXdOrzVKLUHmsZk
rRj6kPt3hpGhPoOCTDI0hfB0KGhgM/43OKWy2HMAECC6zGQjh+89FyFer/c+FQsq
dVmsNHZxMXQJuh4vvOqNvzjq1vxSHajQ6GmlemhHz4rQr7bZB3Xsb7ITw1nvuT4g
oyXHdRzZlschdUhDs1+4X+5I1o6hL3wK3S/QtdX/dyA6FIzbgHZKFQDIk43DsusV
Tnc+bZV8UhJN+H+gK0gO4Q==
EOF
    chmod 600 ~/id_rsa
fi

ssh ${SSH_ID_ARG} -oStrictHostKeyChecking=no build@build.liqd.net deploy a4_kosmo master
