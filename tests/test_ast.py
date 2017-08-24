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

from pytest import mark
from whitfield import ast

hex = [
    ["0x1234", 0x1234],
    ["0x12345678901234567890", 0x12345678901234567890],
    ["0x1 234", 0x1234],
    ["0x12 345 678 901 234 567 890", 0x12345678901234567890],
]

dec = [
    ["1234", 1234],
    ["12345678901234567890", 12345678901234567890],
    ["1 234", 1234],
    ["12 345 678 901 234 567 890", 12345678901234567890],
]

idn = [
    "abc",
    "ab0",
    "ab_",
    "a0_",
    mark.xfail("0bc"),
    mark.xfail("!ab"),
    mark.xfail("_ab"),
]

exp = [
    ["1", 1],
    ["a", "a"],

    ["1 @ b",     [1, "@", "b"]],
    ["1 * b",     [1, "*", "b"]],
    ["1 / b",     [1, "/", "b"]],
    ["1 + b",     [1, "+", "b"]],
    ["1 - b",     [1, "-", "b"]],

    ["1 @ b @ 3", [1, "@", ["b", "@", 3]]],
    ["1 @ b * 3", [[1, "@", "b"], "*", 3]],
    ["1 @ b / 3", [[1, "@", "b"], "/", 3]],
    ["1 @ b + 3", [[1, "@", "b"], "+", 3]],
    ["1 @ b - 3", [[1, "@", "b"], "-", 3]],

    ["1 * b @ 3", [1, "*", ["b", "@", 3]]],
    ["1 * b * 3", [[1, "*", "b"], "*", 3]],
    ["1 * b / 3", [[1, "*", "b"], "/", 3]],
    ["1 * b + 3", [[1, "*", "b"], "+", 3]],
    ["1 * b - 3", [[1, "*", "b"], "-", 3]],

    ["1 / b @ 3", [1, "/", ["b", "@", 3]]],
    ["1 / b * 3", [[1, "/", "b"], "*", 3]],
    ["1 / b / 3", [[1, "/", "b"], "/", 3]],
    ["1 / b + 3", [[1, "/", "b"], "+", 3]],
    ["1 / b - 3", [[1, "/", "b"], "-", 3]],

    ["1 + b @ 3", [1, "+", ["b", "@", 3]]],
    ["1 + b * 3", [1, "+", ["b", "*", 3]]],
    ["1 + b / 3", [1, "+", ["b", "/", 3]]],
    ["1 + b + 3", [[1, "+", "b"], "+", 3]],
    ["1 + b - 3", [[1, "+", "b"], "-", 3]],

    ["1 - b @ 3", [1, "-", ["b", "@", 3]]],
    ["1 - b * 3", [1, "-", ["b", "*", 3]]],
    ["1 - b / 3", [1, "-", ["b", "/", 3]]],
    ["1 - b + 3", [[1, "-", "b"], "+", 3]],
    ["1 - b - 3", [[1, "-", "b"], "-", 3]],

    ["1 @ (b @ 3)", [1, "@", ["b", "@", 3]]],
    ["1 @ (b * 3)", [1, "@", ["b", "*", 3]]],
    ["1 @ (b / 3)", [1, "@", ["b", "/", 3]]],
    ["1 @ (b + 3)", [1, "@", ["b", "+", 3]]],
    ["1 @ (b - 3)", [1, "@", ["b", "-", 3]]],

    ["1 * (b @ 3)", [1, "*", ["b", "@", 3]]],
    ["1 * (b * 3)", [1, "*", ["b", "*", 3]]],
    ["1 * (b / 3)", [1, "*", ["b", "/", 3]]],
    ["1 * (b + 3)", [1, "*", ["b", "+", 3]]],
    ["1 * (b - 3)", [1, "*", ["b", "-", 3]]],

    ["1 / (b @ 3)", [1, "/", ["b", "@", 3]]],
    ["1 / (b * 3)", [1, "/", ["b", "*", 3]]],
    ["1 / (b / 3)", [1, "/", ["b", "/", 3]]],
    ["1 / (b + 3)", [1, "/", ["b", "+", 3]]],
    ["1 / (b - 3)", [1, "/", ["b", "-", 3]]],

    ["1 + (b @ 3)", [1, "+", ["b", "@", 3]]],
    ["1 + (b * 3)", [1, "+", ["b", "*", 3]]],
    ["1 + (b / 3)", [1, "+", ["b", "/", 3]]],
    ["1 + (b + 3)", [1, "+", ["b", "+", 3]]],
    ["1 + (b - 3)", [1, "+", ["b", "-", 3]]],

    ["1 - (b @ 3)", [1, "-", ["b", "@", 3]]],
    ["1 - (b * 3)", [1, "-", ["b", "*", 3]]],
    ["1 - (b / 3)", [1, "-", ["b", "/", 3]]],
    ["1 - (b + 3)", [1, "-", ["b", "+", 3]]],
    ["1 - (b - 3)", [1, "-", ["b", "-", 3]]],

    ["1 * b - 3 @ c / 5", [[1, "*", "b"], "-", [[3, "@", "c"], "/", 5]]],
]

