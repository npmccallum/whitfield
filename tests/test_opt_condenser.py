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

from whitfield.opt.condenser import *
from whitfield import ast
from pytest import mark

LIMIT = 2 ** 255 - 19


@mark.parametrize("tst,exp", [
    ["field 2 @ 255 - 19;", f"field {LIMIT};"],
])
def test_limit_condenser(tst, exp):
    t = {"limit": ast.FLD.parseString(tst).asList()[0]}
    e = {"limit": ast.FLD.parseString(exp).asList()[0]}
    LimitCondenser()(t)
    assert t == e


@mark.parametrize("tst,exp", [
    ["a = 5;",                "a = 5;"],
    ["a = 5 + 5;",            "a = 10;"],
    ["a = 5; b = a + 5;",     "a = 5; b = 10;"],
    [f"c = {LIMIT-1} + 3;",   "c = 2;"],
    mark.xfail(["a = b;",     "a = b;"]),
    mark.xfail(["b = a + 5;", "b = 10;"]),
])
def test_constants_condenser(tst, exp):
    t = {"limit": LIMIT, "items": ast.BDY.parseString(tst).asList()[0]}
    e = {"limit": LIMIT, "items": ast.BDY.parseString(exp).asList()[0]}
    ConstantCondenser()(t)
    assert t == e


@mark.parametrize("tst,exp", [
    ["a = 5; foo(x, y)(z) { z = x + y; }",
     "a = 5; foo(x, y)(z) { z = x + y; }"],
    ["a = 5; foo(x, y)(z) { z = x + a; }",
     "a = 5; foo(x, y)(z) { z = x + 5; }"],
    ["a = 5; foo(x, y)(z) { z = 6 + a; }",
     "a = 5; foo(x, y)(z) { z = 11; }"],
    ["a = 5; foo(x, y)(z) { t = x + a; z = t + y; }",
     "a = 5; foo(x, y)(z) { t = x + 5; z = t + y; }"],
    ["a = 5; foo(x, y)(z) { t = 6 + a; z = t + y; }",
     "a = 5; foo(x, y)(z) { z = 11 + y; }"],
    ["A = 5; foo(a, b)(x, y) { x = a + A; y = b + A; }",
     "A = 5; foo(a, b)(x, y) { x = a + 5; y = b + 5; }"],
])
def test_function_condenser(tst, exp):
    t = {"limit": LIMIT, "items": ast.BDY.parseString(tst).asList()[0]}
    e = {"limit": LIMIT, "items": ast.BDY.parseString(exp).asList()[0]}
    FunctionCondenser()(t)
    assert t == e
