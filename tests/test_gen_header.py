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

from whitfield.gen.header import HeaderGenerator
from pytest import mark

ast = {
    "name": "foo",
    "limit": 2 ** 255 - 19,
    "items": [
        ["x", 7],
        {"name": "bar", "args": ["x"], "rets": ["y"]}
    ]
}

out = """#pragma once
typedef unsigned char wht_foo_t[32];
extern wht_foo_t wht_foo_x;
void wht_foo_bar(const wht_foo_t x, wht_foo_t y);"""


@mark.parametrize("tst,exp", [
    [ast, out],
])
def test_gen_header(tst, exp):
    txt = ""
    for chunk in HeaderGenerator()(ast):
        txt += chunk + "\n"
    assert txt.strip() == exp