asn = [[f"x = {e[0]};", ["x", e[1]]] for e in exp] + [
    ["x = 7;", ["x", 7]],
    mark.xfail(["0x = 7;", ["x", 7]]),
    mark.xfail(["_x = 7;", ["x", 7]]),
]

arg = [[x, [x]] for x in idn if isinstance(x, str)] \
    + [[f"{x}, {x}", [x, x]] for x in idn if isinstance(x, str)] \
    + [mark.xfail([f"{x} {x}", [x, x]]) for x in idn if isinstance(x, str)]

fnc = [
    mark.xfail(["0foo(a)(b){ b = a; }", {}]),
    mark.xfail(["_foo(a)(b){ b = a; }", {}]),
    mark.xfail(["foo(a)(b){}", {}]),
    ["foo(a)(b) { b = a; }",
     {"name": "foo", "args": ["a"], "rets": ["b"], "body": [["b", "a"]]}],
    ["foo(a, b)(c, d) { c = a; d = a + b - 7; }",
     {"name": "foo", "args": ["a", "b"], "rets": ["c", "d"],
      "body": [["c", "a"], ["d", [["a", "+", "b"], "-", 7]]]}],
]

imp = [
    "foo",
    "bar",
    "foo.bar",
    "foo_bar",
    "foo-bar",
    "foo/bar",
    "../foo",
    "./f00",
    "../../foo/b4r",
    mark.xfail("foo."),
    mark.xfail("bar/"),
]

bdy = [
    ["import foo;", ["foo"]],
    ["c = 7; a = 12;", [["c", 7], ["a", 12]]],
    ["foo(a)(b) { b = a; }",
     [{"name": "foo", "args": ["a"], "rets": ["b"], "body": [["b", "a"]]}]],
    ["import bar; c = 7; foo(a)(b) { b = a; }",
     ["bar", ["c", 7],
      {"name": "foo", "args": ["a"], "rets": ["b"], "body": [["b", "a"]]}]],
]

fld = [
    ["127", 127],
    ["2 @ 255 - 19", [[2, "@", 255], "-", 19]]
]

wht = [[f"field {f[0]}; {b[0]}", {"limit": f[1], "items": b[1]}]
        for b in bdy for f in fld]


@mark.parametrize("tst,exp", hex)
def test_hex(tst, exp):
    assert ast.HEX.parseString(tst)[0] == exp


@mark.parametrize("tst,exp", dec)
def test_dec(tst, exp):
    assert ast.DEC.parseString(tst)[0] == exp


@mark.parametrize("tst,exp", hex + dec)
def test_num(tst, exp):
    assert ast.NUM.parseString(tst)[0] == exp


@mark.parametrize("tst", idn)
def test_idn(tst):
    assert ast.IDN.parseString(tst)[0] == tst


@mark.parametrize("tst,exp", exp)
def test_exp(tst, exp):
    assert ast.EXP.parseString(tst).asList()[0] == exp


@mark.parametrize("tst,exp", asn)
def test_asn(tst, exp):
    assert ast.ASN.parseString(tst).asList()[0] == exp


@mark.parametrize("tst,exp", arg)
def test_arg(tst, exp):
    assert ast.ARG.parseString(tst).asList()[0] == exp


@mark.parametrize("tst,exp", fnc)
def test_fnc(tst, exp):
    assert ast.FNC.parseString(tst).asList()[0] == exp


@mark.parametrize("tst", imp)
def test_imp(tst):
    assert ast.IMP.parseString(f"import {tst};").asList()[0] == tst


@mark.parametrize("tst,exp", bdy)
def test_bdy(tst, exp):
    assert ast.BDY.parseString(tst).asList()[0] == exp


@mark.parametrize("tst,exp", fld)
def test_fld(tst, exp):
    assert ast.FLD.parseString(tst).asList()[0] == exp


@mark.parametrize("tst,exp", wht)
def test_fld(tst, exp):
    assert ast.WHT.parseString(tst).asList()[0] == exp
