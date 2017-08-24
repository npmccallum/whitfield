#
# Copyright: 2017 Red Hat, Inc.
# Author: Nathaniel McCallum <npmccallum@redhat.com>
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from pyparsing import *
from string import hexdigits


def exp_parse(x):
    x = x[0]
    while not isinstance(x, (int, str)) and len(x) > 3:
        x = [x[:3]] + x[3:]
    return [x]


def fnc_parse(x):
    keys = ["name", "args", "rets", "body"]
    return dict(zip(keys, x.asList()))


def wht_parse(x):
    keys = ["limit", "items"]
    return dict(zip(keys, x.asList()))


OPS = [
    ("@",          2, opAssoc.RIGHT),
    (oneOf("* /"), 2, opAssoc.LEFT),
    (oneOf("+ -"), 2, opAssoc.LEFT),
]

HEX = Suppress("0x") + Word(hexdigits + " \t\n")
HEX = HEX.setParseAction(lambda t: int(''.join(t[0].split()), 16))
DEC = Word(nums + " \t\n")
DEC = DEC.setParseAction(lambda t: int(''.join(t[0].split())))
NUM = HEX | DEC

IDN = Word(alphas, alphanums + '_')
EXP = infixNotation(NUM | IDN, OPS).setParseAction(exp_parse)
LIT = infixNotation(NUM, OPS).setParseAction(exp_parse)

ASN = Group(IDN + Suppress('=') + EXP + Suppress(';'))

ARG = Group(delimitedList(IDN))
LST = Suppress('(') + ARG + Suppress(')')
FNC = IDN + LST + LST + Suppress('{') + Group(OneOrMore(ASN)) + Suppress('}')
FNC = FNC.setParseAction(fnc_parse)

IMP = Regex(r"[a-zA-Z0-9/._-]+[a-zA-Z0-9_-]")
IMP = Suppress("import") + IMP + Suppress(";")
BDY = Group(OneOrMore(IMP | ASN | FNC))

FLD = Suppress("field") + LIT + Suppress(";")

WHT = (FLD + BDY).setParseAction(wht_parse)
