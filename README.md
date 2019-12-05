# adhocracy+

[adhocracy.plus](https://adhocracy.plus/) is a free Open-Source participation platform maintained and primarily developed by Liquid Democracy e.V.. It is based on [adhocracy 4](https://github.com/liqd/adhocracy4) and [Django](https://github.com/django/django).

[![Build Status](https://travis-ci.org/liqd/a4-product.svg?branch=master)](https://travis-ci.org/liqd/a4-product)
[![Coverage Status](https://coveralls.io/repos/github/liqd/adhocracy-plus/badge.svg?branch=master)](https://coveralls.io/github/liqd/adhocracy-plus?branch=master)

## Getting started

adhocracy+ is designed to make online participation easy and accessible to everyone. It can be used on our SaaS-platform or installed on your own servers. How to get started on our platform is explained [here](https://adhocracy.plus/info/start/).

### Installation

Requirements:
*   nodejs (+ npm)
*   python 3.x (+ venv + pip)
*   libmagic
*   libjpeg
*   libpq (only if postgres should be used)

Installation:
    git clone https://github.com/liqd/adhocracy-plus.git
    cd adhocracy-plus
    make install
    make fixtures

Check if it works:
    make test

Check it out:
    make watch

Go to '''http://localhost:8004/''' and login with admin@liqd.net | password

### Contributing
If you found an issue or want to contribute check out [contributing](https://github.com/liqd/adhocracy-plus/blob/master/docs/contributing.md)

## Security
We care about security. So, if you find any issues concerning security, please send us an email at info [at] liqd [dot] net.
