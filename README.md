# adhocracy+

Participation platform by Liquid Democracy

[![Build Status](https://travis-ci.org/liqd/a4-product.svg?branch=master)](https://travis-ci.org/liqd/a4-product)

## Codebase

This project is based on <https://github.com/liqd/a4-meinberlin/>

It has been derived from commit
[7de114193f1eb4d016a67603cc860476c2463714](https://github.com/liqd/a4-meinberlin/commit/7de114193f1eb4d016a67603cc860476c2463714)
on 13.07.2017

## Requirements

*   nodejs (+ npm)
*   python 3.x (+ venv + pip)
*   libmagic
*   libjpeg
*   libpq (only if postgres should be used)

## Installation

    git clone https://github.com/liqd/a4-product.git
    cd a4-product
    make install
    make fixtures
    make watch
